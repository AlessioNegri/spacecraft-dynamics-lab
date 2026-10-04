import astropy.time as t
import astropy.units as u
import asyncio
import numpy as np
import typing

import schemas.common as common
import schemas.circular_restricted_three_body_problem_schema as schema

from common.app_data import AppData
from common.web_socket_manager import WebSocketManager

import astro.bodies as bd
import astro.circular_restricted_three_body_problem as cr3bp

async def cr3bp_analysis(payload: schema.SimulationModel, wsm: WebSocketManager, data: AppData) -> dict:
    """Asynchronous execution of CR3BP propagation.

    Args:
        payload (schema.SimulationModel): Simulation data
        wsm (WebSocketManager): Web Socket manager
        data (AppData): Application data

    Returns:
        dict: JSON
    """

    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    def run() -> dict:
        
        gen: typing.Generator[dict, dict, None] = compute_cr3bp(payload, data)

        while True:
            
            try:
                
                update = next(gen)

                asyncio.run_coroutine_threadsafe(
                    wsm.send_json(
                        {
                            "type": update.get("type"),
                            "source": update.get("source"),
                            "counter": update.get("counter"),
                            "total": update.get("total"),
                            "running": update.get("running")
                        }
                    ),
                    loop
                )

                if not update.get("running"): return update

            except StopIteration as exc:
                
                return exc.value

    result = await asyncio.to_thread(run)
    
    return result

def compute_cr3bp(payload: schema.SimulationModel, data: AppData) -> typing.Generator[dict, dict, None]:
    """Compute CR3BP propagation

    Args:
        payload (schema.SimulationModel): Simulation data
        data (AppData): Application data

    Returns:
        typing.Generator[dict, dict, None]: JSON data

    Yields:
        Iterator[typing.Generator[dict, dict, None]]: JSON data
    """
    
    # * Generate timestamps for 1-day steps

    body_1: bd.Attractor = bd.Attractor(payload.body1.lower())
    body_2: bd.Attractor = bd.Attractor(payload.body2.lower())

    step: u.Quantity = 1 * u.day
    
    total: u.Quantity = payload.integrationTime * u.h

    n_full_days: int = int((total.to_value(u.h) // step.to_value(u.h)))
    
    deltas: np.ndarray = np.array([0]) * u.day
    
    for k in range(1, n_full_days + 1):
        
        deltas = np.append(deltas, k * step)

    remainder: u.Quantity = total - n_full_days * step

    if remainder > 0 * u.day:
        
        deltas = np.append(deltas, n_full_days * step + remainder)

    parameters: cr3bp.OrbitParametersCR3BP = cr3bp.Orbit.orbit_parameters(body_1=body_1, body_2=body_2)

    lagrange_point: u.Quantity = get_lagrange_point(parameters=parameters, name=payload.lagrangePoint)
    
    is_eulerian: bool = False
    
    is_lagrangian: bool = False
    
    match payload.lagrangePoint:
        
        case "L1": libration_point: cr3bp.LibrationPoint = cr3bp.LibrationPoint.L1; is_eulerian = True
        case "L2": libration_point: cr3bp.LibrationPoint = cr3bp.LibrationPoint.L2; is_eulerian = True
        case "L3": libration_point: cr3bp.LibrationPoint = cr3bp.LibrationPoint.L3; is_eulerian = True
        case "L4": libration_point: cr3bp.LibrationPoint = cr3bp.LibrationPoint.L4; is_lagrangian = True
        case "L5": libration_point: cr3bp.LibrationPoint = cr3bp.LibrationPoint.L5; is_lagrangian = True
        case _: libration_point: cr3bp.LibrationPoint = cr3bp.LibrationPoint.L1; is_eulerian = True
    
    offset: u.Quantity = np.array([payload.position.x, payload.position.y, payload.position.z], dtype=float) * u.km

    info_data: common.InfoModel = common.InfoModel(source="circular-restricted-three-body-problem",
                                                   counter=0,
                                                   total=deltas.size)

    info_data.running = True
    
    # * Initial conditions
    
    r_0: u.Quantity = lagrange_point + offset
    
    v_0: u.Quantity = np.array([payload.velocity.x, payload.velocity.y, payload.velocity.z], dtype=float) * u.km / u.s
    
    r_0_libration: u.Quantity = offset
    
    v_0_libration: u.Quantity = v_0
    
    r_0_eulerian: u.Quantity = offset
    
    v_0_eulerian: u.Quantity = v_0
    
    r_0_lagrangian: u.Quantity = offset
    
    v_0_lagrangian: u.Quantity = v_0

    position_x: list[float] = []
    position_y: list[float] = []
    position_z: list[float] = []
    
    relative_position_x: list[float] = []
    relative_position_y: list[float] = []
    relative_position_z: list[float] = []
    
    eulerian_position_x: list[float] = []
    eulerian_position_y: list[float] = []
    eulerian_position_z: list[float] = []
    
    lagrangian_position_x: list[float] = []
    lagrangian_position_y: list[float] = []
    lagrangian_position_z: list[float] = []

    orbit: cr3bp.Orbit = cr3bp.Orbit()
    
    # * Iteration
    
    prev_delta: u.Quantity = deltas[0]
    
    for idx, delta in enumerate(deltas[1:]):
        
        # * Stop simulation check
        
        if data.stop_simulation:
            
            info_data.counter = 0
            info_data.running = False
            
            return info_data.model_dump()
        
        # * Propagate orbit and store results
        
        dt: u.Quantity = delta - prev_delta
        
        prev_delta = delta
        
        orbit.init(body_1=body_1, body_2=body_2, position=r_0, velocity=v_0)
        
        result: cr3bp.ResultCR3BP = orbit.propagate_for(delta=t.TimeDelta(dt.to(u.s)))
        
        orbit.init(body_1=body_1, body_2=body_2, position=r_0_libration, velocity=v_0_libration)
        
        result_libration: cr3bp.ResultCR3BP = orbit.propagate_libration_for(delta=t.TimeDelta(dt.to(u.s)),
                                                                            libration_point=libration_point)
        
        if is_eulerian:
            
            orbit.init(body_1=body_1, body_2=body_2, position=r_0_eulerian, velocity=v_0_eulerian)
            
            result_eulerian: cr3bp.ResultCR3BP = orbit.propagate_eulerian_for(delta=t.TimeDelta(dt.to(u.s)),
                                                                              libration_point=libration_point)
        
        if is_lagrangian:
            
            orbit.init(body_1=body_1, body_2=body_2, position=r_0_lagrangian, velocity=v_0_lagrangian)
            
            result_lagrangian: cr3bp.ResultCR3BP = orbit.propagate_lagrangian_for(delta=t.TimeDelta(dt.to(u.s)),
                                                                                  libration_point=libration_point)
        
        if not result.success:
            
            print("Integration error")
            
            info_data.counter = idx
            info_data.running = False
            
            info_data.data =\
            {
                "absolute":
                {
                    "position_x": [0],
                    "position_y": [0],
                    "position_z": [0]
                },
                "relative":
                {
                    "position_x": [0],
                    "position_y": [0],
                    "position_z": [0]
                },
                "eulerian":
                {
                    "position_x": [0],
                    "position_y": [0],
                    "position_z": [0]
                },
                "lagrangian":
                {
                    "position_x": [0],
                    "position_y": [0],
                    "position_z": [0]
                }
            }
            
            return info_data.model_dump()
        
        for i, _ in enumerate(result.time):

            position_x.append(result.position_x[i].to_value(u.km) - lagrange_point[0].to_value(u.km))
            position_y.append(result.position_y[i].to_value(u.km) - lagrange_point[1].to_value(u.km))
            position_z.append(result.position_z[i].to_value(u.km) - lagrange_point[2].to_value(u.km))
        
        for i, _ in enumerate(result_libration.time):
        
            relative_position_x.append(result_libration.position_x[i].to_value(u.km))
            relative_position_y.append(result_libration.position_y[i].to_value(u.km))
            relative_position_z.append(result_libration.position_z[i].to_value(u.km))
        
        if is_eulerian:
            
            for i, _ in enumerate(result_eulerian.time):
            
                eulerian_position_x.append(result_eulerian.position_x[i].to_value(u.km))
                eulerian_position_y.append(result_eulerian.position_y[i].to_value(u.km))
                eulerian_position_z.append(result_eulerian.position_z[i].to_value(u.km))
        
        if is_lagrangian:
            
            for i, _ in enumerate(result_lagrangian.time):
            
                lagrangian_position_x.append(result_lagrangian.position_x[i].to_value(u.km))
                lagrangian_position_y.append(result_lagrangian.position_y[i].to_value(u.km))
                lagrangian_position_z.append(result_lagrangian.position_z[i].to_value(u.km))

        # * New initial conditions for next iteration
        
        r_0 = np.array([
            result.position_x[-1].to_value(u.km),
            result.position_y[-1].to_value(u.km),
            result.position_z[-1].to_value(u.km)
        ]) * u.km
        
        v_0 = np.array([
            result.velocity_x[-1].to_value(u.km / u.s),
            result.velocity_y[-1].to_value(u.km / u.s),
            result.velocity_z[-1].to_value(u.km / u.s),
        ]) * u.km / u.s
        
        r_0_libration = np.array([
            result_libration.position_x[-1].to_value(u.km),
            result_libration.position_y[-1].to_value(u.km),
            result_libration.position_z[-1].to_value(u.km)
        ]) * u.km
        
        v_0_libration = np.array([
            result_libration.velocity_x[-1].to_value(u.km / u.s),
            result_libration.velocity_y[-1].to_value(u.km / u.s),
            result_libration.velocity_z[-1].to_value(u.km / u.s),
        ]) * u.km / u.s
        
        if is_eulerian:
        
            r_0_eulerian = np.array([
                result_eulerian.position_x[-1].to_value(u.km),
                result_eulerian.position_y[-1].to_value(u.km),
                result_eulerian.position_z[-1].to_value(u.km)
            ]) * u.km
            
            v_0_eulerian = np.array([
                result_eulerian.velocity_x[-1].to_value(u.km / u.s),
                result_eulerian.velocity_y[-1].to_value(u.km / u.s),
                result_eulerian.velocity_z[-1].to_value(u.km / u.s),
            ]) * u.km / u.s
        
        if is_lagrangian:
        
            r_0_lagrangian = np.array([
                result_lagrangian.position_x[-1].to_value(u.km),
                result_lagrangian.position_y[-1].to_value(u.km),
                result_lagrangian.position_z[-1].to_value(u.km)
            ]) * u.km
            
            v_0_lagrangian = np.array([
                result_lagrangian.velocity_x[-1].to_value(u.km / u.s),
                result_lagrangian.velocity_y[-1].to_value(u.km / u.s),
                result_lagrangian.velocity_z[-1].to_value(u.km / u.s),
            ]) * u.km / u.s
        
        # * Notify progress to WebSocket

        info_data.counter = idx
        
        yield info_data.model_dump()

    info_data.counter = deltas.size
    info_data.running = False
    info_data.data =\
    {
        "absolute":
        {
            "position_x": position_x,
            "position_y": position_y,
            "position_z": position_z    
        },
        "relative":
        {
            "position_x": relative_position_x,
            "position_y": relative_position_y,
            "position_z": relative_position_z 
        }
    }
    
    if is_eulerian:
        
        info_data.data["eulerian"] =\
        {
            "position_x": eulerian_position_x,
            "position_y": eulerian_position_y,
            "position_z": eulerian_position_z
        }
    
    if is_lagrangian:
        
        info_data.data["lagrangian"] =\
        {
            "position_x": lagrangian_position_x,
            "position_y": lagrangian_position_y,
            "position_z": lagrangian_position_z
        }

    return info_data.model_dump()

def get_lagrange_point(parameters: cr3bp.OrbitParametersCR3BP, name: str) -> u.Quantity:
    """Retrieve the Lagrange point

    Args:
        parameters (cr3bp.OrbitParametersCR3BP): Orbit parameters
        name (str): Lagrange point name

    Returns:
        u.Quantity: Lagrange point
    """
    
    if name == "L1": return parameters.lagrangian_equilibrium_point_1.to(u.km)
    
    if name == "L2": return parameters.lagrangian_equilibrium_point_2.to(u.km)
    
    if name == "L3": return parameters.lagrangian_equilibrium_point_3.to(u.km)
    
    if name == "L4": return parameters.lagrangian_equilibrium_point_4.to(u.km)
    
    if name == "L5": return parameters.lagrangian_equilibrium_point_5.to(u.km)
    
    raise ValueError("Unsupported Lagrange point")
