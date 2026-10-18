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


class FrozenOrbitType2OutModelInfo(pydantic.BaseModel):
    inclination: list[float]
    semimajorAxis: list[float]
    firstOrderEccentricity: list[list[float | None]]
    eccentricity: list[list[float | None]]
    type1Inclination: float


class FrozenSunSynchronousOrbitOutModelInfo(pydantic.BaseModel):
    semimajorAxis: list[float]
    sunSynchronousEccentricity: list[float | None]


class CommensurateOrbitOutModelInfo(pydantic.BaseModel):
    altitude: list[float]
    repeatCycle: list[int]
    orbitalRevolutions: list[int]


class GPSOrbitOutModelInfo(pydantic.BaseModel):
    longitudeAscendingNode: list[float]
    driftHarmonics32: list[float]
    driftHarmonics3244: list[float]
    driftHarmonics324452: list[float]
    geoDriftHarmonics22: list[float]
    geoDriftHarmonics2231: list[float]
    geoDriftHarmonics223133: list[float]


class DragOrbitTimesInModelInfo(pydantic.BaseModel):
    semimajorAxis: float = pydantic.Field(gt=0)
    eccentricity: float = pydantic.Field(ge=0, lt=1)
    ballisticCoefficient: float = pydantic.Field(gt=0)


class DragOrbitTimesOutModelInfo(pydantic.BaseModel):
    circularizationTimeDays: float
    circularizationTimeYears: float
    orbitLifetimeDays: float
    orbitLifetimeYears: float
