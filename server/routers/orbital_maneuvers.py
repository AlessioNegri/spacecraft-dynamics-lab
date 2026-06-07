import astropy.time as time
import astropy.units as u
import copy
import fastapi
import typing

import schemas.orbital_maneuvers_schema as schema

import astro.bodies as bodies
import astro.orbit_3d as o3d
import astro.orbital_maneuvers as om
import astro.two_body_problem as tbp
import astro.orbital_position as op

# --- UTILITY ---

def fill_rocket_motor(spacecraft_schema: schema.Spacecraft) -> om.RocketMotor:
    """
    Fill the rocket motor from schema values

    Args:
        spacecraft_schema (schema.Spacecraft): Pydantic schema spacecraft

    Returns:
        om.RocketMotor: Rocket motor
    """
    
    rocket_motor: om.RocketMotor = om.RocketMotor()
    
    rocket_motor.specific_impulse = spacecraft_schema.specificImpulse * u.s
    rocket_motor.thrust = spacecraft_schema.thrust * u.N
    rocket_motor.spacecraft_mass = spacecraft_schema.mass * u.kg
    rocket_motor.propellant_mass = 0.0 * u.kg
    
    return rocket_motor

def fill_orbital_elements(orbital_elements_schema: schema.OrbitalElements) -> o3d.OrbitalElements:
    """
    Fill the orbital elements from schema values

    Args:
        orbital_elements_schema (schema.OrbitalElements): Pydantic schema orbital elements

    Returns:
        o3d.OrbitalElements: Orbital elements
    """
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements()
    
    oe.specific_angular_momentum = orbital_elements_schema.sam * u.km**2 / u.s
    oe.semimajor_axis = orbital_elements_schema.sma * u.km
    oe.eccentricity = orbital_elements_schema.ecc * u.dimensionless_unscaled
    oe.inclination = orbital_elements_schema.inc * u.deg
    oe.right_ascension_of_ascending_node = orbital_elements_schema.raan * u.deg
    oe.argument_of_periapsis = orbital_elements_schema.aop * u.deg
    oe.true_anomaly = orbital_elements_schema.ta * u.deg
    
    return oe

def propagate_orbit(attractor: bodies.Attractor,
                    orbital_elements: o3d.OrbitalElements,
                    delta_time: time.TimeDelta) -> typing.List[schema.Vector3D]:
    """
    Propagate the orbit with given Orbital Parameters for a given time

    Args:
        attractor (bodies.Attractor): Main attractor
        orbital_elements (o3d.OrbitalElements): Orbital Elements with true anomaly from initial position
        delta_timedt (time.TimeDelta): Time of integration

    Returns:
        typing.List[schema.Vector3D]: Simulation points
    """
    
    r_gef, v_gef = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=orbital_elements)
    
    orbit: tbp.Orbit = tbp.Orbit()
    
    orbit.from_cartesian(attractor=attractor, position=r_gef, velocity=v_gef)
    
    result: tbp.Result = orbit.propagate_for(delta_time)
    
    simulation_points: typing.List[schema.Vector3D] = []
    
    for x, y, z in zip(result.position_x.to_value(), result.position_y.to_value(), result.position_z.to_value()):
        
        simulation_points.append(schema.Vector3D(x=x, y=y, z=z))
    
    return simulation_points

def calculate_simulation_time(attractor: bodies.Attractor,
                              orbital_elements: o3d.OrbitalElements,
                              true_anomaly_1: u.Quantity,
                              true_anomaly_2: u.Quantity) -> u.Quantity:
    """
    Calculate the simulation time to move from two true anomalies on the same orbit

    Args:
        attractor (bodies.Attractor): Main attractor
        orbital_elements (o3d.OrbitalElements): Orbital Elements
        true_anomaly_1 (u.Quantity): First true anomaly
        true_anomaly_2 (u.Quantity): Second true anomaly

    Returns:
        u.Quantity: Simulation time from first true anomaly
    """
    
    if orbital_elements.eccentricity < 1:
        
        t_1: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=true_anomaly_1,
                                                                   period=orbital_elements.calc_orbital_period(attractor),
                                                                   eccentricity=orbital_elements.eccentricity)
        
        t_2: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=true_anomaly_2,
                                                                   period=orbital_elements.calc_orbital_period(attractor),
                                                                   eccentricity=orbital_elements.eccentricity)
    
    else:
        
        t_1: u.Quantity = op.OrbitalPosition.hyperbolic_orbit_time(true_anomaly=true_anomaly_1,
                                                                   specific_angular_momentum=orbital_elements.specific_angular_momentum,
                                                                   eccentricity=orbital_elements.eccentricity,
                                                                   attractor=attractor)
        
        t_2: u.Quantity = op.OrbitalPosition.hyperbolic_orbit_time(true_anomaly=true_anomaly_2,
                                                                   specific_angular_momentum=orbital_elements.specific_angular_momentum,
                                                                   eccentricity=orbital_elements.eccentricity,
                                                                   attractor=attractor)
    
    if t_2 > t_1:
        
        t_sim = t_2 - t_1
        
    else:
        
        if orbital_elements.eccentricity < 1:
            
            t_sim = orbital_elements.calc_orbital_period(attractor) - (t_1 - t_2)
        
        else:
            
            t_sim = t_1 - t_2
    
    return t_sim

# --- HTTP ---

router: fastapi.APIRouter = fastapi.APIRouter(prefix='/orbital-maneuvers', tags=['Orbital Maneuvers'])

# >>> PUT

@router.put("/hohmann", response_model=schema.OrbitalManeuverOutModelInfo)
async def put_hohmann(data: schema.HohmannInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Execute an Hohmann maneuver

    Args:
        data (schema.HohmannInModelInfo): Hohmann maneuver

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Maneuver
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    rocket_motor: om.RocketMotor = fill_rocket_motor(data.spacecraft)
    
    oe_1: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElements)
    
    oe_2_schema: schema.OrbitalElements = copy.deepcopy(data.orbitalElements)
    
    oe_2_schema.sma = data.maneuver.data.sma
    oe_2_schema.ecc = data.maneuver.data.ecc
    
    oe_2: o3d.OrbitalElements = fill_orbital_elements(oe_2_schema)

    if data.maneuver.data.direction == 0:
        
        direction = om.HohmannDirection.PERICENTER_APOCENTER
        
        oe_2.true_anomaly = 180.0 * u.deg
        
    else:
        
        direction = om.HohmannDirection.APOCENTER_PERICENTER
        
        oe_2.true_anomaly = 0.0 * u.deg
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements_1=oe_1,
                                                                       orbital_elements_2=oe_2,
                                                                       direction=direction)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  orbital_elements=oe_1,
                                                                  delta_time=time.TimeDelta(oe_1.calc_orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              orbital_elements=oe_1,
                                                              true_anomaly_1=oe_1.true_anomaly,
                                                              true_anomaly_2=maneuver.true_anomaly_list[0])
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=oe_1,
                                          delta_time=time.TimeDelta(dt_maneuver_point)))
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=maneuver.orbital_elements_list[0],
                                          delta_time=time.TimeDelta(maneuver.orbital_elements_list[0].calc_orbital_period(attractor) / 2)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                orbital_elements=oe_2,
                                                                delta_time=time.TimeDelta(oe_2.calc_orbital_period(attractor)))
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe_2.specific_angular_momentum.to_value(),
            sma=oe_2.semimajor_axis.to_value(),
            ecc=oe_2.eccentricity.to_value(),
            inc=oe_2.inclination.to_value(),
            raan=oe_2.right_ascension_of_ascending_node.to_value(),
            aop=oe_2.argument_of_periapsis.to_value(),
            ta=oe_2.true_anomaly.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.delta_velocity_list]),
            dt=sum([x.to_value(u.hour) for x in maneuver.flight_time_list]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.delta_mass_list]),
            burnTime=sum([x.to_value() for x in maneuver.burn_time_list])
        ),
        initialOrbit=initial_orbit,
        transferOrbit=transfer_orbit,
        finalOrbit=final_orbit
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/bi-elliptic-hohmann", response_model=schema.OrbitalManeuverOutModelInfo)
async def put_bi_elliptic_hohmann(data: schema.BiEllipticHohmannInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Execute a Bi-Elliptic Hohmann maneuver

    Args:
        data (schema.BiEllipticHohmannInModelInfo): Bi-Elliptic Hohmann maneuver

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Maneuver
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    rocket_motor: om.RocketMotor = fill_rocket_motor(data.spacecraft)
    
    oe_1: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElements)
    
    oe_2_schema : schema.OrbitalElements = copy.deepcopy(data.orbitalElements)
    
    oe_2_schema.sma = data.maneuver.data.sma
    oe_2_schema.ecc = data.maneuver.data.ecc
    
    oe_2: o3d.OrbitalElements = fill_orbital_elements(oe_2_schema)

    r_3: u.Quantity = data.maneuver.data.supportApocenterRadius * u.km
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.bi_elliptic_hohmann_transfer(attractor=attractor,
                                                                                   rocket_motor=rocket_motor,
                                                                                   orbital_elements_1=oe_1,
                                                                                   orbital_elements_2=oe_2,
                                                                                   apoapsis_radius=r_3)
    
    oe_2.true_anomaly = 0.0 * u.deg
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  orbital_elements=oe_1,
                                                                  delta_time=time.TimeDelta(oe_1.calc_orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              orbital_elements=oe_1,
                                                              true_anomaly_1=oe_1.true_anomaly,
                                                              true_anomaly_2=maneuver.orbital_elements_list[0].true_anomaly)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=oe_1,
                                          delta_time=time.TimeDelta(dt_maneuver_point)))
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=maneuver.orbital_elements_list[0],
                                          delta_time=time.TimeDelta(maneuver.orbital_elements_list[0].calc_orbital_period(attractor) / 2)))
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=maneuver.orbital_elements_list[1],
                                          delta_time=time.TimeDelta(maneuver.orbital_elements_list[1].calc_orbital_period(attractor) / 2)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                orbital_elements=oe_2,
                                                                delta_time=time.TimeDelta(oe_2.calc_orbital_period(attractor)))
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe_2.specific_angular_momentum.to_value(),
            sma=oe_2.semimajor_axis.to_value(),
            ecc=oe_2.eccentricity.to_value(),
            inc=oe_2.inclination.to_value(),
            raan=oe_2.right_ascension_of_ascending_node.to_value(),
            aop=oe_2.argument_of_periapsis.to_value(),
            ta=oe_2.true_anomaly.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.delta_velocity_list]),
            dt=sum([x.to_value(u.hour) for x in maneuver.flight_time_list]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.delta_mass_list]),
            burnTime=sum([x.to_value() for x in maneuver.burn_time_list])
        ),
        initialOrbit=initial_orbit,
        transferOrbit=transfer_orbit,
        finalOrbit=final_orbit
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/phasing", response_model=schema.OrbitalManeuverOutModelInfo)
async def put_phasing(data: schema.PhasingInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Execute a Phasing maneuver

    Args:
        data (schema.PhasingInModelInfo): Phasing maneuver

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Maneuver
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    rocket_motor: om.RocketMotor = fill_rocket_motor(data.spacecraft)
    
    oe: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElements)

    nu_target: u.Quantity = data.maneuver.data.targetTrueAnomaly * u.deg
    
    num_revolutions: int = data.maneuver.data.numRevolutions
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.phasing_maneuver(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements=oe,
                                                                       true_anomaly_target=nu_target,
                                                                       num_revolutions=num_revolutions)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  orbital_elements=oe,
                                                                  delta_time=time.TimeDelta(oe.calc_orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              orbital_elements=oe,
                                                              true_anomaly_1=oe.true_anomaly,
                                                              true_anomaly_2=maneuver.orbital_elements_list[0].true_anomaly)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=oe,
                                          delta_time=time.TimeDelta(dt_maneuver_point)))
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=maneuver.orbital_elements_list[0],
                                          delta_time=time.TimeDelta(maneuver.orbital_elements_list[0].calc_orbital_period(attractor))))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = []
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe.specific_angular_momentum.to_value(),
            sma=oe.semimajor_axis.to_value(),
            ecc=oe.eccentricity.to_value(),
            inc=oe.inclination.to_value(),
            raan=oe.right_ascension_of_ascending_node.to_value(),
            aop=oe.argument_of_periapsis.to_value(),
            ta=oe.true_anomaly.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.delta_velocity_list]),
            dt=sum([x.to_value(u.hour) for x in maneuver.flight_time_list]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.delta_mass_list]),
            burnTime=sum([x.to_value() for x in maneuver.burn_time_list])
        ),
        initialOrbit=initial_orbit,
        transferOrbit=transfer_orbit,
        finalOrbit=final_orbit
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/non-hohmann", response_model=schema.OrbitalManeuverOutModelInfo)
async def put_non_hohmann(data: schema.NonHohmannInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Execute a Non-Hohmann maneuver

    Args:
        data (schema.NonHohmannInModelInfo): Non-Hohmann maneuver

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Maneuver
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    rocket_motor: om.RocketMotor = fill_rocket_motor(data.spacecraft)
    
    oe_1: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElements)
    
    oe_2:o3d.OrbitalElements = copy.deepcopy(oe_1)

    oe_2.semimajor_axis = data.maneuver.data.sma * u.km
    oe_2.eccentricity = data.maneuver.data.ecc * u.one
    oe_2.true_anomaly = data.maneuver.data.targetTrueAnomaly * u.deg
    
    oe_2.calc_specific_angular_momentum(attractor=attractor)
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.non_hohmann_transfer(attractor=attractor,
                                                                           rocket_motor=rocket_motor,
                                                                           orbital_elements_1=oe_1,
                                                                           orbital_elements_2=oe_2)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  orbital_elements=oe_1,
                                                                  delta_time=time.TimeDelta(oe_1.calc_orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              orbital_elements=maneuver.orbital_elements_list[0],
                                                              true_anomaly_1=maneuver.orbital_elements_list[0].true_anomaly,
                                                              true_anomaly_2=oe_2.true_anomaly)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=maneuver.orbital_elements_list[0],
                                          delta_time=time.TimeDelta(dt_maneuver_point)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                orbital_elements=oe_2,
                                                                delta_time=time.TimeDelta(oe_2.calc_orbital_period(attractor)))
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe_2.specific_angular_momentum.to_value(),
            sma=oe_2.semimajor_axis.to_value(),
            ecc=oe_2.eccentricity.to_value(),
            inc=oe_2.inclination.to_value(),
            raan=oe_2.right_ascension_of_ascending_node.to_value(),
            aop=oe_2.argument_of_periapsis.to_value(),
            ta=oe_2.true_anomaly.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.delta_velocity_list]),
            dt=sum([x.to_value(u.hour) for x in maneuver.flight_time_list]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.delta_mass_list]),
            burnTime=sum([x.to_value() for x in maneuver.burn_time_list])
        ),
        initialOrbit=initial_orbit,
        transferOrbit=transfer_orbit,
        finalOrbit=final_orbit
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/apse-line-rotation", response_model=schema.OrbitalManeuverOutModelInfo)
async def put_apse_line_rotation(data: schema.ApseLineRotationInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Execute an Apse Line Rotation maneuver

    Args:
        data (schema.ApseLineRotationInModelInfo): Apse Line Rotation maneuver

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Maneuver
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    rocket_motor: om.RocketMotor = fill_rocket_motor(data.spacecraft)
    
    oe_1: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElements)
    
    oe_2_schema: schema.OrbitalElements = copy.deepcopy(data.orbitalElements)
    
    oe_2_schema.aop = data.maneuver.data.aop
    
    oe_2: o3d.OrbitalElements = fill_orbital_elements(oe_2_schema)

    sip: bool = data.maneuver.data.intersectionPoint == 1
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.apse_line_rotation_from_eta(attractor=attractor,
                                                                                  rocket_motor=rocket_motor,
                                                                                  orbital_elements_1=oe_1,
                                                                                  orbital_elements_2=oe_2,
                                                                                  eta=oe_2.argument_of_periapsis - oe_1.argument_of_periapsis,
                                                                                  second_intersection_point=sip)
    
    oe_2.true_anomaly = maneuver.orbital_elements_list[0].true_anomaly
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  orbital_elements=oe_1,
                                                                  delta_time=time.TimeDelta(oe_1.calc_orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              orbital_elements=oe_1,
                                                              true_anomaly_1=oe_1.true_anomaly,
                                                              true_anomaly_2=maneuver.true_anomaly_list[0])
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=oe_1,
                                          delta_time=time.TimeDelta(dt_maneuver_point)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                orbital_elements=oe_2,
                                                                delta_time=time.TimeDelta(oe_2.calc_orbital_period(attractor)))
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe_2.specific_angular_momentum.to_value(),
            sma=oe_2.semimajor_axis.to_value(),
            ecc=oe_2.eccentricity.to_value(),
            inc=oe_2.inclination.to_value(),
            raan=oe_2.right_ascension_of_ascending_node.to_value(),
            aop=oe_2.argument_of_periapsis.to_value(),
            ta=maneuver.orbital_elements_list[0].true_anomaly.to_value(u.deg)
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.delta_velocity_list]),
            dt=sum([x.to_value(u.hour) for x in maneuver.flight_time_list]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.delta_mass_list]),
            burnTime=sum([x.to_value() for x in maneuver.burn_time_list])
        ),
        initialOrbit=initial_orbit,
        transferOrbit=transfer_orbit,
        finalOrbit=final_orbit
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/chase", response_model=schema.OrbitalManeuverOutModelInfo)
async def put_chase(data: schema.ChaseInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Execute a Chase maneuver

    Args:
        data (schema.ChaseInModelInfo): Chase maneuver

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Maneuver
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    rocket_motor: om.RocketMotor = fill_rocket_motor(data.spacecraft)
    
    oe: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElements)

    nu_T: u.Quantity = data.maneuver.data.trueAnomalyTarget * u.deg
    
    dt: time.TimeDelta = time.TimeDelta(u.Quantity(data.maneuver.data.dt, u.hour))
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.chase_maneuver(attractor=attractor,
                                                                     rocket_motor=rocket_motor,
                                                                     orbital_elements=oe,
                                                                     true_anomaly_target=nu_T,
                                                                     delta_time=dt)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  orbital_elements=oe,
                                                                  delta_time=time.TimeDelta(oe.calc_orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                        orbital_elements=maneuver.orbital_elements_list[0],
                                                        true_anomaly_1=maneuver.orbital_elements_list[0].true_anomaly,
                                                        true_anomaly_2=maneuver.orbital_elements_list[1].true_anomaly)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=maneuver.orbital_elements_list[0],
                                          delta_time=time.TimeDelta(dt_maneuver)))
    
    # * Final Orbit
    
    r_fin, _ = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor,
                                                  orbital_elements=maneuver.orbital_elements_list[-1])
    
    final_orbit: typing.List[schema.Vector3D] = [schema.Vector3D(x=r_fin[0].to_value(u.km),
                                                                 y=r_fin[1].to_value(u.km),
                                                                 z=r_fin[2].to_value(u.km))]
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe.specific_angular_momentum.to_value(),
            sma=oe.semimajor_axis.to_value(),
            ecc=oe.eccentricity.to_value(),
            inc=oe.inclination.to_value(),
            raan=oe.right_ascension_of_ascending_node.to_value(),
            aop=oe.argument_of_periapsis.to_value(),
            ta=oe.true_anomaly.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.delta_velocity_list]),
            dt=sum([x.to_value(u.hour) for x in maneuver.flight_time_list]),
            dm=sum([x.to_value() for x in maneuver.delta_mass_list]),
            burnTime=sum([x.to_value() for x in maneuver.burn_time_list])
        ),
        initialOrbit=initial_orbit,
        transferOrbit=transfer_orbit,
        finalOrbit=final_orbit
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/inclination-change", response_model=schema.OrbitalManeuverOutModelInfo)
async def put_inclination_change(data: schema.InclinationChangeInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Execute an inclination change maneuver

    Args:
        data (schema.InclinationChangeInModelInfo): Inclination change maneuver

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    # * Maneuver

    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())

    rocket_motor: om.RocketMotor = fill_rocket_motor(data.spacecraft)

    oe_1: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElements)

    oe_2_schema: schema.OrbitalElements = copy.deepcopy(data.orbitalElements)

    oe_2_schema.inc = data.maneuver.data.inc

    oe_2: o3d.OrbitalElements = fill_orbital_elements(oe_2_schema)

    maneuver: om.ManeuverResult = om.OrbitalManeuvers.inclination_change_maneuver(attractor=attractor,
                                                                                   rocket_motor=rocket_motor,
                                                                                   orbital_elements_1=oe_1,
                                                                                   orbital_elements_2=oe_2)

    oe_2.true_anomaly = maneuver.true_anomaly_list[0]
    
    # * Initial Orbit

    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  orbital_elements=oe_1,
                                                                  delta_time=time.TimeDelta(oe_1.calc_orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []

    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              orbital_elements=oe_1,
                                                              true_anomaly_1=oe_1.true_anomaly,
                                                              true_anomaly_2=maneuver.true_anomaly_list[0])

    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=oe_1,
                                          delta_time=time.TimeDelta(dt_maneuver_point)))

    # * Final Orbit

    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                orbital_elements=oe_2,
                                                                delta_time=time.TimeDelta(oe_2.calc_orbital_period(attractor)))

    # * Result

    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe_2.specific_angular_momentum.to_value(),
            sma=oe_2.semimajor_axis.to_value(),
            ecc=oe_2.eccentricity.to_value(),
            inc=oe_2.inclination.to_value(),
            raan=oe_2.right_ascension_of_ascending_node.to_value(),
            aop=oe_2.argument_of_periapsis.to_value(),
            ta=oe_2.true_anomaly.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.delta_velocity_list]),
            dt=sum([x.to_value(u.hour) for x in maneuver.flight_time_list]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.delta_mass_list]),
            burnTime=sum([x.to_value() for x in maneuver.burn_time_list])
        ),
        initialOrbit=initial_orbit,
        transferOrbit=transfer_orbit,
        finalOrbit=final_orbit
    )

    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())

@router.put("/plane-change", response_model=schema.OrbitalManeuverOutModelInfo)
async def put_plane_change(data: schema.PlaneChangeInModelInfo) -> fastapi.responses.JSONResponse:
    """HTTP PUT Execute a plane change maneuver

    Args:
        data (schema.PlaneChangeInModelInfo): Plane change maneuver

    Returns:
        fastapi.responses.JSONResponse: JSON response
    """
    
    # * Maneuver
    
    attractor: bodies.Attractor = bodies.Attractor(data.attractor.lower())
    
    rocket_motor: om.RocketMotor = fill_rocket_motor(data.spacecraft)
    
    oe_1: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElements)
    
    oe_2_schema: schema.OrbitalElements = copy.deepcopy(data.orbitalElements)
    
    oe_2_schema.inc = data.maneuver.data.inc
    oe_2_schema.raan = data.maneuver.data.raan
    
    oe_2: o3d.OrbitalElements = fill_orbital_elements(oe_2_schema)
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.plane_change_maneuver_from_raan_and_inclination(attractor=attractor,
                                                                                                      rocket_motor=rocket_motor,
                                                                                                      orbital_elements_1=oe_1,
                                                                                                      orbital_elements_2=oe_2)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  orbital_elements=oe_1,
                                                                  delta_time=time.TimeDelta(oe_1.calc_orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              orbital_elements=oe_1,
                                                              true_anomaly_1=oe_1.true_anomaly,
                                                              true_anomaly_2=maneuver.orbital_elements_list[0].true_anomaly)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          orbital_elements=oe_1,
                                          delta_time=time.TimeDelta(dt_maneuver_point)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                orbital_elements=maneuver.orbital_elements_list[0],
                                                                delta_time=time.TimeDelta(maneuver.orbital_elements_list[0].calc_orbital_period(attractor)))
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=maneuver.orbital_elements_list[0].specific_angular_momentum.to_value(u.km**2 / u.s),
            sma=maneuver.orbital_elements_list[0].semimajor_axis.to_value(u.km),
            ecc=maneuver.orbital_elements_list[0].eccentricity.to_value(u.dimensionless_unscaled),
            inc=maneuver.orbital_elements_list[0].inclination.to_value(u.deg),
            raan=maneuver.orbital_elements_list[0].right_ascension_of_ascending_node.to_value(u.deg),
            aop=maneuver.orbital_elements_list[0].argument_of_periapsis.to_value(u.deg),
            ta=maneuver.orbital_elements_list[0].true_anomaly.to_value(u.deg)
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.delta_velocity_list]),
            dt=sum([x.to_value(u.hour) for x in maneuver.flight_time_list]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.delta_mass_list]),
            burnTime=sum([x.to_value() for x in maneuver.burn_time_list])
        ),
        initialOrbit=initial_orbit,
        transferOrbit=transfer_orbit,
        finalOrbit=final_orbit
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
