"""
Orbital Position Module

Implements equations and algorithms for computing the position of an orbiting body at a given time.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 3: Orbital Position as a Function of Time
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import numpy as np
import scipy.optimize as optimize

import astro.bodies as bodies
import astro.common as common

class OrbitalPosition():
    """OrbitalPosition
    """
    
    def __init__(self):
        """Constructor
        """
        
        pass
    
    @staticmethod
    def circular_orbit_time(nu: float | int, T: float | int) -> float:
        """Calculate the time on a circular orbit at given true anomaly

        Args:
            nu (float): True anomaly [deg]
            T (float): Period [s]

        Returns:
            float: Time [s]
        """
        
        common.check_angle(nu)
        
        t: float = np.deg2rad(nu) / (2 * np.pi) * T
        
        return t
    
    @staticmethod
    def circular_orbit_true_anomaly(t: float | int, T: float | int) -> float:
        """Calculate the true anomaly on a circular orbit at given time

        Args:
            t (float): Time on orbit [s]
            T (float): Period [s]

        Returns:
            float: True anomaly [deg]
        """
        
        nu: float = np.rad2deg((2 * np.pi / T) * t)
        
        return common.wrap_angle(nu, low=0, high=360)
    
    @staticmethod
    def elliptical_orbit_time(nu: float | int, T: float | int, e: float | int) -> float:
        """Calculate the time on an elliptical orbit at given true anomaly

        Args:
            nu (float): True anomaly [deg]
            T (float): Period [s]
            e (float): Eccentricity

        Returns:
            float: Time [s]
        """
        
        common.check_angle(nu)
        
        E: float = 2 * np.arctan(np.sqrt((1 - e) / (1 + e)) * np.tan(np.deg2rad(nu) / 2))
        
        M_e: float = E - e * np.sin(E) # ? Mean anomaly
        
        t: float = M_e / (2 * np.pi) * T
        
        return t
    
    @staticmethod
    def elliptical_orbit_true_anomaly(t: float | int, T: float | int, e: float | int) -> float:
        """Calculate the true anomaly on an elliptical orbit at given time

        Args:
            t (float): Time on orbit [s]
            T (float): Period [s]
            e (float): Eccentricity

        Returns:
            float: True anomaly [deg]
        """
        
        M_e: float = (2 * np.pi / T) * t # ? Mean anomaly
        
        f: callable = lambda E: E - e * np.sin(E) - M_e
        
        df: callable = lambda E: 1 - e * np.cos(E)
        
        E_0: float = (M_e + 0.5 * e) if M_e < np.pi else (M_e - 0.5 * e)
        
        E = optimize.newton(f, x0=E_0, fprime=df, maxiter=100, tol=1e-8) # ? Eccentric anomaly
        
        nu: float = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))
        
        return common.wrap_angle(np.rad2deg(nu), low=0, high=360)
    
    @staticmethod
    def parabolic_orbit_time(nu: float | int, h: float | int, attractor: str) -> float:
        """Calculate the time on a parabolic orbit at given true anomaly

        Args:
            nu (float): True anomaly [deg]
            h (float): Specific angular momentum [km^2/s]
            attractor (str): Main attractor name

        Returns:
            float: Time [s]
        """
        
        common.check_angle(nu)
        common.check_attractor(attractor)
        
        body: bodies.Body = bodies.get_body(attractor.lower())
        
        D: float = np.tan(np.deg2rad(nu) / 2) # ? Parabolic eccentric anomaly
        
        M_p: float = 1/2 * D + 1/6 * D**3 # ? Mean anomaly
        
        t: float = M_p * h**3 / body.mu.to_value()**2
        
        return t
    
    @staticmethod
    def parabolic_orbit_true_anomaly(t: float | int, h: float | int, attractor: str) -> float:
        """Calculate the true anomaly on a parabolic orbit at given time

        Args:
            t (float): Time on orbit [s]
            h (float): Specific angular momentum [km^2/s]
            attractor (str): Main attractor name

        Returns:
            float: True anomaly [deg]
        """
        
        common.check_attractor(attractor)
        
        body: bodies.Body = bodies.get_body(attractor.lower())
        
        M_p: float = t * body.mu.to_value()**2 / h**3 # ? Mean anomaly
        
        nu: float = 2 * np.arctan( (3 * M_p + np.sqrt((3 * M_p)**2 + 1))**(1/3) - (3 * M_p + np.sqrt((3 * M_p)**2 + 1))**(-1/3) )
        
        return common.wrap_angle(np.rad2deg(nu), low=0, high=360)
    
    @staticmethod
    def hyperbolic_orbit_time(nu: float | int, h: float | int, e: float | int, attractor: str) -> float:
        """Calculate the time on a hyperbolic orbit at given true anomaly

        Args:
            nu (float): True anomaly [deg]
            h (float): Specific angular momentum [km^2/s]
            e (float): Eccentricity
            attractor (str): Main attractor name

        Returns:
            float: Time [s]
        """
        
        common.check_angle(nu)
        common.check_attractor(attractor)
        
        if e <= 1: raise ValueError("'e' must be greater than 1 for hyperbolic orbits")
        
        body: bodies.Body = bodies.get_body(attractor.lower())
        
        F: float = 2 * np.arctanh(np.sqrt((e - 1) / (e + 1)) * np.tan(np.deg2rad(nu) / 2)) # ? Hyperbolic eccentric anomaly
        
        M_h: float = e * np.sinh(F) - F # ? Mean anomaly
        
        t: float = M_h * h**3 / body.mu.to_value()**2 * (e**2 - 1)**(-3/2)
        
        return t
    
    @staticmethod
    def hyperbolic_orbit_true_anomaly(t: float | int, h: float | int, e: float | int, attractor: str) -> float:
        """Calculate the true anomaly on a hyperbolic orbit at given time

        Args:
            t (float): Time on orbit [s]
            h (float): Specific angular momentum [km^2/s]
            e (float): Eccentricity
            attractor (str): Main attractor name

        Returns:
            float: True anomaly [deg]
        """
        
        common.check_attractor(attractor)
        
        if e <= 1: raise ValueError("'e' must be greater than 1 for hyperbolic orbits")
        
        body: bodies.Body = bodies.get_body(attractor.lower())
        
        M_h: float = t * body.mu.to_value()**2 / h**3 * (e**2 - 1)**(3/2) # ? Mean anomaly
        
        F_0: float = np.arcsinh(M_h / e) # np.log(2 * M_h / e + 1.8) if M_h > 0 else -np.log(-2 * M_h / e + 1.8)
        
        f: callable = lambda F: e * np.sinh(F) - F - M_h
        
        df: callable = lambda F: e * np.cosh(F) - 1
        
        F = optimize.newton(f, x0=F_0, fprime=df, maxiter=100, tol=1e-8) # ? Hyperbolic eccentric anomaly
        
        nu: float = 2 * np.arctan(np.sqrt((e + 1) / (e - 1)) * np.tanh(F / 2))
        
        return common.wrap_angle(np.rad2deg(nu), low=0, high=360)