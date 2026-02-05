import asyncio
import fastapi
import routers.utility as utility

from web_socket_manager import WebSocketManager
from app_data import AppData

import schemas.common as common
import schemas.interplanetary_schema as schema

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/interplanetary', tags=['Interplanetary'])

# >>> POST

@router.post("/run", response_model=common.ActionModel)
async def post_run(payload: schema.SimulationModel, background: fastapi.BackgroundTasks, request: fastapi.Request):
    """HTTP POST RUN interplanetary pork‑chop simulation
    
    This endpoint computes a Δv grid, time‑of‑flight grid, and related transfer‑analysis data for a given pair of
    celestial bodies and launch/arrival date windows.

    Args:
        payload (SimulationModel): JSON data for the simulation.

    Returns:
        ActionModel: Result
    """
    
    wsm: WebSocketManager = request.app.state.wsm
    
    data: AppData = request.app.state.data
    
    data.stop_simulation = False
    
    async def task():
        
        results: dict = await pork_chop_analysis(payload, wsm, data)
        
        await wsm.send_json(results)
    
    background.add_task(task)
    
    info_data: common.InfoModel = common.InfoModel()
        
    info_data.source    = "interplanetary"
    info_data.counter   = 0
    info_data.total     = 100
    info_data.running   = not data.stop_simulation
    
    await wsm.send_json(info_data.model_dump())
    
    return utility.ok("Ok")
    
# --- BACKGROUND ---

import numpy as np

import astropy.coordinates as coordinates
import astropy.units as units

import astrora.bodies as bodies
import astrora.util as util

from hapsira.maneuver import lambert_izzo

async def pork_chop_analysis(payload: schema.SimulationModel, wsm: WebSocketManager, data: AppData):

    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    # * Run the heavy solver in a worker thread
    
    def run():
        
        gen = compute_pork_chop_sync(payload, data)
        
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

def compute_pork_chop_sync(payload: schema.SimulationModel, data: AppData) -> dict:
    
    # >>> 1. Define departure and arrival windows
    
    spacing: units.Quantity = units.Quantity(payload.gridSize, units.day)
    
    t_launch: util.Time = util.time_range(payload.launchWindowStart, end=payload.launchWindowEnd, spacing=spacing)
    t_arrive: util.Time = util.time_range(payload.arrivalWindowStart, end=payload.arrivalWindowEnd, spacing=spacing)
    
    # >>> 2. Prepare grid
    
    DV  : np.ndarray = np.zeros((len(t_launch), len(t_arrive)))
    DV_1: np.ndarray = np.zeros((len(t_launch), len(t_arrive)))
    DV_2: np.ndarray = np.zeros((len(t_launch), len(t_arrive)))
    TOF : np.ndarray = np.zeros((len(t_launch), len(t_arrive)))
    
    # >>> 3. Loop over all date pairs
    
    mu_sun: units.Quantity = (bodies.Sun.mu * units.m**3 / units.s**2).to(units.km**3 / units.s**2)
    
    for i, tl in enumerate(t_launch):
        
        if (data.stop_simulation):
            
            info_data: common.InfoModel = common.InfoModel()
        
            info_data.source    = "interplanetary"
            info_data.counter   = 0
            info_data.total     = len(t_launch)
            info_data.running   = not data.stop_simulation
            
            return info_data.model_dump()
        
        r1, v1 = coordinates.get_body_barycentric_posvel(payload.departureBody, tl)
        
        r1 = r1.get_xyz().to(units.km)
        v1 = v1.get_xyz().to(units.km / units.s)
        
        for j, ta in enumerate(t_arrive):
            
            if (data.stop_simulation):
            
                info_data: common.InfoModel = common.InfoModel()
            
                info_data.source    = "interplanetary"
                info_data.counter   = 0
                info_data.total     = len(t_launch)
                info_data.running   = not data.stop_simulation
                
                return info_data.model_dump()
            
            if ta <= tl:
                
                DV[i, j]    = np.nan
                DV_1[i, j]  = np.nan
                DV_2[i, j]  = np.nan
                TOF[i, j]   = np.nan
                
                continue
            
            tof = (ta - tl).to(units.s)
            
            TOF[i, j] = (ta - tl).to(units.day).to_value()

            r2, v2 = coordinates.get_body_barycentric_posvel(payload.arrivalBody, ta)
            
            r2 = r2.get_xyz().to(units.km)
            v2 = v2.get_xyz().to(units.km / units.s)

            # * Lambert solution
                
            lambert = lambert_izzo(mu_sun, r1, r2, tof)
            
            # * Δv at departure
            
            dv_1: float = np.linalg.norm((lambert[0] - v1).to_value())
            dv_2: float = np.linalg.norm((v2 - lambert[1]).to_value())
            
            if dv_1 > 100: dv_1 = 100
            if dv_2 > 100: dv_2 = 100
            
            DV_1[i, j] = dv_1
            DV_2[i, j] = dv_2
            
            DV[i, j] = dv_1 + dv_2
            
        info_data: common.InfoModel = common.InfoModel()
        
        info_data.source    = "interplanetary"
        info_data.counter   = i + 1
        info_data.total     = len(t_launch)
        info_data.running   = not data.stop_simulation
        
        yield info_data.model_dump()
    
    # >>> 4. Return data
    
    info_data: common.InfoModel = common.InfoModel()
        
    info_data.source    = "interplanetary"
    info_data.counter   = len(t_launch)
    info_data.total     = len(t_launch)
    info_data.running   = False
    info_data.data      =   {
                                "tof": TOF.T.tolist(),
                                "dv_1": DV_1.T.tolist(),
                                "dv_2": DV_2.T.tolist(),
                                "dv": DV.T.tolist(),
                                "launch_dates": [t.to_datetime().date().isoformat() for t in t_launch],
                                "arrival_dates": [t.to_datetime().date().isoformat() for t in t_arrive]
                            }
    
    return info_data.model_dump()