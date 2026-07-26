import fastapi
import routers.utility as utility

import schemas.common as common
import schemas.circular_restricted_three_body_problem_schema as schema
import tasks.circular_restricted_three_body_problem_simulation as cr3bp_simulation

import astropy.units as u
import astro.bodies as bd
import astro.circular_restricted_three_body_problem as cr3bp

from common.app_data import AppData
from common.web_socket_manager import WebSocketManager

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/circular-restricted-three-body-problem',
                                              tags=['Circular Restricted Three-Body Problem'])

# >>> POST

@router.post("/run", response_model=common.ActionModel)
async def post_run(payload: schema.SimulationModel,
                   background: fastapi.BackgroundTasks,
                   request: fastapi.Request) -> fastapi.responses.JSONResponse:
    """HTTP POST Circular Restricted Three-Body Problem simulation
    
    This endpoint computes the evolution of a spacecraft's orbit near a Lagrange point over a specified time period.

    Args:
        payload (SimulationModel): JSON data for the simulation

    Returns:
        ActionModel: Result
    """
    
    wsm: WebSocketManager = request.app.state.wsm
    
    data: AppData = request.app.state.data
    
    data.stop_simulation = False
    
    async def task():
        
        results: dict = await cr3bp_simulation.cr3bp_analysis(payload, wsm, data)
        
        await wsm.send_json(results)
    
    background.add_task(task)
    
    info_data: common.InfoModel = common.InfoModel()
        
    info_data.source    = "circular-restricted-three-body-problem"
    info_data.counter   = 0
    info_data.total     = 100
    info_data.running   = not data.stop_simulation
    
    await wsm.send_json(info_data.model_dump())
    
    return utility.ok("Ok")

# >>> PUT

@router.put("/orbit-parameters", response_model=schema.OrbitParametersOutModelInfo)
async def put_cr3bp_orbit_parameters(data: schema.OrbitParametersInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT CR3BP orbit parameters
    
    Args:
        data (schema.OrbitParametersInModelInfo): Bodies

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    body_1: bd.Attractor = bd.Attractor(data.body1.lower())
    body_2: bd.Attractor = bd.Attractor(data.body2.lower())

    parameters: cr3bp.OrbitParametersCR3BP = cr3bp.Orbit.orbit_parameters(body_1=body_1, body_2=body_2)
    
    result: schema.OrbitParametersOutModelInfo = schema.OrbitParametersOutModelInfo(
        inertialAngularVelocity=parameters.inertial_angular_velocity.to_value(u.deg / u.day),
        dimensionlessMassRatio1=parameters.dimensionless_mass_ratio_1.to_value(u.one),
        dimensionlessMassRatio2=parameters.dimensionless_mass_ratio_2.to_value(u.one),
        gravitationalParameter1=parameters.gravitational_parameter_1.to_value(u.km**3 / u.s**2),
        gravitationalParameter2=parameters.gravitational_parameter_2.to_value(u.km**3 / u.s**2),
        bodyPosition1=parameters.body_position_1.to_value(u.km),
        bodyPosition2=parameters.body_position_2.to_value(u.km),
        lagrangianPoint1=parameters.lagrangian_equilibrium_point_1.to_value(u.km).tolist(),
        lagrangianPoint2=parameters.lagrangian_equilibrium_point_2.to_value(u.km).tolist(),
        lagrangianPoint3=parameters.lagrangian_equilibrium_point_3.to_value(u.km).tolist(),
        lagrangianPoint4=parameters.lagrangian_equilibrium_point_4.to_value(u.km).tolist(),
        lagrangianPoint5=parameters.lagrangian_equilibrium_point_5.to_value(u.km).tolist()
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
