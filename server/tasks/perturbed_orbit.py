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

    n_steps: int = int(((end_date - start_date) / step).to_value(u.dimensionless_unscaled))

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
    
    oe_0: o3d.OrbitalElements = o3d.OrbitalElements(h=0 * u.km**2 / u.s,
                                                    a=payload.orbitalElements.sma * u.km,
                                                    ecc=payload.orbitalElements.ecc * u.dimensionless_unscaled,
                                                    inc=payload.orbitalElements.inc * u.deg,
                                                    raan=payload.orbitalElements.raan * u.deg,
                                                    argp=payload.orbitalElements.aop * u.deg,
                                                    nu=payload.orbitalElements.ta * u.deg)
    
    oe_0.h = oe_0.specific_angular_momentum(attractor=attractor)

    r_0, v_0 = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe_0)
    
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
                r=r_0,
                v=v_0,
                julian_day=JD_0,
                ballistic_coefficient=payload.ballisticCoefficient * u.m**2 / u.kg,
                ballistic_coefficient_srp=payload.ballisticCoefficientSRP * u.m**2 / u.kg)
        
        orbit.choose_perturbations(atmospheric_drag=payload.atmosphericDrag,
                                   gravitational_perturbation=payload.gravitationalPerturbation,
                                   solar_radiation_pressure=payload.solarRadiationPressure,
                                   lunar_gravity=payload.lunarGravity,
                                   solar_gravity=payload.solarGravity)
        
        result: op.Result = orbit.propagate_gauss_for(delta=delta)
        
        for i in range(len(result.oe)):
            
            times.append((timestamp + result.t[i]).isot)
            sam.append((result.oe[i].h - oe_ini.h).to_value(u.km**2 / u.s))
            sma.append((result.oe[i].a - oe_ini.a).to_value(u.km))
            ecc.append((result.oe[i].ecc - oe_ini.ecc).to_value(u.dimensionless_unscaled))
            inc.append((result.oe[i].inc - oe_ini.inc).to_value(u.deg))
            raan.append((result.oe[i].raan - oe_ini.raan).to_value(u.deg))
            aop.append((result.oe[i].argp - oe_ini.argp).to_value(u.deg))

        # * New initial conditions for next iteration
        
        oe_0 = o3d.OrbitalElements(h=result.oe[-1].h,
                                   a=result.oe[-1].a,
                                   ecc=result.oe[-1].ecc,
                                   inc=cm.wrap_angle(result.oe[-1].inc, low=-90, high=180),
                                   raan=cm.wrap_angle(result.oe[-1].raan, low=0, high=360),
                                   argp=cm.wrap_angle(result.oe[-1].argp, low=0, high=360),
                                   nu=cm.wrap_angle(result.oe[-1].nu, low=0, high=360)) # ! Do not use [-180 ; 360]
        
        r_0, v_0 = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe_0)
        
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
