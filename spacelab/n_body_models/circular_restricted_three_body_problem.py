import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.integrate as ode
import scipy.optimize as optimize
import typing as ty

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.models.orbit_parameters as sl_orbit_parameters
import spacelab.models.results as sl_results
import spacelab.physical_constants as sl_physical_constants
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

class Orbit:
    """
    This class implements a **Generic Orbit** model, which is based on the **circular restricted three-body problem**.
    
    🧮 **Attributes**
        
        ready : bool
            Orbit readiness flag.
    
        body_1 : sl_bodies.Body
            Primary attractor.
            
        body_2 : sl_bodies.Body
            Secondary attractor.
    
        position : np.ndarray
            Position vector (initial conditions).
    
        velocity : np.ndarray
            Velocity vector (initial conditions).
    
    📌 **Notes**
    
    We consider a third body of mass :math:`m`, which is vanishingly small compared to the primary masses :math:`m_1`
    and :math:`m_2` - like the mass of a spacecraft compared to that of a planet or moon of the solar system. This is
    called the *restricted three-body problem*, because the mass :math:`m` is assumed to be so small that it has no
    effect on the motion of the primary bodies. We are interested in the motion of :math:`m` due to the gravitational
    fields of :math:`m_1` and :math:`m_2`. Unlike the two-body problem, there is no general, closed form solution for
    this motion.
    
    Two major assumptions are required for the CR3BP:
    
    1. the mass of the third body is negligible and does not influence the motion of the two primary bodies (R3BP);
    2. the two gravitational bodies move in circular orbits about their center of mass (CR3BP).
    
    While the second assumption seems reasonable, the first assumption causes some loss of accuracy for translunar
    trajectories.
    
    📖 **References**
    
    - :cite:`curtis`
        - Chapter 2 *The Two-Body Problem*
    - :cite:`kluever`
        - Chapter 5 *Non-Keplerian Motion*
    - :cite:`walter`
        - Chapter 11 *Three-Body Problem*
    """
    
    def __init__(self):
        
        self.ready: bool = False
        
        self.body_1: sl_bodies.Attractor = sl_bodies.Attractor.EARTH
        
        self.body_2: sl_bodies.Attractor = sl_bodies.Attractor.MOON
        
        self.position: np.ndarray = np.zeros(3)
        
        self.velocity: np.ndarray = np.zeros(3)
    
    # --- STATIC ---
    
    @staticmethod
    def orbit_parameters(
        body_1: sl_bodies.Attractor,
        body_2: sl_bodies.Attractor) -> sl_orbit_parameters.OrbitParametersCR3BP:
        """
        Calculate the orbit parameters of the *restricted three-body problem*.

        :param body_1: First body
        :type body_1: sl_bodies.Attractor
        :param body_2: Second body
        :type body_2: sl_bodies.Attractor
        :return: Orbit parameters
        :rtype: sl_orbit_parameters.OrbitParametersCR3BP
        
        📌 **Notes**
        
        Euler defined the R3BP in 1772, after he had already discovered in 1765 the *collinear equilibrium points*, the
        results of which also apply to the R3BP. Also in 1772 Lagrange discovered all five equilibrium points in the
        R3BP including the two *equilateral equilibrium points*.
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 2.12 *Restricted three-body problem*
        - :cite:`kluever`
            - Section 5.6.2 *Lagrangian Points*
        - :cite:`walter`
            - Section 11.3 *Restricted Three-Body Problem*
            - Section 11.3.1 *Collinear Libration Points*
            - Section 11.3.2 *Equilateral Libration Points*
        """
        
        parameters = sl_orbit_parameters.OrbitParametersCR3BP()
        
        # >>> Validation
        
        # * body_1
        
        err_msg: str | None = sl_validator.validate_attractor(body_1)
        
        if err_msg: sl_logger.logger.warning(err_msg); return parameters
        
        # * body_2
        
        err_msg = sl_validator.validate_attractor(body_2)
        
        if err_msg: sl_logger.logger.warning(err_msg); return parameters
        
        # >>> Algorithm
        
        # ? Global gravitational parameter
        
        mass_1: u.Quantity = sl_bodies.BODIES[body_1].M
        
        mass_2: u.Quantity = sl_bodies.BODIES[body_2].M
        
        mu: u.Quantity = sl_physical_constants.universal_gravitational_constant * (mass_1 + mass_2)
        
        # ? Inertial angular velocity
        
        body_distance: u.Quantity = sl_bodies.BODIES[body_2].semi_major_axis.to(u.km)
        
        parameters.body_distance = body_distance # ? r_12
        
        parameters.inertial_angular_velocity = np.sqrt(mu / body_distance**3) * u.rad
        
        # ? Dimensionless mass ratio
        
        parameters.dimensionless_mass_ratio_1 = mass_1 / (mass_1 + mass_2) # ? pi_1
        
        parameters.dimensionless_mass_ratio_2 = mass_2 / (mass_1 + mass_2) # ? pi_2
        
        # ? Gravitational parameter
        
        parameters.gravitational_parameter_1 = mu * parameters.dimensionless_mass_ratio_1
        
        parameters.gravitational_parameter_2 = mu * parameters.dimensionless_mass_ratio_2
        
        # ? Bodies position
        
        parameters.body_position_1 = - parameters.dimensionless_mass_ratio_2 * body_distance
        
        parameters.body_position_2 = + parameters.dimensionless_mass_ratio_1 * body_distance
        
        # ? Libration points
        
        pi_2: float = parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        f: callable = lambda xi: (1 - pi_2) / np.abs(xi + pi_2)**3 * (xi + pi_2) +\
            pi_2 / np.abs(xi + pi_2 - 1)**3 * (xi + pi_2 - 1) - xi
        
        # Analytic approximations
        
        eps: float = (pi_2 / 3)**(1/3)

        x0_lagrange_1: float = 1 - eps
        x0_lagrange_2: float = 1 + eps
        x0_lagrange_3: float = - 1 - 5 * pi_2 / 12
        
        # Bracketed roots (guaranteed)
        
        csi_1: float = optimize.brentq(f, a=0 + 1e-6, b=1 - pi_2 - 1e-6, maxiter=100, xtol=1e-8, rtol=1e-8)
        csi_2: float = optimize.brentq(f, a=1 - pi_2 + 1e-6, b=10, maxiter=100, xtol=1e-8, rtol=1e-8)
        csi_3: float = optimize.brentq(f, a=-10, b=- pi_2 - 1e-6, maxiter=100, xtol=1e-8, rtol=1e-8)
        
        # Optional Newton refinement
        
        try: csi_1 = optimize.newton(f, x0=x0_lagrange_1, maxiter=100, tol=1e-8)
        except any: pass

        try: csi_2 = optimize.newton(f, x0=x0_lagrange_2, maxiter=100, tol=1e-8);
        except any: pass

        try: csi_3 = optimize.newton(f, x0=x0_lagrange_3, maxiter=100, tol=1e-8)
        except any: pass
        
        r_12: float = body_distance.to_value(u.km)
        
        x_1: float = parameters.body_position_1.to_value(u.km)
        
        # Eulerian points
        
        parameters.libration_point_1 = np.array([csi_1 * r_12, 0, 0]) * u.km
        parameters.libration_point_2 = np.array([csi_2 * r_12, 0, 0]) * u.km
        parameters.libration_point_3 = np.array([csi_3 * r_12, 0, 0]) * u.km
        
        # Lagrangian points
        
        parameters.libration_point_4 = np.array([0.5 * r_12 + x_1, + np.sqrt(3) / 2 * r_12, 0]) * u.km
        parameters.libration_point_5 = np.array([0.5 * r_12 + x_1, - np.sqrt(3) / 2 * r_12, 0]) * u.km
        
        return parameters
    
    @staticmethod
    def zero_velocity_curves(
        body_1: sl_bodies.Attractor,
        body_2: sl_bodies.Attractor,
        jacobi_constant: u.Quantity) -> np.ndarray:
        """
        Calculates the **Zero Velocity Curves** (*ZVC*), a.k.a. **Hill curve** (after the astronomer Hill studied it in
        detail in the 19th century), given the *Jacobi constant/integral*.
        
        It returns an array 1000 x 1000 with +1 for the allowed regions and 0 for the forbidden regions, in the synodic
        frame of reference.

        :param body_1: First body
        :type body_1: sl_bodies.Attractor
        :param body_2: Second body
        :type body_2: sl_bodies.Attractor
        :param jacobi_constant: Jacobi constant
        :type jacobi_constant: u.Quantity
        :return: Zero Velocity Curves
        :rtype: np.ndarray
        
        📌 **Notes**
        
        The constant :math:`C` is known as the *Jacobi constant*, after the German mathematician Carl Jacobi (1804-1851),
        who discovered it in 1836. Jacobi's constant may be interpreted as the total energy of the secondary particle
        relative to the rotating frame. :math:`C` is a constant of the motion of the secondary mass just like the energy
        and angular momentum are constants of the relative motion in the two-body problem.
        
        For a given value of the Jacobi constant the curves of zero velocity are determined by the equation
        
            :math:`\\Omega^2 \\cdot (x^2 + y^2) + \\frac{2 \\mu_1}{r_1} + \\frac{2 \\mu_2}{r_2} + 2 C = 0`
        
        These boundaries cannot be crossed by a secondary mass (spacecraft) moving within an allowed region. Since the
        first three terms on the equation are all positive, it follows that the zero velocity curves correspond to
        negative values of the Jacobi constant. Large negative values of :math:`C` mean that the secondary body is far
        from the system center of mass (:math:`x^2 + y^2` is large) or that the body is close to one of the primary
        bodies (:math:`r_1` is small or :math:`r_2` is small).
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 2.12 *Restricted three-body problem*
        - :cite:`kluever`
            - Section 5.6.1 *Jacobi's Integral*
        - :cite:`walter`
            - Section 11.4 *Circular Restricted Three-Body Problem*
            - Section 11.4.2 *Jacobi's Integral*
        """
        
        size: int = 1000
        
        # >>> Validation
        
        # * body_1
        
        err_msg: str | None = sl_validator.validate_attractor(body_1)
        
        if err_msg: sl_logger.logger.warning(err_msg); return np.zeros(shape=(size, size))
        
        # * body_2
        
        err_msg = sl_validator.validate_attractor(body_2)
        
        if err_msg: sl_logger.logger.warning(err_msg); return np.zeros(shape=(size, size))
        
        # * jacobi_constant
        
        err_msg = sl_validator.validate_quantity("jacobi_constant", jacobi_constant, u.km**2 / u.s**2)
        
        if err_msg: sl_logger.logger.warning(err_msg); return np.zeros(shape=(size, size))
        
        # >>> Algorithm
        
        op = Orbit.orbit_parameters(body_1=body_1, body_2=body_2)
        
        C: float = jacobi_constant.to_value(u.km**2 / u.s**2)
        
        OMEGA: float = op.inertial_angular_velocity.to_value(u.rad / u.s)
        
        pi_1: float = op.dimensionless_mass_ratio_1.to_value(u.one)
        
        pi_2: float = op.dimensionless_mass_ratio_2.to_value(u.one)
        
        mu_1: float = op.gravitational_parameter_1.to_value(u.km**3 / u.s**2)
        
        mu_2: float = op.gravitational_parameter_2.to_value(u.km**3 / u.s**2)
        
        r_12: float = sl_bodies.BODIES[body_2].semi_major_axis.to_value(u.km)
        
        # ? Create a grid using the Lagrange points as reference
        
        x_arr: np.ndarray = np.linspace(
            start=op.libration_point_3[0].to_value(u.km) * 1.5,
            stop=op.libration_point_2[0].to_value(u.km) * 1.5,
            num=size)
        
        y_arr: np.ndarray = np.linspace(
            start=op.libration_point_5[1].to_value(u.km) * 2,
            stop=op.libration_point_4[1].to_value(u.km) * 2,
            num=size)
        
        regions: np.ndarray = np.zeros(shape=(size, size))
        
        # ? Iterate and apply the Jacobi equation
        
        for x_idx, x in enumerate(x_arr):
            
            for y_idx, y in enumerate(y_arr):
            
                r_1: float = np.sqrt((x + pi_2 * r_12)**2 + y**2)
                r_2: float = np.sqrt((x - pi_1 * r_12)**2 + y**2)
                
                v_squared: float = OMEGA**2 * (x**2 + y**2) + 2 * mu_1 / r_1 + 2 * mu_2 / r_2 + 2 * C
                
                regions[x_idx][y_idx] = +1 if v_squared >= 0.0 else 0.0
        
        return regions
    
    # --- PUBLIC ---
    
    def init(
        self,
        body_1: sl_bodies.Attractor,
        body_2: sl_bodies.Attractor,
        position: u.Quantity,
        velocity: u.Quantity) -> None:
        """
        Initializes the orbit based on cartesian position and velocity vectors.

        :param body_1: First body
        :type body_1: sl_bodies.Attractor
        :param body_2: Second body
        :type body_2: sl_bodies.Attractor
        :param position: Position vector
        :type position: u.Quantity
        :param velocity: Velocity vector
        :type velocity: u.Quantity
        """
        
        self.ready = False
        
        # >>> Validation
        
        # * body_1
        
        err_msg: str | None = sl_validator.validate_attractor(body_1)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # * body_2
        
        err_msg = sl_validator.validate_attractor(body_2)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # * position
        
        err_msg = sl_validator.validate_quantity_vector("position", position, u.km, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # * velocity
        
        err_msg = sl_validator.validate_quantity_vector("velocity", velocity, u.km / u.s, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return
        
        # >>> Initialization
        
        self.ready = True
        
        self.body_1 = body_1
        
        self.body_2 = body_2
        
        self.position = ty.cast(np.ndarray, position.to(u.km).to_value())
        
        self.velocity = ty.cast(np.ndarray, velocity.to(u.km / u.s).to_value())
    
    def propagate_for(self, delta: time.TimeDelta, dimensionless: bool = False) -> sl_results.ResultCR3BP:
        """
        Propagates the orbit for the given delta time.

        :param delta: Delta time for propagation
        :type delta: time.TimeDelta
        :param dimensionless: If True use dimensionless equations of motion, defaults to False
        :type dimensionless: bool, optional
        :return: Integration result
        :rtype: sl_results.ResultCR3BP
        """
        
        result = sl_results.ResultCR3BP(success=False)
        
        # >>> Validation
        
        # * delta
        
        err_msg: str | None = sl_validator.validate_time_delta("delta", delta)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        if not self.ready:
            
            sl_logger.logger.error("'Orbit' object is not ready")
            
            return result
        
        # >>> Algorithm
        
        parameters: sl_orbit_parameters.OrbitParametersCR3BP =\
            Orbit.orbit_parameters(body_1=self.body_1, body_2=self.body_2)
        
        if dimensionless:
            
            L: float = sl_bodies.BODIES[self.body_2].semi_major_axis.to_value(u.km)
            n: float = parameters.inertial_angular_velocity.to_value(u.rad / u.s)
            
            solution: dict = ode.solve_ivp(
                fun=self._equations_relative_motion_dimensionless,
                t_span=[0, delta.to_value(u.s) * n],
                y0=np.concat([self.position / L, self.velocity / L / n]),
                method='RK45',
                args=(parameters, ),
                rtol=1e-12,
                atol=1e-12)
            
            result.success = solution['success']
            result.time = solution['t'] / n * u.s
            result.position_x = solution['y'][0, :] * L * u.km
            result.position_y = solution['y'][1, :] * L * u.km
            result.position_z = solution['y'][2, :] * L * u.km
            result.velocity_x = solution['y'][3, :] * n * L * u.km / u.s
            result.velocity_y = solution['y'][4, :] * n * L * u.km / u.s
            result.velocity_z = solution['y'][5, :] * n * L * u.km / u.s
        
        else:
            
            solution: dict = ode.solve_ivp(
                fun=self._equations_relative_motion,
                t_span=[0, delta.to_value(u.s)],
                y0=np.concat([self.position, self.velocity]),
                method='RK45',
                args=(parameters, ),
                rtol=1e-12,
                atol=1e-12)
            
            result.success = solution['success']
            result.time = solution['t'] * u.s
            result.position_x = solution['y'][0, :] * u.km
            result.position_y = solution['y'][1, :] * u.km
            result.position_z = solution['y'][2, :] * u.km
            result.velocity_x = solution['y'][3, :] * u.km / u.s
            result.velocity_y = solution['y'][4, :] * u.km / u.s
            result.velocity_z = solution['y'][5, :] * u.km / u.s
        
        return result
    
    def propagate_libration_for(
        self,
        delta: time.TimeDelta,
        libration_point: sl_enums.LibrationPoint) -> sl_results.ResultCR3BP:
        """
        Propagates the orbit for the given delta time around a selected libration point.

        :param delta: Delta time for propagation
        :type delta: time.TimeDelta
        :param libration_point: Selected equilibrium point (L1-L5)
        :type libration_point: sl_enums.LibrationPoint
        :return: Integration result
        :rtype: sl_results.ResultCR3BP
        
        📌 **Notes**
        
        It uses the dimensionless libration-point-centered equations of motion:
        
        - Distance unit: separation between the primaries (:math:`L`)
        - Time unit: :math:`1 / n`, where :math:`n` is the mean motion of the primaries
        - Velocity unit: :math:`n \\cdot L`
        
        The result is converted back to physical units.
        """
        
        result = sl_results.ResultCR3BP(success=False)
        
        # >>> Validation
        
        # * delta
        
        err_msg: str | None = sl_validator.validate_time_delta("delta", delta)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * delta
        
        err_msg = sl_validator.validate_type("libration_point", libration_point, sl_enums.LibrationPoint)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        if not self.ready:
            
            sl_logger.logger.error("'Orbit' object is not ready")
            
            return result
        
        # >>> Algorithm
        
        parameters: sl_orbit_parameters.OrbitParametersCR3BP =\
            Orbit.orbit_parameters(body_1=self.body_1, body_2=self.body_2)
            
        L: float = sl_bodies.BODIES[self.body_2].semi_major_axis.to_value(u.km)
        n: float = parameters.inertial_angular_velocity.to_value(u.rad / u.s)
        
        solution: dict = ode.solve_ivp(
            fun=self._equations_relative_motion_libration_dimensionless,
            t_span=[0, delta.to_value(u.s) * n],
            y0=np.concat([self.position / L, self.velocity / L / n]),
            method='RK45',
            args=(parameters, libration_point),
            rtol=1e-12,
            atol=1e-12)
        
        result.success = solution['success']
        result.time = solution['t'] / n * u.s
        result.position_x = solution['y'][0, :] * L * u.km
        result.position_y = solution['y'][1, :] * L * u.km
        result.position_z = solution['y'][2, :] * L * u.km
        result.velocity_x = solution['y'][3, :] * n * L * u.km / u.s
        result.velocity_y = solution['y'][4, :] * n * L * u.km / u.s
        result.velocity_z = solution['y'][5, :] * n * L * u.km / u.s
        
        return result
    
    def propagate_eulerian_for(
        self,
        delta: time.TimeDelta,
        libration_point: sl_enums.LibrationPoint) -> sl_results.ResultCR3BP:
        """
        Propagates the orbit for the given delta time around a selected eulerian libration point.

        :param delta: Delta time for propagation
        :type delta: time.TimeDelta
        :param libration_point: Selected eularian point (L1-L3)
        :type libration_point: sl_enums.LibrationPoint
        :return: Integration result
        :rtype: sl_results.ResultCR3BP
        
        📌 **Notes**
        
        It uses the dimensionless libration-point-centered equations of motion:
        
        - Distance unit: separation between the primaries (:math:`L`)
        - Time unit: :math:`1 / n`, where :math:`n` is the mean motion of the primaries
        - Velocity unit: :math:`n \\cdot L`
        
        The result is converted back to physical units.
        """
        
        result = sl_results.ResultCR3BP(success=False)
        
        # >>> Validation
        
        # * delta
        
        err_msg: str | None = sl_validator.validate_time_delta("delta", delta)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * delta
        
        err_msg = sl_validator.validate_type("libration_point", libration_point, sl_enums.LibrationPoint)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        if not self.ready:
            
            sl_logger.logger.error("'Orbit' object is not ready")
            
            return result
        
        # >>> Algorithm
        
        parameters: sl_orbit_parameters.OrbitParametersCR3BP =\
            Orbit.orbit_parameters(body_1=self.body_1, body_2=self.body_2)
            
        L: float = sl_bodies.BODIES[self.body_2].semi_major_axis.to_value(u.km)
        n: float = parameters.inertial_angular_velocity.to_value(u.rad / u.s)
        
        solution: dict = ode.solve_ivp(
            fun=self._equations_relative_motion_eulerian_dimensionless,
            t_span=[0, delta.to_value(u.s) * n],
            y0=np.concat([self.position / L, self.velocity / L / n]),
            method='RK45',
            args=(parameters, libration_point),
            rtol=1e-12,
            atol=1e-12)
        
        result.success = solution['success']
        result.time = solution['t'] / n * u.s
        result.position_x = solution['y'][0, :] * L * u.km
        result.position_y = solution['y'][1, :] * L * u.km
        result.position_z = solution['y'][2, :] * L * u.km
        result.velocity_x = solution['y'][3, :] * n * L * u.km / u.s
        result.velocity_y = solution['y'][4, :] * n * L * u.km / u.s
        result.velocity_z = solution['y'][5, :] * n * L * u.km / u.s
        
        return result
    
    def propagate_lagrangian_for(
        self,
        delta: time.TimeDelta,
        libration_point: sl_enums.LibrationPoint) -> sl_results.ResultCR3BP:
        """
        Propagates the orbit for the given delta time around a selected lagrangian libration point.

        :param delta: Delta time for propagation
        :type delta: time.TimeDelta
        :param libration_point: Selected lagrangian point (L4-L5)
        :type libration_point: sl_enums.LibrationPoint
        :return: Integration result
        :rtype: sl_results.ResultCR3BP
        
        📌 **Notes**
        
        It uses the dimensionless libration-point-centered equations of motion:
        
        - Distance unit: separation between the primaries (:math:`L`)
        - Time unit: :math:`1 / n`, where :math:`n` is the mean motion of the primaries
        - Velocity unit: :math:`n \\cdot L`
        
        The result is converted back to physical units.
        """
        
        result = sl_results.ResultCR3BP(success=False)
        
        # >>> Validation
        
        # * delta
        
        err_msg: str | None = sl_validator.validate_time_delta("delta", delta)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        # * delta
        
        err_msg = sl_validator.validate_type("libration_point", libration_point, sl_enums.LibrationPoint)
        
        if err_msg: sl_logger.logger.warning(err_msg); return result
        
        if not self.ready:
            
            sl_logger.logger.error("'Orbit' object is not ready")
            
            return result
        
        # >>> Algorithm
        
        parameters: sl_orbit_parameters.OrbitParametersCR3BP =\
            Orbit.orbit_parameters(body_1=self.body_1, body_2=self.body_2)
            
        L: float = sl_bodies.BODIES[self.body_2].semi_major_axis.to_value(u.km)
        n: float = parameters.inertial_angular_velocity.to_value(u.rad / u.s)
        
        solution: dict = ode.solve_ivp(
            fun=self._equations_relative_motion_lagrangian_dimensionless,
            t_span=[0, delta.to_value(u.s) * n],
            y0=np.concat([self.position / L, self.velocity / L / n]),
            method='RK45',
            args=(parameters, libration_point),
            rtol=1e-12,
            atol=1e-12)
        
        result.success = solution['success']
        result.time = solution['t'] / n * u.s
        result.position_x = solution['y'][0, :] * L * u.km
        result.position_y = solution['y'][1, :] * L * u.km
        result.position_z = solution['y'][2, :] * L * u.km
        result.velocity_x = solution['y'][3, :] * n * L * u.km / u.s
        result.velocity_y = solution['y'][4, :] * n * L * u.km / u.s
        result.velocity_z = solution['y'][5, :] * n * L * u.km / u.s
        
        return result
    
    # --- PRIVATE ---
    
    def _equations_relative_motion(
        self,
        t: float,
        X: np.ndarray,
        orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP) -> np.ndarray:
        """
        Equations of motion for the **Circular Restricted Three-Body Problem** (CR3BP) in the rotating synodic frame.

        :param t: Time (included for ODE solver compatibility)
        :type t: float
        :param X: State vector :math:`[\\vec{r} = (x, y, z), \\vec{v} = (v_x, v_y, v_z)]`
        :type X: np.ndarray
        :param orbit_parameters: Precomputed CR3BP parameters
        :type orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP
        :return: Time derivative :math:`\\dot{x}`
        :rtype: np.ndarray
        
        📌 **Notes**
        
        This function integrates the standard dimensional circular restricted three-body equations in the uniformly
        rotating synodic frame:
        
        .. math::

            \\begin{aligned}
            
            \\frac{dx}{dt} &= v_x

            \\frac{dy}{dt} &= v_y

            \\frac{dz}{dt} &= v_z

            \\frac{dv_x}{dt} &= + 2 \\Omega v_y + \\Omega^2 x - \\frac{\\mu_1 (x - x_1)}{r_1^3} - \\frac{\\mu_2 (x - x_2)}{r_2^3}

            \\frac{dv_y}{dt} &= - 2 \\Omega v_x + \\Omega^2 y - \\frac{\\mu_1 y}{r_1^3} - \\frac{\\mu_2 y}{r_2^3}

            \\frac{dv_z}{dt} &= - \\frac{\\mu_1 z}{r_1^3} - \\frac{\\mu_2 z}{r_2^3}
            
            \\end{aligned}

        Let the two primaries have gravitational parameters :math:`\\mu_1` and :math:`\\mu_2`, and let their positions
        along the x-axis in the rotating frame be :math:`x_1` and :math:`x_2`. The distances from the third body to each
        primary are:

            :math:`r_1 = \\sqrt{(x - x_1)^2 + y^2 + z^2}`
            
            :math:`r_2 = \\sqrt{(x - x_2)^2 + y^2 + z^2}`

        The rotating frame has angular velocity :math:`\\Omega`, so the Coriolis and centrifugal terms appear explicitly.
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 2.12 *Restricted three-body problem*
        - :cite:`kluever`
            - Section 5.6 *Circular Restricted Three-Body Problem*
        """
        
        # ? Data
        
        x, y, z, v_x, v_y, v_z = X
        
        # ? Orbit parameters
        
        OMEGA: float = orbit_parameters.inertial_angular_velocity.to_value(u.rad / u.s)
        
        mu_1: float = orbit_parameters.gravitational_parameter_1.to_value(u.km**3 / u.s**2)
        
        mu_2: float = orbit_parameters.gravitational_parameter_2.to_value(u.km**3 / u.s**2)
        
        x_1: float = orbit_parameters.body_position_1.to_value(u.km)
        
        x_2: float = orbit_parameters.body_position_2.to_value(u.km)
        
        r_1: float = np.sqrt((x - x_1)**2 + y**2 + z**2)
        
        r_2: float = np.sqrt((x - x_2)**2 + y**2 + z**2)
        
        # ? ODE
        
        dx_dt: np.ndarray = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = + 2 * OMEGA * v_y + OMEGA**2 * x - mu_1 / r_1**3 * (x - x_1) - mu_2 / r_2**3 * (x - x_2)
        dx_dt[4] = - 2 * OMEGA * v_x + OMEGA**2 * y - mu_1 / r_1**3 * y - mu_2 / r_2**3 * y
        dx_dt[5] = - mu_1 / r_1**3 * z - mu_2 / r_2**3 * z
        
        return dx_dt
    
    def _equations_relative_motion_dimensionless(
        self,
        t: float,
        X: np.ndarray,
        orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP) -> np.ndarray:
        """
        Dimensionless differential equation of motion (EoM in the CR3BP) (actually three coupled scalar equations) of a
        small body at :math:`\\vec{\\rho} = (\\xi, \\eta, \\zeta)` moving in the normalized gravitational potential
        :math:`U'` of a minor primary with reduced mass :math:`\\mu` at :math:`\\csi_2 = 1 - \\mu` plus a major primary
        with reduced mass :math:`1 - \\mu` at location :math:`\\csi_1 = - \\mu` expressed in the synodic (co-rotating)
        barycentric reference frame.

        :param t: Dimensionless time (included for ODE solver compatibility)
        :type t: float
        :param X: State vector :math:`[\\vec{r} = (\\xi, \\eta, \\zeta), \\vec{v} = (v_{\\xi}, v_{\\eta}, v_{\\zeta})]`
        :type X: np.ndarray
        :param orbit_parameters: Precomputed CR3BP parameters
        :type orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP
        :return: Time derivative :math:`\\dot{x}`
        :rtype: np.ndarray
        
        📌 **Notes**
        
        This function integrates the standard nondimensional circular restricted three-body equations in the uniformly
        rotating synodic frame:
        
        .. math::

            \\begin{aligned}
            
            \\frac{d\\xi}{dt} &= v_{\\xi}
            
            \\frac{d\\eta}{dt} &= v_{\\eta}
            
            \\frac{d\\zeta}{dt} &= v_{\\zeta}

            \\frac{dv_{\\xi}}{dt} &= + 2 v_{\\eta} + \\xi - \\frac{(1 - \\mu)(\\xi + \\mu)}{\\rho_1^3} - \\frac{\\mu\\left[\\xi - (1 - \\mu)\\right]}{\\rho_2^3}

            \\frac{dv_{\\eta}}{dt} &= - 2 v_{\\xi} + \\eta - \\frac{(1 - \\mu)\\eta}{\\rho_1^3} - \\frac{\\mu\\eta}{\\rho_2^3}

            \\frac{dv_{\\zeta}}{dt} &= - \\frac{(1 - \\mu)\\zeta}{\\rho_1^3} - \\frac{\\mu\\zeta}{\\rho_2^3}
            
            \\end{aligned}
        
        .. math::
        
            \\begin{aligned}
            
            \\rho_1 &= \\sqrt{(\\xi + \\mu)^2 + \\eta^2 + \\zeta^2}
            
            \\rho_2 &= \\sqrt{\\left[\\xi - (1 - \\mu)\\right]^2 + \\eta^2 + \\zeta^2}
            
            \\end{aligned}
        
        with the standard CR3BP normalization:
        
        - Distance unit: separation between the two primaries
        - Mass unit: total mass of the system
        - Time unit: chosen such that the mean motion :math:`n = 1`
        - Gravitational parameters satisfy :math:`\\mu_1 = 1 - \\mu` and math:`\\mu_2 = \\mu`
        
        📖 **References**
        
        - :cite:`walter`
            - Section 11.4 *Circular Restricted Three-Body Problem*
            - Section 11.4.1 *Equation of Motion*
        """
        
        # ? Data
        
        xi, eta, zeta, v_csi, v_eta, v_zeta = X
        
        # ? Orbit parameters
        
        mu: float = orbit_parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        drho_1: float = np.sqrt((xi + mu)**2 + eta**2 + zeta**2)
        
        drho_2: float = np.sqrt((xi - (1 - mu))**2 + eta**2 + zeta**2)
        
        # ? ODE
        
        dx_dt: np.ndarray = np.zeros(shape=(6))
        
        dx_dt[0] = v_csi
        dx_dt[1] = v_eta
        dx_dt[2] = v_zeta
        dx_dt[3] = + 2 * v_eta + xi - (1 - mu) / drho_1**3 * (xi + mu) - mu / drho_2**3 * (xi - (1 - mu))
        dx_dt[4] = - 2 * v_csi + eta - (1 - mu) / drho_1**3 * eta - mu / drho_2**3 * eta
        dx_dt[5] = - (1 - mu) / drho_1**3 * zeta - mu / drho_2**3 * zeta
        
        return dx_dt
    
    def _equations_relative_motion_libration_dimensionless(
        self,
        t: float,
        X: np.ndarray,
        orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP,
        libration_point: sl_enums.LibrationPoint) -> np.ndarray:
        """
        Dimensionless differential equation of motion of a massless particle relative to a libration point in the CR3BP
        rotating frame, preserving the nondimensional structure of the classical formulation.

        :param t: Dimensionless time (included for ODE solver compatibility)
        :type t: float
        :param X: State vector :math:`[\\vec{r} = (x, y, z), \\vec{v} = (v_x, v_y, v_z)]`
        :type X: np.ndarray
        :param orbit_parameters: Precomputed CR3BP parameters
        :type orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP
        :param libration_point: Selected libration point
        :type libration_point: sl_enums.LibrationPoint
        :return: Time derivative :math:`\\dot{x}`
        :rtype: np.ndarray
        
        📌 **Notes**
        
        This function integrates the nondimensional circular restricted three-body equations in a
        libration-point-centered rotating synodic frame:
        
        .. math::
        
            \\begin{aligned}
            
            \\frac{dx}{dt} &= v_x
            
            \\frac{dy}{dt} &= v_y
            
            \\frac{dz}{dt} &= v_z

            \\frac{dv_x}{dt} &= + 2 v_y + x - \\frac{(1 - \\mu)(x - x_1)}{\\Delta r_1^3} - \\frac{\\mu(x - x_2)}{\\Delta r_2^3}

            \\frac{dv_y}{dt} &= - 2 v_x + y - \\frac{(1 - \\mu)(y - y_1)}{\\Delta r_1^3} - \\frac{\\mu(y - y_2)}{\\Delta r_2^3}

            \\frac{dv_z}{dt} &= - \\frac{(1 - \\mu)z}{\\Delta r_1^3} - \\frac{\\mu z}{\\Delta r_2^3}
            
            \\end{aligned}
        
        .. math::
        
            \\begin{aligned}
            
            \\Delta r_1 &= \\sqrt{(x - x_1)^2 + (y - y_1)^2 + z^2}
            
            \\Delta r_2 &= \\sqrt{(x - x_2)^2 + (y - y_2)^2 + z^2}
            
            \\end{aligned}
        
        with the standard CR3BP normalization:
        
        - Distance unit: separation between the two primaries
        - Mass unit: total mass of the system
        - Time unit: chosen such that the mean motion :math:`n = 1`
        - Gravitational parameters satisfy :math:`\\mu_1 = 1 - \\mu` and math:`\\mu_2 = \\mu`
        
        The libration point coordinates :math:`(\\xi_L, \\eta_L)` are obtained from the supplied orbit parameters and
        used to shift the frame so that the origin coincides with the selected equilibrium point.
        
        📖 **References**
        
        - :cite:`walter`
            - Section 11.5 *Dynamics About Libration Points*
            - Section 11.5.1 *Equation of Motion*
        """
        
        # ? Data
        
        x, y, z, v_x, v_y, v_z = X
        
        # ? Orbit parameters
        
        mu: float = orbit_parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        L: float = orbit_parameters.body_distance.to_value(u.km)
        
        # ? Libration point
        
        csi_lp: float = 0.0
        eta_lp: float = 0.0
        
        match libration_point:
            
            case sl_enums.LibrationPoint.L1:
            
                csi_lp = orbit_parameters.libration_point_1[0].to_value(u.km) / L
                eta_lp = orbit_parameters.libration_point_1[1].to_value(u.km) / L
        
            case sl_enums.LibrationPoint.L2:
            
                csi_lp = orbit_parameters.libration_point_2[0].to_value(u.km) / L
                eta_lp = orbit_parameters.libration_point_2[1].to_value(u.km) / L
                
            case sl_enums.LibrationPoint.L3:
            
                csi_lp = orbit_parameters.libration_point_3[0].to_value(u.km) / L
                eta_lp = orbit_parameters.libration_point_3[1].to_value(u.km) / L
                
            case sl_enums.LibrationPoint.L4:
            
                csi_lp = orbit_parameters.libration_point_4[0].to_value(u.km) / L
                eta_lp = orbit_parameters.libration_point_4[1].to_value(u.km) / L
                
            case sl_enums.LibrationPoint.L5:
            
                csi_lp = orbit_parameters.libration_point_5[0].to_value(u.km) / L
                eta_lp = orbit_parameters.libration_point_5[1].to_value(u.km) / L
        
        rho_lp: np.ndarray = np.array([csi_lp, eta_lp, 0])
        
        # ? Bodies relative position
        
        csi_1: float = orbit_parameters.body_position_1.to_value(u.km) / L
        eta_1: float = 0
        csi_2: float = orbit_parameters.body_position_2.to_value(u.km) / L
        eta_2: float = 0
        
        x_1: float = csi_1 - csi_lp
        y_1: float = eta_1 - eta_lp
        x_2: float = csi_2 - csi_lp
        y_2: float = eta_2 - eta_lp
        
        dr_1: float = np.sqrt((x - x_1)**2 + (y - y_1)**2 + z**2)
        
        dr_2: float = np.sqrt((x - x_2)**2 + (y - y_2)**2 + z**2)
        
        # ? ODE
        
        dx_dt: np.ndarray = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = + 2 * v_y + x + rho_lp[0] - (1 - mu) / dr_1**3 * (x - x_1) - mu / dr_2**3 * (x - x_2)
        dx_dt[4] = - 2 * v_x + y + rho_lp[1] - (1 - mu) / dr_1**3 * (y - y_1) - mu / dr_2**3 * (y - y_2)
        dx_dt[5] =                 rho_lp[2] - (1 - mu) / dr_1**3 * z         - mu / dr_2**3 * z
        
        return dx_dt
    
    def _equations_relative_motion_eulerian_dimensionless(
        self,
        t: float,
        X: np.ndarray,
        orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP,
        libration_point: sl_enums.LibrationPoint) -> np.ndarray:
        """
        Dimensionless linearized (Eulerian) CR3BP equations of motion about a collinear libration point (L1, L2, or L3)
        in the rotating synodic frame.

        :param t: Dimensionless time (included for ODE solver compatibility)
        :type t: float
        :param X: State vector :math:`[\\vec{r} = (x, y, z), \\vec{v} = (v_x, v_y, v_z)]`
        :type X: np.ndarray
        :param orbit_parameters: Precomputed CR3BP parameters
        :type orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP
        :param libration_point: Selected eulerian libration point
        :type libration_point: sl_enums.LibrationPoint
        :return: Time derivative :math:`\\dot{x}`
        :rtype: np.ndarray
        
        📌 **Notes**
        
        This function integrates the nondimensional linearized Eulerian equations in a libration-point-centered rotating
        synodic frame:
        
        .. math::
        
            \\begin{aligned}
            
            \\frac{dx}{dt} &= v_x
            
            \\frac{dy}{dt} &= v_y
            
            \\frac{dz}{dt} &= v_z

            \\frac{dv_x}{dt} &= + 2 v_y - (1 + 2 c_2) x

            \\frac{dv_y}{dt} &= - 2 v_x - (1 - c_2) y

            \\frac{dv_z}{dt} &= - c_2 z
            
            \\end{aligned}
        
        with the standard CR3BP normalization:
        
        - Distance unit: separation between the two primaries
        - Mass unit: total mass of the system
        - Time unit: chosen such that the mean motion :math:`n = 1`
        - Gravitational parameters satisfy :math:`\\mu_1 = 1 - \\mu` and :math:`\\mu_2 = \\mu`
        
        The dimensionless Eulerian approximation is obtained by linearizing the CR3BP equations of motion around a
        collinear equilibrium point. The nonlinear gravitational terms are replaced by constant curvature coefficients
        (:math:`c_2`) derived from the second derivatives of the effective potential at the chosen libration point.
        The curvature parameter :math:`c_2` is selected according to the libration point:
        
        - L1: :math:`c_2 = 4 + 6 \\lambda + O(\\lambda^2)`
        - L2: :math:`c_2 = 4 - 6 \\lambda + O(\\lambda^2)`
        - L3: :math:`c_2 = 1 + (7/8) \\mu + O(\\mu^2)`
        
        where :math:`\\lambda = (\\mu / 3)^{1/3}`. These values arise from the second derivatives of the effective
        potential evaluated at the collinear equilibrium points.
        
        This model represents the second-order Taylor expansion of the CR3BP equations around an equilibrium point. The
        nonlinear gravitational terms are replaced by constant coefficients derived from the curvature of the effective
        potential at the selected libration point. The resulting system is linear and captures the local saddle-center
        dynamics characteristic of collinear points.
        
        These equations describe the local dynamics near a collinear libration point and are commonly used for stability
        analysis, invariant manifold computation, and initialization of periodic orbits.
        
        📖 **References**
        
        - :cite:`walter`
            - Section 11.5 *Dynamics About Libration Points*
            - Section 11.5.2 *Collinear Libration Points*
        """
        
        # ? Data
        
        x, y, z, v_x, v_y, v_z = X
        
        # ? Orbit parameters
        
        mu: float = orbit_parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        # ? Curvature parameter
        
        lambda_: float = (mu / 3)**(1/3)
        
        c_2: float = 0.0
        
        match libration_point:
            
            case sl_enums.LibrationPoint.L1: c_2 = 4 + 6 * lambda_
            case sl_enums.LibrationPoint.L2: c_2 = 4 - 6 * lambda_
            case sl_enums.LibrationPoint.L3: c_2 = 1 + 7/8 * mu
        
        # ? ODE
        
        dx_dt: np.ndarray = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = + 2 * v_y + (1 + 2 * c_2) * x
        dx_dt[4] = - 2 * v_x + (1 - c_2) * y
        dx_dt[5] =           - c_2 * z
        
        return dx_dt
    
    def _equations_relative_motion_lagrangian_dimensionless(
        self,
        t: float,
        X: np.ndarray,
        orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP,
        libration_point: sl_enums.LibrationPoint) -> np.ndarray:
        """
        Dimensionless linearized (Lagrangian) CR3BP equations of motion about an equilateral libration point (L4 or L5)
        in the rotating synodic frame.

        :param t: Dimensionless time (included for ODE solver compatibility)
        :type t: float
        :param X: State vector :math:`[\\vec{r} = (x, y, z), \\vec{v} = (v_x, v_y, v_z)]`
        :type X: np.ndarray
        :param orbit_parameters: Precomputed CR3BP parameters
        :type orbit_parameters: sl_orbit_parameters.OrbitParametersCR3BP
        :param libration_point: Selected lagrangian libration point
        :type libration_point: sl_enums.LibrationPoint
        :return: Time derivative :math:`\\dot{x}`
        :rtype: np.ndarray
        
        📌 **Notes**
        
        This function integrates the nondimensional linearized Lagrangian equations in a libration-point-centered
        rotating synodic frame:
        
        .. math::
        
            \\begin{aligned}
                    
            \\frac{dx}{dt} &= v_x
            
            \\frac{dy}{dt} &= v_y
            
            \\frac{dz}{dt} &= v_z

            \\frac{dv_x}{dt} &= + 2 v_y + \\frac{3}{4} x + c y

            \\frac{dv_y}{dt} &= - 2 v_x + \\frac{9}{4} y + c x

            \\frac{dv_z}{dt} &= - z
            
            \\end{aligned}
        
        with the standard CR3BP normalization:
        
        - Distance unit: separation between the two primaries
        - Mass unit: total mass of the system
        - Time unit: chosen such that the mean motion :math:`n = 1`
        - Gravitational parameters satisfy :math:`\\mu_1 = 1 - \\mu` and :math:`\\mu_2 = \\mu`
        
        The dimensionless Lagrangian approximation is obtained by linearizing the CR3BP equations of motion around an
        equilateral equilibrium point. The nonlinear gravitational terms are replaced by constant curvature coefficients
        (:math:`c`) derived from the second derivatives of the effective potential at the chosen libration point.
        For the equilateral points, the coupling coefficient :math:`c` is:
                
        - L4: :math:`c = +(3\\sqrt{3}/4)(1 - 2 \\mu)`
        - L5: :math:`c = -(3\\sqrt{3}/4)(1 - 2 \\mu)`
                
        These values arise from the mixed second derivatives of the effective potential at the triangular equilibrium
        points.
        
        This model represents the second-order Taylor expansion of the CR3BP equations around an equilibrium point. The
        nonlinear gravitational terms are replaced by constant coefficients derived from the curvature of the effective
        potential at the selected libration point. The resulting system is linear and captures the local saddle-center
        dynamics characteristic of equilateral points.
        
        These equations describe the local dynamics near an equilateral libration point and are commonly used for
        stability analysis, invariant manifold computation, and initialization of periodic orbits.
        
        📖 **References**
        
        - :cite:`walter`
            - Section 11.5 *Dynamics About Libration Points*
            - Section 11.5.3 *Equilateral Libration Points*
        """
        
        # ? Data
        
        x, y, z, v_x, v_y, v_z = X
        
        # ? Orbit parameters
        
        mu: float = orbit_parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        # ? Coupling coefficient
        
        c: float = 0.0
        
        match libration_point:
            
            case sl_enums.LibrationPoint.L4: c = + 3 * np.sqrt(3) * (1 - 2 * mu) / 4
            case sl_enums.LibrationPoint.L5: c = - 3 * np.sqrt(3) * (1 - 2 * mu) / 4
        
        # ? ODE
        
        dx_dt: np.ndarray = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = + 2 * v_y + 3/4 * x + c * y
        dx_dt[4] = - 2 * v_x + 9/4 * y + c * x
        dx_dt[5] =           - z
        
        return dx_dt
