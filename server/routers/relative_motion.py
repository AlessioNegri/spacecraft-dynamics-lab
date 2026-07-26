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

def fill_orbital_elements(attractor: bd.Attractor,
                          orbital_elements_schema: schema.OrbitalElements) -> o3d.OrbitalElements:
    """
    Fill the orbital elements from schema values

    Args:
        attractor (bodies.Attractor): Main attractor
        orbital_elements_schema (schema.OrbitalElements): Pydantic schema orbital elements

    Returns:
        o3d.OrbitalElements: Orbital elements
    """
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements()
    
    oe.specific_angular_momentum = orbital_elements_schema.sam * u.km**2 / u.s
    oe.semimajor_axis = orbital_elements_schema.sma * u.km
    oe.eccentricity = orbital_elements_schema.ecc * u.one
    oe.inclination = orbital_elements_schema.inc * u.deg
    oe.right_ascension_of_ascending_node = orbital_elements_schema.raan * u.deg
    oe.argument_of_periapsis = orbital_elements_schema.aop * u.deg
    oe.true_anomaly = orbital_elements_schema.ta * u.deg
    
    oe.calc_specific_angular_momentum(attractor=attractor)
    
    return oe

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/relative-motion', tags=['Relative Motion'])

# >>> PUT

@router.put("/comparison", response_model=schema.ComparisonOutModelInfo)
async def put_hohmann(data: schema.ComparisonInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Compare a linearized integration with the Clohessy-Wiltshire approximation + 2-impulsive maneuver

    Args:
        data (schema.ComparisonInModelInfo): Target and Chaser orbital elements

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Extract all data
    
    attractor: bd.Attractor = bd.Attractor(data.attractor.lower())
    
    oe_target: o3d.OrbitalElements = fill_orbital_elements(attractor=attractor,
                                                           orbital_elements_schema=data.orbitalElementsTarget)
    
    r_target, v_target = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_target)
    
    oe_chaser: o3d.OrbitalElements = fill_orbital_elements(attractor=attractor,
                                                           orbital_elements_schema=data.orbitalElementsChaser)
    
    r_rel_lvlh, v_rel_lvlh, _, omega_lvlh = rm.RelativeMotion.lvlh_kinematics(attractor=attractor,
                                                                              orbital_elements_target=oe_target,
                                                                              orbital_elements_chaser=oe_chaser)
    
    # * Linearized
    
    relavive_motion: rm.RelativeMotion = rm.RelativeMotion()
    
    relavive_motion.init(attractor=attractor,
                         position=r_target,
                         velocity=v_target,
                         relative_position=r_rel_lvlh,
                         relative_velocity=v_rel_lvlh)
    
    linearized_result: rm.ResultRM = relavive_motion.propagate_for(delta=time.TimeDelta(data.integrationTime * u.hour))
    
    linearized_solution: typing.List[schema.Vector3D] = []
    
    for x, y, z in zip(linearized_result.relative_position_x.to_value(),
                       linearized_result.relative_position_y.to_value(),
                       linearized_result.relative_position_z.to_value()):
        
        linearized_solution.append(schema.Vector3D(x=x, y=y, z=z))
    
    # * Clohessy-Wiltshire
    
    n: u.Quantity = np.linalg.norm(omega_lvlh.to_value(u.rad / u.s)) * u.rad / u.s
    
    clohessy_wiltshire_solution: typing.List[schema.Vector3D] = []
    
    for t in np.linspace(0, u.Quantity(data.integrationTime * u.hour).to_value(u.s), len(linearized_solution)):
            
        dr, _ = rm.RelativeMotion.clohessy_wiltshire_equations(relative_position_0=r_rel_lvlh,
                                                               relative_velocity_0=v_rel_lvlh,
                                                               mean_motion=n,
                                                               final_time=t * u.s)
        
        clohessy_wiltshire_solution.append(schema.Vector3D(x=dr[0].to_value(u.km),
                                                           y=dr[1].to_value(u.km),
                                                           z=dr[2].to_value(u.km)))
    
    # * 2-Impulsive Maneuver
    
    dv_tot, dx, dy, dz = rm.RelativeMotion.two_impulsive_rendezvous_maneuver(attractor=attractor,
                                                                             orbital_elements_target=oe_target,
                                                                             orbital_elements_chaser=oe_chaser,
                                                                             maneuver_time=data.maneuverTime * u.hour)
    
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

@router.put("/lvlh-kinematics", response_model=schema.LvlhKinematicsOutModelInfo)
async def put_lvlh_kinematics(data: schema.LvlhKinematicsInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Local Vertical Local Horizontal Kinematics
    
    Args:
        data (schema.LvlhKinematicsInModelInfo): Attractor and orbital elements of target and chaser
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bd.Attractor = bd.Attractor(data.attractor.lower())
    
    oe_target: o3d.OrbitalElements = fill_orbital_elements(attractor=attractor,
                                                           orbital_elements_schema=data.orbitalElementsTarget)
    
    oe_chaser: o3d.OrbitalElements = fill_orbital_elements(attractor=attractor,
                                                           orbital_elements_schema=data.orbitalElementsChaser)
    
    kinematics = rm.RelativeMotion.lvlh_kinematics(attractor=attractor,
                                                   orbital_elements_target=oe_target,
                                                   orbital_elements_chaser=oe_chaser)
    
    r: np.ndarray = kinematics[0].to_value(u.km)
    
    v: np.ndarray = kinematics[1].to_value(u.km / u.s)
    
    a: np.ndarray = kinematics[2].to_value(u.km / u.s**2)
    
    o: np.ndarray = kinematics[3].to_value(u.deg / u.s)
    
    x, y, z = rm.RelativeMotion.simulate_lvlh_kinematics(attractor=attractor,
                                                         orbital_elements_target=oe_target,
                                                         orbital_elements_chaser=oe_chaser)
    
    result: schema.LvlhKinematicsOutModelInfo = schema.LvlhKinematicsOutModelInfo(
        position = schema.Vector3D(x=r[0], y=r[1], z=r[2]),
        velocity = schema.Vector3D(x=v[0], y=v[1], z=v[2]),
        acceleration = schema.Vector3D(x=a[0], y=a[1], z=a[2]),
        angularVelocity = schema.Vector3D(x=o[0], y=o[1], z=o[2]),
        x = x,
        y = y,
        z = z
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/geocentric-equatorial-kinematics", response_model=schema.GeocentricEquatorialKinematicsOutModelInfo)
async def put_geocentric_equatorial_kinematics(data: schema.GeocentricEquatorialKinematicsInModelInfo)\
    -> fastapi.responses.JSONResponse:
    """HTTP PUT Geocentric Equatorial Kinematics
    
    Args:
        data (schema.GeocentricEquatorialKinematicsInModelInfo): Attractor, orbital elements of target, and chaser lvlh
        
    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    attractor: bd.Attractor = bd.Attractor(data.attractor.lower())
    
    oe_target: o3d.OrbitalElements = fill_orbital_elements(attractor=attractor,
                                                           orbital_elements_schema=data.orbitalElementsTarget)
    
    r_target, v_target = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_target)
    
    r_rel_lvlh: u.Quantity = np.array([data.lvlhPosition.x, data.lvlhPosition.y, data.lvlhPosition.z]) * u.km
    
    v_rel_lvlh: u.Quantity = np.array([data.lvlhVelocity.x, data.lvlhVelocity.y, data.lvlhVelocity.z]) * u.km / u.s
    
    r_chaser, v_chaser = rm.RelativeMotion.geocentric_equatorial_kinematics(position_target=r_target,
                                                                            velocity_target=v_target,
                                                                            position_rel_lvlh=r_rel_lvlh,
                                                                            velocity_rel_lvlh=v_rel_lvlh)
    
    oe_chaser: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor,
                                                                        position=r_chaser,
                                                                        velocity=v_chaser)
    
    result: schema.GeocentricEquatorialKinematicsOutModelInfo = schema.GeocentricEquatorialKinematicsOutModelInfo(
        orbitalElementsChaser=schema.OrbitalElements(
            sam=oe_chaser.specific_angular_momentum.to_value(u.km**2 / u.s),
            sma=oe_chaser.semimajor_axis.to_value(u.km),
            ecc=oe_chaser.eccentricity.to_value(u.one),
            inc=oe_chaser.inclination.to_value(u.deg),
            raan=oe_chaser.right_ascension_of_ascending_node.to_value(u.deg),
            aop=oe_chaser.argument_of_periapsis.to_value(u.deg),
            ta=oe_chaser.true_anomaly.to_value(u.deg)
        )
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
