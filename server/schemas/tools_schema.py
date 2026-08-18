import fastapi
import pydantic

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
    semiLatusRectum: float
    transverseVelocity: float
    eccentricity: float
    periapsisVelocity: float
    apoapsisVelocity: float
    orbitalPeriod: float
    apoapsisRadius: float
    periapsisRadius: float
    semiMajorAxis: float
    semiMinorAxis: float
    firstCosmicVelocity: float
    secondCosmicVelocity: float
    escapeVelocity: float
    infiniteTrueAnomaly: float
    hyperbolaAsymptoteAngle: float
    turnAngle: float
    aimingRadius: float
    hyperbolicExcessSpeed: float
    characteristicEnergy: float
    oberthManeuverVelocity: float
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

class EquinoctialInModelInfo(pydantic.BaseModel):
    
    orbitalElements: OrbitalElements
    
class EquinoctialOutModelInfo(pydantic.BaseModel):
    
    semimajorAxis: float
    eccentricityVectorH: float
    eccentricityVectorK: float
    ascendingNodeVectorP: float
    ascendingNodeVectorQ: float
    periapsisLocation: float
    
class GroundTrackInModelInfo(pydantic.BaseModel):
    attractor: str
    oe: OrbitalElements
    duration: float | None = None
    samples: int | None = None

class GroundTrackOutModelInfo(pydantic.BaseModel):
    draan_dt: float
    daop_dt: float
    alpha: float
    delta: float
    tangentPointAngle: float
    lineOfSightAngle: float
    horizonFootprintArcLengthAttractor: float
    longitude: list[float]
    latitude: list[float]
    horizonFootprintArcLengthEarth: list[float]
    
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
    
    positionGeocentricEquatorial: Vector3D # ? Geocentric Equatorial Observer
    positionTopocentricEquatorial: Vector3D # ? Topocentric Equatorial
    positionTopocentricHorizon: Vector3D # ? Topocentric Horizon
    azimuth: float # ? Azimuth
    elevation: float # ? Elevation
    rightAscension: float # ? Right Ascension
    declination: float # ? Declination

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
