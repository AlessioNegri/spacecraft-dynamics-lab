"""
Two Body Problem

Implements core algorithms for solving the classical two-body problem,
including orbital geometry, conic classification, and the fundamental
relationships between position, velocity, and orbital elements.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 2: The Two-Body Problem
    - Chapter 6: Orbital Maneuvers
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as time
import astropy.units as u
import dataclasses
import numpy as np
import scipy.integrate as ode
import typing

import astro.bodies as bodies
import astro.common as common
import astro.orbital_maneuvers as om

class Result:
    """Result of integration
    """
    
    success: bool
    t: u.Quantity
    r_x: u.Quantity
    r_y: u.Quantity
    r_z: u.Quantity
    v_x: u.Quantity
    v_y: u.Quantity
    v_z: u.Quantity
    m_sc: u.Quantity
    
@dataclasses.dataclass
class OrbitParameters:
    """Orbit parameters based on orbit geometry (linear - circular - elliptical - parabolic - hyperbolic)
    """
    
    conic_type  : str = ""                              # ? Type of conic section
    h           : u.Quantity = 0.0 * u.km**2 / u.s      # ? Specific Angular Momentum
    epsilon     : u.Quantity = 0.0 * u.km**2 / u.s**2   # ? Specific Mechanical Energy
    e           : float = 0.0                           # ? Eccentricity
    T           : u.Quantity = 0.0 * u.s                # ? Orbital Period
    r_a         : u.Quantity = 0.0 * u.km               # ? Apoapsis Radius
    r_p         : u.Quantity = 0.0 * u.km               # ? Periapsis Radius
    a           : u.Quantity = 0.0 * u.km               # ? Semi-Major Axis
    b           : u.Quantity = 0.0 * u.km               # ? Semi-Minor Axis
    v_esc       : u.Quantity = 0.0 * u.km / u.s         # ? Escape Velocity
    theta_inf   : u.Quantity = 0.0 * u.deg              # ? Infinite True Anomaly
    beta        : u.Quantity = 0.0 * u.deg              # ? Hyperbola Asymptote Angle
    delta_ta    : u.Quantity = 0.0 * u.deg              # ? Turn Angle
    delta_ar    : u.Quantity = 0.0 * u.km               # ? Aiming Radius
    v_inf       : u.Quantity = 0.0 * u.km / u.s         # ? Hyperbolic Excess Speed
    C_3         : u.Quantity = 0.0 * u.km**2 / u.s**2   # ? Characteristic Energy

class Orbit:
    """Generic orbit in 2 Body Problem
    """
    
    def __init__(self):
        """Constructor
        """
        
        self.ready      : bool = False
        self.attractor  : bodies.Body = bodies.get_body(bodies.Attractor.EARTH)
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
    def cartesian_to_orbit_parameters(attractor: bodies.Attractor, r: u.Quantity, v: u.Quantity) -> OrbitParameters:
        """Convert the given cartesian parameters in orbit ones

        Args:
            attractor (bodies.Attractor): Main attractor
            r (u.Quantity): Position vector
            v (u.Quantity): Velocity vector

        Returns:
            OrbitParameters: Orbit parameters
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(r.to_value(u.km))
        common.check_velocity_vector(v.to_value(u.km / u.s))
        
        r: np.ndarray = typing.cast(np.ndarray, r.to(u.km).to_value())
        v: np.ndarray = typing.cast(np.ndarray, v.to(u.km / u.s).to_value())
        
        body: bodies.Body = bodies.BODIES[attractor]
        
        mu: float = body.mu.to(u.km**3 / u.s**2).to_value()

        parameters: OrbitParameters = OrbitParameters()
        
        # >>> Angular Momentum
        
        h: np.ndarray = np.cross(r, v)
        
        h_m: float = float(np.linalg.norm(h))
        
        parameters.h = h_m * u.km**2 / u.s
        
        # >>> Energy
        
        epsilon: float = float(np.linalg.norm(v)**2 / 2 - mu / np.linalg.norm(r))
        
        parameters.epsilon = epsilon * u.km**2 / u.s**2
        
        # >>> Eccentricity
        
        e: float = float(np.sqrt((2 * np.linalg.norm(h)**2 * epsilon) / (mu **2) + 1))
        
        parameters.e = e
        
        if parameters.h.to_value() == 0:
            
            parameters.conic_type = "line"
            
            return parameters
        
        # >>> Select Orbit Type
        
        # * Circular Orbit
        if parameters.e == 0:
            
            parameters.conic_type   = "circle"
            parameters.r_p          = float(np.linalg.norm(r)) * u.km
            parameters.r_a          = float(np.linalg.norm(r)) * u.km
            parameters.a            = float(np.linalg.norm(r)) * u.km
            parameters.b            = float(np.linalg.norm(r)) * u.km
            parameters.T            = float((2 * np.pi) /  np.sqrt(mu) * np.linalg.norm(r) ** (3 / 2)) * u.s
        
        # * Elliptical Orbit
        elif parameters.e > 0 and parameters.e < 1:
            
            parameters.conic_type   = "ellipse"
            parameters.r_p          = float(h_m ** 2 / mu * 1 / (1 + e)) * u.km
            parameters.r_a          = float(h_m ** 2 / mu * 1 / (1 - e)) * u.km
            parameters.a            = float((parameters.r_p.to_value() + parameters.r_a.to_value()) / 2) * u.km
            parameters.b            = float(parameters.a.to_value() * np.sqrt(1 - e ** 2)) * u.km
            parameters.T            = float((2 * np.pi) /  np.sqrt(mu) * parameters.a.to_value() ** (3 / 2)) * u.s
        
        # * Parabolic Orbit
        elif parameters.e == 1:
            
            parameters.conic_type   = "parabola"
            parameters.r_p          = float(h_m ** 2 / mu * 1 / (1 + 1)) * u.km
            parameters.r_a          = float(-1) * u.km
            parameters.a            = float(-1) * u.km
            parameters.b            = float(0) * u.km
            parameters.T            = float(-1) * u.s
            parameters.v_esc        = float(np.sqrt(2 * mu / parameters.r_p.to_value())) * u.km / u.s
        
        # * Hyperbolic Orbit
        elif parameters.e > 1:
            
            parameters.conic_type   = "hyperbola"
            parameters.r_p          = float(h_m ** 2 / mu * 1 / (1 + e)) * u.km
            parameters.r_a          = float(h_m ** 2 / mu * 1 / (1 - e)) * u.km
            parameters.a            = float((np.abs(parameters.r_a.to_value()) - parameters.r_p.to_value()) / 2) * u.km
            parameters.b            = float(parameters.a.to_value() * np.sqrt(e ** 2 - 1)) * u.km
            parameters.T            = float(-1) * u.s
            parameters.v_esc        = float(np.sqrt(2 * mu  / parameters.r_p.to_value())) * u.km / u.s
            parameters.theta_inf    = float(np.rad2deg(np.arccos(-1 / e))) * u.deg
            parameters.beta         = float(np.rad2deg(np.arccos(1 / e))) * u.deg
            parameters.delta_ta     = float(np.rad2deg(2 * np.arcsin(1 / e))) * u.deg
            parameters.delta_ar     = float(parameters.a.to_value() * np.sqrt(e ** 2 - 1)) * u.km
            parameters.v_inf        = float(np.sqrt(mu / parameters.a.to_value())) * u.km / u.s
            parameters.C_3          = float(parameters.v_inf.to_value() ** 2) * u.km**2 / u.s**2
        
        # NOTE -1 is np.inf
        
        return parameters
    
    # --- PUBLIC ---
    
    def from_cartesian(self,
                       attractor: bodies.Attractor,
                       r: u.Quantity,
                       v: u.Quantity,
                       epoch: time.Time = time.Time(0, format="unix", scale="utc")) -> None:
        """Initialize the orbit based on cartesian orbit parameters

        Args:
            attractor (bodies.Attractor): Main attractor
            r (u.Quantity): Position vector
            v (u.Quantity): Velocity vector
            epoch (time.Time, optional): Epoch of orbit position. Defaults to 0.
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(r.to_value(u.km))
        common.check_velocity_vector(v.to_value(u.km / u.s))
        common.check_time(epoch)
        
        self.ready      = True
        self.attractor  = bodies.BODIES[attractor]
        self.r          = r.to(u.km).to_value()
        self.v          = v.to(u.km / u.s).to_value()
        self.epoch      = epoch
    
    def from_keplerian(self,
                       attractor: bodies.Attractor,
                       a: u.Quantity,
                       ecc: float | int,
                       inc: u.Quantity,
                       raan: u.Quantity,
                       argp: u.Quantity,
                       nu: u.Quantity,
                       epoch: time.Time = time.Time(0, format="unix", scale="utc")) -> None:
        """Initialize the orbit based on keplerian orbit parameters

        Args:
            attractor (bodies.Attractor): Main attractor
            a (u.Quantity): Semi-major axis
            ecc (u.Quantity): Eccentricity
            inc (u.Quantity): Inclination
            raan (u.Quantity): Right Ascension of the Ascending Node
            argp (u.Quantity): Argumento of Periapsis
            nu (u.Quantity): True anomaly
            epoch (time.Time, optional): Epoch of orbit position. Defaults to 0.
        """
        
        common.check_attractor(attractor)
        common.check_keplerian_parameters(a.to_value(u.km),
                                          ecc,
                                          inc.to_value(u.deg),
                                          raan.to_value(u.deg),
                                          argp.to_value(u.deg),
                                          nu.to_value(u.deg))
        common.check_time(epoch)
        
        self.ready      = True
        self.attractor  = bodies.BODIES[attractor]
        self.a          = a.to_value(u.km)
        self.ecc        = ecc
        self.inc        = inc.to_value(u.deg)
        self.raan       = raan.to_value(u.deg)
        self.argp       = argp.to_value(u.deg)
        self.nu         = nu.to_value(u.deg)
        self.epoch      = epoch
        
    def propagate_until(self, end_epoch: time.Time, rocket_motor: om.RocketMotor = None) -> Result:
        """Propagate the orbit until end_epoch

        Args:
            end_epoch (time.Time): End epoch for propagation
            rocket_motor (om.RocketMotor, optional): Rocket motor for thrust. Defaults to None.

        Returns:
            Result: Integration result
        """
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        common.check_time(end_epoch)
        
        if end_epoch < self.epoch: raise TypeError(f"'end_epoch' {end_epoch} must come after 'epoch' {self.epoch}")
        
        result: Result = Result()
        
        if rocket_motor == None:
        
            solution: dict = ode.solve_ivp(fun=self._equations_relative_motion,
                                           t_span=[0, (end_epoch - self.epoch).to(u.s).to_value()],
                                           y0=np.concat([self.r, self.v]),
                                           method='RK45',
                                           args=(),
                                           rtol=1e-8,
                                           atol=1e-8)
            
            
            
            result.success = solution['success']
            result.t = solution['t'] * u.s
            result.r_x = solution['y'][0, :] * u.km
            result.r_y = solution['y'][1, :] * u.km
            result.r_z = solution['y'][2, :] * u.km
            result.v_x = solution['y'][3, :] * u.km / u.s
            result.v_y = solution['y'][4, :] * u.km / u.s
            result.v_z = solution['y'][5, :] * u.km / u.s
            
        else:
            
            if rocket_motor.T.to_value(u.N) <= 0:
                
                raise ValueError("Rocket motor thrust must be greater than 0")
            
            if rocket_motor.I_sp.to_value(u.s) <= 0:
                
                raise ValueError("Rocket motor specific impulse must be greater than 0")
            
            solution: dict = ode.solve_ivp(fun=self._equations_relative_motion_with_thrust,
                                           t_span=[0, (end_epoch - self.epoch).to(u.s).to_value()],
                                           y0=np.concat([self.r, self.v, rocket_motor.m_sc.to_value(u.kg)]),
                                           method='RK45',
                                           args=(rocket_motor.T.to_value(u.N) * 1e-3, rocket_motor.I_sp.to_value(u.s)),
                                           rtol=1e-8,
                                           atol=1e-8)
            
            result.success = solution['success']
            result.t = solution['t'] * u.s
            result.r_x = solution['y'][0, :] * u.km
            result.r_y = solution['y'][1, :] * u.km
            result.r_z = solution['y'][2, :] * u.km
            result.v_x = solution['y'][3, :] * u.km / u.s
            result.v_y = solution['y'][4, :] * u.km / u.s
            result.v_z = solution['y'][5, :] * u.km / u.s
            result.m_sc = solution['y'][6, :] * u.kg
        
        return result
    
    def propagate_for(self, delta: time.TimeDelta, rocket_motor: om.RocketMotor = None) -> Result:
        """Propagate the orbit for delta time

        Args:
            delta (time.TimeDelta): Delta time for propagation
            rocket_motor (om.RocketMotor, optional): Rocket motor for thrust. Defaults to None.

        Returns:
            Result: Integration result
        """
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        common.check_time_delta(delta)
        
        result: Result = Result()
        
        if rocket_motor == None:
        
            solution: dict = ode.solve_ivp(fun=self._equations_relative_motion,
                                           t_span=[0, delta.to(u.s).to_value()],
                                           y0=np.concat([self.r, self.v]),
                                           method='RK45',
                                           args=(),
                                           rtol=1e-8,
                                           atol=1e-8)
            
            result.success = solution['success']
            result.t = solution['t'] * u.s
            result.r_x = solution['y'][0, :] * u.km
            result.r_y = solution['y'][1, :] * u.km
            result.r_z = solution['y'][2, :] * u.km
            result.v_x = solution['y'][3, :] * u.km / u.s
            result.v_y = solution['y'][4, :] * u.km / u.s
            result.v_z = solution['y'][5, :] * u.km / u.s
            
        else:
        
            if rocket_motor.T.to_value(u.N) <= 0:
                
                raise ValueError("Rocket motor thrust must be greater than 0")
            
            if rocket_motor.I_sp.to_value(u.s) <= 0:
                
                raise ValueError("Rocket motor specific impulse must be greater than 0")
            
            solution: dict = ode.solve_ivp(fun=self._equations_relative_motion_with_thrust,
                                           t_span=[0, delta.to(u.s).to_value()],
                                           y0=np.hstack([self.r, self.v, np.array([rocket_motor.m_sc.to_value(u.kg)])]),
                                           method='RK45',
                                           args=(rocket_motor.T.to_value(u.N) * 1e-3, rocket_motor.I_sp.to_value(u.s)),
                                           rtol=1e-8,
                                           atol=1e-8)
            
            result.success = solution['success']
            result.t = solution['t'] * u.s
            result.r_x = solution['y'][0, :] * u.km
            result.r_y = solution['y'][1, :] * u.km
            result.r_z = solution['y'][2, :] * u.km
            result.v_x = solution['y'][3, :] * u.km / u.s
            result.v_y = solution['y'][4, :] * u.km / u.s
            result.v_z = solution['y'][5, :] * u.km / u.s
            result.m_sc = solution['y'][6, :] * u.kg
        
        return result
        
    # --- PRIVATE ---
    
    def _equations_relative_motion(self, t: float, X: np.ndarray) -> np.ndarray:
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
        dx_dt[3] = - (self.attractor.mu.to_value(u.km**3 / u.s**2) / r**3) * x
        dx_dt[4] = - (self.attractor.mu.to_value(u.km**3 / u.s**2) / r**3) * y
        dx_dt[5] = - (self.attractor.mu.to_value(u.km**3 / u.s**2) / r**3) * z
        
        return dx_dt
    
    def _equations_relative_motion_with_thrust(self,
                                               t : float,
                                               X : np.ndarray,
                                               T : float,
                                               I_sp : float) -> np.ndarray:
        """Equations of relative motion with thrust

        Args:
            t (float): Time
            X (np.ndarray): State [7,1]
            T (float): Thrust
            I_sp (float): Specific impulse

        Returns:
            np.ndarray: Derivative of state
        """
        
        x, y, z, v_x, v_y, v_z, m = X
        
        r: float = np.sqrt(x**2 + y**2 + z**2)
        
        v: float = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        
        dx_dt = np.zeros(shape=(7))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = - (self.attractor.mu.to_value(u.km**3 / u.s**2) / r**3) * x + (T / m) * (v_x / v)
        dx_dt[4] = - (self.attractor.mu.to_value(u.km**3 / u.s**2) / r**3) * y + (T / m) * (v_y / v)
        dx_dt[5] = - (self.attractor.mu.to_value(u.km**3 / u.s**2) / r**3) * z + (T / m) * (v_z / v)
        dx_dt[6] = - T / (I_sp * self.attractor.g_0.to_value(u.km / u.s**2))
        
        return dx_dt