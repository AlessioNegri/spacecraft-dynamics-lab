import fastapi
import pydantic

class Vector3D(pydantic.BaseModel):
    
    x: float
    y: float
    z: float
    
class OrbitalElements(pydantic.BaseModel):
    
    sam: float
    sma: float
    ecc: float
    inc: float
    raan: float
    aop: float
    ta: float

# * "tools" actions
    
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

class KeplerianInModelInfo(pydantic.BaseModel):
    
    attractor: str
    a: float
    ecc: float
    inc: float
    raan: float
    argp: float
    nu: float
    dt: float | None = None
    
    @classmethod
    def as_form(cls,
                attractor: str = fastapi.Form(...),
                a: float = fastapi.Form(..., alias="semiMajorAxis"),
                ecc: float = fastapi.Form(..., alias="eccentricity"),
                inc: float = fastapi.Form(..., alias="inclination"),
                raan: float = fastapi.Form(..., alias="rightAscensionOfAscendingNode"),
                argp: float = fastapi.Form(..., alias="argumentOfPeriapsis"),
                nu: float = fastapi.Form(..., alias="trueAnomaly"),
                dt: float | None = fastapi.Form(None, alias="deltaTime")):
        
        return cls \
        (
            attractor=attractor,
            a=a,
            ecc=ecc,
            inc=inc,
            raan=raan,
            argp=argp,
            nu=nu,
            dt=dt
        )

class GibbsMethodInModelInfo(pydantic.BaseModel):
    
    class Position(pydantic.BaseModel):
        
        x: float
        y: float
        z: float
    
    position1: Position
    position2: Position
    position3: Position

class TopocentricFrameInModelInfo(pydantic.BaseModel):
    
    class Position(pydantic.BaseModel):
        
        x: float
        y: float
        z: float
    
    position: Position
    localSiderealTime: float
    latitude: float
    elevation: float
    
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

class GaussMethodInModelInfo(pydantic.BaseModel):
    
    latitude: float
    elevation: float
    localSiderealTime: list
    rightAscension: list
    declination: list
    time: list
    
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

class GeocentricEquatorialOutModelInfo(pydantic.BaseModel):
    
    positionX: float
    positionY: float
    positionZ: float
    velocityX: float
    velocityY: float
    velocityZ: float

class GroundTrackOutModelInfo(pydantic.BaseModel):
    
    rightAscensionOfAscendingNodeVariation: float
    argumentOfPeriapsisVariation: float
    rightAscension: float
    declination: float

class GibbsMethodOutModelInfo(pydantic.BaseModel):
    
    sam: float
    sma: float
    ecc: float
    inc: float
    raan: float
    aop: float
    ta: float

class TopocentricFrameOutModelInfo(pydantic.BaseModel):
    
    class Position(pydantic.BaseModel):
        
        x: float
        y: float
        z: float
    
    geo: Position # ? Geocentric Equatorial Observer
    te: Position # ? Topocentric Equatorial
    th: Position # ? Topocentric Horizon
    A: float # ? Azimuth
    a: float # ? Elevation
    alpha: float # ? Right Ascension
    delta: float # ? Declination

class AngleRangeOutModelInfo(pydantic.BaseModel):
    
    position: Vector3D
    velocity: Vector3D
    oe: OrbitalElements

class GaussMethodOutModelInfo(pydantic.BaseModel):
    
    position: Vector3D
    velocity: Vector3D
    oe: OrbitalElements