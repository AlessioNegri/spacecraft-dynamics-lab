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
