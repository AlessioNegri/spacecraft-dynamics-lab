"""
This module contains some of the classical ways in which the orbit of a satellite can be determined from earth-bound
observations. All of the methods presented here are based on the two-body equations of motion. As such, they must be
considered preliminary **orbit determination** techniques.

📖 **References**

- :cite:`curtis`
    - Chapter 5 *Preliminary Orbit Determination*
    - Chapter 6 *Orbital Maneuvers*
- :cite:`kluever`
    - Chapter 3 *Orbit Determination*
- :cite:`walter`
    - Chapter 8 *Orbital Maneuvering*
    - Chapter 14 *Orbit Geometry and Determination*
"""

import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.optimize as optimize
import typing as ty

import spacelab.bodies as bodies
import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.n_body_models.lagrange_coefficients as sl_lagrange_coefficients
import spacelab.orbit.frames as sl_frames
import spacelab.orbit.representation as sl_representation
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

# * curtis

def launch_azimuth(
    launch_site_latitude: u.Quantity,
    target_inclination: u.Quantity,
    direction: sl_enums.LaunchPass = sl_enums.LaunchPass.ASCENDING) -> ty.Optional[u.Quantity]:
    """
    Launch azimuth calculation for a given target inclination and launch site latitude.

    :param launch_site_latitude: Launch site latitude
    :type launch_site_latitude: u.Quantity
    :param target_inclination: Target inclination
    :type target_inclination: u.Quantity
    :param direction: Launch pass direction, defaults to sl_enums.LaunchPass.ASCENDING
    :type direction: sl_enums.LaunchPass, optional
    :return: Launch azimuth
    :rtype: ty.Optional[u.Quantity]
    
    📌 **Notes**
    
    The choice of launch azimuth has an effect on the orbit. It does not change the fact that the orbit is retrograde;
    it simply determines whether the ascending node will be in the same hemisphere as the launch site or on the opposite
    side of the earth.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.9 *Plane change maneuvers*
    - :cite:`kluever`
        - Section 3.6 *Ground Tracks*
    - :cite:`walter`
        - Section 8.6 *Orbital Rendezvous*
        - Section 8.6.1 *Launch Phase*
    """
    
    # >>> Validation
    
    # * launch_site_latitude
    
    err_msg: str | None = sl_validator.validate_quantity_angle("launch_site_latitude", launch_site_latitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * target_inclination
    
    err_msg = sl_validator.validate_quantity_angle("target_inclination", target_inclination)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    phi: float = launch_site_latitude.to_value(u.rad)
    inc: float = target_inclination.to_value(u.rad)
    
    if inc < abs(phi):
        
        sl_logger.logger.warning(
            "Target inclination must be greater than or equal to the absolute value of the launch site latitude")
        
        return None
    
    if inc > (np.pi - abs(phi)):
        
        sl_logger.logger.warning(
            "Target inclination must be less than or equal to 180° - absolute value of the launch site latitude")
        
        return None
    
    azimuth: float = np.arcsin(np.cos(inc) / np.cos(phi))
    
    azimuth = azimuth % (2 * np.pi)
    
    return (azimuth if direction == sl_enums.LaunchPass.ASCENDING else (np.pi - azimuth)) * u.rad

def gibbs_method(
    attractor: bodies.Attractor,
    position_1 : u.Quantity,
    position_2 : u.Quantity,
    position_3 : u.Quantity) -> ty.Optional[sl_orbital_elements.OrbitalElements]:
    """
    Gibbs method of orbit determination from tree position vectors.

    :param attractor: Main attractor
    :type attractor: bodies.Attractor
    :param position_1: Position vector 1
    :type position_1: u.Quantity
    :param position_2: Position vector 2
    :type position_2: u.Quantity
    :param position_3: Position vector 3
    :type position_3: u.Quantity
    :return: Orbital elements
    :rtype: ty.Optional[sl_orbital_elements.OrbitalElements]
    
    📌 **Notes**
    
    This is a geometric method for orbit determination that is based on three successive inertial position vectors. This
    method utilizes concepts from vector calculus pioneered by Josiah Willard Gibbs at the end of the nineteenth century
    and is therefore known as the *Gibbs method*.
    
    The three vectors must lie in the same plane and not too close to each other.
    
    This method is useful when the geocentric angles of the three subsequent measurements are more apart than 15° for
    LEO and 6° for GSO.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.2 *Gibbs method of orbit determination from three position vectors*
    - :cite:`kluever`
        - Section 3.8 *Orbit Determination from Three Position Vectors*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * position_1
    
    err_msg = sl_validator.validate_quantity_vector("position_1", position_1, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * position_2
    
    err_msg = sl_validator.validate_quantity_vector("position_2", position_2, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * position_3
    
    err_msg = sl_validator.validate_quantity_vector("position_3", position_3, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    r_1: np.ndarray = position_1.to_value(u.km)
    r_2: np.ndarray = position_2.to_value(u.km)
    r_3: np.ndarray = position_3.to_value(u.km)
    
    mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    # ? 1. Norm
    
    r_1_m: float = np.linalg.norm(r_1)
    r_2_m: float = np.linalg.norm(r_2)
    r_3_m: float = np.linalg.norm(r_3)
    
    # ? 2. Cross products
    
    C_12: np.ndarray = np.cross(r_1, r_2)
    C_23: np.ndarray = np.cross(r_2, r_3)
    C_31: np.ndarray = np.cross(r_3, r_1)
    
    # ? 3. Verify
    
    u_r_1: np.ndarray = r_1 / r_1_m
    
    if np.abs(np.dot(u_r_1, C_23 / np.linalg.norm(C_23))) > 0.0349:
        
        sl_logger.logger.warning("Not coplanar position vectors (vectors plane - orbital plane angle > 2°)")
        
        return None
    
    theta_12: float = np.arccos(np.dot(r_1, r_2) / (r_1_m * r_2_m))
    
    theta_23: float = np.arccos(np.dot(r_2, r_3) / (r_2_m * r_3_m))
    
    if theta_12 < np.deg2rad(1) or theta_23 < np.deg2rad(1):
        
        sl_logger.logger.warning("The three position vectors are too close to each other (angle < 1°)")
        
        return None

    # ? 4. Calculate N, D, and S auxiliary vectors
    
    N: np.ndarray = r_1_m * C_23 + r_2_m * C_31 + r_3_m * C_12
    
    n_m: float = np.linalg.norm(N) # ? N_m
    
    D: np.ndarray = C_12 + C_23 + C_31
    
    d_m: float = np.linalg.norm(D) # ? D_m
    
    S: np.ndarray = r_1 * (r_2_m - r_3_m) + r_2 * (r_3_m - r_1_m) + r_3 * (r_1_m - r_2_m)
    
    # ? 5. Calculate velocity at 2
    
    v_2: np.ndarray = np.sqrt(mu / (n_m * d_m)) * (np.cross(D, r_2) / r_2_m + S)
    
    # ? 6. Compute the orbital elements
    
    oe: sl_orbital_elements.OrbitalElements = sl_representation.cartesian_to_keplerian(
        attractor=attractor, position=r_2 * u.km, velocity=v_2 * u.km / u.s)
    
    return oe

def _lambert_equation(z: float, mu: float, r_1 : float, r_2 : float, A : float, dt : float) -> float: # NOSONAR python:S117
    """
    Lambert's equation.

    :param z: Variable
    :type z: float
    :param mu: Gravitational constant [km^3 / s^2]
    :type mu: float
    :param r_1: Position 1
    :type r_1: float
    :param r_2: Position 2
    :type r_2: float
    :param A: Parameter A
    :type A: float
    :param dt: Delta time
    :type dt: float
    :return: Result
    :rtype: float
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.3 *Lambert's problem*
    """
    
    s_z: float = sl_lagrange_coefficients.S(z)
    c_z: float = sl_lagrange_coefficients.C(z)
    
    y: float = max(r_1 + r_2 + A * (z * s_z - 1) / np.sqrt(c_z), 0)
    
    return (y / c_z)**(3/2) * s_z + A * np.sqrt(y) - np.sqrt(mu) * dt

def _lambert_equation_first_derivative(z : float, mu: float, r_1 : float, r_2 : float, A : float, dt : float) -> float: # NOSONAR python:S117
    """
    Lambert's equation first derivative.

    :param z: Variable
    :type z: float
    :param mu: Gravitational constant [km^3 / s^2]
    :type mu: float
    :param r_1: Position 1
    :type r_1: float
    :param r_2: Position 2
    :type r_2: float
    :param A: Parameter A
    :type A: float
    :param dt: Delta time
    :type dt: float
    :return: Result
    :rtype: float
    """
    
    s_0: float = sl_lagrange_coefficients.S(0)
    c_0: float = sl_lagrange_coefficients.C(0)
    s_z: float = sl_lagrange_coefficients.S(z)
    c_z: float = sl_lagrange_coefficients.C(z)
    
    y_0: float = r_1 + r_2 + A * (0 * s_0 - 1) / np.sqrt(c_0)
    
    y: float = r_1 + r_2 + A * (z * s_z - 1) / np.sqrt(c_z)
    
    if z == 0:
        
        return np.sqrt(2) / 40 * y_0**(3/2) + A / 8 * (np.sqrt(y_0) + A * 1 / np.sqrt(2 * y_0))
    
    else:
        
        return (y / c_z)**(3/2) * (1 / (2 * z) * (c_z - 3/2 * s_z / c_z) + 3/4 * s_z**2 / c_z) +\
            A / 8 * (3 * s_z / c_z * np.sqrt(y) + A * np.sqrt(c_z / y))

def lambert(
    attractor: bodies.Attractor,
    departure_position: u.Quantity,
    arrival_position: u.Quantity,
    delta_time: time.TimeDelta,
    direction: sl_enums.OrbitDirection = sl_enums.OrbitDirection.PROGRADE)\
        -> ty.Optional[ty.Tuple[u.Quantity, u.Quantity, sl_orbital_elements.OrbitalElements, u.Quantity]]:
    """
    Solves **Lambert**'s problem.

    :param attractor: Main attractor
    :type attractor: bodies.Attractor
    :param departure_position: Position vector at departure
    :type departure_position: u.Quantity
    :param arrival_position: Position vector at arrival
    :type arrival_position: u.Quantity
    :param delta_time: Time of flight between `departure_position` and `arrival_position`
    :type delta_time: time.TimeDelta
    :param direction: Type of orbit direction, defaults to sl_enums.OrbitDirection.PROGRADE
    :type direction: sl_enums.OrbitDirection, optional
    :return: (velocity at departure, velocity at arrival, transfer orbital elements, true anomaly at arrival)
    :rtype: ty.Optional[ty.Tuple[u.Quantity, u.Quantity, sl_orbital_elements.OrbitalElements, u.Quantity]]

    📌 **Notes**
    
    Given the position vectors at *departure* and *arrival*, with the *time-of-flight* between them, computes the
    velocity vectors that connect the two positions in the specified time under the gravitational field of the attractor.
        
    The implementation uses the universal variable formulation and solves for the universal anomaly with Newton's method.
    
    The most general description of this problem is that, under the influence of a common central gravitational
    potential, a spacecraft in the initial orbit at :math:`P_1` possesses the state vector
    :math:`(\\mathbf{r}_1,\\mathbf{v}_1)` and wants to transfer to :math:`P_2` with state vector
    :math:`(\\mathbf{r}_2,\\mathbf{v}_2)`. This is a general two-impulse transfer, called a *Lambert transfer*. A first
    impulse maneuver :math:`\\Delta v_1` at :math:`P_1` injects the spacecraft into an unpowered coplanar conic transfer
    orbit characterized by the orbital elements :math:`a` and :math:`e`. The transfer orbit terminates at :math:`P_2`,
    where a second impulse maneuver :math:`\\Delta v_2` is performed.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.3 *Lambert's problem*
    - :cite:`walter`
        - Section 8.2 *Lambert Transfer*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * departure_position
    
    err_msg = sl_validator.validate_quantity_vector("departure_position", departure_position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * arrival_position
    
    err_msg = sl_validator.validate_quantity_vector("arrival_position", arrival_position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * delta_time
    
    err_msg = sl_validator.validate_time_delta("delta_time", delta_time)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * direction
    
    err_msg = sl_validator.validate_type("direction", direction, sl_enums.OrbitDirection)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    r_1: np.ndarray = departure_position.to_value(u.km)
    r_2: np.ndarray = arrival_position.to_value(u.km)
    
    mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    dt: float = delta_time.to_value(u.s)
    
    # ? 1. Norm
    
    r_1_m : float = np.linalg.norm(r_1)
    r_2_m: float = np.linalg.norm(r_2)
    
    # ? 2. Delta theta
    
    delta_theta: float = 0.0
    
    temp: float = np.arccos((np.dot(r_1, r_2)) / (r_1_m * r_2_m))
    
    condition: float = np.cross(r_1, r_2)[2] # ? Z component
    
    if direction == sl_enums.OrbitDirection.PROGRADE:
        
        delta_theta = temp if condition >= 0 else (2 * np.pi - temp)
        
    elif direction == sl_enums.OrbitDirection.RETROGRADE:
        
        delta_theta = temp if condition < 0 else (2 * np.pi - temp)
        
    # ? 3. Parameter A
    
    A: float = np.sin(delta_theta) * np.sqrt((r_1_m * r_2_m) / (1 - np.cos(delta_theta)))
    
    # ? 4. Orbit type
    
    z_0: float = -4.0
    
    while _lambert_equation(z_0, mu, r_1_m, r_2_m, A, dt) < 0:
        
        z_0 = z_0 + 0.1
    
    z: float = 0.0
    
    # * Used for returning a failed result in case the Newton's method fails to converge (i.e. impossible orbit)
    failed_result: np.ndarray = [
        np.ones(r_1.shape) * 100.0 * u.km / u.s,
        np.ones(r_2.shape) * 100.0 * u.km / u.s,
        sl_orbital_elements.OrbitalElements(),
        0.0 * u.deg]

    try:
        
        z = optimize.newton(
            func=_lambert_equation,
            x0=z_0,
            fprime=_lambert_equation_first_derivative,
            args=(mu, r_1_m, r_2_m, A, dt))
    
    except Exception:
        
        return failed_result
    
    # ? 5. Parameter y
    
    s_z: float = sl_lagrange_coefficients.S(z)
    c_z: float = sl_lagrange_coefficients.C(z)
    
    y: float = r_1_m + r_2_m + A * (z * s_z - 1) / np.sqrt(c_z)
    
    # ? 6. Lagrange functions
    
    f: float = 1 - y / r_1_m
    
    g: float = A * np.sqrt(y / mu)
    
    dg_dt: float = 1 - y / r_2_m
    
    # ? 7. Velocities
    
    v_1: np.ndarray = 1 / g * (r_2 - f * r_1)
    
    v_2: np.ndarray = 1 / g * (dg_dt * r_2 - r_1)
    
    # ? 8. Orbital elements of the transfer orbit
    
    oe_1: sl_orbital_elements.OrbitalElements = sl_representation.cartesian_to_keplerian(
        attractor=attractor, position=r_1 * u.km, velocity=v_1 * u.km / u.s)
    
    oe_2: sl_orbital_elements.OrbitalElements = sl_representation.cartesian_to_keplerian(
        attractor=attractor, position=r_2 * u.km, velocity=v_2 * u.km / u.s)
    
    return [v_1 * u.km / u.s, v_2 * u.km / u.s, oe_1, oe_2.true_anomaly]

def predict_from_angle_range(
    attractor: sl_bodies.Attractor,
    slant_range: u.Quantity,
    azimuth: u.Quantity,
    elevation: u.Quantity,
    range_rate: u.Quantity,
    azimuth_rate: u.Quantity,
    elevation_rate: u.Quantity,
    local_sidereal_time: u.Quantity,
    latitude: u.Quantity,
    site_altitude: u.Quantity = 0 * u.km) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Predicts the geocentric position and velocity vectors from angle and range measurements.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param slant_range: Slant range
    :type slant_range: u.Quantity
    :param azimuth: Azimuth (A, beta)
    :type azimuth: u.Quantity
    :param elevation: Elevation (a, sigma)
    :type elevation: u.Quantity
    :param range_rate: Range rate
    :type range_rate: u.Quantity
    :param azimuth_rate: Azimuth rate
    :type azimuth_rate: u.Quantity
    :param elevation_rate: Elevation rate
    :type elevation_rate: u.Quantity
    :param local_sidereal_time: Local sidereal time (theta)
    :type local_sidereal_time: u.Quantity
    :param latitude: Latitude (phi)
    :type latitude: u.Quantity
    :param site_altitude: Ground station elevation above sea level, defaults to 0 * u.km
    :type site_altitude: u.Quantity, optional
    :return: [position, velocity]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    We know that an orbit around the earth is determined once the state vectors :math:`\\vec{r}` and :math:`\\vec{v}` in
    the inertial geocentric equatorial frame are provided at a given instant of time (epoch). Satellites are of course
    observed from the earth's surface and not from its center. The state vector can be determined from measurements by
    an earth-based tracking station.
    
    We assume that the tracking station is able to measure simultaneously the six quantities: range and range rate;
    azimuth and azimuth rate; plus elevation and elevation rate. This data leads directly to the state vector and,
    hence, to a complete determination of the orbit.
    
    This is the most straightforward (and perhaps least realistic) orbit-determination method that relies on six
    independent Earth-based measurements taken together at one time instant. The basic idea is that an Earth-based
    station measures the position and velocity vectors of a satellite relative to a moving coordinate system fixed with
    the station.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.8 *Orbit determination from angle and range measurements*
    - :cite:`kluever`
        - Section 3.7 *Orbit Determination from One Ground-Based Observation*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * slant_range
    
    err_msg = sl_validator.validate_quantity("slant_range", slant_range, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * azimuth
    
    err_msg = sl_validator.validate_quantity_angle("azimuth", azimuth)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * elevation
    
    err_msg = sl_validator.validate_quantity_angle("elevation", elevation)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * range_rate
    
    err_msg = sl_validator.validate_quantity("range_rate", range_rate, u.km / u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * azimuth_rate
    
    err_msg = sl_validator.validate_quantity("azimuth_rate", azimuth_rate, u.deg / u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * elevation_rate
    
    err_msg = sl_validator.validate_quantity("elevation_rate", elevation_rate, u.deg / u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * local_sidereal_time
    
    err_msg = sl_validator.validate_quantity_angle("local_sidereal_time", local_sidereal_time)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * latitude
    
    err_msg = sl_validator.validate_quantity_angle("latitude", latitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * site_altitude
    
    err_msg = sl_validator.validate_quantity("site_altitude", site_altitude, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    # ? 1. Geocentric position vector of the site
    
    R: ty.Optional[u.Quantity] = sl_frames.geocentric_equatorial_position_vector(
        attractor=attractor, local_sidereal_time=local_sidereal_time, latitude=latitude, site_altitude=site_altitude)
    
    if R is None: return None
    
    rho: float = slant_range.to_value(u.km)
    
    A: float = azimuth.to_value(u.rad)
    
    a: float = elevation.to_value(u.rad)
    
    drho_dt: float = range_rate.to_value(u.km / u.s)
    
    dA_dt: float = azimuth_rate.to_value(u.rad / u.s) # NOSONAR python:S117
    
    da_dt: float = elevation_rate.to_value(u.rad / u.s)
    
    omega: float = bodies.BODIES[attractor].omega.to_value(u.rad / u.s)
    
    theta: float = local_sidereal_time.to_value(u.rad)
    
    phi: float = latitude.to_value(u.rad)
    
    # ? 2. Topocentric declination
    
    delta: float = np.arcsin(np.cos(phi) * np.cos(A) * np.cos(a) + np.sin(phi) * np.sin(a))
    
    # ? 3. Topocentric right ascension
    
    h: float = 0.0 # * Hour Angle
    
    if A > 0 and A < np.pi:
        
        h = 2* np.pi - np.arccos((np.cos(phi) * np.sin(a) - np.sin(phi) * np.cos(A) * np.cos(a)) / np.cos(delta))
        
    else:
        
        h = np.arccos((np.cos(phi) * np.sin(a) - np.sin(phi) * np.cos(A) * np.cos(a)) / np.cos(delta))
    
    alpha: float = theta - h
    
    # ? 4. Direction cosine unit vector
    
    rho_h: np.ndarray = np.array([np.cos(delta) * np.cos(alpha), np.cos(delta) * np.sin(alpha), np.sin(delta)])
    
    # ? 5. Geocentric position vector
    
    r: np.ndarray = R.to_value(u.km) + rho * rho_h
    
    # ? 6. Inertial velocity of the site
    
    dR_dt: np.ndarray = np.cross(np.array([0, 0, omega]), R.to_value(u.km)) # NOSONAR python:S117
    
    # ? 7. Declination rate
    
    ddelta_dt: float = 1 / np.cos(delta) * (-dA_dt * np.cos(phi) * np.sin(A) * np.cos(a) + \
        da_dt * (np.sin(phi) * np.cos(a) - np.cos(phi) * np.cos(A) * np.sin(a)))
    
    # ? 8. Right ascension rate
    
    dalpha_dt: float = omega + (dA_dt * np.cos(A) * np.cos(a) - da_dt * np.sin(A) * np.sin(a) + \
        ddelta_dt * np.sin(A) * np.cos(a) * np.tan(delta)) / \
            (np.cos(phi) * np.sin(a) - np.sin(phi) * np.cos(A) * np.cos(a))
    
    # ? 9. Direction cosine rate unit vector
    
    drho_h_dt: np.ndarray = np.array([
        -dalpha_dt * np.sin(alpha) * np.cos(delta) - ddelta_dt * np.cos(alpha) * np.sin(delta),
        dalpha_dt * np.cos(alpha) * np.cos(delta) - ddelta_dt * np.sin(alpha) * np.sin(delta),
        ddelta_dt * np.cos(delta)])
    
    # ? 10 Geocentric velocity vector
    
    v = dR_dt + drho_dt * rho_h + rho * drho_h_dt
    
    return [r * u.km, v * u.km / u.s]

def predict_from_gauss_method(
    attractor: sl_bodies.Attractor,
    latitude: u.Quantity,
    local_sidereal_time_list: u.Quantity,
    right_ascension_list: u.Quantity,
    declination_list: u.Quantity,
    observation_time_list: u.Quantity,
    site_altitude: u.Quantity = 0 * u.km) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Predicts position and velocity with the Gauss method.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param latitude: Latitude (phi)
    :type latitude: u.Quantity
    :param local_sidereal_time_list: Vector of 3 local sidereal times (theta)
    :type local_sidereal_time_list: u.Quantity
    :param right_ascension_list: Vector of 3 right ascensions (alpha)
    :type right_ascension_list: u.Quantity
    :param declination_list: Vector of 3 declinations (delta)
    :type declination_list: u.Quantity
    :param observation_time_list: Vector of 3 observation times
    :type observation_time_list: u.Quantity
    :param site_altitude: Ground station elevation above sea level, defaults to 0 * u.km
    :type site_altitude: u.Quantity, optional
    :return: [positon, velocity] at second point
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    To determine an orbit requires specifying six independent quantities. These can be the six classical orbital
    elements or the total of six components the state vector at a given instant. To determine an orbit solely from
    observations therefore requires six independent measurements.  In the absence of range and range rate measuring
    capability, as with a telescope, we must rely on measurements of just the two angles, azimuth and elevation, to
    determine the orbit. A minimum of three observations of azimuth and elevation is therefore required to accumulate
    the six quantitieswe need to predict the orbit. We shall henceforth assume that the angular measurements are
    converted to topocentric right ascension and declination. We consider the classical method of angles-only orbit
    determination due to Carl Friedrich Gauss (1777-1855). This method requires gathering angular information over
    closely spaced intervals of time and yields a preliminary orbit determination based on those initial observations.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.9 *Angles-only preliminary orbit determination*
        - Section 5.10 *Gauss method of preliminary orbit determination*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * latitude
    
    err_msg = sl_validator.validate_quantity_angle("latitude", latitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * local_sidereal_time_list
    
    err_msg = sl_validator.validate_quantity_vector("local_sidereal_time_list", local_sidereal_time_list, u.deg, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * right_ascension_list
    
    err_msg = sl_validator.validate_quantity_vector("right_ascension_list", right_ascension_list, u.deg, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * declination_list
    
    err_msg = sl_validator.validate_quantity_vector("declination_list", declination_list, u.deg, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * observation_time_list
    
    err_msg = sl_validator.validate_quantity_vector("observation_time_list", observation_time_list, u.s, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * site_altitude
    
    err_msg = sl_validator.validate_quantity("site_altitude", site_altitude, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    alpha: np.ndarray = right_ascension_list.to_value(u.rad)
    
    delta: np.ndarray = declination_list.to_value(u.rad)
    
    t: np.ndarray = observation_time_list.to_value(u.s)
    
    # ? 0. Geocentric position vector of the site - Topocentric Horizon position vector
    
    R_1: np.ndarray = sl_frames.geocentric_equatorial_position_vector(
        attractor=attractor,
        local_sidereal_time=local_sidereal_time_list[0],
        latitude=latitude,
        site_altitude=site_altitude).to_value(u.km)
    
    R_2: np.ndarray = sl_frames.geocentric_equatorial_position_vector(
        attractor=attractor,
        local_sidereal_time=local_sidereal_time_list[1],
        latitude=latitude,
        site_altitude=site_altitude).to_value(u.km)
    
    R_3: np.ndarray = sl_frames.geocentric_equatorial_position_vector(
        attractor=attractor,
        local_sidereal_time=local_sidereal_time_list[2],
        latitude=latitude,
        site_altitude=site_altitude).to_value(u.km)
    
    rho_h_1: np.ndarray =\
        np.array([ np.cos(delta[0]) * np.cos(alpha[0]), np.cos(delta[0]) * np.sin(alpha[0]), np.sin(delta[0]) ])
        
    rho_h_2: np.ndarray =\
        np.array([ np.cos(delta[1]) * np.cos(alpha[1]), np.cos(delta[1]) * np.sin(alpha[1]), np.sin(delta[1]) ])
        
    rho_h_3: np.ndarray =\
        np.array([ np.cos(delta[2]) * np.cos(alpha[2]), np.cos(delta[2]) * np.sin(alpha[2]), np.sin(delta[2]) ])
    
    # ? 1. Time intervals
    
    tau_1: float = t[0] - t[1]
    tau_3: float = t[2] - t[1]
    tau: float = tau_3 - tau_1
    
    # ? 2. Cross products
    
    p_1: np.ndarray = np.cross(rho_h_2, rho_h_3)
    p_2: np.ndarray = np.cross(rho_h_1, rho_h_3)
    p_3: np.ndarray = np.cross(rho_h_1, rho_h_2)
    
    # ? 3. D_0
    
    D_0: float = np.dot(rho_h_1, p_1)
    
    # ? 4. D matrix
    
    D: np.ndarray = np.array(
        [
            [ np.dot(R_1, p_1), np.dot(R_1, p_2), np.dot(R_1, p_3) ],
            [ np.dot(R_2, p_1), np.dot(R_2, p_2), np.dot(R_2, p_3) ],
            [ np.dot(R_3, p_1), np.dot(R_3, p_2), np.dot(R_3, p_3) ]
        ]
    )
    
    # ? 5. Calculate parameters A and B
    
    A: float = 1 / D_0 * (-D[0,1] * tau_3 / tau + D[1,1] + D[2,1] * tau_1 / tau)
    
    B: float = 1 / (6 * D_0) * (D[0,1] * (tau_3**2 - tau**2) * tau_3 / tau + D[2,1] * (tau**2 - tau_1**2) * tau_1 / tau)
    
    # ? 6. Calculate E
    
    E: float = np.dot(R_2, rho_h_2)
    
    # ? 7. Calculate a, b, and c
    
    a: float = - (A**2 + 2 * A * E + np.linalg.norm(R_2)**2)
    
    b: float = - 2 * mu * B * (A + E)
    
    c: float = - mu**2 * B**2
    
    # ? 8. Find r_2
    
    f: callable = lambda x: x**8 + a * x**6 + b * x**3 + c
    
    dfdt: callable = lambda x: 8 * x**7 + 6 * a * x**5 + 3 * b * x**2
    
    r_2_m: float = optimize.newton(f, x0=10000, fprime=dfdt, maxiter=100, tol=1e-8)
    
    # ? 9. Slant ranges
    
    rho_1: float = 1 / D_0 * \
        ((6 * (D[2,0] * tau_1 / tau_3 + D[1,0] * tau / tau_3) * r_2_m**3 + \
            mu * D[2,0] * (tau**2 - tau_1**2) * tau_1 / tau_3 ) /
            (6 * r_2_m**3 + mu * (tau**2 - tau_3**2)) - D[0,0])
    
    rho_2: float = A + mu * B / r_2_m**3
    
    rho_3: float = 1 / D_0 * \
        ((6 * (D[0,2] * tau_3 / tau_1 - D[1,2] * tau / tau_1) * r_2_m**3 + \
            mu * D[0,2] * (tau**2 - tau_3**2) * tau_3 / tau_1 ) /
            (6 * r_2_m**3 + mu * (tau**2 - tau_1**2)) - D[2,2])
    
    # ? 10. Geocentric position vector of the target
    
    r_1: np.ndarray = R_1 + rho_1 * rho_h_1
    r_2: np.ndarray = R_2 + rho_2 * rho_h_2
    r_3: np.ndarray = R_3 + rho_3 * rho_h_3
    
    # ? 11. Lagrange coefficients
    
    f_1: float = 1 - 1/2 * mu / r_2_m**3 * tau_1**2
    f_3: float = 1 - 1/2 * mu / r_2_m**3 * tau_3**2
    g_1: float = tau_1 - 1/6 * mu / r_2_m**3 * tau_1**3
    g_3: float = tau_3 - 1/6 * mu / r_2_m**3 * tau_3**3
    
    # ? 12. Position and velocity vectors
    
    v_2: np.ndarray = 1 / (f_1 * g_3 - f_3 * g_1) * (-f_3 * r_1 + f_1 * r_3)
    
    return [r_2 * u.km, v_2 * u.km / u.s]

def predict_from_gauss_method_extended( # NOSONAR python:S3776
    attractor: sl_bodies.Attractor,
    latitude: u.Quantity,
    local_sidereal_time_list: u.Quantity,
    right_ascension_list: u.Quantity,
    declination_list: u.Quantity,
    observation_time_list: u.Quantity,
    site_altitude: u.Quantity = 0 * u.km) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Predicts position and velocity with the extended Gauss method.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param latitude: Latitude (phi)
    :type latitude: u.Quantity
    :param local_sidereal_time_list: Vector of 3 local sidereal times (theta)
    :type local_sidereal_time_list: u.Quantity
    :param right_ascension_list: Vector of 3 right ascensions (alpha)
    :type right_ascension_list: u.Quantity
    :param declination_list: Vector of 3 declinations (delta)
    :type declination_list: u.Quantity
    :param observation_time_list: Vector of 3 observation times
    :type observation_time_list: u.Quantity
    :param site_altitude: Ground station elevation above sea level, defaults to 0 * u.km
    :type site_altitude: u.Quantity, optional
    :return: [positon, velocity] at second point
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    It improves the standard Gauss method by using the values of :math:`\\vec{r}_2` and :math:`\\vec{v}_2` obtained from
    *predict_from_gauss_method* to compute the 'exact' values of the :math:`f` and :math:`g` functions from their
    universal formulation.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.9 *Angles-only preliminary orbit determination*
        - Section 5.10 *Gauss method of preliminary orbit determination*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * latitude
    
    err_msg = sl_validator.validate_quantity_angle("latitude", latitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * local_sidereal_time_list
    
    err_msg = sl_validator.validate_quantity_vector("local_sidereal_time_list", local_sidereal_time_list, u.deg, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * right_ascension_list
    
    err_msg = sl_validator.validate_quantity_vector("right_ascension_list", right_ascension_list, u.deg, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * declination_list
    
    err_msg = sl_validator.validate_quantity_vector("declination_list", declination_list, u.deg, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * observation_time_list
    
    err_msg = sl_validator.validate_quantity_vector("observation_time_list", observation_time_list, u.s, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * site_altitude
    
    err_msg = sl_validator.validate_quantity("site_altitude", site_altitude, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    # ? 0. Gauss method
    
    r_2, v_2 = predict_from_gauss_method(
        attractor=attractor,
        latitude=latitude,
        local_sidereal_time_list=local_sidereal_time_list,
        right_ascension_list=right_ascension_list,
        declination_list=declination_list,
        observation_time_list=observation_time_list,
        site_altitude=site_altitude)
    
    r_2: np.ndarray = r_2.to_value(u.km)
    v_2: np.ndarray = v_2.to_value(u.km / u.s)
    
    R_1: np.ndarray = sl_frames.geocentric_equatorial_position_vector(
        attractor=attractor,
        local_sidereal_time=local_sidereal_time_list[0],
        latitude=latitude,
        site_altitude=site_altitude).to_value(u.km)
    
    R_2: np.ndarray = sl_frames.geocentric_equatorial_position_vector(
        attractor=attractor,
        local_sidereal_time=local_sidereal_time_list[1],
        latitude=latitude,
        site_altitude=site_altitude).to_value(u.km)
    
    R_3: np.ndarray = sl_frames.geocentric_equatorial_position_vector(
        attractor=attractor,
        local_sidereal_time=local_sidereal_time_list[2],
        latitude=latitude,
        site_altitude=site_altitude).to_value(u.km)
    
    alpha: np.ndarray = right_ascension_list.to_value(u.rad)
    delta: np.ndarray = declination_list.to_value(u.rad)
    
    rho_h_1: np.ndarray =\
        np.array([ np.cos(delta[0]) * np.cos(alpha[0]), np.cos(delta[0]) * np.sin(alpha[0]), np.sin(delta[0]) ])
        
    rho_h_2: np.ndarray =\
        np.array([ np.cos(delta[1]) * np.cos(alpha[1]), np.cos(delta[1]) * np.sin(alpha[1]), np.sin(delta[1]) ])
        
    rho_h_3: np.ndarray =\
        np.array([ np.cos(delta[2]) * np.cos(alpha[2]), np.cos(delta[2]) * np.sin(alpha[2]), np.sin(delta[2]) ])
    
    p_1: np.ndarray = np.cross(rho_h_2, rho_h_3)
    p_2: np.ndarray = np.cross(rho_h_1, rho_h_3)
    p_3: np.ndarray = np.cross(rho_h_1, rho_h_2)
    
    D_0: float = np.dot(rho_h_1, p_1)
    
    D: np.ndarray = np.array(
        [
            [ np.dot(R_1, p_1), np.dot(R_1, p_2), np.dot(R_1, p_3) ],
            [ np.dot(R_2, p_1), np.dot(R_2, p_2), np.dot(R_2, p_3) ],
            [ np.dot(R_3, p_1), np.dot(R_3, p_2), np.dot(R_3, p_3) ]
        ]
    )
    
    mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    f_1_prev: float = 0
    f_3_prev: float = 0
    g_1_prev: float = 0
    g_3_prev: float = 0
    
    rho_1_prev: float = np.inf
    rho_2_prev: float = np.inf
    rho_3_prev: float = np.inf
    
    tol: float = 1e-6
    
    iteration: int = 1
    
    max_iteration: int = 100
    
    while True:
        
        # ? 1. Magnitudes
        
        r_2_m: float = np.linalg.norm(r_2)
        v_2_m: float = np.linalg.norm(v_2)
        
        # ? 2. Alpha
        
        Alpha: float = 2 / r_2_m - v_2_m**2 / mu # NOSONAR python:S117
        
        # ? 3. Radial velocity
        
        v_r_2: float = np.dot(v_2, r_2) / r_2_m
        
        # ? 4. Universal variables
        
        chi_1: u.Quantity = sl_lagrange_coefficients.universal_kepler_solution(
            attractor=attractor,
            initial_position=r_2_m * u.km,
            initial_radial_velocity=v_r_2 * u.km / u.s,
            alpha=Alpha * 1 / u.km,
            delta_time=time.TimeDelta(observation_time_list[0] - observation_time_list[1], format='sec'))
        
        if chi_1 is None: return None
        
        chi_3: u.Quantity = sl_lagrange_coefficients.universal_kepler_solution(
            attractor=attractor,
            initial_position=r_2_m * u.km,
            initial_radial_velocity=v_r_2 * u.km / u.s,
            alpha=Alpha * 1 / u.km,
            delta_time=time.TimeDelta(observation_time_list[2] - observation_time_list[1], format='sec'))
        
        if chi_3 is None: return None
        
        # ? 5. Lagrange coefficients
        
        result: ty.List[u.Quantity] = sl_lagrange_coefficients.lagrange_coefficients(
            attractor=attractor,
            initial_position=r_2_m * u.km,
            alpha=Alpha * 1 / u.km,
            delta_time=time.TimeDelta(observation_time_list[0] - observation_time_list[1], format='sec'),
            universal_anomaly=chi_1)
        
        if result is None: return None
        
        f_1, g_1 = result
        
        f_1 = float(f_1.to_value(u.one))
        g_1 = float(g_1.to_value(u.s))
        
        result = sl_lagrange_coefficients.lagrange_coefficients(
            attractor=attractor,
            initial_position=r_2_m * u.km,
            alpha=Alpha * 1 / u.km,
            delta_time=time.TimeDelta(observation_time_list[2] - observation_time_list[1], format='sec'),
            universal_anomaly=chi_3)
        
        if result is None: return None
        
        f_3, g_3 = result
        
        f_3 = float(f_3.to_value(u.one))
        g_3 = float(g_3.to_value(u.s))
        
        # ? 6. Calculate parameters
        
        f_1 = (f_1 + f_1_prev) / 2 if f_1_prev != 0 else f_1
        f_3 = (f_3 + f_3_prev) / 2 if f_3_prev != 0 else f_3
        g_1 = (g_1 + g_1_prev) / 2 if g_1_prev != 0 else g_1
        g_3 = (g_3 + g_3_prev) / 2 if g_3_prev != 0 else g_3
        
        c_1: float = g_3 / (f_1 * g_3 - f_3 * g_1)
        c_3: float = -g_1 / (f_1 * g_3 - f_3 * g_1)
        
        f_1_prev = f_1
        f_3_prev = f_3
        g_1_prev = g_1
        g_3_prev = g_3
        
        # ? 7. Updated slant ranges
        
        rho_1 = 1 / D_0 * (-D[0,0] + D[1,0] / c_1 - D[2,0] * c_3 / c_1)
        rho_2 = 1 / D_0 * (-c_1 * D[0,1] + D[1,1] - c_3 * D[2,1])
        rho_3 = 1 / D_0 * (-D[0,2] * c_1 / c_3 + D[1,2] / c_3 - D[2,2])
        
        # ? 8. Geocentric position vector of the target
    
        r_1 = R_1 + rho_1 * rho_h_1
        r_2 = R_2 + rho_2 * rho_h_2
        r_3 = R_3 + rho_3 * rho_h_3
        
        # ? 9. Velocity vector
        
        v_2 = 1 / (f_1 * g_3 - f_3 * g_1) * (-f_3 * r_1 + f_1 * r_3)
        
        if iteration > max_iteration:
            
            sl_logger.logger.info(f"Maximum number of iterations reached [{max_iteration}]")
            
            break
        
        if np.abs(rho_1 - rho_1_prev) <= tol and np.abs(rho_2 - rho_2_prev) <= tol and np.abs(rho_3 - rho_3_prev) <= tol:
            
            break
        
        rho_1_prev = rho_1
        rho_2_prev = rho_2
        rho_3_prev = rho_3
        
        iteration += 1
    
    # ? 10. Position and velocity vectors
    
    return [r_2 * u.km, v_2 * u.km / u.s]

# * walter

def herrick_gibbs_method(
    attractor: bodies.Attractor,
    position_1 : u.Quantity,
    time_1: u.Quantity,
    position_2 : u.Quantity,
    time_2: u.Quantity,
    position_3 : u.Quantity,
    time_3: u.Quantity) -> ty.Optional[sl_orbital_elements.OrbitalElements]:
    """
    Herrick-Gibbs method of orbit determination from tree position vectors with associated times.

    :param attractor: Main attractor
    :type attractor: bodies.Attractor
    :param position_1: Position vector 1
    :type position_1: u.Quantity
    :param time_1: Time for position vector 1
    :type time_1: u.Quantity
    :param position_2: Position vector 2
    :type position_2: u.Quantity
    :param time_2: Time for position vector 2
    :type time_2: u.Quantity
    :param position_3: Position vector 3
    :type position_3: u.Quantity
    :param time_3: Time for position vector 3
    :type time_3: u.Quantity
    :return: Orbital elements
    :rtype: ty.Optional[sl_orbital_elements.OrbitalElements]
    
    📌 **Notes**
    
    The three vectors must lie in the same plane and not too close to each other.
    
    This method is useful when the geocentric angles of the three subsequent measurements are more apart than 15° for
    LEO and 6° for GSO.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 14.2 *Orbit Determination*
        - Section 14.2.4 *Simple Orbit Estimation*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * position_1
    
    err_msg = sl_validator.validate_quantity_vector("position_1", position_1, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * time_1
    
    err_msg = sl_validator.validate_quantity("time_1", time_1, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * position_2
    
    err_msg = sl_validator.validate_quantity_vector("position_2", position_2, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * time_2
    
    err_msg = sl_validator.validate_quantity("time_2", time_2, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * position_3
    
    err_msg = sl_validator.validate_quantity_vector("position_3", position_3, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * time_3
    
    err_msg = sl_validator.validate_quantity("time_3", time_3, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    r_1: np.ndarray = position_1.to_value(u.km)
    r_2: np.ndarray = position_2.to_value(u.km)
    r_3: np.ndarray = position_3.to_value(u.km)
    
    t_1: np.ndarray = time_1.to_value(u.s)
    t_2: np.ndarray = time_2.to_value(u.s)
    t_3: np.ndarray = time_3.to_value(u.s)
    
    mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    r_1_m: float = np.linalg.vector_norm(r_1)
    r_2_m: float = np.linalg.vector_norm(r_2)
    r_3_m: float = np.linalg.vector_norm(r_3)
    
    dt_21: float = t_2 - t_1
    dt_32: float = t_3 - t_2
    dt_31: float = t_3 - t_1
    
    v_2: np.ndarray =\
                    dt_32 * (mu / (12 * r_1_m**3) - 1 / (dt_21 * dt_31)) * r_1 +\
        (dt_32 - dt_21) * (mu / (12 * r_2_m**3) + 1 / (dt_21 * dt_32)) * r_2 +\
                    dt_21 * (mu / (12 * r_3_m**3) + 1 / (dt_31 * dt_32)) * r_3
    
    oe: sl_orbital_elements.OrbitalElements = sl_representation.cartesian_to_keplerian(
        attractor=attractor, position=r_2 * u.km, velocity=v_2 * u.km / u.s)

    return oe
