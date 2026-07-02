import pydantic

from schemas.common import Vector3D

# * Simulation

class SimulationModel(pydantic.BaseModel):
    
    body1: str
    body2: str
    integrationTime: float
    lagrangePoint: str
    position: Vector3D
    velocity: Vector3D

# * Orbit Parameters

class OrbitParametersInModelInfo(pydantic.BaseModel):

    body1: str
    body2: str

class OrbitParametersOutModelInfo(pydantic.BaseModel):

    inertialAngularVelocity: float
    dimensionlessMassRatio1: float
    dimensionlessMassRatio2: float
    gravitationalParameter1: float
    gravitationalParameter2: float
    bodyPosition1: float
    bodyPosition2: float
    lagrangianPoint1: list[float]
    lagrangianPoint2: list[float]
    lagrangianPoint3: list[float]
    lagrangianPoint4: list[float]
    lagrangianPoint5: list[float]
