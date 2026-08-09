import astropy.time as time
import astropy.units as u
import copy
import fastapi
import numpy as np
import schemas.tools_schema as schema

import astro.bodies as bodies
import astro.two_body_problem as tbp
import astro.orbit_3d as o3d
import astro.orbit_determination as od
import astro.orbital_position as op

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
    
    orbit_parameters: tbp.OrbitParameters = tbp.Orbit.cartesian_to_orbit_parameters(attractor=attractor,
                                                                                    position=r,
                                                                                    velocity=v)
    
    alpha, delta = o3d.Orbit3D.right_ascension_declination(position=r)
    
    result: schema.OrbitParametersOutModelInfo = schema.OrbitParametersOutModelInfo(
        conicType                = orbit_parameters.conic_type,
        specificAngularMomentum  = orbit_parameters.specific_angular_momentum.to_value(),
        specificMechanicalEnergy = orbit_parameters.specific_energy.to_value(),
        eccentricity             = orbit_parameters.eccentricity,
        orbitalPeriod            = orbit_parameters.period.to_value(),
        apoapsisRadius           = orbit_parameters.apoapsis_radius.to_value(),
        periapsisRadius          = orbit_parameters.periapsis_radius.to_value(),
        semiMajorAxis            = orbit_parameters.semimajor_axis.to_value(),
        semiMinorAxis            = orbit_parameters.semiminor_axis.to_value(),
        escapeVelocity           = orbit_parameters.escape_velocity.to_value(),
        infiniteTrueAnomaly      = orbit_parameters.asymptotic_true_anomaly.to_value(),
        hyperbolaAsymptoteAngle  = orbit_parameters.asymptote_angle.to_value(),
        turnAngle                = orbit_parameters.turning_angle.to_value(),
        aimingRadius             = orbit_parameters.aiming_radius.to_value(),
        hyperbolicExcessSpeed    = orbit_parameters.hyperbolic_excess_speed.to_value(),
        characteristicEnergy     = orbit_parameters.characteristic_energy.to_value(),
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
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r, velocity=v)
    
    result: schema.OrbitalElements = schema.OrbitalElements(
        sam = oe.specific_angular_momentum.to_value(),
        sma = oe.semimajor_axis.to_value(),
        ecc = oe.eccentricity.to_value(),
        inc = oe.inclination.to_value(),
        raan = oe.right_ascension_of_ascending_node.to_value(),
        aop = oe.argument_of_periapsis.to_value(),
        ta = oe.true_anomaly.to_value()
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
    
    r_PF, v_PF = o3d.Orbit3D.geocentric_equatorial_to_perifocal(attractor=attractor, position=r, velocity=v)
    
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
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                  semimajor_axis=data.oe.sma * u.km,
                                                  eccentricity=data.oe.ecc * u.one,
                                                  inclination=data.oe.inc * u.deg,
                                                  right_ascension_of_ascending_node=data.oe.raan * u.deg,
                                                  argument_of_periapsis=data.oe.aop * u.deg,
                                                  true_anomaly=data.oe.ta * u.deg)
    
    r_GEF, v_GEF = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe)
    
    result: schema.CartesianOutModelInfo = schema.CartesianOutModelInfo(
        position = schema.Vector3D(x=r_GEF[0].to_value(), y=r_GEF[1].to_value(), z=r_GEF[2].to_value()),
        velocity = schema.Vector3D(x=v_GEF[0].to_value(), y=v_GEF[1].to_value(), z=v_GEF[2].to_value())
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/propagate-ground-track", response_model=schema.GroundTrackOutModelInfo)
async def put_propagate_ground_track(data: schema.GroundTrackInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Propagate Ground Track
    
    Args:
        data (schema.GroundTrackPathInModelInfo): Keplerian orbital elements and path settings

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Extract
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    R_E: u.Quantity = bodies.BODIES[attractor].R_E

    duration: u.Quantity = data.duration * u.s if data.duration is not None else 0 * u.s
    
    samples: int = data.samples if data.samples is not None else 180
    
    if samples < 2: samples = 2

    oe: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=data.oe.sma * u.km,
                                                  eccentricity=data.oe.ecc * u.one,
                                                  inclination=data.oe.inc * u.deg,
                                                  right_ascension_of_ascending_node=data.oe.raan * u.deg,
                                                  argument_of_periapsis=data.oe.aop * u.deg,
                                                  true_anomaly=data.oe.ta * u.deg)
    
    # * Generic ground track
    
    d_raan_dt, d_argp_dt = o3d.Orbit3D.planet_oblateness_effect(attractor=attractor, orbital_elements=oe)
    
    alpha, delta = o3d.Orbit3D.ground_track_propagation(attractor=attractor,
                                                        orbital_elements=copy.deepcopy(oe),
                                                        time_step=time.TimeDelta(duration))
    
    # * Horizon footprint
    
    r, _ = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe)
    
    c_f, beta, delta_hf = o3d.Orbit3D.horizon_footprint(attractor=attractor, altitude=np.linalg.norm(r) - R_E)
    
    # * Earth ground track
    
    period: u.Quantity = oe.calc_orbital_period(attractor=bodies.Attractor.EARTH)

    if duration.to_value(u.s) <= 0: duration = period

    if period.to_value(u.s) <= 0: duration = 0 * u.s

    t_0: u.Quantity

    if oe.eccentricity.to_value(u.one) == 0:
        
        t_0 = op.OrbitalPosition.circular_orbit_time(true_anomaly=oe.true_anomaly, period=period)
        
    else:
        
        t_0 = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=oe.true_anomaly,
                                                       period=period,
                                                       eccentricity=oe.eccentricity)
    
    step_time: float = duration.to_value(u.s) / max(samples - 1, 1)

    longitudes: list[float] = []
    latitudes: list[float] = []
    footprint: list[float] = []
    
    for index in range(samples):
        
        t_i: u.Quantity = t_0 + index * step_time * u.s
        
        if (t_i == 0 * u.s):
            
            ta_i: u.Quantity = 0 * u.deg
        
        else:
        
            if oe.eccentricity.to_value() == 0:
                
                ta_i: u.Quantity = op.OrbitalPosition.circular_orbit_true_anomaly(time_of_flight=t_i, period=period)
                
            else:
                
                ta_i: u.Quantity = op.OrbitalPosition.elliptical_orbit_true_anomaly(time_of_flight=t_i,
                                                                                    period=period,
                                                                                    eccentricity=oe.eccentricity)
        
        oe.true_anomaly = ta_i
        
        r, _ = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe)
        
        c_f_e, _, _ = o3d.Orbit3D.horizon_footprint(attractor=bodies.Attractor.EARTH, altitude=np.linalg.norm(r) - R_E)
        
        latitude: o3d.AngleHemisphere = o3d.Orbit3D.latitude(inclination=oe.inclination, true_anomaly=ta_i)

        longitude: o3d.AngleHemisphere = o3d.Orbit3D.longitude(orbital_elements=copy.deepcopy(oe),
                                                               latitude=latitude,
                                                               orbit_time=t_i)
        
        longitudes.append(longitude.to_signed_angle().to_value(u.deg))
        latitudes.append(latitude.to_signed_angle().to_value(u.deg))
        footprint.append(c_f_e.to_value(u.km))

    result: schema.GroundTrackOutModelInfo = schema.GroundTrackOutModelInfo(
        draan_dt = d_raan_dt.to_value(u.deg / u.day),
        daop_dt = d_argp_dt.to_value(u.deg / u.day),
        alpha = alpha.to_value(u.deg),
        delta = delta.to_value(u.deg),
        tangentPointAngle=beta.to_value(u.deg),
        lineOfSightAngle=delta_hf.to_value(u.deg),
        horizonFootprintArcLengthAttractor=c_f.to_value(u.km),
        longitude = longitudes,
        latitude = latitudes,
        horizonFootprintArcLengthEarth=footprint,
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
    
    oe: o3d.OrbitalElements = od.OrbitDetermination.gibbs_method(attractor=attractor,
                                                                 position_1=r_1,
                                                                 position_2=r_2,
                                                                 position_3=r_3)
    
    result: schema.OrbitalElements = schema.OrbitalElements(
        sam=oe.specific_angular_momentum.to_value(),
        sma=oe.semimajor_axis.to_value(),
        ecc=oe.eccentricity.to_value(),
        inc=oe.inclination.to_value(),
        raan=oe.right_ascension_of_ascending_node.to_value(),
        aop=oe.argument_of_periapsis.to_value(),
        ta=oe.true_anomaly.to_value()
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
                                                                                local_sidereal_time=theta,
                                                                                latitude=phi,
                                                                                site_altitude=H)
    
    rho_te: u.Quantity = od.OrbitDetermination.topocentric_equatorial_position_vector(attractor=attractor,
                                                                                      position=r,
                                                                                      local_sidereal_time=theta,
                                                                                      latitude=phi,
                                                                                      site_altitude=H)
    
    rho_th, A, a = od.OrbitDetermination.topocentric_horizon_position_vector(attractor=attractor,
                                                                             position=r,
                                                                             local_sidereal_time=theta,
                                                                             latitude=phi,
                                                                             site_altitude=H)
    
    _, alpha, delta = od.OrbitDetermination.topocentric_equatorial_right_ascension_declination(attractor=attractor,
                                                                                               local_sidereal_time=theta,
                                                                                               latitude=phi,
                                                                                               azimuth=A,
                                                                                               elevation=a)
    
    result: schema.TopocentricFrameOutModelInfo = schema.TopocentricFrameOutModelInfo(
        positionGeocentricEquatorial=schema.Vector3D(x=R[0].to_value(), y=R[1].to_value(), z=R[2].to_value()),
        positionTopocentricEquatorial=schema.Vector3D(x=rho_te[0].to_value(), y=rho_te[1].to_value(), z=rho_te[2].to_value()),
        positionTopocentricHorizon=schema.Vector3D(x=rho_th[0].to_value(), y=rho_th[1].to_value(), z=rho_th[2].to_value()),
        azimuth=A.to_value(),
        elevation=a.to_value(),
        rightAscension=alpha.to_value(),
        declination=delta.to_value()
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
                                                          slant_range=rho,
                                                          azimuth=A,
                                                          elevation=a,
                                                          range_rate=drho_dt,
                                                          azimuth_rate=dA_dt,
                                                          elevation_rate=da_dt,
                                                          local_sidereal_time=theta,
                                                          latitude=phi,
                                                          site_altitude=H)
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r, velocity=v)
    
    result: schema.AngleRangeOutModelInfo = schema.AngleRangeOutModelInfo(
        position=schema.Vector3D(x=r[0].to_value(), y=r[1].to_value(), z=r[2].to_value()),
        velocity=schema.Vector3D(x=v[0].to_value(), y=v[1].to_value(), z=v[2].to_value()),
        oe=schema.OrbitalElements(sam=oe.specific_angular_momentum.to_value(),
                                  sma=oe.semimajor_axis.to_value(),
                                  ecc=oe.eccentricity.to_value(),
                                  inc=oe.inclination.to_value(),
                                  raan=oe.right_ascension_of_ascending_node.to_value(),
                                  aop=oe.argument_of_periapsis.to_value(),
                                  ta=oe.true_anomaly.to_value())
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
                                                                    latitude=phi,
                                                                    local_sidereal_time_list=theta,
                                                                    right_ascension_list=alpha,
                                                                    declination_list=delta,
                                                                    observation_time_list=t,
                                                                    site_altitude=H)
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r, velocity=v)
    
    result: schema.AngleRangeOutModelInfo = schema.AngleRangeOutModelInfo(
        position=schema.Vector3D(x=r[0].to_value(), y=r[1].to_value(), z=r[2].to_value()),
        velocity=schema.Vector3D(x=v[0].to_value(), y=v[1].to_value(), z=v[2].to_value()),
        oe=schema.OrbitalElements(sam=oe.specific_angular_momentum.to_value(),
                                  sma=oe.semimajor_axis.to_value(),
                                  ecc=oe.eccentricity.to_value(),
                                  inc=oe.inclination.to_value(),
                                  raan=oe.right_ascension_of_ascending_node.to_value(),
                                  aop=oe.argument_of_periapsis.to_value(),
                                  ta=oe.true_anomaly.to_value())
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
