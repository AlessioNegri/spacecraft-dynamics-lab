import astropy.time as time
import astropy.units as u
import fastapi
import routers.utility as utility

import tasks.pork_chop as pork_chop
import schemas.common as common
import schemas.interplanetary_schema as schema

from common.app_data import AppData
from common.web_socket_manager import WebSocketManager

import astro.bodies as bd
import astro.interplanetary_trajectories as it

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/interplanetary', tags=['Interplanetary'])

# >>> POST

@router.post("/run", response_model=common.ActionModel)
async def post_run(payload: schema.SimulationModel, background: fastapi.BackgroundTasks, request: fastapi.Request)\
    -> fastapi.responses.JSONResponse:
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

@router.post("/optimal-transfer", response_model=schema.OptimalTransferOutModelInfo)
async def post_run(data: schema.OptimalTransferInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP POST RUN interplanetary optimal transfer
    
    This endpoint computes the optimal transfer between two celestial bodies, calculating the departure and arrival
    delta-v values.

    Args:
        payload (schema.OptimalTransferInModelInfo): Optimal transfer input information.
        
    Returns:
        schema.OptimalTransferOutModelInfo: Result
    """
    
    departure_timestamp: time.Time = time.Time(data.launchDate, scale='utc')
    
    arrival_timestamp: time.Time = time.Time(data.arrivalDate, scale='utc')
    
    departure_parking_orbit_radius: u.Quantity = bd.BODIES[bd.Attractor(data.departureBody)].R_E + data.departureHeight * u.km
    
    arrival_periapse_radius: u.Quantity = bd.BODIES[bd.Attractor(data.arrivalBody)].R_E + data.arrivalPeriapsisHeight * u.km
    
    if data.flybyDate != "" and data.flybyBody != "":
        
        flyby_timestamp: time.Time = time.Time(data.flybyDate, scale='utc')
        
        dv_dep, _ = it.InterplanetaryTrajectories.optimal_transfer(departure_planet=bd.Attractor(data.departureBody),
                                                                   arrival_planet=bd.Attractor(data.flybyBody),
                                                                   departure_timestamp=departure_timestamp,
                                                                   arrival_timestamp=flyby_timestamp,
                                                                   departure_parking_orbit_radius=departure_parking_orbit_radius,
                                                                   arrival_orbit_period=data.arrivalOrbitalPeriod * u.hour,
                                                                   arrival_periapse_radius=arrival_periapse_radius)
        
        _, dev_arr = it.InterplanetaryTrajectories.optimal_transfer(departure_planet=bd.Attractor(data.flybyBody),
                                                                    arrival_planet=bd.Attractor(data.arrivalBody),
                                                                    departure_timestamp=flyby_timestamp,
                                                                    arrival_timestamp=arrival_timestamp,
                                                                    departure_parking_orbit_radius=departure_parking_orbit_radius,
                                                                    arrival_orbit_period=data.arrivalOrbitalPeriod * u.hour,
                                                                    arrival_periapse_radius=arrival_periapse_radius)
    
    else:
    
        dv_dep, dev_arr = it.InterplanetaryTrajectories.optimal_transfer(departure_planet=bd.Attractor(data.departureBody),
                                                                         arrival_planet=bd.Attractor(data.arrivalBody),
                                                                         departure_timestamp=departure_timestamp,
                                                                         arrival_timestamp=arrival_timestamp,
                                                                         departure_parking_orbit_radius=departure_parking_orbit_radius,
                                                                         arrival_orbit_period=data.arrivalOrbitalPeriod * u.hour,
                                                                         arrival_periapse_radius=arrival_periapse_radius)
    
    result: schema.OptimalTransferOutModelInfo = schema.OptimalTransferOutModelInfo(
        departureDeltaV=dv_dep.to_value(u.km / u.s),
        arrivalDeltaV=dev_arr.to_value(u.km / u.s)
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
