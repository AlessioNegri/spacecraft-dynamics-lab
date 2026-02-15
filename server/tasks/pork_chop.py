import asyncio
import astropy.coordinates as coordinates
import astropy.units as units
import astrora.bodies as bodies
import astrora.util as util
import numpy as np
import schemas.common as common
import schemas.interplanetary_schema as schema
import scipy.optimize as optimize
import typing

from common.app_data import AppData
from hapsira.maneuver import lambert_izzo
from common.web_socket_manager import WebSocketManager

async def pork_chop_analysis(payload: schema.SimulationModel, wsm: WebSocketManager, data: AppData) -> dict:
    """Asynchronous execution of pork-chop analysis

    Args:
        payload (schema.SimulationModel): Simulation data
        wsm (WebSocketManager): Web Socket manager
        data (AppData): Application data

    Returns:
        dict: JSON
    """

    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    # * Run the heavy solver in a worker thread
    
    def run():
        
        gen = compute_pork_chop_sync(payload, data) if payload.flybyBody == "" else compute_pork_chop_flyby_sync(payload, data)
        
        while True:
            
            try:
                
                update = next(gen)
            
                # * Schedule async WebSocket send from thread
                
                asyncio.run_coroutine_threadsafe(
                    wsm.send_json(
                    {
                        "source": update.get("source"),
                        "counter": update.get("counter"),
                        "total": update.get("total"),
                        "running": update.get("running")
                    }),
                    loop)

                # * If cancelled, return immediately
                
                if not update.get("running"): return update
                
            except StopIteration as e:

                # * Final result
            
                return e.value

    result = await asyncio.to_thread(run)

    # * Return final result to background task
    
    return result

def compute_pork_chop_sync(payload: schema.SimulationModel, data: AppData) -> typing.Generator[dict, dict, None]:
    """Compute the standard pork-chop simulation

    Args:
        payload (schema.SimulationModel): Simulation data
        data (AppData): Application data

    Returns:
        typing.Generator[dict, dict, None]: JSON data

    Yields:
        Iterator[typing.Generator[dict, dict, None]]: JSON data
    """
    
    # >>> 1. Define departure and arrival windows
    
    spacing: units.Quantity = units.Quantity(payload.gridSize, units.day)
    
    t_launch: util.Time = util.time_range(payload.launchWindowStart, end=payload.launchWindowEnd, spacing=spacing)
    t_arrive: util.Time = util.time_range(payload.arrivalWindowStart, end=payload.arrivalWindowEnd, spacing=spacing)
    
    info_data: common.InfoModel = common.InfoModel(source="interplanetary", counter=0, total=len(t_launch))
    
    if t_launch[-1] >= t_arrive[0]: return info_data.model_dump()
    
    info_data.running = True
    
    # >>> 2. Prepare grid
    
    size: np.ndarray = np.zeros((len(t_launch), len(t_arrive)))
    
    DV_1: np.ndarray = np.zeros_like(size)
    DV_2: np.ndarray = np.zeros_like(size)
    TOF : np.ndarray = np.zeros_like(size)
    
    # >>> 3. Loop over all date pairs
    
    mu_sun: units.Quantity = (bodies.Sun.mu * units.m**3 / units.s**2).to(units.km**3 / units.s**2)
    
    # >>> 3-1. Launch
    
    for i, tl in enumerate(t_launch):
        
        # * Departure body ephemeris
        
        r1, v1 = coordinates.get_body_barycentric_posvel(payload.departureBody, tl)
        
        r1: units.Quantity = r1.get_xyz().to(units.km)
        v1: units.Quantity = v1.get_xyz().to(units.km / units.s)
        
        # >>> 3-2. Arrival
        
        for j, ta in enumerate(t_arrive):
            
            # * Stop simulation check
            
            if data.stop_simulation:
                
                info_data.counter = 0
                info_data.running = False
                
                return info_data.model_dump()
            
            # * Arrival body ephemeris

            r2, v2 = coordinates.get_body_barycentric_posvel(payload.arrivalBody, ta)
            
            r2: units.Quantity = r2.get_xyz().to(units.km)
            v2: units.Quantity = v2.get_xyz().to(units.km / units.s)
            
            # * Time Of Flight
            
            tof: units.Quantity = (ta - tl).to(units.s)
            
            TOF[i, j] = (ta - tl).to(units.day).to_value()

            # * Lambert solution
                
            lambert: tuple = lambert_izzo(mu_sun, r1, r2, tof)
            
            # * Solution
            
            dv_1: float = np.linalg.norm((lambert[0] - v1).to_value())
            dv_2: float = np.linalg.norm((v2 - lambert[1]).to_value())
            
            if dv_1 > 100: dv_1 = 100
            if dv_2 > 100: dv_2 = 100
            
            DV_1[i, j] = dv_1
            DV_2[i, j] = dv_2
            
        # >>> 3-3. Update UI
        
        info_data.counter = i + 1
        
        yield info_data.model_dump()
    
    # >>> 4. Return simulation data
    
    info_data.counter = len(t_launch)
    info_data.running = False
    info_data.data =\
    {
        "launchDates": [t.to_datetime().date().isoformat() for t in t_launch],
        "arrivalDates": [t.to_datetime().date().isoformat() for t in t_arrive],
        "tof": TOF.T.tolist(),
        "dv1": DV_1.T.tolist(),
        "dv2": DV_2.T.tolist()
    }
    
    return info_data.model_dump()

def compute_pork_chop_flyby_sync(payload: schema.SimulationModel, data: AppData) -> typing.Generator[dict, dict, None]:
    """Compute the pork-chop simulation with a flyby

    Args:
        payload (schema.SimulationModel): Simulation data
        data (AppData): Application data

    Returns:
        typing.Generator[dict, dict, None]: JSON data

    Yields:
        Iterator[typing.Generator[dict, dict, None]]: JSON data
    """
    
    # >>> 1. Define departure, flyby, and arrival windows
    
    spacing: units.Quantity = units.Quantity(payload.gridSize, units.day)
    
    t_launch: util.Time = util.time_range(payload.launchWindowStart, end=payload.launchWindowEnd, spacing=spacing)
    t_flyby : util.Time = util.time_range(payload.flybyWindowStart, end=payload.flybyWindowEnd, spacing=spacing)
    t_arrive: util.Time = util.time_range(payload.arrivalWindowStart, end=payload.arrivalWindowEnd, spacing=spacing)
    
    info_data: common.InfoModel = common.InfoModel(source="interplanetary", counter=0, total=len(t_launch))
    
    if t_launch[-1] >= t_flyby[0]: return info_data.model_dump()
    
    if t_flyby[-1] >= t_arrive[0]: return info_data.model_dump()
    
    info_data.running = True
    
    # >>> 2. Prepare grid
    
    size: np.ndarray = np.zeros((len(t_launch), len(t_flyby), len(t_arrive)))
    
    DV_1 : np.ndarray = np.zeros_like(size)
    DV_GA: np.ndarray = np.zeros_like(size)
    DV_2 : np.ndarray = np.zeros_like(size)
    TOF_1: np.ndarray = np.zeros_like(size)
    TOF_2: np.ndarray = np.zeros_like(size)
    
    # >>> 3. Loop over all date pairs
    
    mu_sun: units.Quantity = (bodies.Sun.mu * units.m**3 / units.s**2).to(units.km**3 / units.s**2)
    
    # >>> 3-1. Launch
    
    for i, tl in enumerate(t_launch):
        
        # * Departure body ephemeris
        
        r1, v1 = coordinates.get_body_barycentric_posvel(payload.departureBody, tl)
        
        r1: units.Quantity = r1.get_xyz().to(units.km)
        v1: units.Quantity = v1.get_xyz().to(units.km / units.s)
        
        # >>> 3-2. Flyby
        
        for j, tfb in enumerate(t_flyby):
            
            # * Flyby body ephemeris
            
            rfb, vfb = coordinates.get_body_barycentric_posvel(payload.flybyBody, tfb)
            
            rfb: units.Quantity = rfb.get_xyz().to(units.km)
            vfb: units.Quantity = vfb.get_xyz().to(units.km / units.s)
            
            # * Time Of Flight 1
            
            tof_1: units.Quantity = (tfb - tl).to(units.s)
            
            # * Lambert solution
            
            lambert_1: tuple = lambert_izzo(mu_sun, r1, rfb, tof_1)
            
            # * Incoming hyperbola excess velocity
            
            v_inf_1: float = (lambert_1[1] - vfb).to_value()
            
            # >>> 3-3. Arrival
        
            for k, ta in enumerate(t_arrive):
                
                # * Stop simulation check
            
                if data.stop_simulation:
                    
                    info_data.counter = 0
                    info_data.running = False
                    
                    return info_data.model_dump()
                
                # * Arrival body ephemeris

                r2, v2 = coordinates.get_body_barycentric_posvel(payload.arrivalBody, ta)
                
                r2: units.Quantity = r2.get_xyz().to(units.km)
                v2: units.Quantity = v2.get_xyz().to(units.km / units.s)
                
                # * Time Of Flight 2
                
                tof_2: units.Quantity = (ta - tfb).to(units.s)
                
                TOF_1[i, j, k] = tof_1.to(units.day).to_value()
                TOF_2[i, j, k] = tof_2.to(units.day).to_value()
                
                # * Lambert solution
                    
                lambert_2: tuple = lambert_izzo(mu_sun, rfb, r2, tof_2)
                
                # * Outgoing hyperbola excess velocity
                
                v_inf_2: float = (lambert_2[0] - vfb).to_value()
                
                # * Solution
                
                dv_1: float = np.linalg.norm((lambert_1[0] - v1).to_value())
                dv_ga: float = gravity_assist_maneuver(v_inf_1, v_inf_2, payload.flybyBody)
                dv_2: float = np.linalg.norm((v2 - lambert_2[1]).to_value())
                
                if dv_1 > 100: dv_1 = 100
                if dv_ga > 100: dv_ga = 100
                if dv_2 > 100: dv_2 = 100
                
                DV_1[i, j, k] = dv_1
                DV_GA[i, j, k] = dv_ga
                DV_2[i, j, k] = dv_2
                
        # >>> 3-4. Update UI
            
        info_data.counter = i + 1
        
        yield info_data.model_dump()
    
    # >>> 4. Return data
        
    info_data.counter = len(t_launch)
    info_data.running = False
    info_data.data =\
    {
        "launchDates": [t.to_datetime().date().isoformat() for t in t_launch],
        "flybyDates": [t.to_datetime().date().isoformat() for t in t_flyby],
        "arrivalDates": [t.to_datetime().date().isoformat() for t in t_arrive],
        "tof1": TOF_1.T.tolist(),
        "tof2": TOF_2.T.tolist(),
        "dv1": DV_1.T.tolist(),
        "dvGA": DV_GA.T.tolist(),
        "dv2": DV_2.T.tolist()
    }
    
    return info_data.model_dump()

def gravity_assist_maneuver(v_inf_1: np.ndarray, v_inf_2: np.ndarray, flyby_body: str) -> float:
    """Compute the Gravity Assiste maneuver to match the incoming and outgoing hyperbolas at the pericenter

    Args:
        v_inf_1 (np.ndarray): Incoming excess velocity
        v_inf_2 (np.ndarray): Outgoing excess velocity
        flyby_body (str): Name of the flyby body

    Returns:
        float: Gravity Assist maneuver cost
    """
    
    # >>> 1. Choose flyby body parameters
    
    mu: float = 0
    
    r: float = 0
    
    match (flyby_body):
        
        case "mercury":
            
            mu = bodies.Mercury.mu
            r  = bodies.Mercury.R_mean * 1e3
            
        case "venus":
            
            mu = bodies.Venus.mu
            r = bodies.Venus.R_mean * 1e3
            
        case "earth":
            
            mu = bodies.Earth.mu
            r = bodies.Earth.R_mean * 1e3
            
        case "mars":
            
            mu = bodies.Mars.mu
            r = bodies.Mars.R_mean * 1e3
        
        case "jupiter":
            
            mu = bodies.Jupiter.mu
            r = bodies.Jupiter.R_mean * 1e3
            
        case "saturn":
            
            mu = bodies.Saturn.mu
            r = bodies.Saturn.R_mean * 1e3
            
        case "uranus":
            
            mu = bodies.Uranus.mu
            r = bodies.Uranus.R_mean * 1e3
            
        case "neptune":
            
            mu = bodies.Neptune.mu
            r = bodies.Neptune.R_mean * 1e3
            
        case "pluto":
            
            mu = bodies.Pluto.mu
            r = bodies.Pluto.R_mean * 1e3
        
    mu = (mu * units.m**3 / units.s**2).to(units.km**3 / units.s**2).to_value()
    
    # >>> 2. Calculate total deviation angle
    
    delta: float = np.acos(np.dot(v_inf_1, v_inf_2) / ( np.linalg.norm(v_inf_1) * np.linalg.norm(v_inf_2) ))
    
    # >>> 3. Compute pericenter radius
    
    def f(rp: float) -> float:
        
        a: float = np.arcsin(1.0 / (1.0 + rp * np.linalg.norm(v_inf_1)**2 / mu))
        b: float = np.arcsin(1.0 / (1.0 + rp * np.linalg.norm(v_inf_2)**2 / mu))
        
        return delta - a - b
    
    rp_ga = optimize.fsolve(f, r + 100.0 - 20.0, xtol=1e-14)[0]

    #rp_ga = optimize.root_scalar(f, bracket=[rp0, rp0*2], method="bisect").root
    
    # >>> 4. Compute all derived parameters
    
    v_p_1: float = np.sqrt(np.linalg.norm(v_inf_1)**2 + 2 * mu / rp_ga)
    v_p_2: float = np.sqrt(np.linalg.norm(v_inf_2)**2 + 2 * mu / rp_ga)
    
    dv_ga: float = np.linalg.norm(v_p_2 - v_p_1)
    
    e_1: float = 1 + (rp_ga * np.linalg.norm(v_inf_1)**2 / mu)
    e_2: float = 1 + (rp_ga * np.linalg.norm(v_inf_2)**2 / mu)
    
    delta_1: float = 2 * np.asin(1 / e_1)
    delta_2: float = 2 * np.asin(1 / e_2)
    
    return dv_ga
