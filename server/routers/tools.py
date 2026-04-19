import astropy.time as time
import astropy.units as u
import fastapi
import numpy as np
import schemas.tools_schema as schema

import astro.bodies as bodies
import astro.two_body_problem as tbp
import astro.orbit_3d as o3d
import astro.orbit_determination as od
import astro.relative_motion as rm

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/tools', tags=['Tools'])

# >>> PUT

# ? Orbit Representation

@router.put("/convert-cartesian-to-orbit-parameters", response_model=schema.OrbitParametersOutModelInfo)
async def put_convert_cartesian_to_orbit_parameters(data: schema.CartesianInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Cartesian --> Orbit Parameters conversion

    Args:
        data (schema.CartesianInModelInfo): Position-Velocity vectors

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    r: np.ndarray = np.array([ data.position.x, data.position.y, data.position.z ]) * u.km
    v: np.ndarray = np.array([ data.velocity.x, data.velocity.y, data.velocity.z ]) * u.km / u.s
    
    orbit_parameters: tbp.OrbitParameters = tbp.Orbit.cartesian_to_orbit_parameters(attractor=attractor, r=r, v=v)
    
    alpha, delta = o3d.Orbit3D.right_ascension_declination(r=r)
    
    result: schema.OrbitParametersOutModelInfo = schema.OrbitParametersOutModelInfo(
        conicType                = orbit_parameters.conic_type,
        specificAngularMomentum  = orbit_parameters.h.to_value(),
        specificMechanicalEnergy = orbit_parameters.epsilon.to_value(),
        eccentricity             = orbit_parameters.e,
        orbitalPeriod            = orbit_parameters.T.to_value(),
        apoapsisRadius           = orbit_parameters.r_a.to_value(),
        periapsisRadius          = orbit_parameters.r_p.to_value(),
        semiMajorAxis            = orbit_parameters.a.to_value(),
        semiMinorAxis            = orbit_parameters.b.to_value(),
        escapeVelocity           = orbit_parameters.v_esc.to_value(),
        infiniteTrueAnomaly      = orbit_parameters.theta_inf.to_value(),
        hyperbolaAsymptoteAngle  = orbit_parameters.beta.to_value(),
        turnAngle                = orbit_parameters.delta_ta.to_value(),
        aimingRadius             = orbit_parameters.delta_ar.to_value(),
        hyperbolicExcessSpeed    = orbit_parameters.v_inf.to_value(),
        characteristicEnergy     = orbit_parameters.C_3.to_value(),
        rightAscension           = alpha.to_value(),
        declination              = delta.to_value()
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/convert-cartesian-to-keplerian", response_model=schema.OrbitalElements)
async def put_convert_cartesian_to_keplerian(data: schema.CartesianInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Cartesian --> Keplerian conversion
    
    Args:
        data (schema.CartesianInModelInfo): Position-Velocity vectors
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    r: np.ndarray = np.array([ data.position.x, data.position.y, data.position.z ]) * u.km
    v: np.ndarray = np.array([ data.velocity.x, data.velocity.y, data.velocity.z ]) * u.km / u.s
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.orbital_elements(attractor=attractor, r=r, v=v)
    
    result: schema.OrbitalElements = schema.OrbitalElements(
        sam     = oe.h.to_value(),
        sma     = oe.a.to_value(),
        ecc     = oe.ecc,
        inc     = oe.inc.to_value(),
        raan    = oe.raan.to_value(),
        aop     = oe.argp.to_value(),
        ta      = oe.nu.to_value()
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/convert-cartesian-to-perifocal", response_model=schema.PerifocalOutModelInfo)
async def put_convert_cartesian_to_perifocal(data: schema.CartesianInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Cartesian --> Perifocal conversion
    
    Args:
        data (schema.CartesianInModelInfo): Position-Velocity vectors
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    r: np.ndarray = np.array([ data.position.x, data.position.y, data.position.z ]) * u.km
    v: np.ndarray = np.array([ data.velocity.x, data.velocity.y, data.velocity.z ]) * u.km / u.s
    
    r_PF, v_PF = o3d.Orbit3D.geocentric_equatorial_to_perifocal(attractor=attractor, r=r, v=v)
    
    result: schema.PerifocalOutModelInfo = schema.PerifocalOutModelInfo(
        position = schema.Vector3D(x=r_PF[0].to_value(), y=r_PF[1].to_value(), z=0),
        velocity = schema.Vector3D(x=v_PF[0].to_value(), y=v_PF[1].to_value(), z=0)
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/convert-keplerian-to-cartesian", response_model=schema.CartesianOutModelInfo)
async def put_convert_keplerian_to_cartesian(data: schema.KeplerianInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Perifocal --> Geocentric Equatorial conversion
    
    Args:
        data (schema.KeplerianInModelInfo): Keplerian orbital elements
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(
        h = 0 * u.km**2 / u.s,
        a = data.oe.sma * u.km,
        ecc = data.oe.ecc * u.one,
        inc = data.oe.inc * u.deg,
        raan = data.oe.raan * u.deg,
        argp = data.oe.aop * u.deg,
        nu = data.oe.ta * u.deg
    )
    
    r_GEF, v_GEF = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe)
    
    result: schema.CartesianOutModelInfo = schema.CartesianOutModelInfo(
        position = schema.Vector3D(x=r_GEF[0].to_value(), y=r_GEF[1].to_value(), z=r_GEF[2].to_value()),
        velocity = schema.Vector3D(x=v_GEF[0].to_value(), y=v_GEF[1].to_value(), z=v_GEF[2].to_value())
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/propagate-ground-track", response_model=schema.GroundTrackOutModelInfo)
async def put_propagate_ground_track(data: schema.KeplerianInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Propagate Ground Track
    
    Args:
        data (schema.KeplerianInModelInfo): Keplerian orbital elements
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(
        h = 0 * u.km**2 / u.s,
        a = data.oe.sma * u.km,
        ecc = data.oe.ecc * u.one,
        inc = data.oe.inc * u.deg,
        raan = data.oe.raan * u.deg,
        argp = data.oe.aop * u.deg,
        nu = data.oe.ta * u.deg
    )
    
    dt: u.Quantity = data.deltaTime * u.s if data.deltaTime is not None else 0 * u.s
    
    d_raan_dt, d_argp_dt = o3d.Orbit3D.planet_oblateness_effect(attractor=attractor, oe=oe)
    
    alpha, delta = o3d.Orbit3D.ground_track_propagation(attractor=attractor, oe=oe, dt=time.TimeDelta(dt))
    
    result: schema.GroundTrackOutModelInfo = schema.GroundTrackOutModelInfo(
        draan_dt = d_raan_dt.to_value(),
        daop_dt = d_argp_dt.to_value(),
        alpha = alpha.to_value(),
        delta = delta.to_value()
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

# ? Orbit Determination

@router.put("/gibbs-method", response_model=schema.OrbitalElements)
async def put_gibbs_method(data: schema.GibbsMethodInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Gibbs method
    
    Args:
        data (schema.GibbsMethodInModelInfo): Three positions vectors
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    r_1: u.Quantity = np.array([data.position1.x, data.position1.y, data.position1.z]) * u.km
    r_2: u.Quantity = np.array([data.position2.x, data.position2.y, data.position2.z]) * u.km
    r_3: u.Quantity = np.array([data.position3.x, data.position3.y, data.position3.z]) * u.km
    
    oe: o3d.OrbitalElements = od.OrbitDetermination.gibbs_method(attractor=attractor, r_1=r_1, r_2=r_2, r_3=r_3)
    
    result: schema.OrbitalElements = schema.OrbitalElements(
        sam=oe.h.to_value(),
        sma=oe.a.to_value(),
        ecc=oe.ecc.to_value(),
        inc=oe.inc.to_value(),
        raan=oe.raan.to_value(),
        aop=oe.argp.to_value(),
        ta=oe.nu.to_value()
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/convert-timestamp-to-julian-day")
async def put_convert_timestamp_to_julian_day(data: dict = fastapi.Body(...)) -> dict:
    """HTTP PUT Convert a timestamp in Julian days
    
    Args:
        timestamp (str): Timestamp
        
    Returns:
        float: Julian day
    """
    
    jd: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp=time.Time(data['timestamp']))
    
    lst: float = od.OrbitDetermination.local_sidereal_time(timestamp=time.Time(data['timestamp']),
                                                           longitude=data['longitude'] * u.deg).to_value(u.deg)
    
    return { "julianDay": jd, "localSiderealTime": lst }

@router.put("/convert-julian-day-to-timestamp")
async def put_convert_julian_day_to_timestamp(jd: float = fastapi.Body(...)) -> str:
    """HTTP PUT Convert Julian days in timestamp
    
    Args:
        jd (float): Julian days
        
    Returns:
        str: Timestamp
    """
    
    timestamp: time.Time = od.OrbitDetermination.julian_day_2_timestamp(julian_day=jd)
    
    return str(timestamp.isot).split(".")[0]

@router.put("/topocentric-frame", response_model=schema.TopocentricFrameOutModelInfo)
async def put_topocentric_frame(data: schema.TopocentricFrameInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Topocentric frame
    
    Args:
        data (schema.TopocentricFrameInModelInfo): Three positions vectors
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    r: u.Quantity = np.array([data.position.x, data.position.y, data.position.z]) * u.km
    
    theta: u.Quantity = data.localSiderealTime * u.deg
    
    phi: u.Quantity = data.latitude * u.deg
    
    H: u.Quantity = data.elevation * u.km
    
    R: u.Quantity = od.OrbitDetermination.geocentric_equatorial_position_vector(attractor=attractor,
                                                                                theta=theta,
                                                                                phi=phi,
                                                                                H=H)
    
    rho_te: u.Quantity = od.OrbitDetermination.topocentric_equatorial_position_vector(attractor=attractor,
                                                                                      r=r,
                                                                                      theta=theta,
                                                                                      phi=phi,
                                                                                      H=H)
    
    rho_th, A, a = od.OrbitDetermination.topocentric_horizon_position_vector(attractor=attractor,
                                                                             r=r,
                                                                             theta=theta,
                                                                             phi=phi,
                                                                             H=H)
    
    _, alpha, delta = od.OrbitDetermination.topocentric_equatorial_right_ascension_declination(attractor=attractor,
                                                                                               theta=theta,
                                                                                               phi=phi,
                                                                                               A=A,
                                                                                               a=a)
    
    result: schema.TopocentricFrameOutModelInfo = schema.TopocentricFrameOutModelInfo(
        geo=schema.Vector3D(x=R[0].to_value(), y=R[1].to_value(), z=R[2].to_value()),
        te=schema.Vector3D(x=rho_te[0].to_value(), y=rho_te[1].to_value(), z=rho_te[2].to_value()),
        th=schema.Vector3D(x=rho_th[0].to_value(), y=rho_th[1].to_value(), z=rho_th[2].to_value()),
        A=A.to_value(),
        a=a.to_value(),
        alpha=alpha.to_value(),
        delta=delta.to_value()
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/predict-angle-range", response_model=schema.AngleRangeOutModelInfo)
async def put_predict_angle_range(data: schema.AngleRangeInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Angle range state vector and orbital elements prediction
    
    Args:
        data (schema.AngleRangeInModelInfo): Model info
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    rho: u.Quantity = data.slantRange * u.km
    
    A: u.Quantity = data.azimuth * u.deg
    
    a: u.Quantity = data.elevationA * u.deg
    
    drho_dt: u.Quantity = data.rangeRate * u.km / u.s
    
    dA_dt: u.Quantity = data.azimuthRate * u.deg / u.s
    
    da_dt: u.Quantity = data.elevationARate * u.deg / u.s
    
    theta: u.Quantity = data.localSiderealTime * u.deg
    
    phi: u.Quantity = data.latitude * u.deg
    
    H: u.Quantity = data.elevationH * u.km
    
    r, v = od.OrbitDetermination.predict_from_angle_range(attractor=attractor,
                                                          rho=rho,
                                                          A=A,
                                                          a=a,
                                                          drho_dt=drho_dt,
                                                          dA_dt=dA_dt,
                                                          da_dt=da_dt,
                                                          theta=theta,
                                                          phi=phi,
                                                          H=H)
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.orbital_elements(attractor=attractor, r=r, v=v)
    
    result: schema.AngleRangeOutModelInfo = schema.AngleRangeOutModelInfo(
        position=schema.Vector3D(x=r[0].to_value(), y=r[1].to_value(), z=r[2].to_value()),
        velocity=schema.Vector3D(x=v[0].to_value(), y=v[1].to_value(), z=v[2].to_value()),
        oe=schema.OrbitalElements(sam=oe.h.to_value(),
                                  sma=oe.a.to_value(),
                                  ecc=oe.ecc.to_value(),
                                  inc=oe.inc.to_value(),
                                  raan=oe.raan.to_value(),
                                  aop=oe.argp.to_value(),
                                  ta=oe.nu.to_value())
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/predict-gauss-method", response_model=schema.GaussMethodOutModelInfo)
async def put_predict_gauss_method(data: schema.GaussMethodInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Gauss method state vector and orbital elements prediction
    
    Args:
        data (schema.GaussMethodInModelInfo): Model info
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    phi: u.Quantity = data.latitude * u.deg
    
    theta: u.Quantity = np.array([data.localSiderealTime[0], data.localSiderealTime[1], data.localSiderealTime[2]]) * u.deg
    
    alpha: u.Quantity = np.array([data.rightAscension[0], data.rightAscension[1], data.rightAscension[2]]) * u.deg
    
    delta: u.Quantity = np.array([data.declination[0], data.declination[1], data.declination[2]]) * u.deg
    
    t: u.Quantity = np.array([data.time[0], data.time[1], data.time[2]]) * u.s
    
    H: u.Quantity = data.elevation * u.km
    
    r, v = od.OrbitDetermination.predict_from_gauss_method_extended(attractor=attractor,
                                                                    phi=phi,
                                                                    theta=theta,
                                                                    alpha=alpha,
                                                                    delta=delta,
                                                                    t=t,
                                                                    H=H)
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.orbital_elements(attractor=attractor, r=r, v=v)
    
    result: schema.AngleRangeOutModelInfo = schema.AngleRangeOutModelInfo(
        position=schema.Vector3D(x=r[0].to_value(), y=r[1].to_value(), z=r[2].to_value()),
        velocity=schema.Vector3D(x=v[0].to_value(), y=v[1].to_value(), z=v[2].to_value()),
        oe=schema.OrbitalElements(sam=oe.h.to_value(),
                                  sma=oe.a.to_value(),
                                  ecc=oe.ecc.to_value(),
                                  inc=oe.inc.to_value(),
                                  raan=oe.raan.to_value(),
                                  aop=oe.argp.to_value(),
                                  ta=oe.nu.to_value())
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

# ? Relative Motion

@router.put("/lvlh-kinematics", response_model=schema.LvlhKinematicsOutModelInfo)
async def put_lvlh_kinematics(data: schema.LvlhKinematicsInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Local Vertical Local Horizontal Kinematics
    
    Args:
        data (schema.LvlhKinematicsInModelInfo): Attractor and orbital elements of target and chaser
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    oe_target: o3d.OrbitalElements = o3d.OrbitalElements(
        h = data.orbitalElementsTarget.sam * u.km**2 / u.s,
        a = data.orbitalElementsTarget.sma * u.km,
        ecc = data.orbitalElementsTarget.ecc * u.one,
        inc = data.orbitalElementsTarget.inc * u.deg,
        raan = data.orbitalElementsTarget.raan * u.deg,
        argp = data.orbitalElementsTarget.aop * u.deg,
        nu = data.orbitalElementsTarget.ta * u.deg
    )
    
    oe_chaser: o3d.OrbitalElements = o3d.OrbitalElements(
        h = data.orbitalElementsChaser.sam * u.km**2 / u.s,
        a = data.orbitalElementsChaser.sma * u.km,
        ecc = data.orbitalElementsChaser.ecc * u.one,
        inc = data.orbitalElementsChaser.inc * u.deg,
        raan = data.orbitalElementsChaser.raan * u.deg,
        argp = data.orbitalElementsChaser.aop * u.deg,
        nu = data.orbitalElementsChaser.ta * u.deg
    )
    
    kinematics = rm.RelativeMotion.lvlh_kinematics(attractor=attractor, oe_target=oe_target, oe_chaser=oe_chaser)
    
    r: np.ndarray = kinematics[0].to_value(u.km)
    
    v: np.ndarray = kinematics[1].to_value(u.km / u.s)
    
    a: np.ndarray = kinematics[2].to_value(u.km / u.s**2)
    
    o: np.ndarray = kinematics[3].to_value(u.deg / u.s)
    
    x, y, z = rm.RelativeMotion.simulate_lvlh_kinematics(attractor=attractor, oe_target=oe_target, oe_chaser=oe_chaser)
    
    result: schema.LvlhKinematicsOutModelInfo = schema.LvlhKinematicsOutModelInfo(
        position = schema.Vector3D(x=r[0], y=r[1], z=r[2]),
        velocity = schema.Vector3D(x=v[0], y=v[1], z=v[2]),
        acceleration = schema.Vector3D(x=a[0], y=a[1], z=a[2]),
        angularVelocity = schema.Vector3D(x=o[0], y=o[1], z=o[2]),
        x = x,
        y = y,
        z = z
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/geocentric-equatorial-kinematics", response_model=schema.GeocentricEquatorialKinematicsOutModelInfo)
async def put_geocentric_equatorial_kinematics(data: schema.GeocentricEquatorialKinematicsInModelInfo)\
    -> fastapi.responses.JSONResponse:
    """HTTP PUT Geocentric Equatorial Kinematics
    
    Args:
        data (schema.GeocentricEquatorialKinematicsInModelInfo): Attractor, orbital elements of target, and chaser lvlh
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    oe_target: o3d.OrbitalElements = o3d.OrbitalElements(
        h = data.orbitalElementsTarget.sam * u.km**2 / u.s,
        a = data.orbitalElementsTarget.sma * u.km,
        ecc = data.orbitalElementsTarget.ecc * u.one,
        inc = data.orbitalElementsTarget.inc * u.deg,
        raan = data.orbitalElementsTarget.raan * u.deg,
        argp = data.orbitalElementsTarget.aop * u.deg,
        nu = data.orbitalElementsTarget.ta * u.deg
    )
    
    r_target, v_target = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe_target)
    
    r_rel_lvlh: u.Quantity = np.array([data.lvlhPosition.x, data.lvlhPosition.y, data.lvlhPosition.z]) * u.km
    
    v_rel_lvlh: u.Quantity = np.array([data.lvlhVelocity.x, data.lvlhVelocity.y, data.lvlhVelocity.z]) * u.km / u.s
    
    kinematics = rm.RelativeMotion.geocentric_equatorial_kinematics(r_target=r_target,
                                                                    v_target=v_target,
                                                                    r_rel_lvlh=r_rel_lvlh,
                                                                    v_rel_lvlh=v_rel_lvlh)
    
    oe_chaser: o3d.OrbitalElements = o3d.Orbit3D.orbital_elements(attractor=attractor, r=kinematics[0], v=kinematics[1])
    
    result: schema.GeocentricEquatorialKinematicsOutModelInfo = schema.GeocentricEquatorialKinematicsOutModelInfo(
        orbitalElementsChaser=schema.OrbitalElements(
            sam=oe_chaser.h.to_value(u.km**2 / u.s),
            sma=oe_chaser.a.to_value(u.km),
            ecc=oe_chaser.ecc.to_value(u.dimensionless_unscaled),
            inc=oe_chaser.inc.to_value(u.deg),
            raan=oe_chaser.raan.to_value(u.deg),
            aop=oe_chaser.argp.to_value(u.deg),
            ta=oe_chaser.nu.to_value(u.deg)
        )
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
