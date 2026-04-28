import fastapi
import pydantic
import typing

from schemas.common import Vector3D, OrbitalElements

# * Orbit Representation
    
class CartesianInModelInfo(pydantic.BaseModel):
    
    attractor: str
    position: Vector3D
    velocity: Vector3D
    
    @classmethod
    def as_form(cls,
                attractor: str = fastapi.Form(...),
                r_x: float = fastapi.Form(..., alias="positionX"),
                r_y: float = fastapi.Form(..., alias="positionY"),
                r_z: float = fastapi.Form(..., alias="positionZ"),
                v_x: float = fastapi.Form(..., alias="velocityX"),
                v_y: float = fastapi.Form(..., alias="velocityY"),
                v_z: float = fastapi.Form(..., alias="velocityZ")):
        
        return cls \
        (
            attractor=attractor,
            r_x=r_x,
            r_y=r_y,
            r_z=r_z,
            v_x=v_x,
            v_y=v_y,
            v_z=v_z
        )

class OrbitParametersOutModelInfo(pydantic.BaseModel):
    
    conicType: str
    specificAngularMomentum: float
    specificMechanicalEnergy: float
    eccentricity: float
    orbitalPeriod: float
    apoapsisRadius: float
    periapsisRadius: float
    semiMajorAxis: float
    semiMinorAxis: float
    escapeVelocity: float
    infiniteTrueAnomaly: float
    hyperbolaAsymptoteAngle: float
    turnAngle: float
    aimingRadius: float
    hyperbolicExcessSpeed: float
    characteristicEnergy: float
    rightAscension: float
    declination: float

class PerifocalOutModelInfo(pydantic.BaseModel):
    
    position: Vector3D
    velocity: Vector3D

class KeplerianInModelInfo(pydantic.BaseModel):
    
    attractor: str
    oe: OrbitalElements
    deltaTime: float | None = None
    
class CartesianOutModelInfo(pydantic.BaseModel):
    
    position: Vector3D
    velocity: Vector3D
    
class GroundTrackOutModelInfo(pydantic.BaseModel):
    
    draan_dt: float
    daop_dt: float
    alpha: float
    delta: float
    
# * Orbit Determination

class GibbsMethodInModelInfo(pydantic.BaseModel):
    
    position1: Vector3D
    position2: Vector3D
    position3: Vector3D

class TopocentricFrameInModelInfo(pydantic.BaseModel):
    
    position: Vector3D
    localSiderealTime: float
    latitude: float
    elevation: float

class TopocentricFrameOutModelInfo(pydantic.BaseModel):
    
    geo: Vector3D # ? Geocentric Equatorial Observer
    te: Vector3D # ? Topocentric Equatorial
    th: Vector3D # ? Topocentric Horizon
    A: float # ? Azimuth
    a: float # ? Elevation
    alpha: float # ? Right Ascension
    delta: float # ? Declination
    
class AngleRangeInModelInfo(pydantic.BaseModel):
    
    slantRange: float
    azimuth: float
    elevationA: float
    rangeRate: float
    azimuthRate: float
    elevationARate: float
    localSiderealTime: float
    latitude: float
    elevationH: float

class AngleRangeOutModelInfo(pydantic.BaseModel):
    
    position: Vector3D
    velocity: Vector3D
    oe: OrbitalElements

class GaussMethodInModelInfo(pydantic.BaseModel):
    
    latitude: float
    elevation: float
    localSiderealTime: list
    rightAscension: list
    declination: list
    time: list

class GaussMethodOutModelInfo(pydantic.BaseModel):
    
    position: Vector3D
    velocity: Vector3D
    oe: OrbitalElements

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

# * Interplanetary Trajectory

class SynodicPeriodInModelInfo(pydantic.BaseModel):
    
    departurePlanet: str
    arrivalPlanet: str
    
class SynodicPeriodOutModelInfo(pydantic.BaseModel):
    
    synodicPeriod: float
    initialPhaseAngle: float
    finalPhaseAngle: float
    waitTime: float

class SphereOfInfluenceInModelInfo(pydantic.BaseModel):
    
    mainAttractor: str
    body: str

class SphereOfInfluenceOutModelInfo(pydantic.BaseModel):
    
    sphereOfInfluence: float

class TransferInModelInfo(pydantic.BaseModel):
    
    departurePlanet: str
    arrivalPlanet: str
    departureParkingOrbitHeight: float
    arrivalOrbitalPeriod: float

class TransferOutModelInfo(pydantic.BaseModel):
    
    departureDeltaV: float
    departureHyperbolaEccentricity: float
    departureHyperbolaAsymptoteAngle: float
    arrivalDeltaV: float
    arrivalHyperbolaEccentricity: float
    arrivalHyperbolaAsymptoteAngle: float
