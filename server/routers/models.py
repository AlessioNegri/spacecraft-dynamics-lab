import astropy.units as u
import fastapi
import numpy as np

import schemas.models_schema as schema

import astro.atmosphere as atmosphere

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/models', tags=['Models'])

# >>> PUT

# ? Models

@router.put("/atmosphere", response_model=schema.AtmosphereOutModelInfo)
async def put_atmosphere() -> fastapi.responses.JSONResponse:    
    """HTTP PUT Atmosphere properties sampled over an altitude range for plotting

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """

    atmosphere_model = atmosphere.Atmosphere()
    
    altitudes: u.Quantity = np.linspace(0, 1000, 1000) * u.km

    temperature_ref, pressure_ref, density_ref = atmosphere_model.sample_properties(altitude_grid=altitudes)
    
    temperature_con, pressure_con, density_con = atmosphere_model.sample_properties(altitude_grid=altitudes,
                                                                                    thermodynamic_consistency=True)

    result: schema.AtmosphereOutModelInfo = schema.AtmosphereOutModelInfo(
        altitude=altitudes.to_value(u.km).tolist(),
        temperature_reference=temperature_ref.tolist(),
        temperature_consistent=temperature_con.tolist(),
        pressure_reference=pressure_ref.tolist(),
        pressure_consistent=pressure_con.tolist(),
        density_reference=density_ref.tolist(),
        density_consistent=density_con.tolist()
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
