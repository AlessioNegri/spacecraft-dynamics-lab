import pydantic

class OrbitModel(pydantic.BaseModel):
    
    sma: float
    ecc: float
    inc: float
    raan: float
    aop: float
    tan: float

class SpacecraftModel(pydantic.BaseModel):
    
    id: str = pydantic.Field(alias='_id')
    name: str
    mass: float
    orbit: OrbitModel
    image: str | None
    
class ActionModel(pydantic.BaseModel):
    
    id: str | None
    error: str | None