import fastapi
import routers.utility as utility

import tasks.pork_chop as pork_chop
import schemas.common as common
import schemas.interplanetary_schema as schema

from common.app_data import AppData
from common.web_socket_manager import WebSocketManager

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
        
        results: dict = await pork_chop.pork_chop_analysis(payload, wsm, data)
        
        await wsm.send_json(results)
    
    background.add_task(task)
    
    info_data: common.InfoModel = common.InfoModel()
        
    info_data.source    = "interplanetary"
    info_data.counter   = 0
    info_data.total     = 100
    info_data.running   = not data.stop_simulation
    
    await wsm.send_json(info_data.model_dump())
    
    return utility.ok("Ok")