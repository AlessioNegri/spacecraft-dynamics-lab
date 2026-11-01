import astropy.units as u
import numpy as np
import typing as ty

import spacelab.bodies as sl_bodies
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator
import spacelab.models.orbit_parameters as sl_orbit_parameters

def cartesian_to_orbit_parameters(
    attractor: sl_bodies.Attractor,
    position: u.Quantity,
    velocity: u.Quantity) -> sl_orbit_parameters.OrbitParameters:
    """
    Converts the given cartesian parameters (position and velocity vector) in orbit ones.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param position: Position vector
    :type position: u.Quantity
    :param velocity: Velocity vector
    :type velocity: u.Quantity
    :return: Orbit parameters
    :rtype: sl_orbit_parameters.OrbitParameters
    
    📖 **References**
    
    - :cite:`curtis`
        - Chapter 2 *The Two-Body Problem*
            - Section 2.4 *Angular momentum and the orbit formulas*
            - Section 2.5 *The energy law*
            - Section 2.6 *Circular orbits (e = 0)*
            - Section 2.7 *Elliptical orbits (0 < e < 1)*
            - Section 2.8 *Parabolic trajectories (e = 1)*
            - Section 2.9 *Hyperbolic trajectories (e > 1)*
    - :cite:`kluever`
        - Chapter 2 *Two-Body Orbital Mechanics*
            - Section 2.3 *Constants of Motion*
            - Section 2.4 *Conic Sections*
            - Section 2.5 *Elliptical Orbit*
            - Section 2.6 *Parabolic Trajectory*
            - Section 2.7 *Hyperbolic Trajectory*
    - :cite:`sforza`
        - Chapter 5 *ORBITAL MECHANICS*
            - Section 5.1.2 *CLOSED ORBITS IN A CENTRAL FORCE FIELD*
            - Section 5.2 *ENERGY AND ANGULAR MOMENTUM IN ORBITS*
    - :cite:`walter`
        - Chapter 7 *Orbits*
            - Section 7.2 *General Principles of Motion*
            - Section 7.3 *Motion in a Gravitational Field*
            - Section 7.4 *Keplerian Orbits*
    """
    
    parameters = sl_orbit_parameters.OrbitParameters()
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return parameters
    
    # * position
    
    err_msg = sl_validator.validate_quantity_vector("position", position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return parameters
    
    # * velocity
    
    err_msg = sl_validator.validate_quantity_vector("velocity", velocity, u.km / u.s, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return parameters
    
    # >>> Algorithm
    
    r: np.ndarray = ty.cast(np.ndarray, position.to(u.km).to_value())
    
    r_m: float = np.linalg.norm(r)

    v: np.ndarray = ty.cast(np.ndarray, velocity.to(u.km / u.s).to_value())
    
    v_m: float = np.linalg.norm(v)
    
    mu: float = sl_bodies.BODIES[attractor].mu.to(u.km**3 / u.s**2).to_value()
    
    g_0: float = sl_bodies.BODIES[attractor].g_0.to(u.km / u.s**2).to_value()
    
    R_E: float = sl_bodies.BODIES[attractor].R_E.to(u.km).to_value()
    
    # ? Angular Momentum
    
    h: np.ndarray = np.cross(r, v)
    
    h_m: float = np.linalg.norm(h)
    
    parameters.specific_angular_momentum = h_m * u.km**2 / u.s
    
    parameters.transverse_velocity = h_m / r_m * u.km / u.s
    
    # ? Energy (vis-viva equation)
    
    epsilon: float = 1 / 2 * v_m**2 - mu / r_m
    
    parameters.specific_energy = epsilon * u.km**2 / u.s**2
    
    # ? Semilatus Rectum / Parameter
    
    p: float = h_m**2 / mu
    
    parameters.semilatus_rectum = p * u.km
    
    # ? Semimajor axis
    
    a: float = - mu / (2 * epsilon) if epsilon != 0 else np.inf
    
    parameters.semimajor_axis = a * u.km
    
    # ? Eccentricity
    
    # ! Avoid very small negative numbers
    e: float = np.sqrt(max((2 * h_m**2 * epsilon) / (mu **2) + 1, 0))
    
    parameters.eccentricity = e * u.one
    
    # ? Cosmic Velocities
    
    parameters.first_cosmic_velocity = np.sqrt(g_0 * R_E) * u.km / u.s
    
    parameters.second_cosmic_velocity = np.sqrt(2 * g_0 * R_E) * u.km / u.s
    
    # ? Select Orbit Type
    
    if np.isclose(h_m, 0.0, rtol=1e-3, atol=1e-6):
        
        parameters.conic_type = "line"
        
        return parameters
    
    if np.isclose(e, 0.0, rtol=1e-2, atol=1e-4):
        
        parameters.conic_type           = "circle"
        parameters.periapsis_radius     = r_m * u.km
        parameters.apoapsis_radius      = r_m * u.km
        parameters.periapsis_velocity   = np.sqrt(mu / r_m) * u.km / u.s
        parameters.apoapsis_velocity    = np.sqrt(mu / r_m) * u.km / u.s
        parameters.semiminor_axis       = r_m * u.km
        parameters.period               = (2 * np.pi) /  np.sqrt(mu) * r_m ** (3 / 2) * u.s
    
    elif np.isclose(e, 1.0, rtol=1e-3, atol=1e-6):
        
        parameters.conic_type           = "parabola"
        parameters.periapsis_radius     = p / 2 * u.km
        parameters.apoapsis_radius      = 0 * u.km
        parameters.periapsis_velocity   = 2 * np.sqrt(mu / p) * u.km / u.s
        parameters.apoapsis_velocity    = 0 * u.km / u.s
        parameters.semiminor_axis       = 0 * u.km
        parameters.period               = 0 * u.s
        parameters.escape_velocity      = np.sqrt(2 * mu / parameters.periapsis_radius.to_value()) * u.km / u.s
        
        # ! The escape velocity is calculated at periapsis, even if defined for each position
    
    elif e < 1:
        
        parameters.conic_type           = "ellipse"
        parameters.periapsis_radius     = p / (1 + e) * u.km
        parameters.apoapsis_radius      = p / (1 - e) * u.km
        parameters.periapsis_velocity   = mu / h_m * (1 + e) * u.km / u.s
        parameters.apoapsis_velocity    = mu / h_m * (1 - e) * u.km / u.s
        parameters.semiminor_axis       = a * np.sqrt(1 - e ** 2) * u.km
        parameters.period               = (2 * np.pi) /  np.sqrt(mu) * a ** (3 / 2) * u.s
    
    else:
        
        parameters.conic_type               = "hyperbola"
        parameters.periapsis_radius         = - a * (e - 1) * u.km
        parameters.apoapsis_radius          = 0 * u.km
        parameters.periapsis_velocity       = mu / h_m * (e + 1) * u.km / u.s
        parameters.apoapsis_velocity        = 0 * u.km / u.s
        parameters.semiminor_axis           = np.abs(a) * np.sqrt(e ** 2 - 1) * u.km
        parameters.period                   = 0 * u.s
        parameters.escape_velocity          = np.sqrt(2 * mu  / parameters.periapsis_radius.to_value()) * u.km / u.s
        parameters.hyperbolic_excess_speed  = np.sqrt(2 * epsilon) * u.km / u.s
        parameters.oberth_maneuver_velocity = np.sqrt(parameters.second_cosmic_velocity ** 2 + parameters.hyperbolic_excess_speed ** 2)
        parameters.turning_angle            = np.rad2deg(2 * np.arcsin(1 / e)) * u.deg
        parameters.asymptotic_true_anomaly  = np.rad2deg(np.arccos(-1 / e)) * u.deg
        parameters.asymptote_angle          = np.rad2deg(np.arccos(+1 / e)) * u.deg
        parameters.aiming_radius            = np.abs(a) * np.sqrt(e ** 2 - 1) * u.km
        parameters.characteristic_energy    = parameters.hyperbolic_excess_speed ** 2
        
        # ! The escape velocity is calculated at periapsis, even if defined for each position
    
    return parameters
