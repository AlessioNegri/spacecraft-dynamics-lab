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
