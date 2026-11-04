import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.optimize as optimize
import typing as ty

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.n_body_models.conversions as sl_conversions
import spacelab.models.orbit_parameters as sl_orbit_parameters
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

class LagrangeCoefficients():
    """
    The *f* and *g* functions are referred to as the **Lagrange coefficients** after Joseph- Louis Lagrange (1736-1813),
    a French mathematical physicist whose numerous contributions include calculations of planetary motion.
    
    Kepler's equation may also be written in terms of a **Universal Variable**, or **Universal 'anomaly'** :math:`\\chi`,
    that is valid for all orbits.
    
    📌 **Notes**
    
    Position and velocity vectors :math:`\\vec{r}` and :math:`\\vec{v}` are linear combinations of the initial position
    and velocity vectors. The Lagrange coefficients and their time derivatives are themselves functions of time and the
    initial conditions.
    
    Observe that using the Lagrange coefficients to determine the position and velocity from the initial conditions does
    not require knowing the type of orbit we are dealing with (ellipse, parabola, hyperbola), since the eccentricity
    does not appear in the equations. However, the initial position and velocity give us that information.
    
    📖 **References**
    
    - :cite:`curtis`
        - Chapter 2 *The Two-Body Problem*
        - Chapter 3 *Orbital Position as a Function of Time*
    - :cite:`kluever`
        - Chapter 4 *Time of Flight*
    - :cite:`walter`
        - Chapter 7 *Orbits*
    """
    
    # --- STATIC ---
    
    @staticmethod
    def propagate_of_angle( # NOSONAR python:S3776
        attractor: sl_bodies.Attractor,
        initial_position: u.Quantity,
        initial_velocity: u.Quantity,
        delta_true_anomaly: u.Quantity,
        true_anomalies: ty.List[u.Quantity] | None = None,
        angle_type: sl_enums.AngleType = sl_enums.AngleType.TRUE_ANOMALY) -> ty.List[u.Quantity]:
        """
        Given initial position and velocity, find position and velocity after true anomaly changes by delta.

        :param attractor: Main attractor
        :type attractor: sl_bodies.Attractor
        :param initial_position: Initial position vector
        :type initial_position: u.Quantity
        :param initial_velocity: Initial velocity vector
        :type initial_velocity: u.Quantity
        :param delta_true_anomaly: True anomaly variation
        :type delta_true_anomaly: u.Quantity
        :param true_anomalies: Delta time between eccentric anomalies, defaults to None
        :type true_anomalies: ty.List[u.Quantity] | None
        :param angle_type: Angle type associated to the underlying algorithm, defaults to sl_enums.AngleType.TRUE_ANOMALY
        :type angle_type: u.Quantity
        :return: [Position, Velocity]
        :rtype: ty.List[u.Quantity]
        
        📌 **Notes**
        
        Orbit propagation using the Lagrangian coefficients provides an alternative technique for determining the future
        state (:math:`\\vec{r}`, :math:`\\vec{v}`) from the initial state (:math:`\\vec{r}_0`, :math:`\\vec{v}_0`) for a
        selected orbit position :math:`\\theta`. The key point is that the orbit is known and we have selected the
        future angular position :math:`\\theta`.
        
        Selecting the angle type equal to :attr:`~spacelab.enums.AngleType.TRUE_ANOMALY` will use the true anomaly
        variation to propagate the orbit.
        Selecting the angle type equal to :attr:`~spacelab.enums.AngleType.ECCENTRIC_ANOMALY` will use the eccentric
        anomaly variation to propagate the orbit.
        
        It is supposed an elliptical orbit.
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 2.11 *The Lagrange coefficients*
        - :cite:`kluever`
            - Section 4.5 *Orbit Propagation Using Lagrangian Coefficients*
        """
        # >>> Validation
        
        empty: list = [0 * u.km, 0 * u.km / u.s]
        
        # * attractor
        
        err_msg: str | None = sl_validator.validate_attractor(attractor)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * initial_position
        
        err_msg = sl_validator.validate_quantity_vector("initial_position", initial_position, u.km, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * initial_velocity
        
        err_msg = sl_validator.validate_quantity_vector("initial_velocity", initial_velocity, u.km / u.s, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * delta_true_anomaly
        
        err_msg = sl_validator.validate_quantity_angle("delta_true_anomaly", delta_true_anomaly)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * true_anomalies
        
        if angle_type == sl_enums.AngleType.ECCENTRIC_ANOMALY:
            
            if true_anomalies is None or len(true_anomalies) != 2:
            
                sl_logger.logger.warning("'true_anomalies' must be a list of two elements [initial, final]"); return empty
        
            err_msg = sl_validator.validate_quantity("true_anomalies[0]", true_anomalies[0], u.rad)
            
            if err_msg: sl_logger.logger.warning(err_msg); return empty
            
            err_msg = sl_validator.validate_quantity("true_anomalies[1]", true_anomalies[1], u.rad)
            
            if err_msg: sl_logger.logger.warning(err_msg); return empty
            
            if true_anomalies[1] < true_anomalies[0]:
                
                sl_logger.logger.warning("'true_anomalies[1]' must be greater than 'true_anomalies[0]'"); return empty
            
            if true_anomalies[1] - true_anomalies[0] != delta_true_anomaly:
                
                sl_logger.logger.warning("'true_anomalies[1]' - 'true_anomalies[0]' must be equal to 'delta_true_anomaly'"); return empty
        
        # * angle_type
        
        err_msg = sl_validator.validate_type("angle_type", angle_type, sl_enums.AngleType)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # >>> Algorithm
        
        r_0: np.ndarray = initial_position.to_value(u.km)
        
        v_0: np.ndarray = initial_velocity.to_value(u.km / u.s)
        
        delta_theta: float = delta_true_anomaly.to_value(u.rad)
        
        mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2) # ? Gravitational constant [km^3 / s^2]
        
        # ? 1. Magnitudes
        
        r_0_m: float = np.linalg.norm(r_0)
        v_0_m: float = np.linalg.norm(v_0)
        
        # ? 2. Radial Velocity
        
        v_r_0: float = np.dot(r_0, v_0) / r_0_m
        
        # ? 3. Specific Angular momentum
        
        h: float = r_0_m * np.sqrt(v_0_m**2 - v_r_0**2)
        
        # ? 4. Radius
        
        r: float = h**2 / mu * 1 / ( 1 + ( h**2 / (mu * r_0_m) - 1 ) * np.cos(delta_theta) -\
            h * v_r_0 / mu * np.sin(delta_theta) )
        
        # ? 5. Orbit parameters
        
        params: sl_orbit_parameters.OrbitParameters =\
            sl_conversions.cartesian_to_orbit_parameters(
                attractor=attractor, position=initial_position, velocity=initial_velocity)
        
        a: float = params.semimajor_axis.to_value(u.km)
        e: float = params.eccentricity.to_value(u.one)
        n: float = params.mean_motion.to_value(u.rad / u.s)
        
        # ? 6. Orbital positions in time
        
        dt: float = 0.0
        delta_eccentric: float = 0.0
        
        if angle_type == sl_enums.AngleType.ECCENTRIC_ANOMALY:
            
            theta_0: float = true_anomalies[0].to_value(u.rad)
            
            E_0: float = 2 * np.arctan(np.sqrt((1 - e) / (1 + e)) * np.tan(theta_0 / 2))
            
            theta: float = true_anomalies[1].to_value(u.rad)
            
            E: float = 2 * np.arctan(np.sqrt((1 - e) / (1 + e)) * np.tan(theta / 2))
            
            if E_0 < 0:
                
                E_0 += 2 * np.pi
            
            if E < 0:
                
                E += 2 * np.pi
            
            delta_eccentric = E - E_0

            dt = 1 / n * (E - e * np.sin(E) - E_0 + e * np.sin(E_0))
        
        # ? 7. Lagrange coefficients
        
        f: float = 0.0
        g: float = 0.0
        df_dt: float = 0.0
        dg_dt: float = 0.0
        
        if angle_type == sl_enums.AngleType.TRUE_ANOMALY:
        
            f: float = 1 - mu * r / h**2 * (1 - np.cos(delta_theta))
            
            g: float = r * r_0_m / h * np.sin(delta_theta)
            
            df_dt: float = mu / h * (1 - np.cos(delta_theta)) / np.sin(delta_theta) *\
                        (mu / h**2 * (1 - np.cos(delta_theta)) - 1 / r_0_m - 1 / r)
            
            dg_dt: float = 1 - mu * r_0_m / h**2 * (1 - np.cos(delta_theta))
        
        elif angle_type == sl_enums.AngleType.ECCENTRIC_ANOMALY:
            
            f: float = 1 - a / r_0_m * (1 - np.cos(delta_eccentric))
            
            g: float = dt - np.sqrt(a**3 / mu) * (delta_eccentric - np.sin(delta_eccentric))
            
            df_dt: float = - np.sqrt(mu * a) * np.sin(delta_eccentric) / (r * r_0_m)
            
            dg_dt: float = 1 - a / r * (1 - np.cos(delta_eccentric))
        
        # ? 8. Final state
        
        r_f: u.Quantity = (f * r_0 + g * v_0) * u.km
        v_f: u.Quantity = (df_dt * r_0 + dg_dt * v_0) * u.km / u.s
        
        return [r_f, v_f]
    
    @staticmethod
    def S(z: float) -> float: # NOSONAR python:S100
        """
        Stumpff Function S(z) => c_3(z) defined by an infinite series.

        :param z: Variable
        :type z: float
        :return: Evaluation
        :rtype: float
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 3.7 *Universal variables*
        - :cite:`walter`
            - Section 7.4.8 *Universal Variable Formulation*
        """
        
        if z > 0: # ? Ellipse
            
            return (np.sqrt(z) - np.sin(np.sqrt(z))) / np.sqrt(z)**3
        
        elif z < 0: # ? Hyperbola
            
            return (np.sinh(np.sqrt(-z)) - np.sqrt(-z)) / np.sqrt(-z)**3
        
        else: # ? Parabola
            
            return 1/6
    
    @staticmethod
    def C(z: float) -> float: # NOSONAR python:S100
        """
        Stumpff Function C(z) => c_2(z) defined by an infinite series.

        :param z: Variable
        :type z: float
        :return: Evaluation
        :rtype: float
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 3.7 *Universal variables*
        - :cite:`walter`
            - Section 7.4.8 *Universal Variable Formulation*
        """
        
        if z > 0: # ? Ellipse
            
            return (1 - np.cos(np.sqrt(z))) / z
        
        elif z < 0: # ? Hyperbola
            
            return (np.cosh(np.sqrt(-z)) - 1) / (-z)
        
        else: # ? Parabola
            
            return 1/2
        
    @staticmethod
    def universal_kepler_solution(
        attractor: sl_bodies.Attractor,
        initial_position: u.Quantity,
        initial_radial_velocity: u.Quantity,
        alpha: u.Quantity,
        delta_time: time.TimeDelta) -> u.Quantity:
        """
        Calculate the **universal variable** :math:`\\chi` solving the *universal Kepler equation*.

        :param attractor: Main attractor
        :type attractor: sl_bodies.Attractor
        :param initial_position: Initial position
        :type initial_position: u.Quantity
        :param initial_radial_velocity: Initial radial velocity
        :type initial_radial_velocity: u.Quantity
        :param alpha: Parameter alpha (reciprocal of the semimajor axis)
        :type alpha: u.Quantity
        :param delta_time: Delta time
        :type delta_time: time.TimeDelta
        :return: Universal variable :math:`\\chi` [km^0.5]
        :rtype: u.Quantity
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 3.7 *Universal variables*
        """
        
        # >>> Validation
        
        empty: u.Quantity = 0 * u.km**0.5
        
        # * attractor
        
        err_msg: str | None = sl_validator.validate_attractor(attractor)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * initial_position
        
        err_msg = sl_validator.validate_quantity("initial_position", initial_position, u.km)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * initial_radial_velocity
        
        err_msg = sl_validator.validate_quantity("initial_radial_velocity", initial_radial_velocity, u.km / u.s)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * alpha
        
        err_msg = sl_validator.validate_quantity("alpha", alpha, 1 / u.km)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * delta_time
        
        err_msg = sl_validator.validate_time_delta("delta_time", delta_time)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # >>> Algorithm
        
        r_0: float = initial_position.to_value(u.km)
        
        v_r_0: float = initial_radial_velocity.to_value(u.km / u.s)
        
        dt: float = delta_time.to_value(u.s)
        
        alpha: float = alpha.to_value(1 / u.km)
        
        mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
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
        
        chi: float = optimize.newton(f, x0=chi_0, fprime=df, maxiter=100, tol=1e-8)
        
        return chi * u.km**0.5
    
    @staticmethod
    def lagrange_coefficients(
        attractor: sl_bodies.Attractor,
        initial_position: u.Quantity,
        alpha: u.Quantity,
        delta_time: time.TimeDelta,
        universal_anomaly: u.Quantity) -> ty.List[u.Quantity]:
        """
        Calculate the **Lagrange-Gibbs coefficients** :math:`f` and :math:`g` using the universal variable :math:`chi`.

        :param attractor: Main attractor
        :type attractor: sl_bodies.Attractor
        :param initial_position: Initial position
        :type initial_position: u.Quantity
        :param alpha: Parameter alpha (reciprocal of the semimajor axis)
        :type alpha: u.Quantity
        :param delta_time: Delta time
        :type delta_time: time.TimeDelta
        :param universal_anomaly: Universal anomaly (:math:`chi`)
        :type universal_anomaly: u.Quantity
        :return: Lagrange coefficients [f, g]
        :rtype: ty.List[u.Quantity]
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 3.7 *Universal variables*
        """
        
        # >>> Validation
        
        # * attractor
        
        err_msg: str | None = sl_validator.validate_attractor(attractor)
        
        if err_msg: sl_logger.logger.warning(err_msg); return None
        
        # * initial_position
        
        err_msg = sl_validator.validate_quantity("initial_position", initial_position, u.km)
        
        if err_msg: sl_logger.logger.warning(err_msg); return None
        
        # * alpha
        
        err_msg = sl_validator.validate_quantity("alpha", alpha, 1 / u.km)
        
        if err_msg: sl_logger.logger.warning(err_msg); return None
        
        # * delta_time
        
        err_msg = sl_validator.validate_time_delta("delta_time", delta_time)
        
        if err_msg: sl_logger.logger.warning(err_msg); return None
        
        # * universal_anomaly
        
        err_msg = sl_validator.validate_quantity("universal_anomaly", universal_anomaly, u.km**0.5)
        
        if err_msg: sl_logger.logger.warning(err_msg); return None
        
        # >>> Algorithm
        
        r_0: float = initial_position.to_value(u.km)
        
        alpha: float = alpha.to_value(1 / u.km)
        
        dt: float = delta_time.to_value(u.s)
        
        chi: float = universal_anomaly.to_value(u.km**0.5)
        
        mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        f: float = 1 - chi**2 / r_0 * LagrangeCoefficients.C(alpha * chi**2)
        
        g: float = dt - 1 / np.sqrt(mu) * chi**3 * LagrangeCoefficients.S(alpha * chi**2)
        
        return [f * u.one, g * u.s]
    
    @staticmethod
    def propagate_position_velocity(
        attractor: sl_bodies.Attractor,
        initial_position: u.Quantity,
        initial_velocity: u.Quantity,
        delta_time: time.TimeDelta) -> ty.List[u.Quantity]:
        """
        Evaluate the position and velocity after delta time from the initial state using the universal variable
        formulation of Lagrange coefficients.

        :param attractor: _description_
        :type attractor: sl_bodies.Attractor
        :param initial_position: Initial position vector
        :type initial_position: u.Quantity
        :param initial_velocity: Initial velocity vector
        :type initial_velocity: u.Quantity
        :param delta_time: Time variation
        :type delta_time: time.TimeDelta
        :return: [Position, Velocity]
        :rtype: ty.List[u.Quantity]
        
        📖 **References**
        
        - :cite:`curtis`
            - Section 3.7 *Universal variables*
        """
        
        # >>> Validation
        
        empty: list = [0 * u.km, 0 * u.km / u.s]
        
        # * attractor
        
        err_msg: str | None = sl_validator.validate_attractor(attractor)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * initial_position
        
        err_msg = sl_validator.validate_quantity_vector("initial_position", initial_position, u.km, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * initial_velocity
        
        err_msg = sl_validator.validate_quantity_vector("initial_velocity", initial_velocity, u.km / u.s, 3)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # * delta_time
        
        err_msg = sl_validator.validate_time_delta("delta_time", delta_time)
        
        if err_msg: sl_logger.logger.warning(err_msg); return empty
        
        # >>> Algorithm
        
        r_0: np.ndarray = initial_position.to_value(u.km)
        
        v_0: np.ndarray = initial_velocity.to_value(u.km / u.s)
        
        dt: float = delta_time.to_value(u.s)
        
        mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # ? 1.
        
            # ? a) Magnitudes
        
        r_0_m: float = np.linalg.norm(r_0)
        v_0_m: float = np.linalg.norm(v_0)
        
            # ? b) Radial Velocity
        
        v_r_0: float = np.dot(r_0, v_0) / r_0_m
        
            # ? c) Parameter alpha (reciprocal of the semimajor axis)
        
        alpha: float = 2 / r_0_m - v_0_m**2 / mu
        
        # ? 2. Universal variable
        
        chi: u.Quantity = LagrangeCoefficients.universal_kepler_solution(
            attractor=attractor,
            initial_position=r_0_m * u.km,
            initial_radial_velocity=v_r_0 * u.km / u.s,
            alpha=alpha * 1 / u.km,
            delta_time=delta_time)
        
        chi: float = chi.to_value(u.km**0.5)
        
        z: float = alpha * chi**2
        
        # ? 3. Lagrange coefficients
        
        f: float = 1 - chi**2 / r_0_m * LagrangeCoefficients.C(z)
        
        g: float = dt - 1 / np.sqrt(mu) * chi**3 * LagrangeCoefficients.S(z)
        
        # ? 4. Position
        
        r: u.Quantity = (f * r_0 + g * v_0) * u.km
        
        r_m: float = np.linalg.norm(r.to_value(u.km))
        
        # ? 5. Derivatives of Lagrange coefficients
        
        df_dt: float = np.sqrt(mu) / (r_m * r_0_m) * (alpha * chi**3 * LagrangeCoefficients.S(z) - chi)
        
        dg_dt: float = 1 - chi**2 / r_m * LagrangeCoefficients.C(z)
        
        # ? 6. Velocity
        
        v: u.Quantity = (df_dt * r_0 + dg_dt * v_0) * u.km / u.s
        
        return [r, v]
