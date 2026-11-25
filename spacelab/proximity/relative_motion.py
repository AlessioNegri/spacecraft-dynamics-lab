"""
Relative Motion

Implementation of relative motion algorithms.

📖 **References**

- :cite:`curtis`
    - Chapter 7 *Relative Motion and Rendezvous*
- :cite:`walter`
    - Chapter 8 *Orbital Maneuvering*
"""

import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.integrate as ode

import spacelab.bodies as sl_bodies
import spacelab.models.results as sl_results
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

class RelativeMotion():
    """
    This class implements a **Relative Motion** trajectory model, which is based on the **two-body problem**.
        
    🧮 **Attributes**
    
    ready : bool
        Orbit readiness flag.
    
    attractor : sl_bodies.Body
        Main attractor.

    position : np.ndarray
        Absolute position vector (initial conditions).

    velocity : np.ndarray
        Absolute velocity vector (initial conditions).
    
    relative_position : np.ndarray
        Relative position vector (initial conditions).

    relative_velocity : np.ndarray
        Relative velocity vector (initial conditions).
    
    📌 **Notes**
    
    Here we consider the fact that the relative position vector of the Chaser w.r.t. the Target has a magnitude very
    small compared to the distance from the attractor. This is true if the two vehicles are in close proximity to each
    other, as in the case of a rendezvous maneuver or close formation flight. The Target orbit is also called the
    *reference orbit*. We will consider the *linearized* version of the original equations.
    
    📖 **References**
    
    - :cite:`curtis`
        - Chapter 7 *Relative Motion and Rendezvous*
    - :cite:`walter`
        - Chapter 8 *Orbital Maneuvering*
    """
    
    def __init__(self):
        """Constructor"""
        
        self.ready: bool = False
        
        self.attractor: sl_bodies.Body = sl_bodies.get_body(sl_bodies.Attractor.EARTH)
        
        self.position: np.ndarray = np.zeros(3)
        
        self.velocity: np.ndarray = np.zeros(3)
        
        self.relative_position: np.ndarray = np.zeros(3)
        
        self.relative_velocity: np.ndarray = np.zeros(3)
    
    # --- PUBLIC ---
    
    def init(
        self,
        attractor: sl_bodies.Attractor,
        position: u.Quantity,
        velocity: u.Quantity,
        relative_position: u.Quantity,
        relative_velocity: u.Quantity) -> None:
        """
        Initializes the parameters for the propagation of the relative motion.

        :param attractor: Main attractor
        :type attractor: sl_bodies.Attractor
        :param position: Position vector
        :type position: u.Quantity
        :param velocity: Velocity vector
        :type velocity: u.Quantity
        :param relative_position: Relative position vector
        :type relative_position: u.Quantity
        :param relative_velocity: Relative velocity vector
        :type relative_velocity: u.Quantity
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
        
        # * relative_position
        
        err_msg = sl_validator.validate_quantity_vector("relative_position", relative_position, u.km, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # * relative_velocity
        
        err_msg = sl_validator.validate_quantity_vector("relative_velocity", relative_velocity, u.km / u.s, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # >>> Initialization
        
        self.ready = True
        
        self.attractor = sl_bodies.BODIES[attractor]
        
        self.position = position.to(u.km).to_value()
        
        self.velocity = velocity.to(u.km / u.s).to_value()
        
        self.relative_position = relative_position.to(u.km).to_value()
        
        self.relative_velocity = relative_velocity.to(u.km / u.s).to_value()
    
    def propagate_for(self, delta: time.TimeDelta) -> sl_results.ResultRM:
        """
        Propagates the linearized relative motion in the LVLH frame for delta time.

        :param delta: Delta time for propagation
        :type delta: time.TimeDelta
        :return: Integration result
        :rtype: sl_results.ResultRM
        """
        
        result = sl_results.ResultCR3BP(success=False)
        
        # >>> Validation
        
        # * delta
        
        err_msg: str | None = sl_validator.validate_time_delta("delta", delta)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        if not self.ready:
            
            sl_logger.logger.error("'RelativeMotion' object is not ready")
            
            return result
        
        # >>> Algorithm
        
        solution: dict = ode.solve_ivp(
            fun=self._linearized_equations_relative_motion,
            t_span=[0, delta.to_value(u.s)],
            y0=np.concat([self.relative_position, self.relative_velocity, self.position, self.velocity]),
            method='RK45',
            args=(),
            rtol=1e-8,
            atol=1e-8)
        
        result.success = solution['success']
        result.time = solution['t'] * u.s
        result.relative_position_x = solution['y'][0, :] * u.km
        result.relative_position_y = solution['y'][1, :] * u.km
        result.relative_position_z = solution['y'][2, :] * u.km
        result.relative_velocity_x = solution['y'][3, :] * u.km / u.s
        result.relative_velocity_y = solution['y'][4, :] * u.km / u.s
        result.relative_velocity_z = solution['y'][5, :] * u.km / u.s
        result.position_x = solution['y'][6, :] * u.km
        result.position_y = solution['y'][7, :] * u.km
        result.position_z = solution['y'][8, :] * u.km
        result.velocity_x = solution['y'][9, :] * u.km / u.s
        result.velocity_y = solution['y'][10, :] * u.km / u.s
        result.velocity_z = solution['y'][11, :] * u.km / u.s
        
        return result
    
    def propagate_near_circular_orbit_for(self, delta: time.TimeDelta, eccentricity: u.Quantity) -> sl_results.ResultRM:
        """
        Propagates the near-circular relative motion in the LVLH frame for delta time.

        :param delta: Delta time for propagation
        :type delta: time.TimeDelta
        :param eccentricity: Eccentricity of the orbit
        :type eccentricity: u.Quantity
        :return: Integration result
        :rtype: sl_results.ResultRM
        
        📌 **Notes**
        
        These equations are valid for eccentricities :math:`e << 1`, and for :math:`e = 0` they are the
        **Hill's equations**.
        """
        
        result = sl_results.ResultCR3BP(success=False)
        
        # >>> Validation
        
        # * delta
        
        err_msg: str | None = sl_validator.validate_time_delta("delta", delta)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        if not self.ready:
            
            sl_logger.logger.error("'RelativeMotion' object is not ready")
            
            return result

        err_msg = sl_validator.validate_quantity("eccentricity", eccentricity, u.one)

        if err_msg: sl_logger.logger.warning(err_msg); return result

        if eccentricity.to_value(u.one) < 0:

            sl_logger.logger.warning("'eccentricity' must be positive")

            return result
        
        # >>> Algorithm
        
        solution: dict = ode.solve_ivp(
            fun=self._near_circular_orbit_equations_relative_motion,
            t_span=[0, delta.to_value(u.s)],
            y0=np.concat([self.relative_position, self.relative_velocity, self.position, self.velocity]),
            method='RK45',
            args=(eccentricity.to_value(u.one),),
            rtol=1e-8,
            atol=1e-8)
        
        result.success = solution['success']
        result.time = solution['t'] * u.s
        result.relative_position_x = solution['y'][0, :] * u.km
        result.relative_position_y = solution['y'][1, :] * u.km
        result.relative_position_z = solution['y'][2, :] * u.km
        result.relative_velocity_x = solution['y'][3, :] * u.km / u.s
        result.relative_velocity_y = solution['y'][4, :] * u.km / u.s
        result.relative_velocity_z = solution['y'][5, :] * u.km / u.s
        result.position_x = solution['y'][6, :] * u.km
        result.position_y = solution['y'][7, :] * u.km
        result.position_z = solution['y'][8, :] * u.km
        result.velocity_x = solution['y'][9, :] * u.km / u.s
        result.velocity_y = solution['y'][10, :] * u.km / u.s
        result.velocity_z = solution['y'][11, :] * u.km / u.s
        
        return result
    
    # --- PRIVATE ---
    
    def _linearized_equations_relative_motion(self, t: float, X: np.ndarray) -> np.ndarray:
        """
        Linearized equations of relative motion in the LVLH frame.

        :param t: Time (included for ODE solver compatibility)
        :type t: float
        :param X: State vector :math:`[\\vec{\\delta r}, \\vec{\\delta v}, \\vec{r}, \\vec{v}]`
        :type X: np.ndarray
        :return: Time derivative :math:`\\dot{x}`
        :rtype: np.ndarray
        
        📌 **Notes**
        
        This model propagates the first-order (linearized) relative motion between a chaser spacecraft and a target
        spacecraft following a Keplerian two-body orbit.
        
        The state vector contains both the *relative* position/velocity (dx, dy, dz, dv_x, dv_y, dv_z) and the *target*
        inertial position/velocity (x, y, z, v_x, v_y, v_z).
        
        The linearized dynamics are obtained by expanding the full nonlinear equations around the target's
        instantaneous orbital state:
        
        .. math::

            \\begin{aligned}
            
            \\dot{\\delta x} &= \\delta v_x
            
            \\dot{\\delta y} &= \\delta v_y
            
            \\dot{\\delta z} &= \\delta v_z
            
            \\dot{\\delta v}_x &= \\left(\\frac{2\\mu}{R^3} +
                                    \\Omega^2\\right)\\delta x +
                                    \\dot{\\Omega}\\,\\delta y + 2\\Omega\\,\\delta v_y
            
            \\dot{\\delta v}_y &= \\left(\\Omega^2 - \\frac{\\mu}{R^3}\\right)\\delta y
                                    - \\dot{\\Omega}\\,\\delta x
                                    - 2\\Omega\\,\\delta v_x
            
            \\dot{\\delta v}_z &= -\\frac{\\mu}{R^3}\\delta z
            
            \\dot{x} &= v_x
            
            \\dot{y} &= v_y
            
            \\dot{z} &= v_z
            
            \\dot{v}_x &= -\\frac{\\mu}{R^3}x
            
            \\dot{v}_y &= -\\frac{\\mu}{R^3}y
            
            \\dot{v}_z &= -\\frac{\\mu}{R^3}z
            
            \\end{aligned}

        These are the equations of motion of a chaser, not being subject to external forces, relative to a target.
        The resulting system corresponds to the classical first-order variational equations for relative motion, valid
        for small separations and assuming a purely Keplerian (unperturbed) target trajectory.
        
        These equations are:
        
        - Valid for small relative distances compared to the orbital radius.
        
        - Assumes a Keplerian central-gravity field with no perturbations.
        
        - The linearized terms include coupling through the target's angular momentum, radial velocity, and\
            instantaneous orbital geometry.
            
        - These equations are written in LVLH frame:
        
            - x-axis points along the radial direction from the attractor to the target
            
            - y-axis points along the target's velocity direction (tangential)
            
            - z-axis completes the right-handed frame (normal to the orbital plane)
            
        - In case we want to use the RSW frame:
        
            - x-axis points along the target's velocity direction (tangential)
            
            - y-axis completes the right-handed frame (normal to the orbital plane)
            
            - z-axis points along the radial direction from the attractor to the target
        
        The transformation from the LVLH frame to the RSW frame can be achieved as follows:
        
        - x-LVLH = z-RSW
        - y-LVLH = x-RSW
        - z-LVLH = y-RSW
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 7.3 *Linearization of the equations of relative motion in orbit*
        - :cite:`walter`
            - Section 8.5 *Relative Orbits*
            - Section 8.5.1 *General Equation of Motion*
        """
        
        # ? Data
        
        dx, dy, dz, dv_x, dv_y, dv_z, x, y, z, v_x, v_y, v_z = X
        
        # ? Orbit parameters
        
        R: float = np.sqrt(x**2 + y**2 + z**2) # * Target radial distance
        
        h: float = np.linalg.norm(np.cross(np.array([x, y, z]), np.array([v_x, v_y, v_z]))) # * Target specific angular momentum magnitude
        
        VR: float = np.dot(np.array([x, y, z]), np.array([v_x, v_y, v_z])) # * Target radial velocity
        
        mu: float = self.attractor.mu.to_value(u.km**3 / u.s**2)
        
        omega: float = h / R**2 # * Target angular velocity magnitude
        
        domega_dt: float = - 2 * VR * h / R**4 # * Target angular acceleration magnitude
        
        # ? ODE
        
        dx_dt: np.ndarray = np.zeros(shape=(12))
        
        dx_dt[0]  = dv_x
        dx_dt[1]  = dv_y
        dx_dt[2]  = dv_z
        dx_dt[3]  = (2 * mu / R**3 + omega**2) * dx + domega_dt * dy + 2 * omega * dv_y
        dx_dt[4]  = (omega**2 - mu / R**3) * dy - domega_dt * dx - 2 * omega * dv_x
        dx_dt[5]  = - mu / R**3 * dz
        dx_dt[6]  = v_x
        dx_dt[7]  = v_y
        dx_dt[8]  = v_z
        dx_dt[9]  = - (mu / R**3) * x
        dx_dt[10] = - (mu / R**3) * y
        dx_dt[11] = - (mu / R**3) * z
        
        return dx_dt

    def _near_circular_orbit_equations_relative_motion(self, t: float, X: np.ndarray, e: float) -> np.ndarray:
        """
        Linearized equations of relative motion for a near-circular target orbit (HCW + first-order eccentricity terms).

        :param t: Time (included for ODE solver compatibility)
        :type t: float
        :param X: State vector :math:`[\\vec{\\delta r}, \\vec{\\delta v}, \\vec{r}, \\vec{v}]`
        :type X: np.ndarray
        :param e: Target orbital eccentricity (assumed small)
        :type e: float
        :return: Time derivative :math:`\\dot{x}`
        :rtype: np.ndarray
        
        📌 **Notes**
        
        This model propagates the relative motion between a chaser spacecraft and a target spacecraft assuming the
        target follows a *near-circular* Keplerian orbit. The dynamics reduce to the classical *Hill-Clohessy-Wiltshire*
        (*HCW*) equations plus first-order corrections proportional to the target's eccentricity.
        
        .. math::

            \\begin{aligned}
            
            \\dot{\\delta x} &= \\delta v_x
            
            \\dot{\\delta y} &= \\delta v_y
            
            \\dot{\\delta z} &= \\delta v_z
            
            \\dot{\\delta v}_x &= 2n\\delta v_y + 3n^2\\delta x
                                    + 2en(-n\\delta y\\sin(nt)+5n\\delta x\\cos(nt)+2\\delta v_y\\cos(nt))
                                    
            \\dot{\\delta v}_y &= -2n\\delta v_x + en(n\\delta y\\cos(nt)+2n\\delta x\\sin(nt)-4\\delta v_x\\cos(nt))
            
            \\dot{\\delta v}_z &= -n^2\\delta z - 3en^2\\delta z\\cos(nt)
            
            \\dot{x} &= v_x
            
            \\dot{y} &= v_y
            
            \\dot{z} &= v_z
            
            \\dot{v}_x &= -\\frac{\\mu}{R^3}x
            
            \\dot{v}_y &= -\\frac{\\mu}{R^3}y
            
            \\dot{v}_z &= -\\frac{\\mu}{R^3}z
            
            \\end{aligned}

        The state vector contains both the *relative* position/velocity and the *target* inertial position/velocity. The
        linearization is performed around the instantaneous circular reference orbit, with the mean motion:

        .. math::
        
            n = \\frac{h}{R^2}

        where :math:`R` is the target radial distance and :math:`h` its specific angular momentum.

        The resulting system corresponds to the first-order variational equations for near-circular motion, valid for
        small separations and small eccentricities. The eccentricity-dependent terms introduce periodic forcing at the
        orbital frequency `n`, capturing the deviation from ideal circular HCW dynamics.

        These equations are:
        
        - Valid for small relative distances compared to the orbital radius.
        
        - Assumes a near-circular Keplerian orbit: eccentricity :math:`e << 1`.
        
        - Reduces to the classical HCW equations when :math:`e = 0`.
        
        - The linearized terms include coupling through the target's mean motion and first-order periodic corrections\
            proportional to :math:`e \\cdot \\cos(n t)` and :math:`e \\cdot \\sin(n t)`.
            
        - These equations are written in the LVLH frame:
        
            - x-axis: radial direction (from attractor to target)
            
            - y-axis: along-track direction (target velocity)
            
            - z-axis: cross-track direction (normal to orbital plane)
            
        - For the RSW frame:
        
            - x-RSW = y-LVLH
            
            - y-RSW = z-LVLH
            
            - z-RSW = x-LVLH
        
        📖 **References**
        
        - :cite:`walter`
            - Section 8.5 *Relative Orbits*
            - Section 8.5.4 *Near-Circular Orbits*
        """
        
        # ? Data
        
        dx, dy, dz, dv_x, dv_y, dv_z, x, y, z, v_x, v_y, v_z = X
        
        # ? Orbit parameters
        
        R: float = np.sqrt(x**2 + y**2 + z**2) # * Target radial distance
        
        h: float = np.linalg.norm(np.cross(np.array([x, y, z]), np.array([v_x, v_y, v_z]))) # * Target specific angular momentum magnitude
        
        mu: float = self.attractor.mu.to_value(u.km**3 / u.s**2)
        
        n: float = h / R**2 # * Target angular velocity magnitude
        
        # ? ODE
        
        dx_dt: np.ndarray = np.zeros(shape=(12))
        
        dx_dt[0]  = dv_x
        dx_dt[1]  = dv_y
        dx_dt[2]  = dv_z
        dx_dt[3]  = 2 * n * dv_y + 3 * n**2 * dx
        dx_dt[3]  += 2 * e * n * (- n * dy * np.sin(n * t) + 5 * n * dx * np.cos(n * t) + 2 * dv_y * np.cos(n * t))
        dx_dt[4]  = - 2 * n * dv_x
        dx_dt[4]  += e * n * (n * dy * np.cos(n * t) + 2 * n * dx * np.sin(n * t) - 4 * dv_x * np.cos(n * t))
        dx_dt[5]  = - n**2 * dz
        dx_dt[5]  += - 3 * e * n**2 * dz * np.cos(n * t)
        dx_dt[6]  = v_x
        dx_dt[7]  = v_y
        dx_dt[8]  = v_z
        dx_dt[9]  = - (mu / R**3) * x
        dx_dt[10] = - (mu / R**3) * y
        dx_dt[11] = - (mu / R**3) * z
        
        return dx_dt
