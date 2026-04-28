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

# * Optimal Transfer

class OptimalTransferInModelInfo(pydantic.BaseModel):
    
    departureBody: str
    flybyBody: str
    arrivalBody: str
    launchDate: str
    flybyDate: str
    arrivalDate: str
    departureHeight: float
    arrivalPeriapsisHeight: float
    arrivalOrbitalPeriod: float
    
class OptimalTransferOutModelInfo(pydantic.BaseModel):
    
    departureDeltaV: float
    arrivalDeltaV: float
