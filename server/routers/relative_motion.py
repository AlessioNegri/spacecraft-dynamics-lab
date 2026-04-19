import astropy.time as time
import astropy.units as u
import fastapi
import numpy as np
import typing

import schemas.relative_motion_schema as schema

import astro.relative_motion as rm
import astro.bodies as bd
import astro.orbit_3d as o3d

# --- UTILITY ---

def fill_orbital_elements(oe_schema: schema.OrbitalElements) -> o3d.OrbitalElements:
    """Fill the orbital elements from schema values

    Args:
        oe_schema (schema.OrbitalElements): Pydantic schema orbital elements

    Returns:
        o3d.OrbitalElements: Orbital elements
    """
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements()
    
    oe.h = oe_schema.sam * u.km**2 / u.s
    oe.a = oe_schema.sma * u.km
    oe.ecc = oe_schema.ecc * u.dimensionless_unscaled
    oe.inc = oe_schema.inc * u.deg
    oe.raan = oe_schema.raan * u.deg
    oe.argp = oe_schema.aop * u.deg
    oe.nu = oe_schema.ta * u.deg
    
    return oe

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/relative-motion', tags=['Relative Motion'])

# >>> PUT

@router.put("/comparison", response_model=schema.ComparisonOutModelInfo)
async def put_hohmann(data: schema.ComparisonInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Compare a linearized integration with the Clohessy-Wiltshire approximation

    Args:
        data (schema.ComparisonInModelInfo): Target and Chaser orbital elements

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Extract all data
    
    attractor: bd.Attractor = bd.Attractor(data.attractor.lower())
    
    oe_target: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElementsTarget)
    
    r_target, v_target = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe_target)
    
    oe_chaser: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElementsChaser)
    
    kinematics = rm.RelativeMotion.lvlh_kinematics(attractor=attractor, oe_target=oe_target, oe_chaser=oe_chaser)
    
    # * Linearized
    
    relavive_motion: rm.RelativeMotion = rm.RelativeMotion()
    
    relavive_motion.init(attractor=attractor, r=r_target, v=v_target, dr=kinematics[0], dv=kinematics[1])
    
    linearized_result: rm.Result = relavive_motion.propagate_for(delta=time.TimeDelta(data.integrationTime * u.hour))
    
    linearized_solution: typing.List[schema.Vector3D] = []
    
    for x, y, z in zip(linearized_result.dr_x.to_value(),
                       linearized_result.dr_y.to_value(),
                       linearized_result.dr_z.to_value()):
        
        linearized_solution.append(schema.Vector3D(x=x, y=y, z=z))
    
    # * Clohessy-Wiltshire
    
    n: u.Quantity = np.linalg.norm(kinematics[3].to_value(u.rad / u.s)) * u.rad / u.s
    
    clohessy_wiltshire_solution: typing.List[schema.Vector3D] = []
    
    for t in np.linspace(0, u.Quantity(data.integrationTime * u.hour).to_value(u.s), len(linearized_solution)):
            
        dr, _ = rm.RelativeMotion.clohessy_wiltshire_equations(dr_0=kinematics[0], dv_0=kinematics[1], n=n, t=t * u.s)
        
        clohessy_wiltshire_solution.append(schema.Vector3D(x=dr[0].to_value(u.km),
                                                           y=dr[1].to_value(u.km),
                                                           z=dr[2].to_value(u.km)))
    
    # * 2-Impulsive Maneuver
    
    dv_tot, dx, dy, dz = rm.RelativeMotion.two_impulsive_rendezvous_maneuver(attractor=attractor,
                                                                             oe_target=oe_target,
                                                                             oe_chaser=oe_chaser,
                                                                             t_maneuver=data.maneuverTime * u.hour)
    
    two_impulsive_maneuver: typing.List[schema.Vector3D] = []
    
    for x, y, z in zip(dx.to_value(), dy.to_value(),dz.to_value()):
        
        two_impulsive_maneuver.append(schema.Vector3D(x=x, y=y, z=z))
    
    # * Result
    
    result: schema.ComparisonOutModelInfo = schema.ComparisonOutModelInfo(
        linearizedSolution=linearized_solution,
        clohessyWiltshireSolution=clohessy_wiltshire_solution,
        twoImpulsiveManeuver=two_impulsive_maneuver,
        twoImpulsiveManeuverCost=dv_tot.to_value(u.m / u.s)
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())