"""
Two Body Problem

Implements core algorithms for solving the classical two-body problem,
including orbital geometry, conic classification, and the fundamental
relationships between position, velocity, and orbital elements.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 2: The Two-Body Problem
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as time
import astropy.units as u
import dataclasses
import numpy as np
import scipy.integrate as ode

import astro.bodies as bodies
import astro.common as common

class Result:
    """Result of integration
    """
    
    success: bool
    t: np.ndarray
    r_x: np.ndarray
    r_y: np.ndarray
    r_z: np.ndarray
    v_x: np.ndarray
    v_y: np.ndarray
    v_z: np.ndarray
    
@dataclasses.dataclass
class OrbitParameters:
    """Orbit parameters based on orbit geometry (circular - elliptical - parabolic - hyperbolic)
    """
    
    conic_type  : str   = "" # ? Type of conic section
    h           : float = 0.0 # ? Specific Angular Momentum     [ km^2 / s ]
    epsilon     : float = 0.0 # ? Specific Mechanical Energy    [ km^2 / s^2 ]
    e           : float = 0.0 # ? Eccentricity                  [ ]
    T           : float = 0.0 # ? Orbital Period                [ s ]
    r_a         : float = 0.0 # ? Apoapsis Radius               [ km ]
    r_p         : float = 0.0 # ? Periapsis Radius              [ km ]
    a           : float = 0.0 # ? Semi-Major Axis               [ km ]
    b           : float = 0.0 # ? Semi-Minor Axis               [ km ]
    v_esc       : float = 0.0 # ? Escape Velocity               [ km / s ]
    theta_inf   : float = 0.0 # ? Infinite True Anomaly         [ deg ]
    beta        : float = 0.0 # ? Hyperbola Asymptote Angle     [ deg ]
    delta_ta    : float = 0.0 # ? Turn Angle                    [ deg ]
    delta_ar    : float = 0.0 # ? Aiming Radius                 [ km ]
    v_inf       : float = 0.0 # ? Hyperbolic Excess Speed       [ km / s ]
    C_3         : float = 0.0 # ? Characteristic Energy         [ km^2 / s^2 ]

class Orbit:
    """Generic orbit in 2 Body Problem
    """
    
    def __init__(self):
        """Constructor
        """
        
        self.ready      : bool = False
        self.attractor  : bodies.Body = bodies.get_body("earth")
        self.a          : float = 0.0
        self.ecc        : float = 0.0
        self.inc        : float = 0.0
        self.raan       : float = 0.0
        self.argp       : float = 0.0
        self.nu         : float = 0.0
        self.r          : np.ndarray = np.zeros(3)
        self.v          : np.ndarray = np.zeros(3)
        self.epoch      : time.Time = time.Time('1970-01-01T00:00:00', format='isot', scale='utc')
    
    # --- STATIC ---
    
    @staticmethod
    def cartesian_to_orbit_parameter(attractor: str, r: np.ndarray, v: np.ndarray) -> OrbitParameters:
        """Convert the given cartesian parameters in orbit ones

        Args:
            r (np.ndarray): Position vector [km]
            v (np.ndarray): Velocity vector [km/s]

        Returns:
            OrbitParameters: Orbit parameters
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(r)
        common.check_velocity_vector(v)
        
        attractor: bodies.Body = bodies.get_body(attractor.lower())
        
        mu: float = attractor.mu.to_value() # ? Gravitational constant [km^3 / s^2]

        parameters: OrbitParameters = OrbitParameters()
        
        # >>> Angular Momentum
        
        h: np.ndarray = np.cross(r, v)
        
        parameters.h = float(np.linalg.norm(h))
        
        # >>> Energy
        
        parameters.epsilon = float(np.linalg.norm(v)**2 / 2 - mu / np.linalg.norm(r))
        
        # >>> Eccentricity
        
        parameters.e = float(np.sqrt((2 * np.linalg.norm(h)**2 * parameters.epsilon) / (mu **2) + 1))
        
        if parameters.h == 0:
            
            parameters.conic_type = "line"
            
            return parameters
        
        # >>> Select Orbit Type
        
        # * Circular Orbit
        if parameters.e == 0:
            
            parameters.conic_type   = "circle"
            parameters.r_p          = float(np.linalg.norm(r))
            parameters.r_a          = float(np.linalg.norm(r))
            parameters.a            = float(np.linalg.norm(r))
            parameters.b            = float(np.linalg.norm(r))
            parameters.T            = float((2 * np.pi) /  np.sqrt(mu) * np.linalg.norm(r) ** (3 / 2))
        
        # * Elliptical Orbit
        elif parameters.e > 0 and parameters.e < 1:
            
            parameters.conic_type   = "ellipse"
            parameters.r_p          = float(parameters.h ** 2 / mu * 1 / (1 + parameters.e))
            parameters.r_a          = float(parameters.h ** 2 / mu * 1 / (1 - parameters.e))
            parameters.a            = float((parameters.r_p + parameters.r_a) / 2)
            parameters.b            = float(parameters.a * np.sqrt(1 - parameters.e ** 2))
            parameters.T            = float((2 * np.pi) /  np.sqrt(mu) * parameters.a ** (3 / 2))
        
        # * Parabolic Orbit
        elif parameters.e == 1:
            
            parameters.conic_type   = "parabola"
            parameters.r_p          = float(parameters.h ** 2 / mu * 1 / (1 + 1))
            parameters.r_a          = float(-1)
            parameters.a            = float(-1)
            parameters.b            = float(0)
            parameters.T            = float(-1)
            parameters.v_esc        = float(np.sqrt(2 * mu / parameters.r_p))
        
        # * Hyperbolic Orbit
        elif parameters.e > 1:
            
            parameters.conic_type   = "hyperbola"
            parameters.r_p          = float(parameters.h ** 2 / mu * 1 / (1 + parameters.e))
            parameters.r_a          = float(parameters.h ** 2 / mu * 1 / (1 - parameters.e))
            parameters.a            = float((np.abs(parameters.r_a) - parameters.r_p) / 2)
            parameters.b            = float(parameters.a * np.sqrt(parameters.e ** 2 - 1))
            parameters.T            = float(-1)
            parameters.v_esc        = float(np.sqrt(2 * mu  / parameters.r_p))
            parameters.theta_inf    = float(np.rad2deg(np.arccos(-1 / parameters.e)))
            parameters.beta         = float(np.rad2deg(np.arccos(1 / parameters.e)))
            parameters.delta_ta     = float(np.rad2deg(2 * np.arcsin(1 / parameters.e)))
            parameters.delta_ar     = float(parameters.a * np.sqrt(parameters.e ** 2 - 1))
            parameters.v_inf        = float(np.sqrt(mu / parameters.a))
            parameters.C_3          = float(parameters.v_inf ** 2)
        
        # NOTE -1 is np.inf
        
        return parameters
    
    # --- PUBLIC ---
    
    def from_cartesian(self, attractor: str, r: np.ndarray, v: np.ndarray, epoch: time.Time) -> None:
        """Initialize the orbit based on cartesian orbit parameters

        Args:
            attractor (str): Main attractor name
            r (np.ndarray): Position vector [km]
            v (np.ndarray): Velocity vector [km/s]
            epoch (time.Time): Epoch of orbit position
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(r)
        common.check_velocity_vector(v)
        common.check_time(epoch)
        
        self.ready      = True
        self.attractor  = bodies.get_body(attractor.lower())
        self.r          = r
        self.v          = v
        self.epoch      = epoch
    
    def from_keplerian(self, attractor: str, a: float, ecc: float, inc: float, raan: float, argp: float, nu: float, epoch: time.Time) -> None:
        """Initialize the orbit based on keplerian orbit parameters

        Args:
            attractor (str): Main attractor name
            a (float): Semi-major axis [km]
            ecc (float): Eccentricity
            inc (float): Inclination [deg]
            raan (float): Right Ascension of the Ascending Node [deg]
            argp (float): Argumento of Periapsis [deg]
            nu (float): True anomaly [deg]
            epoch (time.Time): Epoch of orbit position
        """
        
        common.check_attractor(attractor)
        common.check_time(epoch)
        common.check_keplerian_parameters(a, ecc, inc, raan, argp, nu)
        
        self.ready      = True
        self.attractor  = bodies.get_body(attractor)
        self.a          = a
        self.ecc        = ecc
        self.inc        = inc
        self.raan       = raan
        self.argp       = argp
        self.nu         = nu
        self.epoch      = epoch
        
    def propagate_until(self, end_epoch: time.Time) -> Result:
        """Propagate the orbit until end_epoch

        Args:
            end_epoch (time.Time): End epoch for propagation

        Returns:
            Result: Integration result
        """
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        common.check_time(end_epoch)
        
        if end_epoch < self.epoch: raise TypeError(f"'end_epoch' {end_epoch} must come after 'epoch' {self.epoch}")
        
        solution: dict = ode.solve_ivp(fun=self._equations_relative_motion,
                                       t_span=[0, (end_epoch - self.epoch).to(u.s).to_value()],
                                       y0=np.concat([self.r, self.v]),
                                       method='RK45',
                                       args=(),
                                       rtol=1e-8,
                                       atol=1e-8)
        
        result: Result = Result()
        
        result.success = solution['success']
        result.t = solution['t']
        result.r_x = solution['y'][0, :]
        result.r_y = solution['y'][1, :]
        result.r_z = solution['y'][2, :]
        result.v_x = solution['y'][3, :]
        result.v_y = solution['y'][4, :]
        result.v_z = solution['y'][5, :]
        
        return result
    
    def propagate_for(self, delta: time.TimeDelta) -> Result:
        """Propagate the orbit for delta time

        Args:
            delta (time.TimeDelta): Delta time for propagation

        Returns:
            Result: Integration result
        """
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        common.check_time_delta(delta)
        
        solution: dict = ode.solve_ivp(fun=self._equations_relative_motion,
                                       t_span=[0, delta.to(u.s).to_value()],
                                       y0=np.concat([self.r, self.v]),
                                       method='RK45',
                                       args=(),
                                       rtol=1e-8,
                                       atol=1e-8)
        
        result: Result = Result()
        
        result.success = solution['success']
        result.t = solution['t']
        result.r_x = solution['y'][0, :]
        result.r_y = solution['y'][1, :]
        result.r_z = solution['y'][2, :]
        result.v_x = solution['y'][3, :]
        result.v_y = solution['y'][4, :]
        result.v_z = solution['y'][5, :]
        
        return result
        
    # --- PRIVATE ---
    
    def _equations_relative_motion(self, t : float, X : np.ndarray) -> np.ndarray:
        """Equations of relative motion

        Args:
            t (float): Time
            X (np.ndarray): State [6,1]

        Returns:
            np.ndarray: Derivative of state
        """
        
        x, y, z, v_x, v_y, v_z = X
        
        r: float = np.sqrt(x**2 + y**2 + z**2)
        
        dx_dt: np.ndarray = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = - (self.attractor.mu.to_value() / r**3) * x
        dx_dt[4] = - (self.attractor.mu.to_value() / r**3) * y
        dx_dt[5] = - (self.attractor.mu.to_value() / r**3) * z
        
        return dx_dt