"""
This module explores the means of describing **orbits in three-dimensional space**, which, of course, is the setting for
real missions and orbital maneuvers. The focus is on the orbits of earth satellites, but the applications are to any
two-body trajectories, including interplanetary missions.

📖 **References**

- :cite:`curtis`
    - Chapter 4 *Orbit in Three Dimensions*

- :cite:`kluever`
    - Chapter 3 *Orbit Determination*

- :cite:`sforza`
    - Chapter 5 *ORBITAL MECHANICS*

- :cite:`walter`
    - Chapter 7 *Orbits*
    - Chapter 13 *Reference Frames*
    - Chapter 14 *Orbit Geometry and Determination*
"""

import astropy.units as u
import astropy.time as time
import numpy as np
import typing as ty

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.models.orbit_parameters as sl_orbit_parameters
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.n_body_models.conversions as sl_conversions
import spacelab.orbit_determination as orbit_determination
import spacelab.orbit.position as sl_position
import spacelab.utils.angle as sl_angle
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

# * curtis

def right_ascension_declination(position: u.Quantity) -> ty.List[u.Quantity]:
    """
    Calculates the **Right Ascension** and **Declination** of the given position vector.

    :param position: Position vector
    :type position: u.Quantity
    :return: [:math:`\\alpha` (-180; +180), :math:`\\delta` (0; 360)]
    :rtype: ty.List[u.Quantity]
    
    📌 **Notes**
    
    The vernal equinox, which lies on the celestial equator, is the origin for measurement of longitude, which in
    astronomical parlance is called *right ascension*. Right ascension (RA or :math:`\\alpha`) is measured along the
    celestial equator in degrees east from the vernal equinox. Latitude on the celestial sphere is called *declination*.
    Declination (Dec or :math:`\\delta`) is measured along a meridian in degrees, positive to the north of the equator
    and negative to the south.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 4.2 *Geocentric right ascension-declination frame*
        - Section 4.3 *State vector and the geocentric equatorial frame*
    """
    
    # >>> Validation
        
    # * position
    
    err_msg: str | None = sl_validator.validate_quantity_vector("position", position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return [0 * u.deg, 0 * u.deg]
    
    # >>> Algorithm
    
    r: np.ndarray = position.to_value(u.km)
    
    # ? 1. Magnitude
    
    r_m: float = np.linalg.norm(r)
    
    # ? 2. Direction cosines
    
    l: float = r[0] / r_m
    m: float = r[1] / r_m
    n: float = r[2] / r_m
    
    # ? 3. Declination
    
    delta: float = np.arcsin(n)
    
    # ? 4. Right Ascension
    
    alpha: float = np.arccos(l / np.cos(delta)) if m > 0 else (2 * np.pi - np.arccos(l / np.cos(delta)))
    
    return [np.rad2deg(alpha) * u.deg, np.rad2deg(delta) * u.deg]

def cartesian_to_keplerian( # NOSONAR python:S3776
    attractor: sl_bodies.Attractor,
    position: u.Quantity,
    velocity: u.Quantity) -> sl_orbital_elements.OrbitalElements:
    """
    Calculates the *Orbital Elements* from position and velocity vectors in *Geocentric Equatorial Frame* (*GEF*) / 
    *Earth-Centered Inertial* (*ECI*) frame.

    :param attractor: Main attractor
    :type attractor: u.Quantity
    :param position: Position vector
    :type position: u.Quantity
    :param velocity: Velocity vector
    :type velocity: u.Quantity
    :return: Orbital Elements
    :rtype: sl_orbital_elements.OrbitalElements
    
    📌 **Notes**
    
    To define an orbit in the plane requires two parameters: eccentricity and angular momentum. Other parameters, such
    as the semimajor axis, the specific energy, and (for an ellipse) the period, are obtained from these two. To locate
    a point on the orbit requires a third parameter, the true anomaly, which leads us to the time since perigee.
    Describing the orientation of an orbit in three dimensions requires three additional parameters, called the Euler
    angles:
    
    - The angle between the positive :math:`X` axis and the node line is the first Euler angle :math:`\\Omega`, the
    **right ascension of the ascending node** (0° - 360°).
    - The dihedral angle between the orbital plane and the equatorial plane is the **inclination** :math:`i`, and is
    also the angle between the positive :math:`Z` axis and the normal to the plane of the orbit (0° - 180°).
    - The third Euler angle :math:`\\omega`, the **argument of perigee**, is the angle between the node line vector
    :math:`\\vec{N}` and the eccentricity vector :math:`\\vec{e}`, measured in the plane of the orbit (0° - 360°).
    
    The angular momentum :math:`h` and true anomaly :math:`\\theta` are frequently replaced by the semimajor axis
    :math:`a` and the mean anomaly :math:`M`, respectively.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 4.4 *Orbital elements and the state vector*
    - :cite:`kluever`
        - Section 3.4 *Transforming Cartesian Coordinates to Orbital Elements*
    - :cite:`walter`:
        - Section 7.3.5 *Orbital Elements*
    """
    
    oe = sl_orbital_elements.OrbitalElements()
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return oe
    
    # * position
    
    err_msg = sl_validator.validate_quantity_vector("position", position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return oe
    
    # * position
    
    err_msg = sl_validator.validate_quantity_vector("velocity", velocity, u.km / u.s, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return oe
    
    # >>> Algorithm
    
    r: np.ndarray = position.to_value(u.km)
    v: np.ndarray = velocity.to_value(u.km / u.s)
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    # ? 1. Distance
    
    r_m: float = np.linalg.norm(r)
    
    # ? 2. Speed
    
    v_m: float = np.linalg.norm(v)
    
    # ? 3. Radial velocity
    
    v_r: float = np.dot(r, v) / r_m
    
    # ? 4. Specific angular momentum
    
    h: np.ndarray = np.cross(r, v)
    
    h_m: float = np.linalg.norm(h)
    
    oe.specific_angular_momentum = h_m * u.km**2 / u.s
    
    # ? 5. Semimajor axis
    
    epsilon: float = v_m**2 / 2 - mu / r_m # ? Specific Mechanical Energy
    
    oe.semimajor_axis = - 0.5 * mu / epsilon * u.km
    
    # ? 6. Inclination
    
    inc: float = np.arccos(h[2] / h_m)
    
    oe.inclination = u.Quantity(inc, u.rad).to(u.deg)
    
    # ? 7. Line of nodes
    
    # ! In case inclination is 0, you can use the longitude of periapsis (Ω + ω)
    
    N: np.ndarray
    
    tol: float = 1e-6 # ? Tolerance to consider the orbit as equatorial or polar
    
    inc_min: float = np.deg2rad(1) # ? Minimum inclination to consider the orbit as non-equatorial
    
    if inc <= 0.5 * np.pi:
    
        if inc > inc_min or (inc < inc_min and inc > tol):
            
            N = np.cross(np.array([0, 0, 1]), h) # ? K x h
            
        else:
        
            N = np.array([1, 0, 0]) # ? I
            
    else:
        
        if inc < (np.pi - inc_min) or (inc > (np.pi - inc_min) and (np.pi - inc) > tol):
            
            N = np.cross(np.array([0, 0, 1]), h) # ? K x h
            
        else:
        
            N = np.array([1, 0, 0]) # ? I
    
    # ? 8. Magnitude of the line of nodes
    
    n_m: float = np.linalg.norm(N) # ? N_M
    
    # ^ 9. Right ascension of the ascending node (RAAN): N / N_m = cos(raan) * I + sin(raan) * J
    
    raan: float = np.arccos(N[0] / n_m)
    
    oe.right_ascension_of_ascending_node = u.Quantity(raan if N[1] >= 0 else (2 * np.pi - raan), u.rad).to(u.deg)
    
    # ? 10. Eccentricity vector (\vec{A} = \mu * \vec{e} => Laplace–Runge–Lenz vector)
    
    ecc: np.ndarray = 1 / mu * ((v_m**2 - mu / r_m) * r - r_m * v_r * v)
    
    # ? 11. Eccentricity
    
    ecc_m: float = np.linalg.norm(ecc)
    
    oe.eccentricity = ecc_m * u.one
    
    # ? 12. Argument of periapsis
    
    # ! In case eccentricity is 0, you can use the orbital longitude (Ω + ω + θ) and the mean longitude (Ω + ω + M)
    
    if ecc_m < tol:
        
        oe.argument_of_periapsis = 0 * u.deg
    
    else: 
    
        argp: float = np.arccos(np.dot(N, ecc) / (n_m * ecc_m))
    
        oe.argument_of_periapsis = u.Quantity(argp if ecc[2] >= 0 else (2 * np.pi - argp), u.rad).to(u.deg)
    
    # ? 13. True anomaly
    
    if ecc_m < tol:
        
        oe.true_anomaly = 0 * u.deg
        
    else:
    
        theta: float = np.arccos(np.dot(ecc, r) / (ecc_m * r_m))
    
        oe.true_anomaly = u.Quantity(theta if v_r >= 0 else (2 * np.pi - theta), u.rad).to(u.deg)
    
    return oe

def rotation_matrix_ijk_to_pqw(orbital_elements: sl_orbital_elements.OrbitalElements) -> np.ndarray:
    """
    Rotation matrix from **Geocentric Equatorial Frame** (*IJK*) to **Perifocal Frame** (*PQW*)

    :param orbital_elements: Orbital Elements
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :return: Rotation matrix
    :rtype: np.ndarray
    
    📌 **Notes**
    
    The transformation from the *geocentric equatorial frame* into the *perifocal frame* may be accomplished by the
    sequence of three rotations.
    
    1. Rotation around the :math:`\\hat{K}` axis, through the right ascension :math:`\\Omega`
    
    2. Rotation around the node line :math:`\\hat{I}'`, through the angle :math:`i` required to bring the :math:`XY`
    plane parallel to the orbital plane
    
    3. Rotation in the orbital plane and that rotates the unit vectors :math:`\\hat{I}'` and :math:`\\hat{J}''` through
    the angle :math:`\\omega` around the :math:`\\hat{w}` axis so that they become aligned with :math:`\\hat{p}` and
    :math:`\\hat{q}`, respectively.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 4.6 *Transformation between geocentric equatorial and perifocal frame*
    - :cite:`kluever`
        - Section 3.5 *Transforming Orbital Elements to Cartesian Coordinates*
        - Section 3.5.1 *Coordinate Transformations*
    """
    
    # >>> Validation
    
    # * orbital_elements
    
    err_msg: str | None = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return np.zeros(shape=(3,3))
    
    # >>> Algorithm
    
    inc: float = orbital_elements.inclination.to_value(u.rad)
    raan: float = orbital_elements.right_ascension_of_ascending_node.to_value(u.rad)
    argp: float = orbital_elements.argument_of_periapsis.to_value(u.rad)
    
    r_3_raan: np.ndarray = np.array( # ? Rotation about K through angle RAAN - R_3_RAAN
        [
            [ + np.cos(raan) , + np.sin(raan) , 0 ],
            [ - np.sin(raan) , + np.cos(raan) , 0 ],
            [ 0              , 0              , 1 ]
        ])
    
    r_1_inc: np.ndarray = np.array( # ? Rotation about X' through angle inc - R_1_INC
        [
            [ 1 , 0             , 0             ],
            [ 0 , + np.cos(inc) , + np.sin(inc) ],
            [ 0 , - np.sin(inc) , + np.cos(inc) ]
        ])
    
    r_3_argp: np.ndarray = np.array( # ? Rotation about Z'' through angle argument of periapsis - R_3_ARGP
        [
            [ + np.cos(argp) , + np.sin(argp) , 0 ],
            [ - np.sin(argp) , + np.cos(argp) , 0 ],
            [ 0              , 0              , 1 ]
        ])
    
    R: np.ndarray = np.matmul(r_3_argp, np.matmul(r_1_inc, r_3_raan))
    
    return R

def geocentric_equatorial_to_perifocal(
    attractor: sl_bodies.Attractor,
    position: u.Quantity,
    velocity: u.Quantity) -> ty.List[u.Quantity]:
    """
    **Geocentric Equatiorial Frame** (*IJK*) --> **Perifocal Frame** (*PQW*)

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param position: Position vector GEF
    :type position: u.Quantity
    :param velocity: Velocity vector GEF
    :type velocity: u.Quantity
    :return: [position vector PQW, velocity vector PQW]
    :rtype: ty.List[u.Quantity]
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 4.6 *Transformation between geocentric equatorial and perifocal frame*
    """
    
    empty: np.ndarray = [np.zeros(3,), np.zeros(3,)]
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * position
    
    err_msg = sl_validator.validate_quantity_vector("position", position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * velocity
    
    err_msg = sl_validator.validate_quantity_vector("velocity", velocity, u.km / u.s, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    r_gef: np.ndarray = position.to_value(u.km) # ? r_GEF
    v_gef: np.ndarray = velocity.to_value(u.km / u.s) # ? v_GEF
    
    # ? 1. Calculate orbital elements
    
    oe: sl_orbital_elements.OrbitalElements = cartesian_to_keplerian(attractor=attractor, position=position, velocity=velocity)
    
    # ? 2. Overall rotation matrix (3-1-3 Euler angles IJK --> PQW)
    
    R: np.ndarray = rotation_matrix_ijk_to_pqw(orbital_elements=oe)
    
    # ? 3. Calculate position and velocity in perifocal frame
    
    r_pf: u.Quantity = np.matmul(R, r_gef) * u.km # ? r_PF
    v_pf: u.Quantity = np.matmul(R, v_gef) * u.km / u.s # ? v_PF
    
    return [r_pf, v_pf]

def keplerian_to_cartesian(
    attractor: sl_bodies.Attractor,
    orbital_elements : sl_orbital_elements.OrbitalElements) -> ty.List[u.Quantity]:
    """
    Calculates the *Geocentric Equatorial Frame* (*GEF*) position and velocity vectors from *Orbital Elements*.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param orbital_elements: Orbital Elements
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :return: [position vector GEF, velocity vector GEF]
    :rtype: ty.List[u.Quantity]
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 4.6 *Transformation between geocentric equatorial and perifocal frame*
    - :cite:`kluever`
        - Section 3.5 *Transforming Orbital Elements to Cartesian Coordinates*
    """
    
    empty: np.ndarray = [np.zeros(3,), np.zeros(3,)]
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * orbital_elements
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    ecc: float = orbital_elements.eccentricity.to_value()
    ta: float = orbital_elements.true_anomaly.to_value(u.rad)
    p: float = orbital_elements.calc_semilatus_rectum(attractor=attractor).to_value(u.km)
    
    # ? 1. Calculate position in perifocal frame
    
    r_pf: np.ndarray = p / (1 + ecc * np.cos(ta)) * np.array([np.cos(ta), np.sin(ta), 0]) # ? r_PF
    
    # ? 2. Calculate velocity in perifocal frame
    
    v_pf: np.ndarray = np.sqrt(mu / p) * np.array([-np.sin(ta), ecc + np.cos(ta), 0]) # ? v_PF
    
    # ? 2. Overall rotation matrix (3-1-3 Euler angles PQW --> IJK)
    
    R: np.ndarray = rotation_matrix_ijk_to_pqw(orbital_elements=orbital_elements).T # ? Transpose
    
    # ? 4. Calculate position and velocity in geocentric equatorial frame
    
    r_gef: u.Quantity = np.matmul(R, r_pf) * u.km # ? r_GEF
    v_gef: u.Quantity = np.matmul(R, v_pf) * u.km / u.s # ? v_GEF
    
    return [r_gef, v_gef]

def planet_oblateness_effect(
    attractor: sl_bodies.Attractor,
    orbital_elements: sl_orbital_elements.OrbitalElements) -> ty.List[u.Quantity]:
    """
    Calculates the planet oblateness effect.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param orbital_elements: Orbital Elements
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :return: [Right Ascension of Ascending Node variation, Argument of Periapsis variation]
    :rtype: ty.List[u.Quantity]
    
    📌 **Notes**
    
    **Right Ascension of Ascending Node**
    
    :math:`\\dot{\\Omega} = - \\frac{3}{2} \\frac{\\sqrt{\\mu} J_2 R_E^2}{(1 - e^2)^2 a^{7/2}} \\cos i`
    
    If :math:`0° \\leq i < 90°`, then :math:`\\dot{\\Omega} < 0`. That is, for prograde orbits, the node line
    drifts westward. Since the right ascension of the node continuously decreases, this phenomenon is called *regression
    of the nodes*. If :math:`90° \\leq i < 180°`, we see that :math:`\\dot{\\Omega} > 0`. The node line of retrograde
    orbits therefore advances eastward. For polar orbits (:math:`i = 90°`), the node line is stationary.
    
    **Argument of Periapsis**
    
    :math:`\\dot{\\omega} = - \\frac{3}{2} \\frac{\\sqrt{\\mu} J_2 R_E^2}{(1 - e^2)^2 a^{7/2}} \\left(\\frac{5}{2} \\sin^2 i - 2\\right)`
    
    This expression shows that if :math:`0° \\leq i < 63.4°` or :math:`116.6° < i \\leq 180°`, then
    :math:`\\dot{\\omega} > 0`, which means the perigee advances in the direction of the motion of the satellite (hence,
    the name *advance of perigee* for this phenomenon). If :math:`63.4° < i \\leq 116.6°`, the perigee regresses, moving
    opposite to the direction of motion. :math:`i = 63.4°` and :math:`i = 116.6°` are the critical inclinations at which
    the apse line does not move.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 4.7 *Effects of the earth's oblateness*
    """
    
    empty: ty.List = [0 * u.deg / u.s, 0 * u.deg / u.s]
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * orbital_elements
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    R_E: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)
    J_2: float = sl_bodies.BODIES[attractor].J2.to_value(u.one) if sl_bodies.BODIES[attractor].J2 is not None else 0
    
    sma: float = orbital_elements.semimajor_axis.to_value(u.km)
    ecc: float = orbital_elements.eccentricity.to_value(u.one)
    inc: float = orbital_elements.inclination.to_value(u.rad)
    
    # ? Right ascension of the ascending node variation
    
    d_raan_dt: float = - 3/2 * (np.sqrt(mu) * J_2 * R_E**2) / ((1 - ecc**2)**2 * sma**(7/2)) * np.cos(inc)
    
    # ? Argument of the periapsis variation
    
    d_argp_dt: float = - 3/2 * (np.sqrt(mu) * J_2 * R_E**2) / ((1 - ecc**2)**2 * sma**(7/2)) * (5/2 * np.sin(inc)**2 - 2)
    
    return [u.Quantity(d_raan_dt, u.rad / u.s).to(u.deg / u.s), u.Quantity(d_argp_dt, u.rad / u.s).to(u.deg / u.s)]

def ground_track_propagation(
    attractor: sl_bodies.Attractor,
    orbital_elements: sl_orbital_elements.OrbitalElements,
    time_step: time.TimeDelta) -> ty.List[u.Quantity]:
    """
    Calculates the **Ground Track** for the given time step.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param orbital_elements: Orbital Elements
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :param time_step: Time step
    :type time_step: time.TimeDelta
    :return: [right ascension (-180; +180), declination (0; 360)]
    :rtype: ty.List[u.Quantity]
    
    📌 **Notes**
    
    The projection of a satellite's orbit onto the earth's surface is called its **ground track**. At a given instant,
    one can image a radial line drawn outward from the center of the earth to the satellite. Where this line pierces the
    earth's spherical surface is a point on the ground track. We locate this point by giving its latitude and longitude
    relative to the earth. As the satellite moves around the earth, the trace of these points is its ground track.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 4.8 *Ground tracks*
    - :cite:`kluever`
        - Section 3.6 *Ground Tracks*
    """
    
    empty: ty.List = [0 * u.deg, 0 * u.deg]
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * orbital_elements
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * time_step
    
    err_msg = sl_validator.validate_time_delta("time_step", time_step)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    omega: u.Quantity = sl_bodies.BODIES[attractor].omega.to(u.deg / u.s)
    ecc: float = orbital_elements.eccentricity.to_value()
    
    if ecc >= 1.0:
        
        sl_logger.logger.warning("Valid only for circular / elliptical orbits")
        
        return empty
    
    # ? 1. Oblateness
    
    d_raan_dt, d_argp_dt = planet_oblateness_effect(attractor=attractor, orbital_elements=orbital_elements)
    
    # ? 2. Initial condition
    
    r_gef, v_gef = keplerian_to_cartesian(attractor=attractor, orbital_elements=orbital_elements)
    
    op: sl_orbit_parameters.OrbitParameters =\
        sl_conversions.cartesian_to_orbit_parameters(attractor=attractor, position=r_gef, velocity=v_gef)
    
    t_0: u.Quantity = 0.0 * u.s
    
    if ecc == 0:
        
        t_0 = sl_position.circular_orbit_time(true_anomaly=orbital_elements.true_anomaly, period=op.period)
        
    elif ecc < 1.0:
        
        t_0 = sl_position.elliptical_orbit_time(
            true_anomaly=orbital_elements.true_anomaly, period=op.period, eccentricity=orbital_elements.eccentricity)
    
    # ? 3. Propagation
    
    t: u.Quantity = t_0.to(u.s) + time_step.to(u.s)
        
        # ? a) True anomaly
    
    ta: u.Quantity = 0.0 * u.rad
    
    if ecc == 0:
        
        ta = sl_position.circular_orbit_true_anomaly(time_of_flight=t, period=op.period)
        
    elif ecc < 1.0:
        
        ta = sl_position.elliptical_orbit_true_anomaly(
            time_of_flight=t, period=op.period, eccentricity=orbital_elements.eccentricity)
    
        # ? b) New Orbital Elements
    
    orbital_elements.right_ascension_of_ascending_node += d_raan_dt * time_step.to(u.s)
    orbital_elements.argument_of_periapsis += d_argp_dt * time_step.to(u.s)

    orbital_elements.true_anomaly = ta    
    orbital_elements.right_ascension_of_ascending_node = sl_angle.wrap_angle(orbital_elements.right_ascension_of_ascending_node)
    orbital_elements.argument_of_periapsis = sl_angle.wrap_angle(orbital_elements.argument_of_periapsis)
    
        # ? c) New state
    
    r_gef, v_gef = keplerian_to_cartesian(attractor=attractor, orbital_elements=orbital_elements)
    
        # ? d) New position
    
    ta: float = sl_angle.wrap_angle(omega * (t.to(u.s) - t_0.to(u.s))).to_value(u.rad)
    
    # * Rotation matrix from inertial frame (XYZ) to rotating frame (Earth-fixed, x'y'z')
    
    r_3_ta = np.array( # ? R_3_TA
        [
            [+ np.cos(ta) , + np.sin(ta), 0],
            [- np.sin(ta) , + np.cos(ta), 0],
            [0            , 0           , 1]
        ])
    
        # ? e) Right Ascension and Declination
    
    alpha, delta = right_ascension_declination(position=np.matmul(r_3_ta, r_gef.to_value(u.km)) * u.km)
    
    return [alpha - 180 * u.deg, delta]

# * sforza

def latitude(inclination: u.Quantity, true_anomaly: u.Quantity) -> sl_enums.AngleHemisphere:
    """
    Calculates the spacecraft latitude.

    :param inclination: Orbit inclination
    :type inclination: u.Quantity
    :param true_anomaly: Orbit true anomaly position
    :type true_anomaly: u.Quantity
    :return: (Latitude, Hemisphere)
    :rtype: sl_enums.AngleHemisphere
    
    📌 **Notes**
    
    The spacecraft latitude angle :math:`l_a` is given by
    
    .. math::

        l_a = \\arcsin(\\sin i \\sin \\theta)
    
    Note that the rotation of the earth plays no role in the determination of the latitude because it always yields the
    same answer for the latitude angle :math:`l_a` when :math:`\\theta` increases by :math:`2\\pi` every revolution.
    
    📖 **References**
    
    - :cite:`sforza`
        - Section 5.4 *THE GROUND TRACK OF AN ORBIT*
        - Section 5.4.2 *THE SPACECRAFT'S LATITUDE*
    """
    
    empty = sl_enums.AngleHemisphere(angle=0 * u.deg, hemisphere=sl_enums.Hemisphere.EQUATOR)
    
    # >>> Validation
    
    # * inclination
    
    err_msg: str | None = sl_validator.validate_quantity_angle("inclination", inclination)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * true_anomaly
    
    err_msg = sl_validator.validate_quantity_angle("true_anomaly", true_anomaly)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    if not (0 <= inclination.to_value(u.deg) <= 180):
        
        sl_logger.logger.warning("'inclination' must be in [0, 180] deg")
        
        return empty
    
    inc: float = inclination.to_value(u.rad)
    ta: float = true_anomaly.to_value(u.rad)
    
    lat: u.Quantity = u.Quantity(np.arcsin(np.sin(inc) * np.sin(ta)) * u.rad, u.deg)
    
    hemisphere = sl_enums.Hemisphere.EQUATOR
    
    if lat > 0 * u.deg:
        
        hemisphere = sl_enums.Hemisphere.NORTH
        
    elif lat < 0 * u.deg:
        
        hemisphere = sl_enums.Hemisphere.SOUTH

    return sl_enums.AngleHemisphere(angle=np.abs(lat), hemisphere=hemisphere)

def longitude(
    orbital_elements: sl_orbital_elements.OrbitalElements,
    latitude: sl_enums.AngleHemisphere,
    epoch: time.Time,
    orbit_time: u.Quantity) -> sl_enums.AngleHemisphere:
    """
    Calculates the spacecraft longitude.

    :param orbital_elements: Orbital elements
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :param latitude: Spacecraft latitude
    :type latitude: sl_enums.AngleHemisphere
    :param epoch: Epoch time
    :type epoch: time.Time
    :param orbit_time: Spacecraft orbit time
    :type orbit_time: u.Quantity
    :return: (Longitude, Hemisphere)
    :rtype: sl_enums.AngleHemisphere
    
    📌 **Notes**
    
    In order to compute the longitude of a spacecraft, we need to consider different values:
    
    - Longitudinal angle (not the conventional earth-based longitude) :math:`l_o = \\arcsin(\\tan l_a / \\tan i)`
    - Corrected longitudinal angle :math:`\\lambda = \\arctan((\\sin u \\cos i) / \\cos u)`
    - Angular increment in longitude due to earth's rotation of 360° in one sidereal day :math:`\\Delta_r = - (360° / 86164) t`
    - Rate of movement (regression) of the longitudinal angle of the ascending node (:math:`l_{o,1}`) :math:`\\Delta_o = (dl_{o,1} / dt) t`
    - Rate of movement (rotation) of the line of apsides :math:`\\Delta_a = (d\\omega / dt) t`
    
    The resulting value is given by
    
    .. math::
    
        L_o = \\lambda + \\{l_{o,1}(0) + \\Delta_o + \\Delta_r + \\Delta_a\\}
    
    📖 **References**
    
    - :cite:`sforza`
        - Section 5.4 *THE GROUND TRACK OF AN ORBIT*
        - Section 5.4.3 *THE SPACECRAFT'S LONGITUDINAL ANGLE*
        - Section 5.4.4 *EFFECT OF THE EARTH'S ROTATION ON LONGITUDE*
        - Section 5.4.5 *EFFECT OF REGRESSION OF NODES ON LONGITUDE*
        - Section 5.4.6 *EFFECT OF ROTATION OF APSIDES ON LONGITUDE*
        - Section 5.4.7 *THE SPACECRAFT'S LONGITUDE*
    """
    
    empty = sl_enums.AngleHemisphere(angle=0 * u.deg, hemisphere=sl_enums.Hemisphere.EQUATOR)
    
    # >>> Validation
    
    # * orbital_elements
    
    err_msg: str | None = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * latitude
    
    err_msg = sl_validator.validate_type("latitude", latitude, sl_enums.AngleHemisphere)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * epoch
    
    err_msg = sl_validator.validate_time("epoch", epoch)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * orbit_time
    
    err_msg = sl_validator.validate_quantity("orbit_time", orbit_time, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    if latitude.hemisphere == sl_enums.Hemisphere.NORTH:
        
        lat: float = latitude.angle.to_value(u.rad)
    
    else:
        
        lat: float = -latitude.angle.to_value(u.rad)
    
    t_since_epoch: float = orbit_time.to_value(u.s)
    sma: float = orbital_elements.semimajor_axis.to_value(u.km)
    ecc: float = orbital_elements.eccentricity.to_value(u.one)
    inc: float = orbital_elements.inclination.to_value(u.rad)
    raan: float = orbital_elements.right_ascension_of_ascending_node.to_value(u.deg)
    aop: float = orbital_elements.argument_of_periapsis.to_value(u.rad)
    ta: float = orbital_elements.true_anomaly.to_value(u.rad)
    r_p: float = orbital_elements.calc_periapsis_radius().to_value(u.km)
    
    # * Calculate reference time in Julian days since J2000
    
    jd_epoch: float = orbit_determination.OrbitDetermination.timestamp_2_julian_day(timestamp=epoch)
    
    dt_epoch_j2000: float = (jd_epoch - orbit_determination.OrbitDetermination.J2000) * 86_400 # ? JD -> seconds
    
    t: float = dt_epoch_j2000 + t_since_epoch
    
    # * Longitudinal angle (not the conventional earth-based longitude)
    
    l_o: u.Quantity = u.Quantity(np.arcsin(np.tan(lat) / np.tan(inc)) * u.rad, u.deg)
    
    # * Corrected longitudinal angle
    
    u_: float = aop + ta
    
    lambda_: u.Quantity = u.Quantity(np.atan2(np.sin(u_) * np.cos(inc), np.cos(u_)) * u.rad, u.deg)
    
    #! Wrong formula found on Book 3
    # lambda_: u.Quantity = l_o
    
    # if 0 * u.deg < u_ and u_ <= 90 * u.deg:
        
    #     lambda_ = l_o
    
    # elif 90 * u.deg < u_ and u_ <= 180 * u.deg:
        
    #     lambda_ = 180 * u.deg - l_o
    
    # elif 180 * u.deg < u_ and u_ <= 270 * u.deg:
        
    #     lambda_ = 180 * u.deg - l_o
    
    # elif 270 * u.deg < u_ and u_ <= 360 * u.deg:
        
    #     lambda_ = 360 * u.deg + l_o
    
    # * Effect of earth rotation
    
    lambda_r: u.Quantity = - (360 / 86_164) * t * u.deg
    
    # * Effect of regression of nodes
    
    r: float = r_p * (1 + ecc) / (1 + ecc * np.cos(ta))
    
    lambda_o: u.Quantity = (- 2.3963e9 * np.cos(inc) * (r ** (-3.5)) * t_since_epoch) * u.deg
    
    # * Effect of rotation of apsides
    
    lambda_a: u.Quantity = (1.1943e10 * (4 - 5 * np.sin(inc)**2) / (sma**3.5 * (1 - ecc**2)**2) * t_since_epoch) * u.deg
    
    # * Earth-based longitude
    
    long: u.Quantity = lambda_.to(u.deg) + lambda_r.to(u.deg) + lambda_o.to(u.deg) + lambda_a.to(u.deg)
    
    # * Longitude of the ascending node
    
    l_o_1: u.Quantity = raan * u.deg
    
    # * Spacecraft longitude
    
    long += l_o_1
    
    long = sl_angle.wrap_angle(long.to(u.deg))
    
    if long < 180 * u.deg:
        
        hemisphere = sl_enums.Hemisphere.EAST
        
    else:
        
        long = 360 * u.deg - long
        
        hemisphere = sl_enums.Hemisphere.WEST
    
    return sl_enums.AngleHemisphere(angle=long, hemisphere=hemisphere)

def horizon_footprint(attractor: sl_bodies.Attractor, altitude: u.Quantity) -> ty.List[u.Quantity]:
    """
    Calculates the **horizon footprint** for maximum line of sight.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param altitude: Altitude of the spacecraft
    :type altitude: u.Quantity
    :return: [horizon footprint, tangent point angle, line of sight angle, instantaneous access area]
    :rtype: ty.List[u.Quantity]
    
    📌 **Notes**
    
    The locus of all the horizon points visible from an orbiting spacecraft encloses a **footprint** on the ground. The
    footprint constitutes the area on the surface of the sphere enclosed by a cone tangent to the sphere when the apex
    of the cone is at the local radius of the spacecraft.
    
    The so-called **instantaneous access area** (IAA) is the spherical segment (expressed in solid angle) of a planet as
    seen by a satellite at an instantaneous point on the orbit.
    
    📖 **References**
    
    - :cite:`sforza`
        - Section 5.5 *THE SPACECRAFT HORIZON*
        - Section 5.5.1 *THE HORIZON FOOTPRINT*
    - :cite:`walter`
        - Section 14.1.2 *Access Area*
    """
    
    empty: ty.List[u.Quantity] = [0 * u.km, 0 * u.rad, 0 * u.rad, 0 * u.rad]
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * altitude
    
    err_msg = sl_validator.validate_quantity("altitude", altitude, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    R_E: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)
    h: float = altitude.to_value(u.km)
    
    if h <= 0:
        
        sl_logger.logger.warning("'altitude' cannot be negative")
        
        return empty
    
    # ? Tangent point angle
    
    beta: float = np.arccos(1 / (1 + h / R_E))
    
    # ? Line of sight angle
    
    delta: float = np.pi - np.pi * 0.5 - beta
    
    # ? Arc length of the horizon footprint
    
    c_f: float = 2 * beta * R_E
    
    # ? Instantaneous access area (IAA)
    
    omega_iaa: float = 2 * np.pi * h / (R_E + h)
    
    return c_f * u.km, beta * u.rad, delta * u.rad, omega_iaa * u.rad

# * walter

def keplerian_to_equinoctial(
    orbital_elements: sl_orbital_elements.OrbitalElements) -> sl_orbital_elements.EquinoctialOrbitalElements:
    """
    Orbital Elements --> Equinoctial Orbital Elements

    :param orbital_elements: Orbital Elements
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :return: Equinoctial Orbital Elements
    :rtype: sl_orbital_elements.EquinoctialOrbitalElements
    
    📌 **Notes**
    
    In terms of the invariant orbit vectors we can identify :math:`[h \\; k]` and :math:`[q \\; p]`: these singular free
    parameters were most probably introduced by Joseph-Louis Lagrange. Today, there are some variants of the standard
    equinoctial orbital elements, most importantly the so-called **modified equinoctial orbital elements**.
    
    📖 **References**
    
    - :cite:`walter`:
        - Section 7.3.5 *Orbital Elements*
    """
    
    # >>> Validation
    
    # * orbital_elements
    
    err_msg: str | None = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return sl_orbital_elements.EquinoctialOrbitalElements()
    
    # >>> Algorithm
    
    sma: float = orbital_elements.semimajor_axis.to_value(u.km)
    ecc: float = orbital_elements.eccentricity.to_value(u.one)
    inc: float = orbital_elements.inclination.to_value(u.rad)
    raan: float = orbital_elements.right_ascension_of_ascending_node.to_value(u.rad)
    aop: float = orbital_elements.argument_of_periapsis.to_value(u.rad)
    ta: float = orbital_elements.true_anomaly.to_value(u.rad)

    # ? Eccentricity vector components
    
    h: float = ecc * np.sin(raan + aop)
    k: float = ecc * np.cos(raan + aop)

    # ? Rescaled ascending node vector components
    
    p: float = np.tan(inc / 2) * np.sin(raan)
    q: float = np.tan(inc / 2) * np.cos(raan)
    
    # ? Location of the periapsis in time
            
    l: float = raan + aop + ta

    return sl_orbital_elements.EquinoctialOrbitalElements(
        semimajor_axis=sma * u.km, eccentricity_vector_h=h * u.one, eccentricity_vector_k=k * u.one,
        ascending_node_vector_p=p * u.one, ascending_node_vector_q=q * u.one, periapsis_location=l * u.rad)

def perifocal_to_geocentric_equatorial_position_vector(
    orbital_elements: sl_orbital_elements.OrbitalElements,
    perifocal_position: u.Quantity) -> u.Quantity:
    """
    Perifocal Frame --> Geocentric Equatiorial Frame for a given position vector

    :param orbital_elements: Orbital Elements
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :param perifocal_position: Position vector in Perifocal Frame
    :type perifocal_position: u.Quantity
    :return: Position vector in Geocentric Equatiorial Frame
    :rtype: u.Quantity
    
    📖 **References**
    
    - :cite:`walter`:
        - Section 13.1.4 *Orbital Reference Frames*
    """
    
    empty: u.Quantity = np.zeros(3) * u.km
    
    # >>> Validation
    
    # * orbital_elements
    
    err_msg: str | None = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * perifocal_position
    
    err_msg = sl_validator.validate_quantity_vector("perifocal_position", perifocal_position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    R: np.ndarray = rotation_matrix_ijk_to_pqw(orbital_elements=orbital_elements).T # ? Transpose
    
    r_gef: u.Quantity = np.matmul(R, perifocal_position.to_value(u.km)) * u.km # ? r_GEF
    
    return r_gef

def position_vector_representations(
    orbital_elements: sl_orbital_elements.OrbitalElements,
    flight_path_angle: u.Quantity,
    position_magnitude: u.Quantity) -> ty.List[u.Quantity]:
    """
    Given the orbital elements, flight path angle, and the absolute value of the position vector, calculates all the
    position vector representations in the following reference frames:
            
    - Equatorial Coordinate System (IJK)
    - Perifocal Coordinate System (PQW)
    - Satellite Coordinate System (NTW)
    - Satellite Coordinate System (RSW)

    :param orbital_elements: Orbital Elements
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :param flight_path_angle: Flight path angle
    :type flight_path_angle: u.Quantity
    :param position_magnitude: Position vector magnitude
    :type position_magnitude: u.Quantity
    :return: Position vector representations
    :rtype: ty.List[u.Quantity]
    
    📖 **References**
    
    - :cite:`walter`:
        - Section 13.1.5 *Vector Representations*
    """
    
    empty: u.Quantity = [np.zeros(3) * u.km, np.zeros(3) * u.km, np.zeros(3) * u.km, np.zeros(3) * u.km]
    
    # >>> Validation
    
    # * orbital_elements
    
    err_msg: str | None = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * flight_path_angle
    
    err_msg = sl_validator.validate_quantity_angle("flight_path_angle", flight_path_angle)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * position_magnitude
    
    err_msg = sl_validator.validate_quantity("position_magnitude", position_magnitude, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    inc: float = orbital_elements.inclination.to_value(u.rad)
    raan: float = orbital_elements.right_ascension_of_ascending_node.to_value(u.rad)
    aop: float = orbital_elements.argument_of_periapsis.to_value(u.rad)
    ta: float = orbital_elements.true_anomaly.to_value(u.rad)
    
    aol: float = aop + ta # ? Argument of latitude
    
    fpa: float = flight_path_angle.to_value(u.rad)
    
    r: float = position_magnitude
    
    # ? Equatorial Coordinate System (IJK)
    
    r_ijk: np.ndarray = r * np.array(
        [
            + np.cos(raan) * np.cos(aol) - np.sin(raan) * np.sin(aol) * np.cos(inc),
            + np.sin(raan) * np.cos(aol) + np.cos(raan) * np.sin(aol) * np.cos(inc),
            + np.sin(aol) * np.sin(inc)
        ])
    
    # ? Perifocal Coordinate System (PQW)
    
    r_pqw: np.ndarray = r * np.array([ np.cos(ta), np.sin(ta), 0 ])
    
    # ? Satellite Coordinate System (NTW)
    
    r_ntw: np.ndarray = r * np.array([ np.cos(fpa), np.sin(fpa), 0 ])
    
    # ? Satellite Coordinate System (RSW)
    
    r_rsw: np.ndarray = r * np.array([ 1, 0, 0 ])
    
    return [r_ijk, r_pqw, r_ntw, r_rsw]

def velocity_vector_representations(
    orbital_elements: sl_orbital_elements.OrbitalElements,
    flight_path_angle: u.Quantity,
    velocity_magnitude: u.Quantity) -> ty.List[u.Quantity]:
    """
    Given the orbital elements, flight path angle, and the absolute value of the velocity vector, calculates all the
    velocity vector representations in the following reference frames:
    
    - Equatorial Coordinate System (IJK)
    - Perifocal Coordinate System (PQW)
    - Satellite Coordinate System (NTW)
    - Satellite Coordinate System (RSW)

    :param orbital_elements: Orbital Elements
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :param flight_path_angle: Flight path angle
    :type flight_path_angle: u.Quantity
    :param velocity_magnitude: Velocity vector magnitude
    :type velocity_magnitude: u.Quantity
    :return: Velocity vector representations
    :rtype: ty.List[u.Quantity]
    
    📖 **References**
    
    - :cite:`walter`:
        - Section 13.1.5 *Vector Representations*
    """
    
    empty: u.Quantity = [np.zeros(3) * u.km / u.s, np.zeros(3) * u.km / u.s, np.zeros(3) * u.km / u.s, np.zeros(3) * u.km / u.s]
    
    # >>> Validation
    
    # * orbital_elements
    
    err_msg: str | None = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * flight_path_angle
    
    err_msg = sl_validator.validate_quantity_angle("flight_path_angle", flight_path_angle)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * velocity_magnitude
    
    err_msg = sl_validator.validate_quantity("velocity_magnitude", velocity_magnitude, u.km / u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    inc: float = orbital_elements.inclination.to_value(u.rad)
    raan: float = orbital_elements.right_ascension_of_ascending_node.to_value(u.rad)
    aop: float = orbital_elements.argument_of_periapsis.to_value(u.rad)
    ta: float = orbital_elements.true_anomaly.to_value(u.rad)
    
    aol: float = aop + ta # ? Argument of latitude
    
    fpa: float = flight_path_angle.to_value(u.rad)
    
    v: float = velocity_magnitude
    
    # ? Equatorial Coordinate System (IJK)
    
    v_ijk: np.ndarray = v * np.array(
        [
            + np.cos(raan) * np.sin(fpa - aol) - np.sin(raan) * np.cos(fpa - aol) * np.cos(inc),
            + np.sin(raan) * np.sin(fpa - aol) + np.cos(raan) * np.cos(fpa - aol) * np.cos(inc),
            + np.cos(fpa - aol) * np.sin(inc)
        ])
    
    # ? Perifocal Coordinate System (PQW)
    
    v_pqw: np.ndarray = v * np.array([ np.cos(fpa - ta), np.sin(fpa - ta), 0 ])
    
    # ? Satellite Coordinate System (RSW)
    
    v_rsw: np.ndarray = v * np.array([ np.sin(fpa), np.cos(fpa), 0 ])
    
    # ? Satellite Coordinate System (NTW)
    
    v_ntw: np.ndarray = v * np.array([ 0, 1, 0 ])
    
    return [v_ijk, v_pqw, v_rsw, v_ntw]

def eclipse_duration(
    attractor: sl_bodies.Attractor,
    circular_orbit_radius: u.Quantity,
    inclination: u.Quantity,
    right_ascension_ascending_node: u.Quantity,
    right_ascension_sun: u.Quantity) -> ty.Tuple[u.Quantity, bool, u.Quantity, bool]:
    """
    Calculates the **eclispe** duration for the given orbit.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param circular_orbit_radius: Circular orbit radius
    :type circular_orbit_radius: u.Quantity
    :param inclination: Orbit inclination
    :type inclination: u.Quantity
    :param right_ascension_ascending_node: Right ascension of the ascending node
    :type right_ascension_ascending_node: u.Quantity
    :param right_ascension_sun: Right ascension of the sun
    :type right_ascension_sun: u.Quantity
    :return: Beta angle, eclipse condition, eclipse duration, hot case
    :rtype: ty.Tuple[u.Quantity, bool, u.Quantity, bool]
    
    📌 **Notes**
    
    Satellites in planetary orbits are generally subject to eclipse. A key parameter is the so-called *beta angle*
    (a.k.a. *orbit beta angle*). The beta angle is the angle between the solar vector and the orbit plane
    (:math:`0° \\leq \\beta \\leq 90°`).
    
    📖 **References**
    
    - :cite:`walter`:
        - Section 14.1.1 *Eclipse Duration*
    """
    
    empty: ty.Tuple[u.Quantity, bool, u.Quantity, bool] = (0 * u.rad, False, 0 * u.s, False)
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * circular_orbit_radius
    
    err_msg = sl_validator.validate_quantity("circular_orbit_radius", circular_orbit_radius, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * inclination
    
    err_msg = sl_validator.validate_quantity("inclination", inclination, u.deg)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * right_ascension_ascending_node
    
    err_msg = sl_validator.validate_quantity("right_ascension_ascending_node", right_ascension_ascending_node, u.deg)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # * right_ascension_sun
    
    err_msg = sl_validator.validate_quantity("right_ascension_sun", right_ascension_sun, u.deg)
    
    if err_msg: sl_logger.logger.warning(err_msg); return empty
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    R: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)
    r: float = circular_orbit_radius.to_value(u.km)
    inc: float = inclination.to_value(u.rad)
    raan: float = right_ascension_ascending_node.to_value(u.rad)
    raan_s: float = right_ascension_sun.to_value(u.rad)
    
    phi: float = np.deg2rad(23.44) # ? Ecliptic angle
    delta_s: float = np.arcsin(np.sin(phi) * np.sin(raan_s))
    
    # ? 1. Beta angle (a.k.a. orbit bera angle)
    
    beta: float = np.arcsin(np.sin(inc) * np.cos(delta_s) * np.sin(raan - raan_s) + np.cos(inc) * np.sin(delta_s))
    
    # ? 2. Eclipse condition
    
    eclipse: bool = abs(np.sin(beta)) <= (R / r)
    
    # ? 3. Eclipse duration
    
    T: float = 2 * np.pi / np.sqrt(mu) * r**(3/2) # ? Period
    
    if eclipse:
        
        t_e: float = T / np.pi * np.arccos(np.sqrt(r**2 - R**2) / (r * np.cos(beta)))
    
    else:
        
        t_e: float = 0.0
    
    # ? 4. Hot case
    
    hot_case: bool = np.sin(inc + phi) > (R / r)
    
    return (beta * u.rad, eclipse, t_e * u.s, hot_case)
