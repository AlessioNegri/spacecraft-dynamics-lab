import pydantic

# * Simulation
    
class SimulationModel(pydantic.BaseModel):
    
    departureBody: str
    flybyBody: str
    arrivalBody: str
    launchWindowStart: str
    launchWindowEnd: str
    flybyWindowStart: str
    flybyWindowEnd: str
    arrivalWindowStart: str
    arrivalWindowEnd: str
    gridSize: int