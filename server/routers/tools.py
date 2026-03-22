import astropy.time as time
import astropy.units as u
import fastapi
import numpy as np
import schemas.tools_schema as schema

import astro.bodies as bodies
import astro.two_body_problem as tbp
import astro.orbit_3d as o3d
import astro.orbit_determination as od

CartesianIMI = schema.CartesianInModelInfo

KeplerianIMI = schema.KeplerianInModelInfo

GibbsMethodIMI = schema.GibbsMethodInModelInfo

GeocentricEquatorialOMI = schema.GeocentricEquatorialOutModelInfo

GroundTrackOMI = schema.GroundTrackOutModelInfo

GibbsMethodOMI = schema.GibbsMethodOutModelInfo

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/tools', tags=['Tools'])

# >>> PUT

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

@router.put("/convert-perifocal-to-geocentric-equatorial", response_model=GeocentricEquatorialOMI)
async def put_convert_perifocal_to_geocentric_equatorial(schema: KeplerianIMI = fastapi.Depends(KeplerianIMI.as_form))\
    -> fastapi.responses.JSONResponse:
    """HTTP PUT Perifocal --> Geocentric Equatorial conversion
    
    Args:
        schema (KeplerianIMI, optional): Keplerian orbital elements. Defaults to fastapi.Depends(KeplerianIMI.as_form).
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(schema.attractor.lower())
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(
        h = 0 * u.km**2 / u.s,
        a = schema.a * u.km,
        ecc = schema.ecc * u.one,
        inc = schema.inc * u.deg,
        raan = schema.raan * u.deg,
        argp = schema.argp * u.deg,
        nu = schema.nu * u.deg
    )
    
    r_GEF, v_GEF = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe)
    
    result: GeocentricEquatorialOMI = GeocentricEquatorialOMI(
        positionX = r_GEF[0].to_value(),
        positionY = r_GEF[1].to_value(),
        positionZ = r_GEF[2].to_value(),
        velocityX = v_GEF[0].to_value(),
        velocityY = v_GEF[1].to_value(),
        velocityZ = v_GEF[2].to_value()
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/propagate-ground-track", response_model=GroundTrackOMI)
async def put_propagate_ground_track(schema: KeplerianIMI = fastapi.Depends(KeplerianIMI.as_form))\
    -> fastapi.responses.JSONResponse:
    """HTTP PUT Propagate Ground Track
    
    Args:
        schema (KeplerianIMI, optional): Keplerian orbital elements. Defaults to fastapi.Depends(KeplerianIMI.as_form).
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(schema.attractor.lower())
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(
        h = 0 * u.km**2 / u.s,
        a = schema.a * u.km,
        ecc = schema.ecc * u.one,
        inc = schema.inc * u.deg,
        raan = schema.raan * u.deg,
        argp = schema.argp * u.deg,
        nu = schema.nu * u.deg
    )
    
    dt: u.Quantity = schema.dt * u.s if schema.dt is not None else 0 * u.s
    
    d_raan_dt, d_argp_dt = o3d.Orbit3D.planet_oblateness_effect(attractor=attractor, oe=oe)
    
    alpha, delta = o3d.Orbit3D.ground_track_propagation(attractor=attractor, oe=oe, dt=time.TimeDelta(dt))
    
    result: GroundTrackOMI = GroundTrackOMI(
        rightAscensionOfAscendingNodeVariation = d_raan_dt.to_value(),
        argumentOfPeriapsisVariation = d_argp_dt.to_value(),
        rightAscension = alpha.to_value(),
        declination = delta.to_value()
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/gibbs-method", response_model=GibbsMethodOMI)
async def put_gibbs_method(schema: GibbsMethodIMI) -> fastapi.responses.JSONResponse:
    """HTTP PUT Gibbs method
    
    Args:
        schema (GibbsMethodIMI): Three positions vectors
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    r_1: u.Quantity = np.array([schema.position1.x, schema.position1.y, schema.position1.z]) * u.km
    r_2: u.Quantity = np.array([schema.position2.x, schema.position2.y, schema.position2.z]) * u.km
    r_3: u.Quantity = np.array([schema.position3.x, schema.position3.y, schema.position3.z]) * u.km
    
    oe: o3d.OrbitalElements = od.OrbitDetermination.gibbs_method(attractor=attractor, r_1=r_1, r_2=r_2, r_3=r_3)
    
    result: GibbsMethodOMI = GibbsMethodOMI(
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
        float: Julian day
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
    
    R: u.Quantity = od.OrbitDetermination.geocentric_equatorial_position_vector(attractor=attractor, theta=theta, phi=phi, H=H)
    
    rho_te: u.Quantity = od.OrbitDetermination.topocentric_equatorial_position_vector(attractor=attractor, r=r, theta=theta, phi=phi, H=H)
    
    rho_th, A, a = od.OrbitDetermination.topocentric_horizon_position_vector(attractor=attractor, r=r, theta=theta, phi=phi, H=H)
    
    _, alpha, delta = od.OrbitDetermination.topocentric_equatorial_right_ascension_declination(attractor=attractor, theta=theta, phi=phi, A=A, a=a)
    
    result: schema.TopocentricFrameOutModelInfo = schema.TopocentricFrameOutModelInfo(
        geo=schema.TopocentricFrameOutModelInfo.Position(x=R[0].to_value(), y=R[1].to_value(), z=R[2].to_value()),
        te=schema.TopocentricFrameOutModelInfo.Position(x=rho_te[0].to_value(), y=rho_te[1].to_value(), z=rho_te[2].to_value()),
        th=schema.TopocentricFrameOutModelInfo.Position(x=rho_th[0].to_value(), y=rho_th[1].to_value(), z=rho_th[2].to_value()),
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