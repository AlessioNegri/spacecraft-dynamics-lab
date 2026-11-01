import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.integrate as ode
import typing as ty

import spacelab.common as common

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator
import spacelab.models.results as sl_results
import spacelab.models.rocket_motor as sl_rocket_motor

class Orbit:
    """
    This class implements a **Generic Orbit** model, which is based on the **two-body problem**.
    
    📌 **Notes**
    
    The vector-based approach is used to solve the classical problem of determining the motion of two bodies due solely
    to their own mutual gravitational attraction. The *two-body problem* is regulated by the second order differential
    equation that governs the motion of the secondary mass relative to primary one. It has two vector constants of
    integration, each having three scalar components (i.e. six constants of integration). Note that interchanging the
    roles of the two masses changes nothing. Thus, the motion of :math:`m_2` as seen from :math:`m_1` is precisely the
    same as the motion of :math:`m_1` as seen from :math:`m_2`.
    
    🧮 **Attributes**
    
    ready : bool
        Orbit readiness flag.

    attractor : sl_bodies.Body
        Main attractor.

    position : np.ndarray
        Position vector (initial conditions).

    velocity : np.ndarray
        Velocity vector (initial conditions).

    epoch : time.Time
        Epoch of the initial state.
    
    📖 **References**
    
    - :cite:`curtis`
        - Chapter 2 *The Two-Body Problem*
        - Chapter 6 *Orbital Maneuvers*
    - :cite:`kluever`
        - Chapter 2 *Two-Body Orbital Mechanics*
    - :cite:`sforza`
        - Chapter 5 *ORBITAL MECHANICS*
    - :cite:`walter`
        - Chapter 7 *Orbits*
    """
    
    def __init__(self):
        
        self.ready: bool = False
        
        self.attractor: sl_bodies.Body = sl_bodies.get_body(sl_bodies.Attractor.EARTH)
        
        self.position: np.ndarray = np.zeros(3)
        
        self.velocity: np.ndarray = np.zeros(3)
        
        self.epoch: time.Time = time.Time('1970-01-01T00:00:00', format='isot', scale='utc')
    
    # --- PUBLIC ---
    
    def from_cartesian(
        self,
        attractor: sl_bodies.Attractor,
        position: u.Quantity,
        velocity: u.Quantity,
        epoch: time.Time = time.Time(0, format="unix", scale="utc")) -> None:
        """
        Initializes the orbit based on cartesian orbit parameters.

        :param attractor: Main attractor
        :type attractor: sl_bodies.Attractor
        :param position: Position vector
        :type position: u.Quantity
        :param velocity: Velocity vector
        :type velocity: u.Quantity
        :param epoch: Epoch of orbit position, defaults to time.Time(0, format="unix", scale="utc")
        :type epoch: time.Time, optional
        """
        
        self.ready = False
        
        # >>> Validation
        
        # * attractor
        
        err_msg: str | None = sl_validator.validate_attractor(attractor)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # * position
        
        err_msg = sl_validator.validate_quantity_vector("position", position, u.km, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # * velocity
        
        err_msg = sl_validator.validate_quantity_vector("velocity", velocity, u.km / u.s, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # * epoch
        
        err_msg = sl_validator.validate_time("epoch", epoch)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # >>> Initialization
        
        self.ready = True
        
        self.attractor = sl_bodies.BODIES[attractor]
        
        self.position = ty.cast(np.ndarray, position.to(u.km).to_value())
        
        self.velocity = ty.cast(np.ndarray, velocity.to(u.km / u.s).to_value())
        
        self.epoch = epoch
    
    def propagate_until(
        self,
        end_epoch: time.Time,
        rocket_motor: sl_rocket_motor.RocketMotor = None,
        thrust_direction: sl_enums.ThrustDirection = sl_enums.ThrustDirection.ALONG_VELOCITY,
        initial_radius: u.Quantity = 0 * u.km,
        target_radius: u.Quantity = 0 * u.km,
        initial_inclination: u.Quantity = 0 * u.rad,
        target_inclination: u.Quantity = 0 * u.rad) -> sl_results.Result:
        """
        Propagates the orbit until end_epoch.

        :param end_epoch: End epoch for propagation
        :type end_epoch: time.Time
        :param rocket_motor: Rocket motor for thrust, defaults to None
        :type rocket_motor: sl_rocket_motor.RocketMotor, optional
        :param thrust_direction: Direction of thrust, defaults to sl_enums.ThrustDirection.ALONG_VELOCITY
        :type thrust_direction: sl_enums.ThrustDirection, optional
        :param initial_radius: Initial radius for thrust, defaults to 0
        :type initial_radius: u.Quantity, optional
        :param target_radius: Target radius for thrust, defaults to 0
        :type target_radius: u.Quantity, optional
        :param initial_inclination: Initial inclination for thrust, defaults to 0
        :type initial_inclination: u.Quantity, optional
        :param target_inclination: Target inclination for thrust, defaults to 0
        :type target_inclination: u.Quantity, optional
        :return: Integration result
        :rtype: sl_results.Result
        """
        
        result = sl_results.Result(success=False)
        
        # >>> Validation
        
        # * end_epoch
        
        err_msg: str | None = sl_validator.validate_time("end_epoch", end_epoch)
                
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        if end_epoch < self.epoch:
            
            sl_logger.logger.warning(f"'end_epoch' {end_epoch} must come after 'epoch' {self.epoch}")
            
            return result
        
        # * rocket_motor
        
        if rocket_motor is not None:

            err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

            if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * thrust_direction
        
        err_msg = sl_validator.validate_type("thrust_direction", thrust_direction, sl_enums.ThrustDirection)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * initial_radius
        
        err_msg = sl_validator.validate_quantity("initial_radius", initial_radius, u.km)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * target_radius
        
        err_msg = sl_validator.validate_quantity("target_radius", target_radius, u.km)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * initial_inclination
        
        err_msg = sl_validator.validate_quantity("initial_inclination", initial_inclination, u.rad)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * target_inclination
        
        err_msg = sl_validator.validate_quantity("target_inclination", target_inclination, u.rad)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # >>> Algorithm
        
        return self._propagate(
            delta=(end_epoch - self.epoch).to_value(u.s),
            rocket_motor=rocket_motor,
            thrust_direction=thrust_direction,
            initial_radius=initial_radius.to_value(u.km),
            target_radius=target_radius.to_value(u.km),
            initial_inclination=initial_inclination.to_value(u.rad),
            target_inclination=target_inclination.to_value(u.rad))

    def propagate_for(
        self,
        delta: time.TimeDelta,
        rocket_motor: sl_rocket_motor.RocketMotor = None,
        thrust_direction: sl_enums.ThrustDirection = sl_enums.ThrustDirection.ALONG_VELOCITY,
        initial_radius: u.Quantity = 0 * u.km,
        target_radius: u.Quantity = 0 * u.km,
        initial_inclination: u.Quantity = 0 * u.rad,
        target_inclination: u.Quantity = 0 * u.rad) -> sl_results.Result:
        """
        Propagates the orbit for delta time.

        :param delta: Delta time for propagation
        :type delta: time.TimeDelta
        :param rocket_motor: Rocket motor for thrust, defaults to None
        :type rocket_motor: sl_rocket_motor.RocketMotor, optional
        :param thrust_direction: Direction of thrust, defaults to sl_enums.ThrustDirection.ALONG_VELOCITY
        :type thrust_direction: sl_enums.ThrustDirection, optional
        :param initial_radius: Initial radius for thrust, defaults to 0
        :type initial_radius: u.Quantity, optional
        :param target_radius: Target radius for thrust, defaults to 0
        :type target_radius: u.Quantity, optional
        :param initial_inclination: Initial inclination for thrust, defaults to 0
        :type initial_inclination: u.Quantity, optional
        :param target_inclination: Target inclination for thrust, defaults to 0
        :type target_inclination: u.Quantity, optional
        :return: Integration result
        :rtype: sl_results.Result
        """
        
        # >>> Validation
        
        # * delta
        
        result = sl_results.Result(success=False)
        
        err_msg: str | None = sl_validator.validate_time_delta("delta", delta)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * rocket_motor
        
        if rocket_motor is not None:

            err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

            if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * thrust_direction
        
        err_msg = sl_validator.validate_type("thrust_direction", thrust_direction, sl_enums.ThrustDirection)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * initial_radius
        
        err_msg = sl_validator.validate_quantity("initial_radius", initial_radius, u.km)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * target_radius
        
        err_msg = sl_validator.validate_quantity("target_radius", target_radius, u.km)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * initial_inclination
        
        err_msg = sl_validator.validate_quantity("initial_inclination", initial_inclination, u.rad)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * target_inclination
        
        err_msg = sl_validator.validate_quantity("target_inclination", target_inclination, u.rad)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # >>> Algorithm
        
        return self._propagate(
            delta=delta.to_value(u.s),
            rocket_motor=rocket_motor,
            thrust_direction=thrust_direction,
            initial_radius=initial_radius.to_value(u.km),
            target_radius=target_radius.to_value(u.km),
            initial_inclination=initial_inclination.to_value(u.rad),
            target_inclination=target_inclination.to_value(u.rad))

    # --- PRIVATE ---
    
    def _propagate(
        self,
        delta: float,
        rocket_motor: sl_rocket_motor.RocketMotor = None,
        thrust_direction: sl_enums.ThrustDirection = sl_enums.ThrustDirection.ALONG_VELOCITY,
        initial_radius: float = 0,
        target_radius: float = 0,
        initial_inclination: float = 0,
        target_inclination: float = 0) -> sl_results.Result:
        """
        Propagate the orbit for delta time, with optional thrust and mass depletion.
        
        📌 **Notes**
        
        If the rocket motor is provided, the thrust is applied with constant direction and with fixed magnitude.
        
        If the thrust direction is set to `sl_enums.ThrustDirection.ALONG_VELOCITY`, the thrust is applied along the
        instantaneous velocity vector (i.e. shape change).
        
        If the thrust direction is set to `sl_enums.ThrustDirection.ALONG_ANGULAR_MOMENTUM`, the thrust is applied along
        the orbital angular momentum vector (i.e. inclination change).

        :param delta: Delta time for propagation
        :type delta: float
        :param rocket_motor: Rocket motor for thrust, defaults to None
        :type rocket_motor: sl_rocket_motor.RocketMotor, optional
        :param thrust_direction: Direction of thrust, defaults to sl_enums.ThrustDirection.ALONG_VELOCITY
        :type thrust_direction: sl_enums.ThrustDirection, optional
        :param initial_radius: Initial radius for thrust, defaults to 0
        :type initial_radius: float, optional
        :param target_radius: Target radius for thrust, defaults to 0
        :type target_radius: float, optional
        :param initial_inclination: Initial inclination for thrust, defaults to 0
        :type initial_inclination: float, optional
        :param target_inclination: Target inclination for thrust, defaults to 0
        :type target_inclination: float, optional
        :return: Integration result
        :rtype: sl_results.Result
        """
        
        result = sl_results.Result(success=False)
        
        if not self.ready:
            
            sl_logger.logger.error("'Orbit' object is not ready")
            
            return result
        
        if rocket_motor == None:
        
            solution: dict = ode.solve_ivp(
                fun=self._equations_relative_motion,
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
        
            if rocket_motor.thrust.to_value(u.N) <= 0:
                
                sl_logger.logger.error("Rocket motor thrust must be greater than 0")
                
                return result
            
            if rocket_motor.specific_impulse.to_value(u.s) <= 0:
                
                sl_logger.logger.error("Rocket motor specific impulse must be greater than 0")
                
                return result
            
            solution: dict = ode.solve_ivp(
                fun=self._equations_relative_motion_with_thrust,
                t_span=[0, delta],
                y0=np.hstack([self.position, self.velocity, np.array([rocket_motor.spacecraft_mass.to_value(u.kg)])]),
                method='BDF', # ! Low‑thrust dynamics are stiff
                args=(
                    rocket_motor.thrust.to_value(u.N) * 1e-3, # ? kg * km / s²
                    rocket_motor.specific_impulse.to_value(u.s),
                    thrust_direction,
                    initial_radius,
                    target_radius,
                    initial_inclination,
                    target_inclination),
                rtol=1e-6,
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
        
        if not solution['success']:
            
            sl_logger.logger.warning(f"Integration failed: {solution['message']}")
        
        return result
    
    def _equations_relative_motion(self, t: float, X: np.ndarray) -> np.ndarray:
        """
        **Newton's gravitational equation of motion** under a central gravitational field.
        
        📌 **Notes**
        
        This function integrates the classical two-body equations:

            :math:`\\frac{dx}{dt}   = v_x`
            
            :math:`\\frac{dy}{dt}   = v_y`
            
            :math:`\\frac{dz}{dt}   = v_z`

            :math:`\\frac{dv_x}{dt} = - \\mu \\frac{x}{r^3}`
            
            :math:`\\frac{dv_y}{dt} = - \\mu \\frac{y}{r^3}`
            
            :math:`\\frac{dv_z}{dt} = - \\mu \\frac{z}{r^3}`

        where :math:`\\mu` is the gravitational parameter of the attractor.
        
        Assumptions:
        
        1. The two bodies are spherically symmetric so that they may be considered as particles or point masses.
        2. The mutually attractive gravitational forces are the only forces acting in the two-body system.
        3. The mass of the satellite is negligible compared with the mass of the celestial body.

        :param t: Time (unused, included for ODE solver compatibility)
        :type t: float
        :param X: State vector [position(x, y, z), velocity(v_x, v_y, v_z)]
        :type X: np.ndarray
        :return: Time derivative dx_dt
        :rtype: np.ndarray
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 2.3 *Equations of relative motion*
        - :cite:`kluever`
            - Section 2.2 *Two-Body Problem*
        - :cite:`sforza`
            - Section 5.1.1 *ORBITS AND HOW THEY WORK*
        - :cite:`walter`
            - Section 7.1.5 *General Two-Body Problem*
        """
        
        # ? Data
        
        x, y, z, v_x, v_y, v_z = X
        
        mu: float = self.attractor.mu.to_value(u.km**3 / u.s**2)
        
        # ? Radial distance
        
        r: float = np.sqrt(x**2 + y**2 + z**2)
        
        # ? ODE
        
        dx_dt: np.ndarray = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = - (mu / r**3) * x
        dx_dt[4] = - (mu / r**3) * y
        dx_dt[5] = - (mu / r**3) * z
        
        return dx_dt
    
    def _equations_relative_motion_with_thrust(
        self,
        t: float,
        X: np.ndarray,
        thrust: float,
        specific_impulse: float,
        thrust_direction: sl_enums.ThrustDirection,
        initial_radius: float,
        target_radius: float,
        initial_inclination: float,
        target_inclination: float) -> np.ndarray:
        """
        **Newton's gravitational equation of motion** under a central gravitational field with constant and continuous
        thrust, and mass depletion (rocket equation).
        
        📌 **Notes**
        
        It is assumed that the thrust is applied with constant direction and with fixed magnitude. The continuous
        application of the thrust is furnished by a contnuous depletion of the propellant mass of the spacecraft.
        
        This function integrates the classical two-body equations with Tsiolkovsky's rocket equation:

            :math:`\\frac{dx}{dt}   = v_x`
            
            :math:`\\frac{dy}{dt}   = v_y`
            
            :math:`\\frac{dz}{dt}   = v_z`

            :math:`\\frac{dv_x}{dt} = - \\mu \\frac{x}{r^3} + a^T_x`
            
            :math:`\\frac{dv_y}{dt} = - \\mu \\frac{y}{r^3} + a^T_y`
            
            :math:`\\frac{dv_z}{dt} = - \\mu \\frac{z}{r^3} + a^T_z`
            
            :math:`\\frac{dm}{dt}   = - \\frac{T}{I_{sp} g_0}`

        where :math:`\\mu` is the gravitational parameter of the attractor.
        
        The thrust acceleration vector is constructed according to the selected `thrust_direction`:

        1. Thrust aligned with the instantaneous velocity vector
        
                :math:`\\vec{a}_T = \\frac{T}{m} \\hat{v}`
                
                :math:`\\hat{v} = \\vec{v} / ||\\vec{v}||`.

        2. Thrust aligned with the orbital angular momentum vector:
        
                :math:`\\vec{a}_T = \\frac{T}{m} \\hat{h}`
                
                :math:`\\vec{h} = \\vec{r} \\times \\vec{v}`
                
                :math:`\\hat{h} = \\vec{h} / ||\\vec{h}||`.

        :param t: Time (unused, included for ODE solver compatibility)
        :type t: float
        :param X: State vector [position(x, y, z), velocity(v_x, v_y, v_z), mass(m)]
        :type X: np.ndarray
        :param thrust: Thrust magnitude [N]
        :type thrust: float
        :param specific_impulse: Specific impulse [s]
        :type specific_impulse: float
        :param thrust_direction: Direction of the thrust
        :type thrust_direction: sl_enums.ThrustDirection
        :param initial_radius: Initial radius [km]
        :type initial_radius: float
        :param target_radius: Target radius [km]
        :type target_radius: float
        :param initial_inclination: Initial inclination [rad]
        :type initial_inclination: float
        :param target_inclination: Target inclination [rad]
        :type target_inclination: float
        :return: Time derivative dx_dt
        :rtype: np.ndarray
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 6.10 *Nonimpulsive orbital maneuvers*
        """
        
        # ? Data
        
        mu: float = self.attractor.mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = self.attractor.g_0.to_value(u.km / u.s**2)
        
        T: float = thrust
        
        i_sp: float = specific_impulse
        
        x, y, z, v_x, v_y, v_z, m = X
        
        # ? Position and velocity magnitudes
        
        r: float = np.sqrt(x**2 + y**2 + z**2)
        
        v: float = np.sqrt(v_x**2 + v_y**2 + v_z**2)
        
        # ? Angular momentum vector and magnitude
        
        h: np.ndarray = np.cross(np.array([x, y, z]), np.array([v_x, v_y, v_z]))
        
        h_m: float = np.linalg.norm(h)
        
        # ? Thrust direction
        
        a_thrust: np.ndarray = np.zeros(3)
        
        if thrust_direction == sl_enums.ThrustDirection.ALONG_VELOCITY:
            
            if np.isclose(v, 0.0, rtol=1e-09, atol=1e-09):
                
                v_hat = np.zeros(3)
                
            else:
                
                v_hat = np.array([v_x, v_y, v_z]) / v
            
            if initial_radius <= target_radius:
                
                sign: int = 1 # ? Along with v_hat
                
            else:
                
                sign: int = -1 # ? Opposite to v_hat
            
            a_thrust = sign * T / m * v_hat
            
        elif thrust_direction == sl_enums.ThrustDirection.ALONG_ANGULAR_MOMENTUM:
            
            if np.isclose(h_m, 0.0, rtol=1e-09, atol=1e-09):
            
                h_hat = np.zeros(3)
                
            else:
                
                h_hat = h / h_m
            
            if initial_inclination <= target_inclination:
                
                sign: int = 1 # ? Along with h_hat
                
            else:
                
                sign: int = -1 # ? Opposite to h_hat
            
            a_thrust = sign * T / m * h_hat
        
        # ? ODE
        
        dx_dt = np.zeros(shape=(7))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = - (mu / r**3) * x + a_thrust[0]
        dx_dt[4] = - (mu / r**3) * y + a_thrust[1]
        dx_dt[5] = - (mu / r**3) * z + a_thrust[2]
        dx_dt[6] = - T / (i_sp * g_0)
        
        return dx_dt
