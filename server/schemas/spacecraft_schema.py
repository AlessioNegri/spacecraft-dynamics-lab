import pydantic

# * generic collection
    
class ActionModel(pydantic.BaseModel):
    
    id: str | None
    error: str | None

# * "spacecrafts" collection

class OrbitModel(pydantic.BaseModel):
    
    sma: float
    ecc: float
    inc: float
    raan: float
    aop: float
    tan: float

class SpacecraftModel(pydantic.BaseModel):
    
    name: str
    mass: float
    orbit: OrbitModel
    image: str | None
    
class SpacecraftModelInfo(SpacecraftModel):
    
    id: str = pydantic.Field(alias='_id')