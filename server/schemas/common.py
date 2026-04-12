import pydantic

class ActionModel(pydantic.BaseModel):
    
    id: str | None
    error: str | None
    
class InfoModel(pydantic.BaseModel):
    
    source: str = ""
    counter: int = 0
    total: int = 0
    running: bool = False
    data: dict = {}

class Vector3D(pydantic.BaseModel):
    
    x: float
    y: float
    z: float
    
class OrbitalElements(pydantic.BaseModel):
    
    sam: float
    sma: float
    ecc: float
    inc: float
    raan: float
    aop: float
    ta: float
