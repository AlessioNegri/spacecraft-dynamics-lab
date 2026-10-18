import fastapi
import routers.utility as utility
import numpy as np

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


@router.put("/frozen-orbit-type-2", response_model=schema.FrozenOrbitType2OutModelInfo)
async def put_frozen_orbit_type_2() -> fastapi.responses.JSONResponse:
    """HTTP PUT Generate eccentricity contours for type-II frozen orbits.

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km)

    inclinations: np.ndarray = np.linspace(0, 180, 181)
    semimajor_axes: np.ndarray = np.linspace(R_E, 3 * R_E, 80)
    
    first_order_eccentricity: list[list[float | None]] = []
    eccentricity: list[list[float | None]] = []

    for semimajor_axis in semimajor_axes:
    
        first_order_row: list[float | None] = []
        eccentricity_row: list[float | None] = []

        for inclination in inclinations:
                
            e_f_0, e_f = op.OrbitalPerturbations.frozen_orbit_type_2(
                semimajor_axis=semimajor_axis * u.km,
                inclination=inclination * u.deg
            )

            first_order_value: float = e_f_0.to_value(u.one)
            corrected_value: float = e_f.to_value(u.one)
            
            first_order_row.append(first_order_value if np.isfinite(first_order_value) and first_order_value <= 0.01 else None)
            eccentricity_row.append(corrected_value if np.isfinite(corrected_value) and corrected_value <= 0.01 else None)

        first_order_eccentricity.append(first_order_row)
        eccentricity.append(eccentricity_row)

    result: schema.FrozenOrbitType2OutModelInfo = schema.FrozenOrbitType2OutModelInfo(
        inclination=inclinations.tolist(),
        semimajorAxis=semimajor_axes.tolist() / R_E,
        firstOrderEccentricity=first_order_eccentricity,
        eccentricity=eccentricity,
        type1Inclination=op.OrbitalPerturbations.frozen_orbit_type_1().to_value(u.deg)
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())


@router.put("/frozen-sun-synchronous-orbit", response_model=schema.FrozenSunSynchronousOrbitOutModelInfo)
async def put_frozen_sun_synchronous_orbit() -> fastapi.responses.JSONResponse:
    """HTTP PUT Generate frozen and sun-synchronous eccentricity contours.
    
    Returns:
            fastapi.responses.JSONResponse: JSON response
    """

    R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km)
    
    semimajor_axes: np.ndarray = np.linspace(R_E, 1.6 * R_E, 80)
    
    sun_synchronous_eccentricity: list[float | None] = []

    for semimajor_axis in semimajor_axes:
        
        _, e_f_sso = op.OrbitalPerturbations.frozen_sun_synchronous_orbit(
            semimajor_axis=semimajor_axis * u.km,
            inclination=90 * u.deg
        )
        
        e_f_sso_value: float = float(e_f_sso.to_value(u.one))
        
        sun_synchronous_eccentricity.append(
            e_f_sso_value if np.isfinite(e_f_sso_value) else None
        )

    result: schema.FrozenSunSynchronousOrbitOutModelInfo = schema.FrozenSunSynchronousOrbitOutModelInfo(
        semimajorAxis=(semimajor_axes / R_E).tolist(),
        sunSynchronousEccentricity=sun_synchronous_eccentricity
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/commensurate-orbits", response_model=schema.CommensurateOrbitOutModelInfo)
async def put_commensurate_orbits() -> fastapi.responses.JSONResponse:
    """HTTP PUT Generate commensurate orbit repeat-cycle points.
    
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km)
    
    k_values: tuple[int, ...] = (
        149, 147, 143, 141, 139, 137, 133, 131, 134, 130, 128, 127, 125, 124, 122, 121,
        119, 118, 117, 115, 113, 111, 109, 107, 105, 104, 103, 102, 101, 100, 99, 97,
        96, 95, 94, 93, 92, 89, 85, 83, 79, 74, 73, 72, 71, 69, 68, 67, 66, 59, 57,
        55, 53, 44, 43, 41, 40, 29, 27, 14, 13
    )
    
    altitudes: list[float] = []
    repeat_cycles: list[int] = []
    orbital_revolutions: list[int] = []

    for repeat_cycle in range(1, 11):
        
        for k in k_values:
            
            # ? The first result is inclination-independent; only the corrected radius depends on inclination.
            
            sma_zeroth, _ = op.OrbitalPerturbations.commensurate_orbit(
                inclination=0 * u.deg,
                k_orbital_revolutions=k,
                l_terrestrial_revolutions=repeat_cycle
            )
            
            h: float = sma_zeroth.to_value(u.km) - R_E

            if 575 <= h <= 1275:
                
                altitudes.append(h)
                repeat_cycles.append(repeat_cycle)
                orbital_revolutions.append(k)

    result: schema.CommensurateOrbitOutModelInfo = schema.CommensurateOrbitOutModelInfo(
        altitude=altitudes,
        repeatCycle=repeat_cycles,
        orbitalRevolutions=orbital_revolutions
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())


@router.put("/gps-orbit", response_model=schema.GPSOrbitOutModelInfo)
async def put_gps_orbit() -> fastapi.responses.JSONResponse:
    """HTTP PUT Compute GPS longitudinal drift for the selected harmonic terms.

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    longitudes: np.ndarray = np.linspace(0, 360, 361)
    
    drift_32: list[float] = []
    drift_3244: list[float] = []
    drift_324452: list[float] = []
    geo_drift_22: list[float] = []
    geo_drift_2231: list[float] = []
    geo_drift_223133: list[float] = []

    def to_radians_per_year_squared(drift: u.Quantity) -> float:
        return (drift.to_value(1 / u.s**2) * u.rad / u.s**2).to_value(u.rad / u.yr**2)

    for longitude in longitudes:
        
        drift_32_quantity: u.Quantity = op.OrbitalPerturbations.gps_orbit(
            inclination=55 * u.deg,
            longitude_ascending_node=longitude * u.deg,
            use_harmonics_32=True,
            use_harmonics_44=False,
            use_harmonics_52=False
        )
        drift_3244_quantity: u.Quantity = op.OrbitalPerturbations.gps_orbit(
            inclination=55 * u.deg,
            longitude_ascending_node=longitude * u.deg,
            use_harmonics_32=True,
            use_harmonics_44=True,
            use_harmonics_52=False
        )
        drift_324452_quantity: u.Quantity = op.OrbitalPerturbations.gps_orbit(
            inclination=55 * u.deg,
            longitude_ascending_node=longitude * u.deg,
            use_harmonics_32=True,
            use_harmonics_44=True,
            use_harmonics_52=True
        )

        geo_drift_22_quantity: u.Quantity = op.OrbitalPerturbations.geo_orbit(
            inclination=0 * u.deg,
            longitude_ascending_node=longitude * u.deg,
            use_harmonics_22=True,
            use_harmonics_31=False,
            use_harmonics_33=False
        )
        geo_drift_2231_quantity: u.Quantity = op.OrbitalPerturbations.geo_orbit(
            inclination=0 * u.deg,
            longitude_ascending_node=longitude * u.deg,
            use_harmonics_22=True,
            use_harmonics_31=True,
            use_harmonics_33=False
        )
        geo_drift_223133_quantity: u.Quantity = op.OrbitalPerturbations.geo_orbit(
            inclination=0 * u.deg,
            longitude_ascending_node=longitude * u.deg,
            use_harmonics_22=True,
            use_harmonics_31=True,
            use_harmonics_33=True
        )

        drift_32.append(to_radians_per_year_squared(drift_32_quantity))
        drift_3244.append(to_radians_per_year_squared(drift_3244_quantity))
        drift_324452.append(to_radians_per_year_squared(drift_324452_quantity))
        geo_drift_22.append(to_radians_per_year_squared(geo_drift_22_quantity))
        geo_drift_2231.append(to_radians_per_year_squared(geo_drift_2231_quantity))
        geo_drift_223133.append(to_radians_per_year_squared(geo_drift_223133_quantity))

    result: schema.GPSOrbitOutModelInfo = schema.GPSOrbitOutModelInfo(
        longitudeAscendingNode=longitudes.tolist(),
        driftHarmonics32=drift_32,
        driftHarmonics3244=drift_3244,
        driftHarmonics324452=drift_324452,
        geoDriftHarmonics22=geo_drift_22,
        geoDriftHarmonics2231=geo_drift_2231,
        geoDriftHarmonics223133=geo_drift_223133
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())


@router.put("/drag-orbit-times", response_model=schema.DragOrbitTimesOutModelInfo)
async def put_drag_orbit_times(data: schema.DragOrbitTimesInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Compute circularization time and circular orbit lifetime under atmospheric drag.
    
    Args:
        data (DragOrbitTimesInModelInfo): Input data

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    semimajor_axis: u.Quantity = data.semimajorAxis * u.km
    eccentricity: u.Quantity = data.eccentricity * u.one
    ballistic_coefficient: u.Quantity = data.ballisticCoefficient * u.m**2 / u.kg
    
    periapsis_radius: u.Quantity = semimajor_axis * (1 - eccentricity)

    circularization_time: u.Quantity = op.OrbitalPerturbations.drag_circularization_time(
        semimajor_axis=semimajor_axis,
        eccentricity=eccentricity,
        ballistic_coefficient=ballistic_coefficient
    )
    
    orbit_lifetime: u.Quantity = op.OrbitalPerturbations.drag_orbit_lifetime(
        semimajor_axis=periapsis_radius,
        ballistic_coefficient=ballistic_coefficient
    )

    result: schema.DragOrbitTimesOutModelInfo = schema.DragOrbitTimesOutModelInfo(
        circularizationTimeDays=circularization_time.to_value(u.day),
        circularizationTimeYears=circularization_time.to_value(u.year),
        orbitLifetimeDays=orbit_lifetime.to_value(u.day),
        orbitLifetimeYears=orbit_lifetime.to_value(u.year)
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
