"""
Orbital Position Module

Implements equations and algorithms for computing the position of an orbiting body at a given time.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 3: Orbital Position as a Function of Time

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 4: Time of Flight

- Pasquale M. Sforza, "Manned Spacecraft - Design Principles"
    - Chapter 5: Orbital Mechanics

- Ulrich Walter, "Astronautics - The Physics of Space Flight"
    - Chapter 7: Orbits
"""

import astropy.units as u
import numpy as np
import scipy.optimize as optimize

import astro.bodies as bodies
import astro.common as common

error_period: str = "'period' must be positive"

error_time_of_flight: str = "'time_of_flight' must be positive"

class OrbitalPosition():
    """OrbitalPosition"""
    
    @staticmethod
    def circular_orbit_time(true_anomaly: u.Quantity, period: u.Quantity) -> u.Quantity:
        """
        Calculate the time on a circular orbit at given true anomaly

        Args:
            true_anomaly (u.Quantity): True anomaly
            period (u.Quantity): Period

        Returns:
            u.Quantity: Time of flight
        """
        
        theta: float = true_anomaly.to_value(u.rad)
        
        T: float = period.to_value(u.s)
        
        common.check_angle(np.rad2deg(theta))
        
        if T <= 0: raise ValueError(error_period)
        
        t: float = theta / (2 * np.pi) * T
        
        return t * u.s
    
    @staticmethod
    def circular_orbit_true_anomaly(time_of_flight: u.Quantity, period: u.Quantity) -> u.Quantity:
        """
        Calculate the true anomaly on a circular orbit at given time of flight

        Args:
            time_of_flight (u.Quantity): Time of flight
            period (u.Quantity): Period

        Returns:
            u.Quantity: True anomaly
        """
        
        tof: float = time_of_flight.to_value(u.s)
        
        T: float = period.to_value(u.s)
        
        if tof <= 0: raise ValueError(error_time_of_flight)
        
        if T <= 0: raise ValueError(error_period)
        
        theta: float = np.rad2deg((2 * np.pi / T) * tof)
        
        return common.wrap_angle(theta, low=0, high=360) * u.deg
    
    @staticmethod
    def elliptical_orbit_time(true_anomaly: u.Quantity, period: u.Quantity, eccentricity: u.Quantity) -> u.Quantity:
        """
        Calculate the time on an elliptical orbit at given true anomaly

        Args:
            true_anomaly (u.Quantity): True anomaly
            period (u.Quantity): Period
            eccentricity (u.Quantity): Eccentricity

        Returns:
            u.Quantity: Time of flight
        """
        
        theta: float = true_anomaly.to_value(u.rad)
        
        T: float = period.to_value(u.s)
        
        e: float = eccentricity.to_value()
        
        common.check_angle(np.rad2deg(theta))
        
        if T <= 0: raise ValueError(error_period)
        
        if e < 0 or e >= 1: raise ValueError("'eccentricity' must be between 0 and 1")
        
        # ! atan2 preserves the correct quadrant, unlike atan
        E: float = 2 * np.arctan2(np.sqrt(1 - e) * np.sin(theta / 2), np.sqrt(1 + e) * np.cos(theta / 2))
        
        m_e: float = E - e * np.sin(E) # ? Mean anomaly (M_E)
        
        t: float = m_e / (2 * np.pi) * T
        
        return t * u.s
    
    @staticmethod
    def elliptical_orbit_true_anomaly(time_of_flight: u.Quantity,
                                      period: u.Quantity,
                                      eccentricity: u.Quantity) -> u.Quantity:
        """
        Calculate the true anomaly on an elliptical orbit at given time of flight

        Args:
            time_of_flight (u.Quantity): Time of flight
            period (u.Quantity): Period
            eccentricity (u.Quantity): Eccentricity

        Returns:
            u.Quantity: True anomaly
        """
        
        tof: float = time_of_flight.to_value(u.s)
        
        T: float = period.to_value(u.s)
        
        e: float = eccentricity.to_value()
        
        if tof <= 0: raise ValueError(error_time_of_flight)
        
        if T <= 0: raise ValueError(error_period)
        
        if e < 0 or e >= 1: raise ValueError("'eccentricity' must be between 0 and 1")
        
        m_e: float = (2 * np.pi / T) * tof # ? Mean anomaly (M_E) [ 0 <= m_e <= np.pi ]
        
        f: callable = lambda E: E - e * np.sin(E) - m_e
        
        df: callable = lambda E: 1 - e * np.cos(E)
        
        E_0: float = (m_e + 0.5 * e) if m_e < np.pi else (m_e - 0.5 * e)
        
        # ? E_0 = m_e + e * np.sin(m_e) + 0.5 * e**2 * np.sin(2 * m_e)
        
        # ? E_0 = m_e + e**2 * ( (6 * m_e)**(1/3) - m_e )                       @ 0 <= m_e < 0.25
        # ? E_0 = m_e + e * np.sin(m_e) / ( 1 - np.sin(m_e + e) + np.sin(m_e) ) @ 0.25 <= m_e < np.pi
        
        E: float = optimize.newton(f, x0=E_0, fprime=df, maxiter=100, tol=1e-8) # ? Eccentric anomaly
        
        theta: float = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))
        
        return common.wrap_angle(np.rad2deg(theta), low=0, high=360) * u.deg
    
    @staticmethod
    def parabolic_orbit_time(true_anomaly: u.Quantity,
                             specific_angular_momentum: u.Quantity,
                             attractor: bodies.Attractor) -> u.Quantity:
        """
        Calculate the time on a parabolic orbit at given true anomaly

        Args:
            true_anomaly (u.Quantity): True anomaly
            specific_angular_momentum (u.Quantity): Specific angular momentum
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: Time of flight
        """
        
        theta: float = true_anomaly.to_value(u.rad)
        
        h: float = specific_angular_momentum.to_value(u.km**2 / u.s)
        
        common.check_angle(np.rad2deg(theta))
        common.check_attractor(attractor)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        D: float = np.tan(theta / 2) # ? Parabolic eccentric anomaly
        
        m_p: float = 1/2 * D + 1/6 * D**3 # ? Mean anomaly (M_p) + Barker's equation
        
        t: float = m_p * h**3 / mu**2
        
        return t * u.s
    
    @staticmethod
    def parabolic_orbit_true_anomaly(time_of_flight: u.Quantity,
                                     specific_angular_momentum: u.Quantity,
                                     attractor: bodies.Attractor) -> u.Quantity:
        """
        Calculate the true anomaly on a parabolic orbit at given time of flight
        
        Barker's equation
            
            M_p = 1/2 * G + 1/3 * G**3 with G = tan(θ / 2) and q = 3 * M_p

        Args:
            time_of_flight (u.Quantity): Time of flight
            specific_angular_momentum (u.Quantity): Specific angular momentum
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: True anomaly
        """
        
        tof: float = time_of_flight.to_value(u.s)
        
        h: float = specific_angular_momentum.to_value(u.km**2 / u.s)
        
        if tof <= 0: raise ValueError(error_time_of_flight)
        
        common.check_attractor(attractor)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        m_p: float = tof * mu**2 / h**3 # ? Mean anomaly (M_p)
        
        q: float = 3 * m_p # ? Auxiliary variable
        
        theta: float = 2 * np.arctan( (q + np.sqrt(q**2 + 1))**(1/3) - (q + np.sqrt(q**2 + 1))**(-1/3) )
        
        return common.wrap_angle(np.rad2deg(theta), low=0, high=360) * u.deg
    
    @staticmethod
    def hyperbolic_orbit_time(true_anomaly: u.Quantity,
                              specific_angular_momentum: u.Quantity,
                              eccentricity: u.Quantity,
                              attractor: bodies.Attractor) -> u.Quantity:
        """
        Calculate the time on a hyperbolic orbit at given true anomaly

        Args:
            true_anomaly (u.Quantity): True anomaly
            specific_angular_momentum (u.Quantity): Specific angular momentum
            eccentricity (u.Quantity): Eccentricity
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: Time of flight
        """
        
        theta: float = true_anomaly.to_value(u.rad)
        
        h: float = specific_angular_momentum.to_value(u.km**2 / u.s)
        
        e: float = eccentricity.to_value()
        
        common.check_angle(np.rad2deg(theta))
        common.check_attractor(attractor)
        
        if e <= 1: raise ValueError("'e' must be greater than 1 for hyperbolic orbits")
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        F: float = 2 * np.arctanh(np.sqrt((e - 1) / (e + 1)) * np.tan(theta / 2)) # ? Hyperbolic eccentric anomaly
        
        m_h: float = e * np.sinh(F) - F # ? Mean anomaly (M_h)
        
        t: float = m_h * h**3 / mu**2 * (e**2 - 1)**(-3/2)
        
        return t * u.s
    
    @staticmethod
    def hyperbolic_orbit_true_anomaly(time_of_flight: u.Quantity,
                                      specific_angular_momentum: u.Quantity,
                                      eccentricity: u.Quantity,
                                      attractor: bodies.Attractor) -> u.Quantity:
        """
        Calculate the true anomaly on a hyperbolic orbit at given time of flight

        Args:
            time_of_flight (u.Quantity): Time of flight
            specific_angular_momentum (u.Quantity): Specific angular momentum
            eccentricity (u.Quantity): Eccentricity
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: True anomaly
        """
        
        tof: float = time_of_flight.to_value(u.s)
        
        h: float = specific_angular_momentum.to_value(u.km**2 / u.s)
        
        e: float = eccentricity.to_value()
        
        if tof <= 0: raise ValueError(error_time_of_flight)
        
        common.check_attractor(attractor)
        
        if e <= 1: raise ValueError("'e' must be greater than 1 for hyperbolic orbits")
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        m_h: float = tof * mu**2 / h**3 * (e**2 - 1)**(3/2) # ? Mean anomaly
        
        F_0: float = np.arcsinh(m_h / e) # np.log(2 * m_h / e + 1.8) if m_h > 0 else -np.log(-2 * m_h / e + 1.8)
        
        f: callable = lambda F: e * np.sinh(F) - F - m_h
        
        df: callable = lambda F: e * np.cosh(F) - 1
        
        F = optimize.newton(f, x0=F_0, fprime=df, maxiter=100, tol=1e-8) # ? Hyperbolic eccentric anomaly
        
        theta: float = 2 * np.arctan(np.sqrt((e + 1) / (e - 1)) * np.tanh(F / 2))
        
        return common.wrap_angle(np.rad2deg(theta), low=0, high=360) * u.deg
