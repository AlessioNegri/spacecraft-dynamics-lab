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
    """Fill the rocket motor from schema values

    Args:
        spacecraft_schema (schema.Spacecraft): Pydantic schema spacecraft

    Returns:
        om.RocketMotor: Rocket motor
    """
    
    rocket_motor: om.RocketMotor = om.RocketMotor()
    
    rocket_motor.I_sp = spacecraft_schema.specificImpulse * u.s
    rocket_motor.T = spacecraft_schema.thrust * u.N
    rocket_motor.m_sc = spacecraft_schema.mass * u.kg
    rocket_motor.m_prop = 0.0 * u.kg
    
    return rocket_motor

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

def propagate_orbit(attractor: bodies.Attractor, oe: o3d.OrbitalElements, dt: time.TimeDelta) -> typing.List[schema.Vector3D]:
    """Propagate the orbit with given Orbital Parameters for a given time

    Args:
        attractor (bodies.Attractor): Main attractor
        oe (o3d.OrbitalElements): Orbital Elements with nu from initial position
        dt (time.TimeDelta): Time of integration

    Returns:
        typing.List[schema.Vector3D]: Simulation points
    """
    
    r_gef, v_gef = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe)
    
    orbit: tbp.Orbit = tbp.Orbit()
    
    orbit.from_cartesian(attractor=attractor, position=r_gef, velocity=v_gef)
    
    result: tbp.Result = orbit.propagate_for(dt)
    
    simulation_points: typing.List[schema.Vector3D] = []
    
    for x, y, z in zip(result.position_x.to_value(), result.position_y.to_value(), result.position_z.to_value()):
        
        simulation_points.append(schema.Vector3D(x=x, y=y, z=z))
    
    return simulation_points

def calculate_simulation_time(attractor: bodies.Attractor,
                              oe: o3d.OrbitalElements,
                              nu_1: u.Quantity,
                              nu_2: u.Quantity) -> u.Quantity:
    """Calculate the simulation time to move from two true anomalies on the same orbit

    Args:
        attractor (bodies.Attractor): Main attractor
        oe (o3d.OrbitalElements): Orbital Elements
        nu_1 (u.Quantity): First true anomaly
        nu_2 (u.Quantity): Second true anomaly

    Returns:
        u.Quantity: Simulation time from first true anomaly
    """
    
    t_1: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(nu=nu_1,
                                                               T=oe.orbital_period(attractor),
                                                               e=oe.ecc.to_value())
    
    t_2: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(nu=nu_2,
                                                               T=oe.orbital_period(attractor),
                                                               e=oe.ecc.to_value())
    
    if t_2 > t_1:
        
        t_sim = t_2 - t_1
        
    else:
        
        t_sim = oe.orbital_period(attractor) - (t_1 - t_2)
    
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
    
    oe_2_schema : schema.OrbitalElements = copy.deepcopy(data.orbitalElements)
    
    oe_2_schema.sma = data.maneuver.data.sma
    oe_2_schema.ecc = data.maneuver.data.ecc
    
    oe_2: o3d.OrbitalElements = fill_orbital_elements(oe_2_schema)

    if data.maneuver.data.direction == 0:
        
        direction = om.HohmannDirection.PERICENTER_APOCENTER
        
        oe_2.nu = 180.0 * u.deg
        
    else:
        
        direction = om.HohmannDirection.APOCENTER_PERICENTER
        
        oe_2.nu = 0.0 * u.deg
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       oe_1=oe_1,
                                                                       oe_2=oe_2,
                                                                       direction=direction)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  oe=oe_1,
                                                                  dt=time.TimeDelta(oe_1.orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              oe=oe_1,
                                                              nu_1=oe_1.nu,
                                                              nu_2=maneuver.nu[0])
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=oe_1,
                                          dt=time.TimeDelta(dt_maneuver_point)))
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=maneuver.oe[0],
                                          dt=time.TimeDelta(maneuver.oe[0].orbital_period(attractor) / 2)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                oe=oe_2,
                                                                dt=time.TimeDelta(oe_2.orbital_period(attractor)))
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe_2.h.to_value(),
            sma=oe_2.a.to_value(),
            ecc=oe_2.ecc.to_value(),
            inc=oe_2.inc.to_value(),
            raan=oe_2.raan.to_value(),
            aop=oe_2.argp.to_value(),
            ta=oe_2.nu.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.dv]),
            dt=sum([x.to_value(u.hour) for x in maneuver.dt]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.dm])
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
                                                                                   oe_1=oe_1,
                                                                                   oe_2=oe_2,
                                                                                   r_3=r_3)
    
    oe_2.nu = 0.0 * u.deg
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  oe=oe_1,
                                                                  dt=time.TimeDelta(oe_1.orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              oe=oe_1,
                                                              nu_1=oe_1.nu,
                                                              nu_2=maneuver.oe[0].nu)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=oe_1,
                                          dt=time.TimeDelta(dt_maneuver_point)))
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=maneuver.oe[0],
                                          dt=time.TimeDelta(maneuver.oe[0].orbital_period(attractor) / 2)))
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=maneuver.oe[1],
                                          dt=time.TimeDelta(maneuver.oe[1].orbital_period(attractor) / 2)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                oe=oe_2,
                                                                dt=time.TimeDelta(oe_2.orbital_period(attractor)))
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe_2.h.to_value(),
            sma=oe_2.a.to_value(),
            ecc=oe_2.ecc.to_value(),
            inc=oe_2.inc.to_value(),
            raan=oe_2.raan.to_value(),
            aop=oe_2.argp.to_value(),
            ta=oe_2.nu.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.dv]),
            dt=sum([x.to_value(u.hour) for x in maneuver.dt]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.dm])
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
                                                                       oe=oe,
                                                                       nu_target=nu_target,
                                                                       num_revolutions=num_revolutions)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  oe=oe,
                                                                  dt=time.TimeDelta(oe.orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              oe=oe,
                                                              nu_1=oe.nu,
                                                              nu_2=maneuver.oe[0].nu)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=oe,
                                          dt=time.TimeDelta(dt_maneuver_point)))
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=maneuver.oe[0],
                                          dt=time.TimeDelta(maneuver.oe[0].orbital_period(attractor))))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = []
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe.h.to_value(),
            sma=oe.a.to_value(),
            ecc=oe.ecc.to_value(),
            inc=oe.inc.to_value(),
            raan=oe.raan.to_value(),
            aop=oe.argp.to_value(),
            ta=oe.nu.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.dv]),
            dt=sum([x.to_value(u.hour) for x in maneuver.dt]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.dm])
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
    
    oe: o3d.OrbitalElements = fill_orbital_elements(data.orbitalElements)

    r_2: u.Quantity = data.maneuver.data.targetRadius * u.km
    
    nu_2: u.Quantity = data.maneuver.data.targetTrueAnomaly * u.deg
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.non_hohmann_transfer(attractor=attractor,
                                                                           rocket_motor=rocket_motor,
                                                                           oe_1=oe,
                                                                           r_2=r_2,
                                                                           nu_2=nu_2)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  oe=oe,
                                                                  dt=time.TimeDelta(oe.orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              oe=maneuver.oe[0],
                                                              nu_1=maneuver.oe[0].nu,
                                                              nu_2=nu_2)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=maneuver.oe[0],
                                          dt=time.TimeDelta(dt_maneuver_point)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = []
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe.h.to_value(),
            sma=oe.a.to_value(),
            ecc=oe.ecc.to_value(),
            inc=oe.inc.to_value(),
            raan=oe.raan.to_value(),
            aop=oe.argp.to_value(),
            ta=oe.nu.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.dv]),
            dt=sum([x.to_value(u.hour) for x in maneuver.dt]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.dm])
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
    
    oe_2_schema : schema.OrbitalElements = copy.deepcopy(data.orbitalElements)
    
    oe_2_schema.aop = data.maneuver.data.aop
    
    oe_2: o3d.OrbitalElements = fill_orbital_elements(oe_2_schema)

    sip : bool = data.maneuver.data.intersectionPoint == 1
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.apse_line_rotation_from_eta(attractor=attractor,
                                                                                  rocket_motor=rocket_motor,
                                                                                  oe_1=oe_1,
                                                                                  oe_2=oe_2,
                                                                                  eta=oe_2.argp - oe_1.argp,
                                                                                  second_intersection_point=sip)
    
    oe_2.nu = maneuver.oe[0].nu
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  oe=oe_1,
                                                                  dt=time.TimeDelta(oe_1.orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              oe=oe_1,
                                                              nu_1=oe_1.nu,
                                                              nu_2=maneuver.oe[0].nu)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=oe_1,
                                          dt=time.TimeDelta(dt_maneuver_point)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                oe=oe_2,
                                                                dt=time.TimeDelta(oe_2.orbital_period(attractor)))
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe_2.h.to_value(),
            sma=oe_2.a.to_value(),
            ecc=oe_2.ecc.to_value(),
            inc=oe_2.inc.to_value(),
            raan=oe_2.raan.to_value(),
            aop=oe_2.argp.to_value(),
            ta=maneuver.oe[0].nu.to_value(u.deg)
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.dv]),
            dt=sum([x.to_value(u.hour) for x in maneuver.dt]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.dm])
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
                                                                     oe=oe,
                                                                     nu_T=nu_T,
                                                                     dt=dt)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  oe=oe,
                                                                  dt=time.TimeDelta(oe.orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                        oe=maneuver.oe[0],
                                                        nu_1=maneuver.oe[0].nu,
                                                        nu_2=maneuver.oe[1].nu)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=maneuver.oe[0],
                                          dt=time.TimeDelta(dt_maneuver)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = []
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=oe.h.to_value(),
            sma=oe.a.to_value(),
            ecc=oe.ecc.to_value(),
            inc=oe.inc.to_value(),
            raan=oe.raan.to_value(),
            aop=oe.argp.to_value(),
            ta=oe.nu.to_value()
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.dv]),
            dt=sum([x.to_value(u.hour) for x in maneuver.dt]),
            dm=sum([x.to_value() for x in maneuver.dm])
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
    
    oe_2_schema : schema.OrbitalElements = copy.deepcopy(data.orbitalElements)
    
    oe_2_schema.inc = data.maneuver.data.inc
    oe_2_schema.raan = data.maneuver.data.raan
    
    oe_2: o3d.OrbitalElements = fill_orbital_elements(oe_2_schema)
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.plane_change_maneuver_from_raan_and_inclination(attractor=attractor,
                                                                                                      rocket_motor=rocket_motor,
                                                                                                      oe_1=oe_1,
                                                                                                      oe_2=oe_2)
    
    # * Initial Orbit
    
    initial_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                  oe=oe_1,
                                                                  dt=time.TimeDelta(oe_1.orbital_period(attractor)))
        
    # * Transfer Orbit
    
    transfer_orbit: typing.List[schema.Vector3D] = []
    
    dt_maneuver_point: u.Quantity = calculate_simulation_time(attractor=attractor,
                                                              oe=oe_1,
                                                              nu_1=oe_1.nu,
                                                              nu_2=maneuver.oe[0].nu)
    
    transfer_orbit.extend(propagate_orbit(attractor=attractor,
                                          oe=oe_1,
                                          dt=time.TimeDelta(dt_maneuver_point)))
    
    # * Final Orbit
    
    final_orbit: typing.List[schema.Vector3D] = propagate_orbit(attractor=attractor,
                                                                oe=maneuver.oe[0],
                                                                dt=time.TimeDelta(maneuver.oe[0].orbital_period(attractor)))
    
    # * Result
    
    result: schema.OrbitalManeuverOutModelInfo = schema.OrbitalManeuverOutModelInfo(
        orbitalElements=schema.OrbitalElements(
            sam=maneuver.oe[0].h.to_value(u.km**2 / u.s),
            sma=maneuver.oe[0].a.to_value(u.km),
            ecc=maneuver.oe[0].ecc.to_value(u.dimensionless_unscaled),
            inc=maneuver.oe[0].inc.to_value(u.deg),
            raan=maneuver.oe[0].raan.to_value(u.deg),
            aop=maneuver.oe[0].argp.to_value(u.deg),
            ta=maneuver.oe[0].nu.to_value(u.deg)
        ),
        maneuver=schema.Maneuver(
            dv=sum([x.to_value() for x in maneuver.dv]),
            dt=sum([x.to_value(u.hour) for x in maneuver.dt]) + dt_maneuver_point.to_value(u.hour),
            dm=sum([x.to_value() for x in maneuver.dm])
        ),
        initialOrbit=initial_orbit,
        transferOrbit=transfer_orbit,
        finalOrbit=final_orbit
    )
    
    return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_200_OK, content=result.model_dump())
