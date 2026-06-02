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


# * Nodal Regression

class NodalRegressionInModelInfo(pydantic.BaseModel):
    attractor: str
    orbitalElements: OrbitalElements


class NodalRegressionOutModelInfo(pydantic.BaseModel):
    gravitational: float
    lunar: float
    solar: float


class ApsidalRotationInModelInfo(pydantic.BaseModel):
    attractor: str
    orbitalElements: OrbitalElements


class ApsidalRotationOutModelInfo(pydantic.BaseModel):
    gravitational: float
    lunar: float
    solar: float


class SunSynchronousInModelInfo(pydantic.BaseModel):
    attractor: str
    orbitalElements: OrbitalElements
    nodalRegressionRate: float


class SunSynchronousOutModelInfo(pydantic.BaseModel):
    inclination: float
