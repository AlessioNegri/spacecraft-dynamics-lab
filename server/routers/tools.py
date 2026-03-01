import astropy.units as u
import fastapi
import numpy as np
import schemas.tools_schema as schema

import astro.bodies as bodies
import astro.two_body_problem as tbp

COPInModelInfo = schema.CartesianOrbitParametersInModelInfo

COPOutModelInfo = schema.CartesianOrbitParametersOutModelInfo

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/tools', tags=['Tools'])

# >>> PUT

@router.put("/convert-cartesian-to-orbit-parameters", response_model=COPOutModelInfo)
async def put_convert_cartesian_to_orbit_parameters(schema: COPInModelInfo = fastapi.Depends(COPInModelInfo.as_form))\
    -> fastapi.responses.JSONResponse:
    """HTTP PUT cartesian --> Orbit Parameters conversion

    Args:
        schema (COPInModelInfo, optional): Position-Velocity vectors. Defaults to fastapi.Depends(COPInModelInfo.as_form).

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bodies.Attractor = bodies.Attractor(schema.attractor.lower())
    
    r: np.ndarray = np.array([ schema.r_x, schema.r_y, schema.r_z ]) * u.km
    v: np.ndarray = np.array([ schema.v_x, schema.v_y, schema.v_z ]) * u.km / u.s
    
    orbit_parameters: tbp.OrbitParameters = tbp.Orbit.cartesian_to_orbit_parameters(attractor=attractor, r=r, v=v)
    
    result: COPOutModelInfo = COPOutModelInfo(
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
        characteristicEnergy     = orbit_parameters.C_3.to_value()
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())