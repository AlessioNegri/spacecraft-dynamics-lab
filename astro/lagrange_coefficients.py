"""
Lagrange Coefficients

Implements algorithms for orbital propagation using the classical Lagrange f and g coefficients.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 2: The Two-Body Problem
    - Chapter 3: Orbital Position as a Function of Time

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 4: Time of Flight
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.optimize as optimize
import typing

import astro.bodies as bodies
import astro.common as common

class LagrangeCoefficients():
    """Lagrange Coefficients
    """
    
    # --- STATIC ---
    
    @staticmethod
    def propagate_of_angle(attractor: bodies.Attractor,
                           initial_position: u.Quantity,
                           initial_velocity: u.Quantity,
                           delta_true_anomaly: u.Quantity) -> typing.List[u.Quantity]:
        """
        Given initial position and velocity, find position and velocity after true anomaly changes by delta

        Args:
            initial_position (u.Quantity): Initial position vector
            initial_velocity (u.Quantity): Initial velocity vector
            delta_true_anomaly (u.Quantity): True anomaly variation

        Returns:
            list: [Position, Velocity]
        """
        
        r_0: np.ndarray = initial_position.to_value(u.km)
        
        v_0: np.ndarray = initial_velocity.to_value(u.km / u.s)
        
        delta_theta: float = delta_true_anomaly.to_value(u.rad)
        
        common.check_attractor(attractor)
        common.check_position_vector(r_0)
        common.check_velocity_vector(v_0)
        common.check_angle(np.rad2deg(delta_theta))
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2) # ? Gravitational constant [km^3 / s^2]
        
        # >>> 1. Magnitudes
        
        r_0_m: float = np.linalg.norm(r_0)
        v_0_m: float = np.linalg.norm(v_0)
        
        # >>> 2. Radial Velocity
        
        v_r_0: float = np.dot(r_0, v_0) / r_0_m
        
        # >>> 3. Specific Angular momentum
        
        h: float = r_0_m * np.sqrt(v_0_m**2 - v_r_0**2)
        
        # >>> 4. Radius
        
        r: float = h**2 / mu * 1 / ( 1 + ( h**2 / (mu * r_0_m) - 1 ) * np.cos(delta_theta) -\
            h * v_r_0 / mu * np.sin(delta_theta) )
        
        # >>> 5. Lagrange coefficients
        
        f: float = 1 - mu * r / h**2 * (1 - np.cos(delta_theta))
        
        g: float = r * r_0_m / h * np.sin(delta_theta)
        
        df_dt: float = mu / h * (1 - np.cos(delta_theta)) / np.sin(delta_theta) *\
                       (mu / h**2 * (1 - np.cos(delta_theta)) - 1 / r_0_m - 1 / r)
        
        dg_dt: float = 1 - mu * r_0_m / h**2 * (1 - np.cos(delta_theta))
        
        return [(f * r_0 + g * v_0) * u.km, (df_dt * r_0 + dg_dt * v_0) * u.km / u.s]
    
    @staticmethod
    def S(z: float) -> float:
        """
        Stumpff Function S

        Args:
            z (float): Variable

        Returns:
            float: Evaluation
        """
        
        if      z > 0:  return (np.sqrt(z) - np.sin(np.sqrt(z))) / np.sqrt(z)**3
        elif    z < 0:  return (np.sinh(np.sqrt(-z)) - np.sqrt(-z)) / np.sqrt(-z)**3
        else:           return 1/6
    
    @staticmethod
    def C(z: float) -> float:
        """
        Stumpff Function C

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
                                  initial_position: u.Quantity,
                                  initial_radial_velocity: u.Quantity,
                                  alpha: u.Quantity,
                                  delta_time: time.TimeDelta) -> u.Quantity:
        """
        Calculate the universal variable chi solving the universal Kepler equation

        Args:
            attractor (bodies.Attractor): Main attractor
            initial_position (u.Quantity): Initial position
            initial_radial_velocity (u.Quantity): Initial radial velocity
            alpha (u.Quantity): Parameter alpha (reciprocal of the semimajor axis)
            delta_time (time.TimeDelta): Delta time
    
        Returns:
            u.Quantity: Universal variable chi [km^0.5]
        """
        
        r_0: float = initial_position.to_value(u.km)
        
        v_r_0: float = initial_radial_velocity.to_value(u.km / u.s)
        
        dt: float = delta_time.to_value(u.s)
        
        alpha: float = alpha.to_value(1 / u.km)
        
        common.check_attractor(attractor)
        common.check_time_delta(delta_time)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # ? Universal Kepler Equation
        
        f: callable = lambda chi:\
                        r_0 * v_r_0 / np.sqrt(mu) * chi**2 * LagrangeCoefficients.C(alpha * chi**2) +\
                        (1 - alpha * r_0) * chi**3 * LagrangeCoefficients.S(alpha * chi**2) +\
                        r_0 * chi - np.sqrt(mu) * dt
        
        # ? First Derivative Of Universal Kepler Equation
        
        df: callable = lambda chi:\
                            r_0 * v_r_0 / np.sqrt(mu) * chi * (1 - alpha * chi**2 * LagrangeCoefficients.S(alpha * chi**2)) +\
                            (1 - alpha * r_0) * chi**2 * LagrangeCoefficients.C(alpha * chi**2) +\
                            r_0
        
        # ? Result
        
        chi_0: float = np.sqrt(mu) * np.abs(alpha) * dt
        
        return optimize.newton(f, x0=chi_0, fprime=df, maxiter=100, tol=1e-8) * u.km**0.5
    
    @staticmethod
    def lagrange_coefficients(attractor: bodies.Attractor,
                              initial_position: u.Quantity,
                              alpha: u.Quantity,
                              delta_time: time.TimeDelta,
                              universal_anomaly: u.Quantity) -> typing.List[u.Quantity]:
        """
        Calculate the Lagrange coefficients f and g using the universal variable chi

        Args:
            attractor (bodies.Attractor): Main attractor
            initial_position (u.Quantity): Initial position
            alpha (u.Quantity): Parameter alpha (reciprocal of the semimajor axis)
            delta_time (time.TimeDelta): Delta time
            universal_anomaly (u.Quantity): Universal anomaly (chi)

        Returns:
            typing.List[u.Quantity]: [f, g]
        """
        
        r_0: float = initial_position.to_value(u.km)
        
        alpha: float = alpha.to_value(1 / u.km)
        
        dt: float = delta_time.to_value(u.s)
        
        chi: float = universal_anomaly.to_value(u.km**0.5)
        
        common.check_time_delta(delta_time)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        f: float = 1 - chi**2 / r_0 * LagrangeCoefficients.C(alpha * chi**2)
        
        g: float = dt - 1 / np.sqrt(mu) * chi**3 * LagrangeCoefficients.S(alpha * chi**2)
        
        return [f * u.dimensionless_unscaled, g * u.s]
    
    @staticmethod
    def propagate_position_velocity(attractor: bodies.Attractor,
                                    initial_position: u.Quantity,
                                    initial_velocity: u.Quantity,
                                    delta_time: time.TimeDelta) -> typing.List[u.Quantity]:
        """
        Evaluate the position and velocity after delta time from the initial state using the universal variable
        formulation of Lagrange coefficients

        Args:
            initial_position (u.Quantity): Initial position vector
            initial_velocity (u.Quantity): Initial velocity vector
            dt (time.TimeDelta): Time variation

        Returns:
            typing.List[u.Quantity]: [Position, Velocity]
        """
        
        r_0: np.ndarray = initial_position.to_value(u.km)
        
        v_0: np.ndarray = initial_velocity.to_value(u.km / u.s)
        
        dt: float = delta_time.to_value(u.s)
        
        common.check_attractor(attractor)
        common.check_position_vector(r_0)
        common.check_velocity_vector(v_0)
        common.check_time_delta(delta_time)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 1.
        
        # >>> a) Magnitudes
        
        r_0_m: float = np.linalg.norm(r_0)
        v_0_m: float = np.linalg.norm(v_0)
        
        # >>> b) Radial Velocity
        
        v_r_0: float = np.dot(r_0, v_0) / r_0_m
        
        # >>> c) Parameter alpha (reciprocal of the semimajor axis)
        
        alpha: float = 2 / r_0_m - v_0_m**2 / mu
        
        # >>> 2. Universal variable
        
        chi: u.Quantity = LagrangeCoefficients.universal_kepler_solution(attractor=attractor,
                                                                         initial_position=r_0_m * u.km,
                                                                         initial_radial_velocity=v_r_0 * u.km / u.s,
                                                                         alpha=alpha * 1 / u.km,
                                                                         delta_time=delta_time)
        
        chi: float = chi.to_value(u.km**0.5)
        
        z: float = alpha * chi**2
        
        # >>> 3. Lagrange coefficients
        
        f: float = 1 - chi**2 / r_0_m * LagrangeCoefficients.C(z)
        
        g: float = dt - 1 / np.sqrt(mu) * chi**3 * LagrangeCoefficients.S(z)
        
        # >>> 4. Position
        
        r: u.Quantity = (f * r_0 + g * v_0) * u.km
        
        r_m: float = np.linalg.norm(r.to_value(u.km))
        
        # >>> 5. Derivatives of Lagrange coefficients
        
        df_dt: float = np.sqrt(mu) / (r_m * r_0_m) * (alpha * chi**3 * LagrangeCoefficients.S(z) - chi)
        
        dg_dt: float = 1 - chi**2 / r_m * LagrangeCoefficients.C(z)
        
        # >>> 6. Velocity
        
        v: u.Quantity = (df_dt * r_0 + dg_dt * v_0) * u.km / u.s
        
        return [r, v]
