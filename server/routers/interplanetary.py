import astropy.time as time
import astropy.units as u
import fastapi
import numpy as np
import routers.utility as utility
import typing

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
    
    payload.flybyBody = payload.flybyBody.strip()
    
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

# >>> PUT

@router.put("/synodic-period", response_model=schema.SynodicPeriodOutModelInfo)
async def put_synodic_period(data: schema.SynodicPeriodInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Synodic Period calculation

    Args:
        data (schema.SynodicPeriodInModelInfo): Departure and arrival planets

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    departure_planet: bd.Attractor = bd.Attractor(data.departurePlanet.lower())
    
    arrival_planet: bd.Attractor = bd.Attractor(data.arrivalPlanet.lower())
    
    synodic_period: u.Quantity = it.InterplanetaryTrajectories.synodic_period(departure_planet=departure_planet,
                                                                              arrival_planet=arrival_planet)

    phi_0, phi_f, wait_time = it.InterplanetaryTrajectories.wait_time(departure_planet=departure_planet,
                                                                      arrival_planet=arrival_planet)

    result: schema.SynodicPeriodOutModelInfo = schema.SynodicPeriodOutModelInfo(
        synodicPeriod=synodic_period.to_value(u.day),
        initialPhaseAngle=phi_0.to_value(u.deg),
        finalPhaseAngle=phi_f.to_value(u.deg),
        waitTime=wait_time.to_value(u.day)
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/sphere-of-influence", response_model=schema.SphereOfInfluenceOutModelInfo)
async def put_sphere_of_influence(data: schema.SphereOfInfluenceInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Sphere of Influence calculation

    Args:
        data (schema.SphereOfInfluenceInModelInfo): Main attractor and body

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    main_attractor: bd.Attractor = bd.Attractor(data.mainAttractor.lower())

    body: bd.Attractor = bd.Attractor(data.body.lower())

    sphere_of_influence: u.Quantity =\
        it.InterplanetaryTrajectories.sphere_of_influence(body=body, main_attractor=main_attractor, approximation=False)
    
    sphere_of_influence_approximated: u.Quantity =\
        it.InterplanetaryTrajectories.sphere_of_influence(body=body, main_attractor=main_attractor, approximation=True)

    result: schema.SphereOfInfluenceOutModelInfo = schema.SphereOfInfluenceOutModelInfo(
        sphereOfInfluence=sphere_of_influence.to_value(u.km),
        sphereOfInfluenceApproximated=sphere_of_influence_approximated.to_value(u.km)
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/transfer", response_model=schema.TransferOutModelInfo)
async def put_transfer(data: schema.TransferInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Simple transfer calculation using Hohmann transfer as approximation

    Args:
        data (schema.TransferInModelInfo): Transfer parameters

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    departure_planet: bd.Attractor = bd.Attractor(data.departurePlanet.lower())

    arrival_planet: bd.Attractor = bd.Attractor(data.arrivalPlanet.lower())
    
    departure_planet_radius: u.Quantity = bd.BODIES[bd.Attractor(data.departurePlanet)].R_E
    
    departure_parking_orbit_radius: u.Quantity = departure_planet_radius + data.departureParkingOrbitHeight * u.km
    
    arrival_planet_radius: u.Quantity = bd.BODIES[bd.Attractor(data.arrivalPlanet)].R_E
    
    arrival_parking_orbit_radius: u.Quantity = arrival_planet_radius + data.arrivalParkingOrbitHeight * u.km

    dv_departure, hyperbola_departure = it.InterplanetaryTrajectories.departure(departure_planet=departure_planet,
                                                                                arrival_planet=arrival_planet,
                                                                                periapse_radius=departure_parking_orbit_radius)


    dv, hyperbola_arrival, _ = it.InterplanetaryTrajectories.rendezvous_with_circular_orbit(departure_planet=departure_planet,
                                                                                            arrival_planet=arrival_planet,
                                                                                            radius=arrival_parking_orbit_radius)
    
    result: schema.TransferOutModelInfo = schema.TransferOutModelInfo(
        departureDeltaV=dv_departure.to_value(u.km / u.s),
        departureHyperbola=schema.TransferOutModelInfo.Hyperbola(
            specificAngularMomentum=hyperbola_departure.specific_angular_momentum.to_value(u.km**2 / u.s),
            eccentricity=hyperbola_departure.eccentricity.to_value(u.one),
            periapsisRadius=hyperbola_departure.periapsis_radius.to_value(u.km),
            asymptoteAngle=hyperbola_departure.asymptote_angle.to_value(u.deg),
            turningAngle=hyperbola_departure.turning_angle.to_value(u.deg),
            aimingRadius=hyperbola_departure.aiming_radius.to_value(u.km),
            specificEnergy=hyperbola_departure.specific_energy.to_value(u.km**2 / u.s**2),
            hyperbolicExcessSpeed=hyperbola_departure.hyperbolic_excess_speed.to_value(u.km / u.s),
            characteristicEnergy=hyperbola_departure.characteristic_energy.to_value(u.km**2 / u.s**2),
            timeOfFlight=hyperbola_departure.time_of_flight.to_value(u.day)
        ),
        arrivalDeltaV=dv.to_value(u.km / u.s),
        arrivalHyperbola=schema.TransferOutModelInfo.Hyperbola(
            specificAngularMomentum=hyperbola_arrival.specific_angular_momentum.to_value(u.km**2 / u.s),
            eccentricity=hyperbola_arrival.eccentricity.to_value(u.one),
            periapsisRadius=hyperbola_arrival.periapsis_radius.to_value(u.km),
            asymptoteAngle=hyperbola_arrival.asymptote_angle.to_value(u.deg),
            turningAngle=hyperbola_arrival.turning_angle.to_value(u.deg),
            aimingRadius=hyperbola_arrival.aiming_radius.to_value(u.km),
            specificEnergy=hyperbola_arrival.specific_energy.to_value(u.km**2 / u.s**2),
            hyperbolicExcessSpeed=hyperbola_arrival.hyperbolic_excess_speed.to_value(u.km / u.s),
            characteristicEnergy=hyperbola_arrival.characteristic_energy.to_value(u.km**2 / u.s**2),
            timeOfFlight=hyperbola_arrival.time_of_flight.to_value(u.day)
        )
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/non-hohmann-transfer", response_model=schema.NonHohmannTransferOutModelInfo)
async def put_non_hohmann_transfer(data: schema.NonHohmannTransferInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Simple transfer calculation using Hohmann transfer as approximation

    Args:
        data (schema.NonHohmannTransferInModelInfo): Non-Hohmann Transfer parameters

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    departure_planet: bd.Attractor = bd.Attractor(data.departurePlanet.lower())

    arrival_planet: bd.Attractor = bd.Attractor(data.arrivalPlanet.lower())
    
    mu_sun: float = bd.BODIES[bd.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
    
    R_1: float = bd.BODIES[departure_planet].semi_major_axis.to_value(u.km)
    
    R_2: float = bd.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
    
    v_inf_H: float = np.sqrt(mu_sun / R_1) * np.abs((np.sqrt(2 * R_2 / (R_1 + R_2)) - 1))
    
    v_inf_values: np.ndarray = np.linspace(v_inf_H, v_inf_H * 2, data.numPoints)
    
    tof_list: typing.List[float] = []
    
    ta_list: typing.List[float] = []

    for v_inf in v_inf_values:
        
        tof, ta, _, _ = it.InterplanetaryTrajectories.non_hohmann_transfer(
            departure_planet=departure_planet,
            arrival_planet=arrival_planet,
            hyperbolic_excess_velocity=v_inf * u.km / u.s
        )

        tof_list.append(tof.to_value(u.day))
        
        ta_list.append(ta.to_value(u.deg))
    
    result: schema.NonHohmannTransferOutModelInfo = schema.NonHohmannTransferOutModelInfo(
        hyperbolicExcessVelocities=v_inf_values.tolist(),
        timeOfFlights=tof_list,
        trueAnomalies=ta_list
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
