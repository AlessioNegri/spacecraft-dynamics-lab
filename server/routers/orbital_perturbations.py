import fastapi
import routers.utility as utility

import schemas.common as common
import schemas.orbital_perturbations_schema as schema
import tasks.perturbed_orbit as perturbed_orbit

import astropy.units as u

import astro.orbital_perturbations as op
import astro.orbit_3d as o3d
import astro.bodies as bodies

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
        payload (SimulationModel): JSON data for the simulation

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

# >>> PUT

@router.put("/nodal-regression-rate", response_model=schema.NodalRegressionOutModelInfo)
async def put_nodal_regression_rate(data: schema.NodalRegressionInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Compute nodal regression rates (deg/day)

    Args:
        data (NodalRegressionInModelInfo): Attractor and orbital elements

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())

    oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                  semimajor_axis=data.orbitalElements.sma * u.km,
                                                  eccentricity=data.orbitalElements.ecc * u.one,
                                                  inclination=data.orbitalElements.inc * u.deg,
                                                  right_ascension_of_ascending_node=0 * u.deg,
                                                  argument_of_periapsis=0 * u.deg,
                                                  true_anomaly=0 * u.deg)

    rates = op.OrbitalPerturbations.nodal_regression_rate(attractor=attractor, orbital_elements=oe)

    result: schema.NodalRegressionOutModelInfo = schema.NodalRegressionOutModelInfo(
        gravitational=rates[0].to_value(u.deg / u.day),
        lunar=rates[1].to_value(u.deg / u.day),
        solar=rates[2].to_value(u.deg / u.day)
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())


@router.put("/apsidal-rotation-rate", response_model=schema.ApsidalRotationOutModelInfo)
async def put_apsidal_rotation_rate(data: schema.ApsidalRotationInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Compute apsidal rotation rates (deg/day)

    Args:
        data (ApsidalRotationInModelInfo): Attractor and orbital elements

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    attractor = bodies.Attractor(data.attractor.lower())

    oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                  semimajor_axis=data.orbitalElements.sma * u.km,
                                                  eccentricity=data.orbitalElements.ecc * u.one,
                                                  inclination=data.orbitalElements.inc * u.deg,
                                                  right_ascension_of_ascending_node=data.orbitalElements.raan * u.deg,
                                                  argument_of_periapsis=data.orbitalElements.aop * u.deg,
                                                  true_anomaly=data.orbitalElements.ta * u.deg)

    rates = op.OrbitalPerturbations.apsidal_rotation_rate(attractor=attractor, orbital_elements=oe)

    result: schema.ApsidalRotationOutModelInfo = schema.ApsidalRotationOutModelInfo(
        gravitational=rates[0].to_value(u.deg / u.day),
        lunar=rates[1].to_value(u.deg / u.day),
        solar=rates[2].to_value(u.deg / u.day)
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())


@router.put("/sun-synchronous-inclination", response_model=schema.SunSynchronousOutModelInfo)
async def put_sun_synchronous_inclination(data: schema.SunSynchronousInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Compute sun-synchronous inclination (deg)

    Args:
        data (SunSynchronousInModelInfo): Attractor, orbital elements and nodal regression rate (deg/day)

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    attractor = bodies.Attractor(data.attractor.lower())

    oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                  semimajor_axis=data.orbitalElements.sma * u.km,
                                                  eccentricity=data.orbitalElements.ecc * u.one,
                                                  inclination=data.orbitalElements.inc * u.deg,
                                                  right_ascension_of_ascending_node=data.orbitalElements.raan * u.deg,
                                                  argument_of_periapsis=data.orbitalElements.aop * u.deg,
                                                  true_anomaly=data.orbitalElements.ta * u.deg)

    nodal_regression_rate: u.Quantity = data.nodalRegressionRate * u.deg / u.day

    inclination: u.Quantity = op.OrbitalPerturbations.sun_synchronous_inclination(attractor=attractor,
                                                                                  orbital_elements=oe,
                                                                                  nodal_regression_rate=nodal_regression_rate)

    result: schema.SunSynchronousOutModelInfo = schema.SunSynchronousOutModelInfo(
        inclination=inclination.to_value()
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())