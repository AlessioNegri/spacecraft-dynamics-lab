"""
Lagrange Coefficients

Implements algorithms for orbital propagation using the classical Lagrange f and g coefficients.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 2: The Two-Body Problem
    - Chapter 3: Orbital Position as a Function of Time
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.optimize as optimize

import astro.bodies as bodies
import astro.common as common

class LagrangeCoefficients():
    """Lagrange Coefficients
    """
    
    def __init__(self):
        """Constructor
        """
        
        pass
    
    # --- STATIC ---
    
    @staticmethod
    def propagate_of_angle(attractor: str, r_0 : np.ndarray, v_0 : np.ndarray, delta : float) -> list:
        """Given r_0 and v_0, find r and v after true anomaly changes by delta

        Args:
            r_0 (np.ndarray): Initial position vector [km]
            v_0 (np.ndarray): Initial velocity vector [km/s]
            delta (float): True anomaly variation [deg]

        Returns:
            list: [ r, v ]
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(r_0)
        common.check_velocity_vector(v_0)
        common.check_angle(delta)
        
        body: bodies.Body = bodies.get_body(attractor.lower())
        
        mu: float = body.mu.to_value() # ? Gravitational constant [km^3 / s^2]
        
        delta = np.deg2rad(delta)
        
        # >>> 1. Magnitudes
        
        r_0_m = np.linalg.norm(r_0)
        v_0_m = np.linalg.norm(v_0)
        
        # >>> 2. Radial Velocity
        
        v_r_0 = np.dot(r_0, v_0) / r_0_m
        
        # >>> 3. Specific Angular momentum
        
        h = r_0_m * np.sqrt(v_0_m**2 - v_r_0**2)
        
        # >>> 4. Radius
        
        r = h**2 / mu * 1 / ( 1 + ( h**2 / (mu * r_0_m) - 1 ) * np.cos(delta) - h * v_r_0 / mu * np.sin(delta) )
        
        # >>> 5. Lagrange coefficients
        
        f = 1 - mu * r / h**2 * (1 - np.cos(delta))
        
        g = r * r_0_m / h * np.sin(delta)
        
        df_dt = mu / h * (1 - np.cos(delta)) / np.sin(delta) * (mu / h**2 * (1 - np.cos(delta)) - 1 / r_0_m - 1 / r)
        
        dg_dt = 1 - mu * r_0_m / h**2 * (1 - np.cos(delta))
        
        return [f * r_0 + g * v_0, df_dt * r_0 + dg_dt * v_0]
    
    @staticmethod
    def S(z : float) -> float:
        """Stumpff Function S

        Args:
            z (float): Variable

        Returns:
            float: Evaluation
        """
        
        if      z > 0:  return (np.sqrt(z) - np.sin(np.sqrt(z))) / np.sqrt(z)**3
        elif    z < 0:  return (np.sinh(np.sqrt(-z)) - np.sqrt(-z)) / np.sqrt(-z)**3
        else:           return 1/6
    
    @staticmethod
    def C(z : float) -> float:
        """Stumpff Function C

        Args:
            z (float): Variable

        Returns:
            float: Evaluation
        """
        
        if      z > 0:  return (1 - np.cos(np.sqrt(z))) / z
        elif    z < 0:  return (np.cosh(np.sqrt(-z)) - 1) / (-z)
        else:           return 1/2
        
    @staticmethod
    def universal_kepler_solution(attractor: str, r_0 : float, v_r_0 : float, alpha : float, dt : time.TimeDelta) -> float:
        """Calculate the universal variable chi solving the universal Kepler equation

        Args:
            attractor (str): Main attractor name
            r_0 (float): Initial distance
            v_r_0 (float): Initial radial velocity
            alpha (float): Parameter alpha
            dt (time.TimeDelta): Delta time
    
        Returns:
            float: Universal variable chi
        """
        
        common.check_attractor(attractor)
        common.check_time_delta(dt)
        
        mu: float = bodies.get_body(attractor.lower()).mu.to_value() # ? Gravitational constant [km^3 / s^2]
        
        # ? Universal Kepler Equation
        
        f: callable = lambda chi:\
                        r_0 * v_r_0 / np.sqrt(mu) * chi**2 * LagrangeCoefficients.C(alpha * chi**2) +\
                        (1 - alpha * r_0) * chi**3 * LagrangeCoefficients.S(alpha * chi**2) +\
                        r_0 * chi - np.sqrt(mu) * dt.to(u.s).to_value()
        
        # ? First Derivative Of Universal Kepler Equation
        
        df: callable = lambda chi:\
                            r_0 * v_r_0 / np.sqrt(mu) * chi * (1 - alpha * chi**2 * LagrangeCoefficients.S(alpha * chi**2)) +\
                            (1 - alpha * r_0) * chi**2 * LagrangeCoefficients.C(alpha * chi**2) +\
                            r_0
        
        # ? Result
        
        chi_0: float = np.sqrt(mu) * np.abs(alpha) * dt.to(u.s).to_value()
        
        return optimize.newton(f, x0=chi_0, fprime=df, maxiter=100, tol=1e-8)
    
    @staticmethod
    def lagrange_coefficients(attractor: str, r_0 : float, alpha : float, dt : time.TimeDelta, chi : float) -> list:
        """Calculates the Lagrange coefficients f and g

        Args:
            attractor (str): Main attractor name
            r_0 (float): Initial position
            alpha (float): Parameter alpha
            dt (time.TimeDelta): Delta time
            chi (float): Universal anomaly

        Returns:
            list: [f, g]
        """
        
        mu: float = bodies.get_body(attractor.lower()).mu.to_value()
        
        f = 1 - chi**2 / r_0 * LagrangeCoefficients.C(alpha * chi**2)
        
        g = dt.to(u.s).to_value() - 1 / np.sqrt(mu) * chi**3 * LagrangeCoefficients.S(alpha * chi**2)
        
        return [f, g]
    
    @staticmethod
    def propagate_position_velocity(attractor: str, r_0 : np.ndarray, v_0 : np.ndarray, dt : time.TimeDelta) -> list:
        """Evaluates the position and velocity after delta time from the initial state

        Args:
            r_0 (np.ndarray): Initial position vector
            v_0 (np.ndarray): Initial velocity vector
            dt (time.TimeDelta): Time variation

        Returns:
            list: [r, v]
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(r_0)
        common.check_velocity_vector(v_0)
        common.check_time_delta(dt)
        
        mu: float = bodies.get_body(attractor.lower()).mu.to_value()
        
        # >>> 1.
        
        # >>> a) Magnitudes
        
        r_0_m = np.linalg.norm(r_0)
        v_0_m = np.linalg.norm(v_0)
        
        # >>> b) Radial Velocity
        
        v_r_0 = np.dot(r_0, v_0) / r_0_m
        
        # >>> c) Parameter alpha
        
        alpha = 2 / r_0_m - v_0_m**2 / mu
        
        # >>> 2. Universal variable
        
        chi = LagrangeCoefficients.universal_kepler_solution(attractor, r_0_m, v_r_0, alpha, dt)
        
        z = alpha * chi**2
        
        # >>> 3. Lagrange coefficients
        
        f = 1 - chi**2 / r_0_m * LagrangeCoefficients.C(z)
        
        g = dt.to(u.s).to_value() - 1 / np.sqrt(mu) * chi**3 * LagrangeCoefficients.S(z)
        
        # >>> 4. Position
        
        r = f * r_0 + g * v_0
        
        # >>> 5. Derivatives of Lagrange coefficients
        
        df_dt = np.sqrt(mu) / (np.linalg.norm(r) * r_0_m) * (alpha * chi**3 * LagrangeCoefficients.S(z) - chi)
        
        dg_dt = 1 - chi**2 / np.linalg.norm(r) * LagrangeCoefficients.C(z)
        
        # >>> 6. Velocity
        
        v = df_dt * r_0 + dg_dt * v_0
        
        return [r, v]