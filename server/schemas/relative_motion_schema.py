import pydantic
import typing

from schemas.common import Vector3D, OrbitalElements

# * Comparison

class ComparisonInModelInfo(pydantic.BaseModel):
    
    attractor: str
    orbitalElementsTarget: OrbitalElements
    orbitalElementsChaser: OrbitalElements
    integrationTime: float
    maneuverTime: float

class ComparisonOutModelInfo(pydantic.BaseModel):
    
    linearizedSolution: typing.List[Vector3D]
    nearCircularSolution: typing.List[Vector3D]
    clohessyWiltshireSolution: typing.List[Vector3D]
    twoImpulsiveManeuver: typing.List[Vector3D]
    twoImpulsiveManeuverCost: float
    
# * Relative Motion

class LvlhKinematicsInModelInfo(pydantic.BaseModel):
    
    attractor: str
    orbitalElementsTarget: OrbitalElements
    orbitalElementsChaser: OrbitalElements

class LvlhKinematicsOutModelInfo(pydantic.BaseModel):
    
    position: Vector3D
    velocity: Vector3D
    acceleration: Vector3D
    angularVelocity: Vector3D
    x: typing.List[float]
    y: typing.List[float]
    z: typing.List[float]

class GeocentricEquatorialKinematicsInModelInfo(pydantic.BaseModel):
    
    attractor: str
    orbitalElementsTarget: OrbitalElements
    lvlhPosition: Vector3D
    lvlhVelocity: Vector3D

class GeocentricEquatorialKinematicsOutModelInfo(pydantic.BaseModel):
    
    orbitalElementsChaser: OrbitalElements

# * Rendezvous and docking

class RendezvousAndDockingInModelInfo(pydantic.BaseModel):
    
    timestamp: str
    launchSiteLatitude: float
    launchSiteLongitude: float
    targetInclination: float
    targetRaan: float
    chaserSemimajorAxis: float
    targetSemimajorAxis: float
    closingDistance: float
    closingStrategy: typing.Literal['R_BAR_POS', 'R_BAR_NEG', 'V_BAR_POS', 'V_BAR_NEG']
    closingTrajectory: typing.Literal['ELLIPTIC', 'CYCLOIDAL']
    cycloidalRevolutions: int = 1
    closingInitialVelocity: float = 0.0
    finalApproachDistance: float
    finalApproachTime: float
    finalApproachStrategy: typing.Literal['R_BAR_POS', 'R_BAR_NEG', 'V_BAR_POS', 'V_BAR_NEG']

class RendezvousAndDockingOutModelInfo(pydantic.BaseModel):
    
    launchPhaseAscending: float
    launchPhaseDescending: float
    phasingAngle: float
    phasingDistance: float
    homingAngle: float
    homingDeltaVelocity: float
    closingDeltaVelocity: float
    finalApproachDeltaVelocity: float
