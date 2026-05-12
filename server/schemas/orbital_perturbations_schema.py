import pydantic

from schemas.common import OrbitalElements

# * Simulation

class SimulationModel(pydantic.BaseModel):
    
    orbitalElements: OrbitalElements
    startDate: str
    endDate: str
    atmosphericDrag: bool
    ballisticCoefficient: float
    gravitationalPerturbation: bool
    solarRadiationPressure: bool
    ballisticCoefficientSRP: float
    lunarGravity: bool
    solarGravity: bool
