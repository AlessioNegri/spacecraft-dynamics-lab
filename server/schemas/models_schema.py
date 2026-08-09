import pydantic

# * Atmosphere

class AtmosphereOutModelInfo(pydantic.BaseModel):
    
    altitude: list
    temperature_reference: list
    temperature_consistent: list
    pressure_reference: list
    pressure_consistent: list
    density_reference: list
    density_consistent: list
