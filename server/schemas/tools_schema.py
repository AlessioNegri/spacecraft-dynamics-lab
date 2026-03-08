import fastapi
import pydantic

# * "tools" actions
    
class CartesianInModelInfo(pydantic.BaseModel):
    
    attractor: str
    r_x: float
    r_y: float
    r_z: float
    v_x: float
    v_y: float
    v_z: float
    
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

class KeplerianOutModelInfo(pydantic.BaseModel):
    
    specificAngularMomentum: float
    semiMajorAxis: float
    eccentricity: float
    inclination: float
    rightAscensionOfAscendingNode: float
    argumentOfPeriapsis: float
    trueAnomaly: float

class PerifocalOutModelInfo(pydantic.BaseModel):
    
    positionX: float
    positionY: float
    velocityX: float
    velocityY: float

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