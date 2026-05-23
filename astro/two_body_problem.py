"""
Two Body Problem

Implements core algorithms for solving the classical two-body problem,
including orbital geometry, conic classification, and the fundamental
relationships between position, velocity, and orbital elements.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 2: The Two-Body Problem
    - Chapter 6: Orbital Maneuvers
    
- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 2: Two-Body Orbital Mechanics
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
    
    success         : bool
    time            : u.Quantity
    position_x      : u.Quantity
    position_y      : u.Quantity
    position_z      : u.Quantity
    velocity_x      : u.Quantity
    velocity_y      : u.Quantity
    velocity_z      : u.Quantity
    mass_spacecraft : u.Quantity
    
@dataclasses.dataclass
class OrbitParameters:
    """Orbit parameters based on orbit geometry (linear - circular - elliptical - parabolic - hyperbolic)
    """
    
    conic_type                  : str = ""                              # ? Type of conic section
    specific_angular_momentum   : u.Quantity = 0.0 * u.km**2 / u.s      # ? Specific Angular Momentum
    transverse_velocity         : u.Quantity = 0.0 * u.km / u.s         # ? Transverse Velocity
    specific_energy             : u.Quantity = 0.0 * u.km**2 / u.s**2   # ? Specific Mechanical Energy
    semilatus_rectum            : u.Quantity = 0.0 * u.km               # ? Semilatus Rectum (Parameter)
    semimajor_axis              : u.Quantity = 0.0 * u.km               # ? Semimajor Axis
    eccentricity                : u.Quantity = 0.0 * u.one              # ? Eccentricity
    periapsis_radius            : u.Quantity = 0.0 * u.km               # ? Periapsis Radius
    apoapsis_radius             : u.Quantity = 0.0 * u.km               # ? Apoapsis Radius
    semiminor_axis              : u.Quantity = 0.0 * u.km               # ? Semi-Minor Axis
    period                      : u.Quantity = 0.0 * u.s                # ? Orbital Period
    escape_velocity             : u.Quantity = 0.0 * u.km / u.s         # ? Escape Velocity
    hyperbolic_excess_speed     : u.Quantity = 0.0 * u.km / u.s         # ? Hyperbolic Excess Speed
    turning_angle               : u.Quantity = 0.0 * u.deg              # ? Turning Angle
    asymptotic_true_anomaly     : u.Quantity = 0.0 * u.deg              # ? Infinite True Anomaly
    asymptote_angle             : u.Quantity = 0.0 * u.deg              # ? Hyperbola Asymptote Angle
    aiming_radius               : u.Quantity = 0.0 * u.km               # ? Aiming Radius
    characteristic_energy       : u.Quantity = 0.0 * u.km**2 / u.s**2   # ? Characteristic Energy

class Orbit:
    """Generic orbit in 2 Body Problem
    """
    
    def __init__(self):
        """Constructor
        """
        
        self.ready: bool = False
        
        self.attractor: bodies.Body = bodies.get_body(bodies.Attractor.EARTH)
        
        self.position: np.ndarray = np.zeros(3)
        
        self.velocity: np.ndarray = np.zeros(3)
        
        self.epoch: time.Time = time.Time('1970-01-01T00:00:00', format='isot', scale='utc')
    
    # --- STATIC ---
    
    @staticmethod
    def cartesian_to_orbit_parameters(attractor: bodies.Attractor,
                                      position: u.Quantity,
                                      velocity: u.Quantity) -> OrbitParameters:
        """
        Convert the given cartesian parameters (position and velocity vector) in orbit ones

        Args:
            attractor (bodies.Attractor): Main attractor
            position (u.Quantity): Position vector
            velocity (u.Quantity): Velocity vector

        Returns:
            OrbitParameters: Orbit parameters
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(position.to_value(u.km))
        common.check_velocity_vector(velocity.to_value(u.km / u.s))
        
        r: np.ndarray = typing.cast(np.ndarray, position.to(u.km).to_value())
        
        r_m: float = np.linalg.norm(r)

        v: np.ndarray = typing.cast(np.ndarray, velocity.to(u.km / u.s).to_value())
        
        v_m: float = np.linalg.norm(v)
        
        mu: float = bodies.BODIES[attractor].mu.to(u.km**3 / u.s**2).to_value()

        parameters: OrbitParameters = OrbitParameters()
        
        # >>> Angular Momentum
        
        h: np.ndarray = np.cross(r, v)
        
        h_m: float = np.linalg.norm(h)
        
        parameters.specific_angular_momentum = h_m * u.km**2 / u.s
        
        parameters.transverse_velocity = h_m / r_m * u.km / u.s
        
        # >>> Energy
        
        epsilon: float = v_m**2 / 2 - mu / r_m
        
        parameters.specific_energy = epsilon * u.km**2 / u.s**2
        
        # >>> Semilatus Rectum / Parameter
        
        p: float = h_m**2 / mu
        
        parameters.semilatus_rectum = p
        
        # >>> Semimajor axis
        
        a: float = - mu / (2 * epsilon) if epsilon != 0 else np.inf
        
        parameters.semimajor_axis = a * u.km
        
        # >>> Eccentricity
        
        e: float = np.sqrt((2 * h_m**2 * epsilon) / (mu **2) + 1)
        
        parameters.eccentricity = e * u.one
        
        # >>> Select Orbit Type
        
        # * Linear Trajectory
        if np.isclose(h_m, 0.0, rtol=1e-3, atol=1e-6):
            
            parameters.conic_type = "line"
            
            return parameters
        
        # * Circular Orbit
        if np.isclose(e, 0.0, rtol=1e-2, atol=1e-4):
            
            parameters.conic_type       = "circle"
            parameters.periapsis_radius = r_m * u.km
            parameters.apoapsis_radius  = r_m * u.km
            parameters.semiminor_axis   = r_m * u.km
            parameters.period           = (2 * np.pi) /  np.sqrt(mu) * r_m ** (3 / 2) * u.s
            
        # * Parabolic Orbit
        elif np.isclose(e, 1.0, rtol=1e-3, atol=1e-6):
            
            parameters.conic_type       = "parabola"
            parameters.periapsis_radius = p / 2 * u.km
            parameters.apoapsis_radius  = 0 * u.km
            parameters.semiminor_axis   = 0 * u.km
            parameters.period           = 0 * u.s
            parameters.escape_velocity  = np.sqrt(2 * mu / parameters.periapsis_radius.to_value()) * u.km / u.s
            
            # ! The escape velocity is calculated at perapsis, even if defined for each position
        
        # * Elliptical Orbit
        elif e < 1:
            
            parameters.conic_type       = "ellipse"
            parameters.periapsis_radius = p / (1 + e) * u.km
            parameters.apoapsis_radius  = p / (1 - e) * u.km
            parameters.semiminor_axis   = a * np.sqrt(1 - e ** 2) * u.km
            parameters.period           = (2 * np.pi) /  np.sqrt(mu) * a ** (3 / 2) * u.s
        
        # * Hyperbolic Orbit
        else:
            
            parameters.conic_type               = "hyperbola"
            parameters.periapsis_radius         = p / (1 + e) * u.km
            parameters.apoapsis_radius          = p / (1 - e) * u.km
            parameters.semiminor_axis           = np.abs(a) * np.sqrt(e ** 2 - 1) * u.km
            parameters.period                   = 0 * u.s
            parameters.escape_velocity          = np.sqrt(2 * mu  / parameters.periapsis_radius.to_value()) * u.km / u.s
            parameters.hyperbolic_excess_speed  = np.sqrt(2 * epsilon) * u.km / u.s
            parameters.turning_angle            = np.rad2deg(2 * np.arcsin(1 / e)) * u.deg
            parameters.asymptotic_true_anomaly  = np.rad2deg(np.arccos(-1 / e)) * u.deg
            parameters.asymptote_angle          = np.rad2deg(np.arccos(+1 / e)) * u.deg
            parameters.aiming_radius            = np.abs(a) * np.sqrt(e ** 2 - 1) * u.km
            parameters.characteristic_energy    = parameters.hyperbolic_excess_speed ** 2
            
            # ! The escape velocity is calculated at perapsis, even if defined for each position
        
        return parameters
    
    # --- PUBLIC ---
    
    def from_cartesian(self,
                       attractor: bodies.Attractor,
                       position: u.Quantity,
                       velocity: u.Quantity,
                       epoch: time.Time = time.Time(0, format="unix", scale="utc")) -> None:
        """
        Initialize the orbit based on cartesian orbit parameters

        Args:
            attractor (bodies.Attractor): Main attractor
            position (u.Quantity): Position vector
            velocity (u.Quantity): Velocity vector
            epoch (time.Time, optional): Epoch of orbit position. Defaults to 0.
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(position.to_value(u.km))
        common.check_velocity_vector(velocity.to_value(u.km / u.s))
        common.check_time(epoch)
        
        r: np.ndarray = typing.cast(np.ndarray, position.to(u.km).to_value())

        v: np.ndarray = typing.cast(np.ndarray, velocity.to(u.km / u.s).to_value())
        
        self.ready = True
        
        self.attractor = bodies.BODIES[attractor]
        
        self.position = r
        
        self.velocity = v
        
        self.epoch = epoch
    
    def propagate_until(self, end_epoch: time.Time, rocket_motor: om.RocketMotor = None) -> Result:
        """
        Propagate the orbit until end_epoch

        Args:
            end_epoch (time.Time): End epoch for propagation
            rocket_motor (om.RocketMotor, optional): Rocket motor for thrust. Defaults to None.

        Returns:
            Result: Integration result
        """
        
        common.check_time(end_epoch)
        
        if end_epoch < self.epoch: raise TypeError(f"'end_epoch' {end_epoch} must come after 'epoch' {self.epoch}")
        
        return self._propagate((end_epoch - self.epoch).to(u.s).to_value(), rocket_motor)

    def propagate_for(self, delta: time.TimeDelta, rocket_motor: om.RocketMotor = None) -> Result:
        """Propagate the orbit for delta time

        Args:
            delta (time.TimeDelta): Delta time for propagation
            rocket_motor (om.RocketMotor, optional): Rocket motor for thrust. Defaults to None.

        Returns:
            Result: Integration result
        """
        
        common.check_time_delta(delta)
        
        return self._propagate(delta.to(u.s).to_value(), rocket_motor)
        
    # --- PRIVATE ---
    
    def _propagate(self, delta: float, rocket_motor: om.RocketMotor = None):
        """
        Propagate the orbit

        Args:
            delta (float): Delta time for propagation
            rocket_motor (om.RocketMotor, optional): Rocket motor for thrust. Defaults to None.

        Returns:
            Result: Integration result
        """
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        result: Result = Result()
        
        if rocket_motor == None:
        
            solution: dict = ode.solve_ivp(fun=self._equations_relative_motion,
                                           t_span=[0, delta],
                                           y0=np.concat([self.position, self.velocity]),
                                           method='RK45',
                                           args=(),
                                           rtol=1e-8,
                                           atol=1e-8)
            
            result.success = solution['success']
            result.time = solution['t'] * u.s
            result.position_x = solution['y'][0, :] * u.km
            result.position_y = solution['y'][1, :] * u.km
            result.position_z = solution['y'][2, :] * u.km
            result.velocity_x = solution['y'][3, :] * u.km / u.s
            result.velocity_y = solution['y'][4, :] * u.km / u.s
            result.velocity_z = solution['y'][5, :] * u.km / u.s
            
        else:
        
            if rocket_motor.T.to_value(u.N) <= 0:
                
                raise ValueError("Rocket motor thrust must be greater than 0")
            
            if rocket_motor.I_sp.to_value(u.s) <= 0:
                
                raise ValueError("Rocket motor specific impulse must be greater than 0")
            
            solution: dict = ode.solve_ivp(fun=self._equations_relative_motion_with_thrust,
                                           t_span=[0, delta],
                                           y0=np.hstack([self.position, self.velocity, np.array([rocket_motor.m_sc.to_value(u.kg)])]),
                                           method='RK45',
                                           args=(rocket_motor.T.to_value(u.N) * 1e-3, rocket_motor.I_sp.to_value(u.s)),
                                           rtol=1e-8,
                                           atol=1e-8)
            
            result.success = solution['success']
            result.time = solution['t'] * u.s
            result.position_x = solution['y'][0, :] * u.km
            result.position_y = solution['y'][1, :] * u.km
            result.position_z = solution['y'][2, :] * u.km
            result.velocity_x = solution['y'][3, :] * u.km / u.s
            result.velocity_y = solution['y'][4, :] * u.km / u.s
            result.velocity_z = solution['y'][5, :] * u.km / u.s
            result.mass_spacecraft = solution['y'][6, :] * u.kg
        
        return result
    
    def _equations_relative_motion(self, t: float, X: np.ndarray) -> np.ndarray:
        """
        Equations of relative motion under a central gravitational field.
        
        This function integrates the classical two‑body equations:

            Let the state vector be:
                X = [x, y, z, v_x, v_y, v_z]

            The radial distance is:
                r = sqrt(x² + y² + z²)

            The equations of motion are:

                dx/dt   = v_x
                dy/dt   = v_y
                dz/dt   = v_z

                dv_x/dt = - μ * x / r³
                dv_y/dt = - μ * y / r³
                dv_z/dt = - μ * z / r³

            where μ is the gravitational parameter of the attractor.

        Args:
            t (float): Time (unused, included for ODE solver compatibility)
            X (np.ndarray): State vector [x, y, z, v_x, v_y, v_z]

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        x, y, z, v_x, v_y, v_z = X
        
        r: float = np.sqrt(x**2 + y**2 + z**2)
        
        mu: float = self.attractor.mu.to_value(u.km**3 / u.s**2)
        
        dx_dt: np.ndarray = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = - (mu / r**3) * x
        dx_dt[4] = - (mu / r**3) * y
        dx_dt[5] = - (mu / r**3) * z
        
        return dx_dt
    
    def _equations_relative_motion_with_thrust(self,
                                               t : float,
                                               X : np.ndarray,
                                               thrust : float,
                                               specific_impulse : float) -> np.ndarray:
        """
        Equations of motion for a point‑mass spacecraft under central gravity and continuous thrust, expressed in the
        inertial frame.

            The state vector is:
                X = [x, y, z, v_x, v_y, v_z, m]
            
            The equations of motion are:

                dx/dt   = v_x
                dy/dt   = v_y
                dz/dt   = v_z

                dv_x/dt = - μ * x / r³ + (T / m) * (v_x / v)
                dv_y/dt = - μ * y / r³ + (T / m) * (v_y / v)
                dv_z/dt = - μ * z / r³ + (T / m) * (v_z / v)

                dm/dt   = - T / (I_sp * g₀)

            The model includes:
                - Newtonian two‑body gravity from the attractor
                - Thrust acceleration aligned with the instantaneous velocity vector
                - Mass depletion according to the rocket equation

        Args:
            t (float): Time (unused, included for ODE solver compatibility)
            X (np.ndarray): State vector [x, y, z, v_x, v_y, v_z, m]
            thrust (float): Thrust magnitude [N]
            specific_impulse (float): Specific impulse [s]

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        T: float = thrust
        
        I_sp: float = specific_impulse
        
        x, y, z, v_x, v_y, v_z, m = X
        
        r: float = np.sqrt(x**2 + y**2 + z**2)
        
        v: float = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        
        mu: float = self.attractor.mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = self.attractor.g_0.to_value(u.km / u.s**2)
        
        dx_dt = np.zeros(shape=(7))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = - (mu / r**3) * x + (T / m) * (v_x / v)
        dx_dt[4] = - (mu / r**3) * y + (T / m) * (v_y / v)
        dx_dt[5] = - (mu / r**3) * z + (T / m) * (v_z / v)
        dx_dt[6] = - T / (I_sp * g_0)
        
        return dx_dt