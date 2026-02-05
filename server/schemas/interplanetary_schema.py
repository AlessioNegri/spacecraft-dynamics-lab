import pydantic

# * Simulation
    
class SimulationModel(pydantic.BaseModel):
    
    departureBody: str
    arrivalBody: str
    launchWindowStart: str
    launchWindowEnd: str
    arrivalWindowStart: str
    arrivalWindowEnd: str
    gridSize: int