import astropy.time as t
import astropy.units as u
import asyncio
import copy
import numpy as np
import typing

import schemas.common as common
import schemas.orbital_perturbations_schema as schema

from common.app_data import AppData
from common.web_socket_manager import WebSocketManager

import astro.bodies as bd
import astro.common as cm
import astro.orbital_perturbations as op
import astro.orbit_3d as o3d
import astro.orbit_determination as od

async def orbital_perturbations_analysis(payload: schema.SimulationModel, wsm: WebSocketManager, data: AppData) -> dict:
    """Asynchronous execution of orbital perturbations analysis

    Args:
        payload (schema.SimulationModel): Simulation data
        wsm (WebSocketManager): Web Socket manager
        data (AppData): Application data

    Returns:
        dict: JSON
    """
    
    # * Event loop for scheduling WebSocket updates from thread
    # ? Grab the currently running asyncio event loop so that, from the worker thread, you can schedule coroutines
    # ? (WebSocket sends) back onto this loop.

    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    # * Run the heavy solver in a worker thread
    # ? Blocking driver of the simulation
    
    def run():
        
        gen: typing.Generator[dict, dict, None] = compute_orbital_perturbations(payload, data)
        
        while True:
            
            try:
                
                update = next(gen)
            
                # * Schedule async WebSocket send from thread
                # ? For each generator update, send progress over WebSocket
                
                asyncio.run_coroutine_threadsafe(
                    wsm.send_json(
                    {
                        "type": update.get("type"),
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

    # * Run run() in a (separate) worker thread
    
    result = await asyncio.to_thread(run)

    # * Return final result to background task
    
    return result

def compute_orbital_perturbations(payload: schema.SimulationModel, data: AppData) -> typing.Generator[dict, dict, None]:
    """Compute the orbital perturbations simulation

    Args:
        payload (schema.SimulationModel): Simulation data
        data (AppData): Application data

    Returns:
        typing.Generator[dict, dict, None]: JSON data

    Yields:
        Iterator[typing.Generator[dict, dict, None]]: JSON data
    """
    
    # * Generate timestamps for 1-hour steps
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    start_date: t.Time = t.Time(payload.startDate, format='isot', scale='utc')
    
    end_date: t.Time = t.Time(payload.endDate, format='isot', scale='utc')
    
    step: u.Quantity = 1 * u.hour

    n_steps: int = int(((end_date - start_date) / step).to_value(u.one))

    deltas: t.TimeDelta = np.arange(0, n_steps + 1) * step

    timestamps: t.Time = start_date + deltas
    
    info_data: common.InfoModel = common.InfoModel(source="orbital-perturbations", counter=0, total=n_steps + 1)
    
    if start_date >= end_date: return info_data.model_dump()
    
    info_data.running = True
    
    # * Initial conditions
    
    times: list = []
    sam: list = []
    sma: list = []
    ecc: list = []
    inc: list = []
    raan: list = []
    aop: list = []
    
    oe_0: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                    semimajor_axis=payload.orbitalElements.sma * u.km,
                                                    eccentricity=payload.orbitalElements.ecc * u.one,
                                                    inclination=payload.orbitalElements.inc * u.deg,
                                                    right_ascension_of_ascending_node=payload.orbitalElements.raan * u.deg,
                                                    argument_of_periapsis=payload.orbitalElements.aop * u.deg,
                                                    true_anomaly=payload.orbitalElements.ta * u.deg)
    
    oe_0.calc_specific_angular_momentum(attractor=attractor)

    r_0, v_0 = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_0)
    
    oe_ini: o3d.OrbitalElements = copy.deepcopy(oe_0)
    
    # * Iteration

    for idx, timestamp in enumerate(timestamps):
        
        # * Stop simulation check
            
        if data.stop_simulation:
            
            info_data.counter = 0
            info_data.running = False
            
            return info_data.model_dump()
        
        # * Propagate orbit and store results
        
        JD_0: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp)
        
        delta: t.TimeDelta = t.TimeDelta(step)
        
        orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
        
        orbit.init(attractor=attractor,
                   position=r_0,
                   velocity=v_0,
                   julian_day=JD_0,
                   ballistic_coefficient=payload.ballisticCoefficient * u.m**2 / u.kg,
                   ballistic_coefficient_srp=payload.ballisticCoefficientSRP * u.m**2 / u.kg)
        
        orbit.choose_perturbations(atmospheric_drag=payload.atmosphericDrag,
                                   gravitational_perturbation=payload.gravitationalPerturbation,
                                   solar_radiation_pressure=payload.solarRadiationPressure,
                                   lunar_gravity=payload.lunarGravity,
                                   solar_gravity=payload.solarGravity)
        
        result: op.ResultOP = orbit.propagate_gauss_for(delta=delta)
        
        for i, oe_i in enumerate(result.orbital_elements):
            
            times.append((timestamp + result.time[i]).isot)
            sam.append((oe_i.specific_angular_momentum - oe_ini.specific_angular_momentum).to_value(u.km**2 / u.s))
            sma.append((oe_i.semimajor_axis - oe_ini.semimajor_axis).to_value(u.km))
            ecc.append((oe_i.eccentricity - oe_ini.eccentricity).to_value(u.dimensionless_unscaled))
            inc.append((oe_i.inclination - oe_ini.inclination).to_value(u.deg))
            raan.append((oe_i.right_ascension_of_ascending_node - oe_ini.right_ascension_of_ascending_node).to_value(u.deg))
            aop.append((oe_i.argument_of_periapsis - oe_ini.argument_of_periapsis).to_value(u.deg))

        # * New initial conditions for next iteration
        
        oe_f: o3d.OrbitalElements = result.orbital_elements[-1]
        
        oe_0 = o3d.OrbitalElements(specific_angular_momentum=oe_f.specific_angular_momentum,
                                   semimajor_axis=oe_f.semimajor_axis,
                                   eccentricity=oe_f.eccentricity,
                                   inclination=cm.wrap_angle(oe_f.inclination, low=-90, high=180),
                                   right_ascension_of_ascending_node=cm.wrap_angle(oe_f.right_ascension_of_ascending_node, low=0, high=360),
                                   argument_of_periapsis=cm.wrap_angle(oe_f.argument_of_periapsis, low=0, high=360),
                                   true_anomaly=cm.wrap_angle(oe_f.true_anomaly, low=0, high=360)) # ! Do not use [-180 ; 360]
        
        r_0, v_0 = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_0)
        
        # * Notify progress to WebSocket
        
        info_data.counter = idx + 1
        
        yield info_data.model_dump()

    info_data.counter = n_steps + 1
    info_data.running = False
    info_data.data =\
    {
        "times": times,
        "sam": sam,
        "sma": sma,
        "ecc": ecc,
        "inc": inc,
        "raan": raan,
        "aop": aop
    }
    
    return info_data.model_dump()
