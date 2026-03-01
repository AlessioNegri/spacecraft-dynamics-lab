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
    def propagate_of_angle(attractor: bodies.Attractor, r_0 : u.Quantity, v_0 : u.Quantity, delta : u.Quantity) -> list:
        """Given r_0 and v_0, find r and v after true anomaly changes by delta

        Args:
            r_0 (u.Quantity): Initial position vector
            v_0 (u.Quantity): Initial velocity vector
            delta (u.Quantity): True anomaly variation

        Returns:
            list: [ r, v ]
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(r_0.to_value(u.km))
        common.check_velocity_vector(v_0.to_value(u.km / u.s))
        common.check_angle(delta.to_value(u.deg))
        
        body: bodies.Body = bodies.BODIES[attractor]
        
        mu: float = body.mu.to_value(u.km**3 / u.s**2) # ? Gravitational constant [km^3 / s^2]
        
        # >>> 1. Magnitudes
        
        r_0_m: float = np.linalg.norm(r_0.to_value(u.km))
        v_0_m: float = np.linalg.norm(v_0.to_value(u.km / u.s))
        
        # >>> 2. Radial Velocity
        
        v_r_0: float = np.dot(r_0.to_value(u.km), v_0.to_value(u.km / u.s)) / r_0_m
        
        # >>> 3. Specific Angular momentum
        
        h: float = r_0_m * np.sqrt(v_0_m**2 - v_r_0**2)
        
        # >>> 4. Radius
        
        r: float = h**2 / mu * 1 / ( 1 + ( h**2 / (mu * r_0_m) - 1 ) * np.cos(delta.to_value(u.rad)) -\
                   h * v_r_0 / mu * np.sin(delta.to_value(u.rad)) )
        
        # >>> 5. Lagrange coefficients
        
        f: float = 1 - mu * r / h**2 * (1 - np.cos(delta.to_value(u.rad)))
        
        g: float = r * r_0_m / h * np.sin(delta.to_value(u.rad))
        
        df_dt: float = mu / h * (1 - np.cos(delta.to_value(u.rad))) / np.sin(delta.to_value(u.rad)) *\
                       (mu / h**2 * (1 - np.cos(delta.to_value(u.rad))) - 1 / r_0_m - 1 / r)
        
        dg_dt: float = 1 - mu * r_0_m / h**2 * (1 - np.cos(delta.to_value(u.rad)))
        
        return [(f * r_0.to_value(u.km) + g * v_0.to_value(u.km / u.s)) * u.km,
                (df_dt * r_0.to_value(u.km) + dg_dt * v_0.to_value(u.km / u.s)) * u.km / u.s]
    
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
    def universal_kepler_solution(attractor: bodies.Attractor,
                                  r_0 : u.Quantity,
                                  v_r_0 : u.Quantity,
                                  alpha : float | int,
                                  dt : time.TimeDelta) -> u.Quantity:
        """Calculate the universal variable chi solving the universal Kepler equation

        Args:
            attractor (bodies.Attractor): Main attractor
            r_0 (u.Quantity): Initial distance
            v_r_0 (u.Quantity): Initial radial velocity
            alpha (float | int): Parameter alpha
            dt (time.TimeDelta): Delta time
    
        Returns:
            u.Quantity: Universal variable chi
        """
        
        common.check_attractor(attractor)
        common.check_time_delta(dt)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # ? Universal Kepler Equation
        
        f: callable = lambda chi:\
                        r_0.to_value(u.km) * v_r_0.to_value(u.km / u.s) / np.sqrt(mu) * chi**2 * LagrangeCoefficients.C(alpha * chi**2) +\
                        (1 - alpha * r_0.to_value(u.km)) * chi**3 * LagrangeCoefficients.S(alpha * chi**2) +\
                        r_0.to_value(u.km) * chi - np.sqrt(mu) * dt.to_value(u.s)
        
        # ? First Derivative Of Universal Kepler Equation
        
        df: callable = lambda chi:\
                            r_0.to_value(u.km) * v_r_0.to_value(u.km / u.s) / np.sqrt(mu) * chi * (1 - alpha * chi**2 * LagrangeCoefficients.S(alpha * chi**2)) +\
                            (1 - alpha * r_0.to_value(u.km)) * chi**2 * LagrangeCoefficients.C(alpha * chi**2) +\
                            r_0.to_value(u.km)
        
        # ? Result
        
        chi_0: float = np.sqrt(mu) * np.abs(alpha) * dt.to_value(u.s)
        
        return optimize.newton(f, x0=chi_0, fprime=df, maxiter=100, tol=1e-8) * u.km**0.5
    
    @staticmethod
    def lagrange_coefficients(attractor: bodies.Attractor, r_0 : u.Quantity, alpha : float, dt : time.TimeDelta, chi : float) -> list:
        """Calculates the Lagrange coefficients f and g

        Args:
            attractor (bodies.Attractor): Main attractor
            r_0 (u.Quantity): Initial position
            alpha (float): Parameter alpha
            dt (time.TimeDelta): Delta time
            chi (float): Universal anomaly

        Returns:
            list: [f, g]
        """
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        f: float = 1 - chi**2 / r_0.to_value(u.km) * LagrangeCoefficients.C(alpha * chi**2)
        
        g: float = dt.to_value(u.s) - 1 / np.sqrt(mu) * chi**3 * LagrangeCoefficients.S(alpha * chi**2)
        
        return [f, g]
    
    @staticmethod
    def propagate_position_velocity(attractor: bodies.Attractor, r_0 : u.Quantity, v_0 : u.Quantity, dt : time.TimeDelta) -> list:
        """Evaluates the position and velocity after delta time from the initial state

        Args:
            r_0 (u.Quantity): Initial position vector
            v_0 (u.Quantity): Initial velocity vector
            dt (time.TimeDelta): Time variation

        Returns:
            list: [r, v]
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(r_0.to_value(u.km))
        common.check_velocity_vector(v_0.to_value(u.km / u.s))
        common.check_time_delta(dt)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 1.
        
        # >>> a) Magnitudes
        
        r_0_m: float = np.linalg.norm(r_0.to_value(u.km))
        v_0_m: float = np.linalg.norm(v_0.to_value(u.km / u.s))
        
        # >>> b) Radial Velocity
        
        v_r_0: float = np.dot(r_0.to_value(u.km), v_0.to_value(u.km / u.s)) / r_0_m
        
        # >>> c) Parameter alpha
        
        alpha: float = 2 / r_0_m - v_0_m**2 / mu
        
        # >>> 2. Universal variable
        
        chi: u.Quantity = LagrangeCoefficients.universal_kepler_solution(attractor, r_0_m * u.km, v_r_0 * u.km / u.s, alpha, dt)
        
        z: float = alpha * chi.to_value(u.km**0.5)**2
        
        # >>> 3. Lagrange coefficients
        
        f: float = 1 - chi.to_value(u.km**0.5)**2 / r_0_m * LagrangeCoefficients.C(z)
        
        g: float = dt.to_value(u.s) - 1 / np.sqrt(mu) * chi.to_value(u.km**0.5)**3 * LagrangeCoefficients.S(z)
        
        # >>> 4. Position
        
        r: u.Quantity = (f * r_0.to_value(u.km) + g * v_0.to_value(u.km / u.s)) * u.km
        
        # >>> 5. Derivatives of Lagrange coefficients
        
        df_dt: float = np.sqrt(mu) / (np.linalg.norm(r.to_value(u.km)) * r_0_m) *\
                       (alpha * chi.to_value(u.km**0.5)**3 * LagrangeCoefficients.S(z) - chi.to_value(u.km**0.5))
        
        dg_dt: float = 1 - chi.to_value(u.km**0.5)**2 / np.linalg.norm(r.to_value(u.km)) * LagrangeCoefficients.C(z)
        
        # >>> 6. Velocity
        
        v: u.Quantity = (df_dt * r_0.to_value(u.km) + dg_dt * v_0.to_value(u.km / u.s)) * u.km / u.s
        
        return [r, v]