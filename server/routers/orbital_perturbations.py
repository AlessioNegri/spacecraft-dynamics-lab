import fastapi
import routers.utility as utility

import schemas.common as common
import schemas.orbital_perturbations_schema as schema
import tasks.perturbed_orbit as perturbed_orbit

from common.app_data import AppData
from common.web_socket_manager import WebSocketManager

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/orbital-perturbations', tags=['Orbital Perturbations'])

# >>> POST

@router.post("/run", response_model=common.ActionModel)
async def post_run(payload: schema.SimulationModel, background: fastapi.BackgroundTasks, request: fastapi.Request)\
    -> fastapi.responses.JSONResponse:
    """HTTP POST RUN orbital perturbations simulation
    
    This endpoint computes the evolution of a spacecraft's orbit under various perturbations over a specified time
    period.

    Args:
        payload (SimulationModel): JSON data for the simulation.

    Returns:
        ActionModel: Result
    """
    
    wsm: WebSocketManager = request.app.state.wsm
    
    data: AppData = request.app.state.data
    
    data.stop_simulation = False
    
    async def task():
        
        results: dict = await perturbed_orbit.orbital_perturbations_analysis(payload, wsm, data)
        
        await wsm.send_json(results)
    
    background.add_task(task)
    
    info_data: common.InfoModel = common.InfoModel()
        
    info_data.source    = "orbital-perturbations"
    info_data.counter   = 0
    info_data.total     = 100
    info_data.running   = not data.stop_simulation
    
    await wsm.send_json(info_data.model_dump())
    
    return utility.ok("Ok")