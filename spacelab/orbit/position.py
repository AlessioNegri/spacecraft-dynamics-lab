"""
This module implements methods for obtaining **position as a function of time**, using the various forms of *Kepler's
equation* relating position to time. These transcendental equations must be solved iteratively using a procedure like
Newton's method.

📌 **Notes**

Kepler's equation determines the *Time Of Flight* (*TOF*) from periapsis to the satellite's current position as a
function of semimajor axis :math:`a`, eccentricity :math:`e`, and eccentric anomaly :math:`E`. Kepler introduced another
angle called the **mean anomaly**, :math:`M`, defined as the parenthetical term in the TOF equation.

The particular usefullness of :math:`M` is due to the fact that it serves two different purposes in one parameter:

1. By definition is an angle that by intention advances linearly with time. Just as for the true anomaly :math:`\\theta`
the mean anomaly is measured relative to the periapsis, but is not cyclically limited to the interval [0°, 360°]. As an
unambiguous angle it perfectly serves as an orbital element.

2. Because it is strictly linear with time and in addition is dimensionless, it is a perfect substitution for time and
hence a orbit position sequencer.

📖 **References**

- :cite:`curtis`
    - Chapter 3 *Orbital Position as a Function of Time*
- :cite:`kluever`
    - Chapter 4 *Time of Flight*
- :cite:`sforza`
    - Chapter 5 *ORBITAL MECHANICS*
- :cite:`walter`
    - Chapter 7 *Orbits*
"""

import astropy.units as u
import numpy as np
import scipy.optimize as optimize

import spacelab.bodies as sl_bodies
import spacelab.utils.angle as sl_angle
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

error_period: str = "'period' must be positive"

error_time_of_flight: str = "'time_of_flight' must be positive"

# * Circular orbit

def circular_orbit_time(true_anomaly: u.Quantity, period: u.Quantity) -> u.Quantity:
    """
    Calculates the time on a circular orbit at given true anomaly.

    :param true_anomaly: True anomaly
    :type true_anomaly: u.Quantity
    :param period: Orbital period
    :type period: u.Quantity
    :return: Time since periapsis
    :rtype: u.Quantity
    
    📌 **Notes**
    
    The reason that :math:`t` is directly proportional to :math:`\\theta` in a circular orbit is simply that the angular
    velocity is constant.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 3.3 *Circular orbits (e = 0)*
    - :cite:`kluever`
        - Section 4.2 *Kepler's Equation*
    - :cite:`walter`
        - Section 7.4 *Keplerian Orbits*
        - Section 7.4.1 *Circular Orbit*
    """
    
    t: u.Quantity = 0 * u.s
    
    # >>> Validation
    
    # * true_anomaly
    
    err_msg: str | None = sl_validator.validate_quantity_angle("true_anomaly", true_anomaly)
    
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # * period
    
    err_msg = sl_validator.validate_quantity("period", period, u.s)
        
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # >>> Algorithm
    
    theta: float = true_anomaly.to_value(u.rad)
    T: float = period.to_value(u.s)
    
    if T <= 0: sl_logger.logger.warning(error_period); return t
    
    t = theta / (2 * np.pi) * T * u.s
    
    return t

def circular_orbit_true_anomaly(time_of_flight: u.Quantity, period: u.Quantity) -> u.Quantity:
    """
    Calculates the true anomaly on a circular orbit at given time of flight.

    :param time_of_flight: Time of flight
    :type time_of_flight: u.Quantity
    :param period: Orbital period
    :type period: u.Quantity
    :return: True anomaly
    :rtype: u.Quantity
    
    📌 **Notes**
    
    The reason that :math:`t` is directly proportional to :math:`\\theta` in a circular orbit is simply that the angular
    velocity is constant.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 3.3 *Circular orbits (e = 0)*
    - :cite:`kluever`
        - Section 4.2 *Kepler's Equation*
    - :cite:`walter`
        - Section 7.4 *Keplerian Orbits*
        - Section 7.4.1 *Circular Orbit*
    """
    
    theta: u.Quantity = 0 * u.deg
    
    # >>> Validation
    
    # * time_of_flight
    
    err_msg: str | None = sl_validator.validate_quantity("time_of_flight", time_of_flight, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # * period
    
    err_msg = sl_validator.validate_quantity("period", period, u.s)
        
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # >>> Algorithm
    
    tof: float = time_of_flight.to_value(u.s)
    T: float = period.to_value(u.s)
    
    if tof <= 0: sl_logger.logger.warning(error_time_of_flight); return theta
    if T <= 0: sl_logger.logger.warning(error_period); return theta
    
    theta = (2 * np.pi / T) * tof * u.rad
    
    return sl_angle.wrap_angle(theta)

# * Elliptical orbit

def elliptical_orbit_time(true_anomaly: u.Quantity, period: u.Quantity, eccentricity: u.Quantity) -> u.Quantity:
    """
    Calculates the time on an elliptical orbit at given true anomaly.

    :param true_anomaly: True anomaly
    :type true_anomaly: u.Quantity
    :param period: Orbital period
    :type period: u.Quantity
    :param eccentricity: Orbit eccentricity
    :type eccentricity: u.Quantity
    :return: Time since periapsis
    :rtype: u.Quantity
    
    📌 **Notes**
    
    The angular velocity of the position vector of an elliptical orbit is not constant.
    
    The mean anomaly is the azimuth position (in radians) of a fictitious body moving around the ellipse at the constant
    angular speed :math:`n`. For a circular orbit, the mean anomaly :math:`M_e` and the true anomaly :math:`\\theta` are
    identical.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 3.4 *Elliptical orbits (e < 1)*
    - :cite:`kluever`
        - Section 4.2 *Kepler's Equation*
    - :cite:`walter`
        - Section 7.4 *Keplerian Orbits*
        - Section 7.4.2 *Elliptic Orbit*
    """
    
    t: u.Quantity = 0 * u.s
    
    # >>> Validation
    
    # * true_anomaly
    
    err_msg: str | None = sl_validator.validate_quantity_angle("true_anomaly", true_anomaly)
    
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # * period
    
    err_msg = sl_validator.validate_quantity("period", period, u.s)
        
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # * eccentricity
    
    err_msg = sl_validator.validate_quantity("eccentricity", eccentricity, u.one)
        
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # >>> Algorithm
    
    theta: float = true_anomaly.to_value(u.rad)
    T: float = period.to_value(u.s)
    e: float = eccentricity.to_value()
    
    if T <= 0: sl_logger.logger.warning(error_period); return t
    if e < 0 or e >= 1: sl_logger.logger.warning("'eccentricity' must be between 0 and 1"); return t
    
    # ! atan2 preserves the correct quadrant, unlike atan
    E: float = 2 * np.arctan2(np.sqrt(1 - e) * np.sin(theta / 2), np.sqrt(1 + e) * np.cos(theta / 2))
    
    m_e: float = E - e * np.sin(E) # ? Mean anomaly (M_E)
    
    t = m_e / (2 * np.pi) * T * u.s
    
    return t

def elliptical_orbit_true_anomaly(
    time_of_flight: u.Quantity,
    period: u.Quantity,
    eccentricity: u.Quantity) -> u.Quantity:
    """
    Calculates the true anomaly on an elliptical orbit at given time of flight.

    :param time_of_flight: Time of flight
    :type time_of_flight: u.Quantity
    :param period: Orbital period
    :type period: u.Quantity
    :param eccentricity: Orbit eccentricity
    :type eccentricity: u.Quantity
    :return: True anomaly
    :rtype: u.Quantity
    
    📌 **Notes**
    
    The angular velocity of the position vector of an elliptical orbit is not constant.
    
    The mean anomaly is the azimuth position (in radians) of a fictitious body moving around the ellipse at the constant
    angular speed :math:`n`. For a circular orbit, the mean anomaly :math:`M_e` and the true anomaly :math:`\\theta` are
    identical.
    
    Newton's method, or one of its variants, is one of the more common and efficient ways of finding the root of a
    well-behaved function, in order to find the true anomaly.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 3.4 *Elliptical orbits (e < 1)*
    - :cite:`kluever`
        - Section 4.2 *Kepler's Equation*
    - :cite:`walter`
        - Section 7.4 *Keplerian Orbits*
        - Section 7.4.2 *Elliptic Orbit*
    """
    
    theta: u.Quantity = 0 * u.deg
    
    # >>> Validation
    
    # * time_of_flight
    
    err_msg: str | None = sl_validator.validate_quantity("time_of_flight", time_of_flight, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # * period
    
    err_msg = sl_validator.validate_quantity("period", period, u.s)
        
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # * eccentricity
    
    err_msg = sl_validator.validate_quantity("eccentricity", eccentricity, u.one)
        
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # >>> Algorithm
    
    tof: float = time_of_flight.to_value(u.s)
    T: float = period.to_value(u.s)
    e: float = eccentricity.to_value()
    
    if tof <= 0: sl_logger.logger.warning(error_time_of_flight); return theta
    if T <= 0: sl_logger.logger.warning(error_period); return theta
    if e < 0 or e >= 1: sl_logger.logger.warning("'eccentricity' must be between 0 and 1"); return theta
    
    m_e: float = (2 * np.pi / T) * tof # ? Mean anomaly (M_E) [ 0 <= m_e <= np.pi ]
    
    f: callable = lambda E: E - e * np.sin(E) - m_e
    
    df: callable = lambda E: 1 - e * np.cos(E)
    
    E_0: float = (m_e + 0.5 * e) if m_e < np.pi else (m_e - 0.5 * e)
    
    # ? E_0 = m_e + e * np.sin(m_e) + 0.5 * e**2 * np.sin(2 * m_e)
    
    # ? E_0 = m_e + e**2 * ( (6 * m_e)**(1/3) - m_e )                       @ 0 <= m_e < 0.25
    # ? E_0 = m_e + e * np.sin(m_e) / ( 1 - np.sin(m_e + e) + np.sin(m_e) ) @ 0.25 <= m_e < np.pi
    
    E: float = optimize.newton(f, x0=E_0, fprime=df, maxiter=100, tol=1e-8) # ? Eccentric anomaly
    
    theta = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2)) * u.rad
    
    return sl_angle.wrap_angle(theta)

# * Parabolic orbit

def parabolic_orbit_time(
    true_anomaly: u.Quantity,
    specific_angular_momentum: u.Quantity,
    attractor: sl_bodies.Attractor) -> u.Quantity:
    """
    Calculates the time on a parabolic orbit at given true anomaly.

    :param true_anomaly: True anomaly
    :type true_anomaly: u.Quantity
    :param specific_angular_momentum: Specific angular momentum
    :type specific_angular_momentum: u.Quantity
    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :return: Time since periapsis
    :rtype: u.Quantity
    
    📌 **Notes**
    
    :math:`M_p` is dimensionless, and it may be thought of as the 'mean anomaly' for the parabola.
    
    It is used the **Barker's equation**.
    
    :math:`M_p = \\frac{1}{2} \\tan\\frac{\\theta}{2} + \\frac{1}{6} \\tan^3\\frac{\\theta}{2}`
    
    Note that parabolic anomaly :math:`D` is not an angle (unlike eccentric anomaly :math:`E` or mean anomaly :math:`M`)
    but that it is dimensionless.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 3.5 *Parabolic trajectories (e = 1)*
    - :cite:`kluever`
        - Section 4.3 *Parabolic and Hyperbolic Time of Flight*
        - Section 4.3.1 *Parabolic Trajectory Flight Time*
    - :cite:`walter`
        - Section 7.4 *Keplerian Orbits*
        - Section 7.4.4 *Parabolic Orbit*
    """
    
    t: u.Quantity = 0 * u.s
    
    # >>> Validation
    
    # * true_anomaly
    
    err_msg: str | None = sl_validator.validate_quantity_angle("true_anomaly", true_anomaly)
    
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # * specific_angular_momentum
    
    err_msg = sl_validator.validate_quantity("specific_angular_momentum", specific_angular_momentum, u.km**2 / u.s)
        
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # * attractor
    
    err_msg = sl_validator.validate_attractor(attractor)
        
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # >>> Algorithm
    
    theta: float = true_anomaly.to_value(u.rad)
    h: float = specific_angular_momentum.to_value(u.km**2 / u.s)
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    D: float = np.tan(theta / 2) # ? Parabolic eccentric anomaly
    
    m_p: float = 1/2 * D + 1/6 * D**3 # ? Mean anomaly (M_p) + Barker's equation
    
    t = m_p * h**3 / mu**2 * u.s
    
    return t

def parabolic_orbit_true_anomaly(
    time_of_flight: u.Quantity,
    specific_angular_momentum: u.Quantity,
    attractor: sl_bodies.Attractor) -> u.Quantity:
    """
    Calculates the true anomaly on a parabolic orbit at given time of flight.

    :param time_of_flight: Time of flight
    :type time_of_flight: u.Quantity
    :param specific_angular_momentum: Specific angular momentum
    :type specific_angular_momentum: u.Quantity
    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :return: True anomaly
    :rtype: u.Quantity
    
    📌 **Notes**
    
    :math:`M_p` is dimensionless, and it may be thought of as the 'mean anomaly' for the parabola.
    
    It is used the Barker's equation.
    
    :math:`M_p = \\frac{1}{2} \\tan\\frac{\\theta}{2} + \\frac{1}{6} \\tan^3\\frac{\\theta}{2}`
    
    Note that parabolic anomaly :math:`D` is not an angle (unlike eccentric anomaly :math:`E` or mean anomaly :math:`M`)
    but that it is dimensionless.
    
    Considering Barker's equation as a cubic function for :math:`\\tan\\frac{\\theta}{2}` we find the roots by applying
    Cardano's method and Descartes' rule of signs. From this, it can be shown that there is only one real solution to
    this equation for :math:`\\theta` and :math:`r`, with :math:`q = 3 M_p` (Chebyshev polynomials).
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 3.5 *Parabolic trajectories (e = 1)*
    - :cite:`kluever`
        - Section 4.3 *Parabolic and Hyperbolic Time of Flight*
        - Section 4.3.1 *Parabolic Trajectory Flight Time*
    - :cite:`walter`
        - Section 7.4 *Keplerian Orbits*
        - Section 7.4.4 *Parabolic Orbit*
    """
    
    theta: u.Quantity = 0 * u.deg
    
    # >>> Validation
    
    # * time_of_flight
    
    err_msg: str | None = sl_validator.validate_quantity("time_of_flight", time_of_flight, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # * specific_angular_momentum
    
    err_msg = sl_validator.validate_quantity("specific_angular_momentum", specific_angular_momentum, u.km**2 / u.s)
        
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # * attractor
    
    err_msg = sl_validator.validate_attractor(attractor)
        
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # >>> Algorithm
    
    tof: float = time_of_flight.to_value(u.s)
    h: float = specific_angular_momentum.to_value(u.km**2 / u.s)
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    if tof <= 0: sl_logger.logger.warning(error_time_of_flight); return theta
    
    m_p: float = tof * mu**2 / h**3 # ? Mean anomaly (M_p)
    
    q: float = 3 * m_p # ? Auxiliary variable
    
    theta = 2 * np.arctan( (q + np.sqrt(q**2 + 1))**(1/3) - (q + np.sqrt(q**2 + 1))**(-1/3) ) * u.rad
    
    return sl_angle.wrap_angle(theta)

# * Hyperbolic orbit

def hyperbolic_orbit_time(
    true_anomaly: u.Quantity,
    specific_angular_momentum: u.Quantity,
    eccentricity: u.Quantity,
    attractor: sl_bodies.Attractor) -> u.Quantity:
    """
    Calculates the time on a hyperbolic orbit at given true anomaly.

    :param true_anomaly: True anomaly
    :type true_anomaly: u.Quantity
    :param specific_angular_momentum: Specific angular momentum
    :type specific_angular_momentum: u.Quantity
    :param eccentricity: Orbit eccentricity
    :type eccentricity: u.Quantity
    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :return: Time since periapsis
    :rtype: u.Quantity
    
    📌 **Notes**
    
    We can simplify the equation by introducing an auxiliary angle analogous to the eccentric anomaly :math:`E` for the
    ellipse, named :math:`F`.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 3.6 *Hyperbolic trajectories (e > 1)*
    - :cite:`kluever`
        - Section 4.3 *Parabolic and Hyperbolic Time of Flight*
        - Section 4.3.2 *Hyperbolic Trajectory Flight Time*
    - :cite:`walter`
        - Section 7.4 *Keplerian Orbits*
        - Section 7.4.3 *Hyperbolic Orbit*
    """
    
    t: u.Quantity = 0 * u.s
    
    # >>> Validation
    
    # * true_anomaly
    
    err_msg: str | None = sl_validator.validate_quantity_angle("true_anomaly", true_anomaly)
    
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # * specific_angular_momentum
    
    err_msg = sl_validator.validate_quantity("specific_angular_momentum", specific_angular_momentum, u.km**2 / u.s)
        
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # * eccentricity
    
    err_msg = sl_validator.validate_quantity("eccentricity", eccentricity, u.one)
        
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # * attractor
    
    err_msg = sl_validator.validate_attractor(attractor)
        
    if err_msg: sl_logger.logger.warning(err_msg); return t
    
    # >>> Algorithm
    
    theta: float = true_anomaly.to_value(u.rad)
    h: float = specific_angular_momentum.to_value(u.km**2 / u.s)
    e: float = eccentricity.to_value(u.one)
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    if e <= 1: sl_logger.logger.warning("'e' must be greater than 1 for hyperbolic orbits"); return t
    
    hyperbolic_argument: float = np.sqrt((e - 1) / (e + 1)) * np.tan(theta / 2)
    
    if np.abs(hyperbolic_argument) >= 1:
        
        sl_logger.logger.warning("'true_anomaly' must be within the hyperbolic asymptote")
        
        return t
    
    F: float = 2 * np.arctanh(hyperbolic_argument) # ? Hyperbolic eccentric anomaly
    
    m_h: float = e * np.sinh(F) - F # ? Mean anomaly (M_h)
    
    t = m_h * h**3 / mu**2 * (e**2 - 1)**(-3/2) * u.s
    
    return t

def hyperbolic_orbit_true_anomaly(
    time_of_flight: u.Quantity,
    specific_angular_momentum: u.Quantity,
    eccentricity: u.Quantity,
    attractor: sl_bodies.Attractor) -> u.Quantity:
    """
    Calculates the true anomaly on a hyperbolic orbit at given time of flight

    :param time_of_flight: Time of flight
    :type time_of_flight: u.Quantity
    :param specific_angular_momentum: Specific angular momentum
    :type specific_angular_momentum: u.Quantity
    :param eccentricity: Orbit eccentricity
    :type eccentricity: u.Quantity
    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :return: True anomaly
    :rtype: u.Quantity
    
    📌 **Notes**
    
    We can simplify the equation by introducing an auxiliary angle analogous to the eccentric anomaly :math:`E` for the
    ellipse, named :math:`F`.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 3.6 *Hyperbolic trajectories (e > 1)*
    - :cite:`kluever`
        - Section 4.3 *Parabolic and Hyperbolic Time of Flight*
        - Section 4.3.2 *Hyperbolic Trajectory Flight Time*
    - :cite:`walter`
        - Section 7.4 *Keplerian Orbits*
        - Section 7.4.3 *Hyperbolic Orbit*
    """
    
    theta: u.Quantity = 0 * u.deg
    
    # >>> Validation
    
    # * time_of_flight
    
    err_msg: str | None = sl_validator.validate_quantity("time_of_flight", time_of_flight, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # * specific_angular_momentum
    
    err_msg = sl_validator.validate_quantity("specific_angular_momentum", specific_angular_momentum, u.km**2 / u.s)
        
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # * eccentricity
    
    err_msg = sl_validator.validate_quantity("eccentricity", eccentricity, u.one)
        
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # * attractor
    
    err_msg = sl_validator.validate_attractor(attractor)
        
    if err_msg: sl_logger.logger.warning(err_msg); return theta
    
    # >>> Algorithm
    
    tof: float = time_of_flight.to_value(u.s)
    h: float = specific_angular_momentum.to_value(u.km**2 / u.s)
    e: float = eccentricity.to_value()
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    if tof <= 0: sl_logger.logger.warning(error_time_of_flight); return theta
    if e <= 1: sl_logger.logger.warning("'e' must be greater than 1 for hyperbolic orbits"); return theta
    
    m_h: float = tof * mu**2 / h**3 * (e**2 - 1)**(3/2) # ? Mean anomaly
    
    F_0: float = np.arcsinh(m_h / e) # np.log(2 * m_h / e + 1.8) if m_h > 0 else -np.log(-2 * m_h / e + 1.8)
    
    f: callable = lambda F: e * np.sinh(F) - F - m_h
    
    df: callable = lambda F: e * np.cosh(F) - 1
    
    F = optimize.newton(f, x0=F_0, fprime=df, maxiter=100, tol=1e-8) # ? Hyperbolic eccentric anomaly
    
    theta = 2 * np.arctan(np.sqrt((e + 1) / (e - 1)) * np.tanh(F / 2)) * u.rad
    
    return sl_angle.wrap_angle(theta)
