import astropy.time as time
import astropy.units as u
import fastapi
import numpy as np
import schemas.tools_schema as schema

import astro.bodies as bodies
import astro.two_body_problem as tbp
import astro.orbit_3d as o3d

CartesianIMI = schema.CartesianInModelInfo

KeplerianIMI = schema.KeplerianInModelInfo

OrbitParametersOMI = schema.OrbitParametersOutModelInfo

KeplerianOMI = schema.KeplerianOutModelInfo

PerifocalOMI = schema.PerifocalOutModelInfo

GeocentricEquatorialOMI = schema.GeocentricEquatorialOutModelInfo

GroundTrackOMI = schema.GroundTrackOutModelInfo

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/tools', tags=['Tools'])

# >>> PUT

@router.put("/convert-cartesian-to-orbit-parameters", response_model=OrbitParametersOMI)
async def put_convert_cartesian_to_orbit_parameters(schema: CartesianIMI = fastapi.Depends(CartesianIMI.as_form))\
    -> fastapi.responses.JSONResponse:
    """HTTP PUT Cartesian --> Orbit Parameters conversion

    Args:
        schema (CartesianIMI, optional): Position-Velocity vectors. Defaults to fastapi.Depends(CartesianIMI.as_form).

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(schema.attractor.lower())
    
    r: np.ndarray = np.array([ schema.r_x, schema.r_y, schema.r_z ]) * u.km
    v: np.ndarray = np.array([ schema.v_x, schema.v_y, schema.v_z ]) * u.km / u.s
    
    orbit_parameters: tbp.OrbitParameters = tbp.Orbit.cartesian_to_orbit_parameters(attractor=attractor, r=r, v=v)
    
    alpha, delta = o3d.Orbit3D.right_ascension_declination(r=r)
    
    result: OrbitParametersOMI = OrbitParametersOMI(
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

@router.put("/convert-cartesian-to-keplerian", response_model=KeplerianOMI)
async def put_convert_cartesian_to_keplerian(schema: CartesianIMI = fastapi.Depends(CartesianIMI.as_form))\
    -> fastapi.responses.JSONResponse:
    """HTTP PUT Cartesian --> Keplerian conversion
    
    Args:
        schema (CartesianIMI, optional): Position-Velocity vectors. Defaults to fastapi.Depends(CartesianIMI.as_form).
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(schema.attractor.lower())
    
    r: np.ndarray = np.array([ schema.r_x, schema.r_y, schema.r_z ]) * u.km
    v: np.ndarray = np.array([ schema.v_x, schema.v_y, schema.v_z ]) * u.km / u.s
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.orbital_elements(attractor=attractor, r=r, v=v)
    
    result: KeplerianOMI = KeplerianOMI(
        specificAngularMomentum         = oe.h.to_value(),
        semiMajorAxis                   = oe.a.to_value(),
        eccentricity                    = oe.ecc,
        inclination                     = oe.inc.to_value(),
        rightAscensionOfAscendingNode   = oe.raan.to_value(),
        argumentOfPeriapsis             = oe.argp.to_value(),
        trueAnomaly                     = oe.nu.to_value()
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/convert-cartesian-to-perifocal", response_model=PerifocalOMI)
async def put_convert_cartesian_to_perifocal(schema: CartesianIMI = fastapi.Depends(CartesianIMI.as_form))\
    -> fastapi.responses.JSONResponse:
    """HTTP PUT Cartesian --> Perifocal conversion
    
    Args:
        schema (CartesianIMI, optional): Position-Velocity vectors. Defaults to fastapi.Depends(CartesianIMI.as_form).
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(schema.attractor.lower())
    
    r: np.ndarray = np.array([ schema.r_x, schema.r_y, schema.r_z ]) * u.km
    v: np.ndarray = np.array([ schema.v_x, schema.v_y, schema.v_z ]) * u.km / u.s
    
    r_PF, v_PF = o3d.Orbit3D.geocentric_equatorial_to_perifocal(attractor=attractor, r=r, v=v)
    
    result: PerifocalOMI = PerifocalOMI(
        positionX = r_PF[0].to_value(),
        positionY = r_PF[1].to_value(),
        velocityX = v_PF[0].to_value(),
        velocityY = v_PF[1].to_value()
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