import fastapi
import pydantic

# * "tools" actions
    
class CartesianOrbitParametersInModelInfo(pydantic.BaseModel):
    
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

    
class CartesianOrbitParametersOutModelInfo(pydantic.BaseModel):
    
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