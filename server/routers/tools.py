import fastapi
import numpy as np
import schemas.tools_schema as schema

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
    
    attractor: str = schema.attractor
    
    r: np.ndarray = np.array([ schema.r_x, schema.r_y, schema.r_z ])
    v: np.ndarray = np.array([ schema.v_x, schema.v_y, schema.v_z ])
    
    orbit_parameters: tbp.OrbitParameters = tbp.Orbit.cartesian_to_orbit_parameter(attractor=attractor, r=r, v=v)
    
    result: COPOutModelInfo = COPOutModelInfo(
        conicType                = orbit_parameters.conic_type,
        specificAngularMomentum  = orbit_parameters.h,
        specificMechanicalEnergy = orbit_parameters.epsilon,
        eccentricity             = orbit_parameters.e,
        orbitalPeriod            = orbit_parameters.T,
        apoapsisRadius           = orbit_parameters.r_a,
        periapsisRadius          = orbit_parameters.r_p,
        semiMajorAxis            = orbit_parameters.a,
        semiMinorAxis            = orbit_parameters.b,
        escapeVelocity           = orbit_parameters.v_esc,
        infiniteTrueAnomaly      = orbit_parameters.theta_inf,
        hyperbolaAsymptoteAngle  = orbit_parameters.beta,
        turnAngle                = orbit_parameters.delta_ta,
        aimingRadius             = orbit_parameters.delta_ar,
        hyperbolicExcessSpeed    = orbit_parameters.v_inf,
        characteristicEnergy     = orbit_parameters.C_3
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())