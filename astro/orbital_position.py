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

import astropy.units as u
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
    def circular_orbit_time(nu: u.Quantity, T: u.Quantity) -> u.Quantity:
        """Calculate the time on a circular orbit at given true anomaly

        Args:
            nu (u.Quantity): True anomaly
            T (u.Quantity): Period

        Returns:
            u.Quantity: Time
        """
        
        common.check_angle(nu.to_value(u.deg))
        
        t: float = nu.to_value(u.rad) / (2 * np.pi) * T.to_value(u.s)
        
        return t * u.s
    
    @staticmethod
    def circular_orbit_true_anomaly(t: u.Quantity, T: u.Quantity) -> u.Quantity:
        """Calculate the true anomaly on a circular orbit at given time

        Args:
            t (u.Quantity): Time on orbit
            T (u.Quantity): Period

        Returns:
            u.Quantity: True anomaly
        """
        
        nu: float = np.rad2deg((2 * np.pi / T.to_value(u.s)) * t.to_value(u.s))
        
        return common.wrap_angle(nu, low=0, high=360) * u.deg
    
    @staticmethod
    def elliptical_orbit_time(nu: u.Quantity, T: u.Quantity, e: float | int) -> u.Quantity:
        """Calculate the time on an elliptical orbit at given true anomaly

        Args:
            nu (u.Quantity): True anomaly
            T (u.Quantity): Period
            e (float): Eccentricity

        Returns:
            u.Quantity: Time
        """
        
        common.check_angle(nu.to_value(u.deg))
        
        E: float = 2 * np.arctan(np.sqrt((1 - e) / (1 + e)) * np.tan(nu.to_value(u.rad) / 2))
        
        M_e: float = E - e * np.sin(E) # ? Mean anomaly
        
        t: float = M_e / (2 * np.pi) * T.to_value(u.s)
        
        return t * u.s
    
    @staticmethod
    def elliptical_orbit_true_anomaly(t: u.Quantity, T: u.Quantity, e: float | int) -> u.Quantity:
        """Calculate the true anomaly on an elliptical orbit at given time

        Args:
            t (u.Quantity): Time on orbit
            T (u.Quantity): Period
            e (float): Eccentricity

        Returns:
            u.Quantity: True anomaly
        """
        
        M_e: float = (2 * np.pi / T.to_value(u.s)) * t.to_value(u.s) # ? Mean anomaly
        
        f: callable = lambda E: E - e * np.sin(E) - M_e
        
        df: callable = lambda E: 1 - e * np.cos(E)
        
        E_0: float = (M_e + 0.5 * e) if M_e < np.pi else (M_e - 0.5 * e)
        
        E = optimize.newton(f, x0=E_0, fprime=df, maxiter=100, tol=1e-8) # ? Eccentric anomaly
        
        nu: float = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))
        
        return common.wrap_angle(np.rad2deg(nu), low=0, high=360) * u.deg
    
    @staticmethod
    def parabolic_orbit_time(nu: u.Quantity, h: u.Quantity, attractor: bodies.Attractor) -> u.Quantity:
        """Calculate the time on a parabolic orbit at given true anomaly

        Args:
            nu (u.Quantity): True anomaly
            h (u.Quantity): Specific angular momentum
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: Time
        """
        
        common.check_angle(nu.to_value(u.deg))
        common.check_attractor(attractor)
        
        body: bodies.Body = bodies.BODIES[attractor]
        
        D: float = np.tan(nu.to_value(u.rad) / 2) # ? Parabolic eccentric anomaly
        
        M_p: float = 1/2 * D + 1/6 * D**3 # ? Mean anomaly
        
        t: float = M_p * h.to_value(u.km**2 / u.s)**3 / body.mu.to_value(u.km**3 / u.s**2)**2
        
        return t * u.s
    
    @staticmethod
    def parabolic_orbit_true_anomaly(t: u.Quantity, h: u.Quantity, attractor: bodies.Attractor) -> u.Quantity:
        """Calculate the true anomaly on a parabolic orbit at given time

        Args:
            t (u.Quantity): Time on orbit
            h (u.Quantity): Specific angular momentum
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: True anomaly
        """
        
        common.check_attractor(attractor)
        
        body: bodies.Body = bodies.BODIES[attractor]
        
        M_p: float = t.to_value(u.s) * body.mu.to_value(u.km**3 / u.s**2)**2 / h.to_value(u.km**2 / u.s)**3 # ? Mean anomaly
        
        nu: float = 2 * np.arctan( (3 * M_p + np.sqrt((3 * M_p)**2 + 1))**(1/3) - (3 * M_p + np.sqrt((3 * M_p)**2 + 1))**(-1/3) )
        
        return common.wrap_angle(np.rad2deg(nu), low=0, high=360) * u.deg
    
    @staticmethod
    def hyperbolic_orbit_time(nu:  u.Quantity, h: u.Quantity, e: float | int, attractor: bodies.Attractor) -> u.Quantity:
        """Calculate the time on a hyperbolic orbit at given true anomaly

        Args:
            nu (u.Quantity): True anomaly
            h (u.Quantity): Specific angular momentum
            e (float | int): Eccentricity
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: Time
        """
        
        common.check_angle(nu.to_value(u.deg))
        common.check_attractor(attractor)
        
        if e <= 1: raise ValueError("'e' must be greater than 1 for hyperbolic orbits")
        
        body: bodies.Body = bodies.BODIES[attractor]
        
        F: float = 2 * np.arctanh(np.sqrt((e - 1) / (e + 1)) * np.tan(nu.to_value(u.rad) / 2)) # ? Hyperbolic eccentric anomaly
        
        M_h: float = e * np.sinh(F) - F # ? Mean anomaly
        
        t: float = M_h * h.to_value(u.km**2 / u.s)**3 / body.mu.to_value(u.km**3 / u.s**2)**2 * (e**2 - 1)**(-3/2)
        
        return t * u.s
    
    @staticmethod
    def hyperbolic_orbit_true_anomaly(t: u.Quantity, h: u.Quantity, e: float | int, attractor: bodies.Attractor) -> u.Quantity:
        """Calculate the true anomaly on a hyperbolic orbit at given time

        Args:
            t (u.Quantity): Time on orbit
            h (u.Quantity): Specific angular momentum
            e (float | int): Eccentricity
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: True anomaly
        """
        
        common.check_attractor(attractor)
        
        if e <= 1: raise ValueError("'e' must be greater than 1 for hyperbolic orbits")
        
        body: bodies.Body = bodies.BODIES[attractor]
        
        M_h: float = t.to_value(u.s) * body.mu.to_value(u.km**3 / u.s**2)**2 / h.to_value(u.km**2 / u.s)**3 * (e**2 - 1)**(3/2) # ? Mean anomaly
        
        F_0: float = np.arcsinh(M_h / e) # np.log(2 * M_h / e + 1.8) if M_h > 0 else -np.log(-2 * M_h / e + 1.8)
        
        f: callable = lambda F: e * np.sinh(F) - F - M_h
        
        df: callable = lambda F: e * np.cosh(F) - 1
        
        F = optimize.newton(f, x0=F_0, fprime=df, maxiter=100, tol=1e-8) # ? Hyperbolic eccentric anomaly
        
        nu: float = 2 * np.arctan(np.sqrt((e + 1) / (e - 1)) * np.tanh(F / 2))
        
        return common.wrap_angle(np.rad2deg(nu), low=0, high=360) * u.deg