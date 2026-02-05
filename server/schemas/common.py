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