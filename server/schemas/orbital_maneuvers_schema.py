import pydantic
import typing

from schemas.common import Vector3D, OrbitalElements

# * Common

class Spacecraft(pydantic.BaseModel):
    
    mass: float
    specificImpulse: float
    thrust: float

class Maneuver(pydantic.BaseModel):
    
    dv: float
    dt: float
    dm: float
    burnTime: float
    
class OrbitalManeuverOutModelInfo(pydantic.BaseModel):
    
    orbitalElements: OrbitalElements
    maneuver: Maneuver
    initialOrbit: typing.List[Vector3D]
    transferOrbit: typing.List[Vector3D]
    finalOrbit: typing.List[Vector3D]

class BaseInModelInfo(pydantic.BaseModel):
    
    spacecraft: Spacecraft
    attractor: str
    orbitalElements: OrbitalElements
    
# * Hohmann

class HohmannInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            sma: float
            ecc: float
            direction: int
        
        type: typing.Literal['hohmann']
        data: Data

    maneuver: ManeuverInfo

# * Bi-Elliptic Hohmann

class BiEllipticHohmannInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            sma: float
            ecc: float
            supportApocenterRadius: float
        
        type: typing.Literal['bi-elliptic-hohmann']
        data: Data

    maneuver: ManeuverInfo

# * Phasing

class PhasingInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            targetTrueAnomaly: float
            numRevolutions: int
        
        type: typing.Literal['phasing']
        data: Data

    maneuver: ManeuverInfo

# * Non-Hohmann

class NonHohmannInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            sma: float
            ecc: float
            targetTrueAnomaly: float
        
        type: typing.Literal['non-hohmann']
        data: Data

    maneuver: ManeuverInfo

# * Apse Line Rotation

class ApseLineRotationInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            aop: float
            intersectionPoint: int
        
        type: typing.Literal['apse-line-rotation']
        data: Data

    maneuver: ManeuverInfo

# * Chase

class ChaseInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            trueAnomalyTarget: float
            dt: float
        
        type: typing.Literal['chase']
        data: Data

    maneuver: ManeuverInfo

# * Inclination Change

class InclinationChangeInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            inc: float
        
        type: typing.Literal['inclination-change']
        data: Data

    maneuver: ManeuverInfo

# * Plane Change

class PlaneChangeInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            inc: float
            raan: float
        
        type: typing.Literal['plane-change']
        data: Data

    maneuver: ManeuverInfo

# * Coplanar Circle-to-Circle

class CoplanarCircleCircleInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            sma: float
        
        type: typing.Literal['coplanar-circle-circle']
        data: Data

    maneuver: ManeuverInfo

# * Inclination Change Non-Impulsive

class InclinationChangeNonImpulsiveInModelInfo(BaseInModelInfo):
    
    class ManeuverInfo(pydantic.BaseModel):
    
        class Data(pydantic.BaseModel):
        
            inc: float
        
        type: typing.Literal['inclination-change-non-impulsive']
        data: Data

    maneuver: ManeuverInfo

# * Coplanar Circle-to-Circle

class ToolsCoplanarCircleCircleInModelInfo(pydantic.BaseModel):
    
    attractor: str
    spacecraft: Spacecraft
    initialRadius: float
    finalRadius: float
    earthShadow: bool

# * Inclination change for circular orbit (non-impulsive)

class ToolsInclinationChangeInModelInfo(pydantic.BaseModel):
    
    attractor: str
    spacecraft: Spacecraft
    radius: float
    initialInclination: float
    finalInclination: float

# * Inclination change between different circular orbits

class ToolsInclinedCircularOrbitsInModelInfo(pydantic.BaseModel):
    
    attractor: str
    spacecraft: Spacecraft
    initialRadius: float
    finalRadius: float
    initialInclination: float
    finalInclination: float

# * Common response for non-impulsive maneuvers

class NonImpulsiveOutModelInfo(pydantic.BaseModel):
    
    timeOfFlight: float
    propellantMass: float
    deltaVelocity: float
