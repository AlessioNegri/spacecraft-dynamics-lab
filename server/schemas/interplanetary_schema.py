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

# * Synodic Period

class SynodicPeriodInModelInfo(pydantic.BaseModel):
    
    departurePlanet: str
    arrivalPlanet: str

class SynodicPeriodOutModelInfo(pydantic.BaseModel):
    
    synodicPeriod: float
    initialPhaseAngle: float
    finalPhaseAngle: float
    waitTime: float

# * Sphere Of Influence

class SphereOfInfluenceInModelInfo(pydantic.BaseModel):
    
    mainAttractor: str
    body: str

class SphereOfInfluenceOutModelInfo(pydantic.BaseModel):
    
    sphereOfInfluence: float

# * Transfer

class TransferInModelInfo(pydantic.BaseModel):
    
    departurePlanet: str
    arrivalPlanet: str
    departureParkingOrbitHeight: float
    arrivalParkingOrbitHeight: float

class TransferOutModelInfo(pydantic.BaseModel):
    
    class Hyperbola(pydantic.BaseModel):
        
        specificAngularMomentum: float
        eccentricity: float
        periapsisRadius: float
        asymptoteAngle: float
        turningAngle: float
        aimingRadius: float
        specificEnergy: float
        hyperbolicExcessSpeed: float
        characteristicEnergy: float
        timeOfFlight: float
    
    departureDeltaV: float
    departureHyperbola: Hyperbola
    arrivalDeltaV: float
    arrivalHyperbola: Hyperbola
