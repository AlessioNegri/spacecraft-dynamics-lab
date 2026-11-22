"""
**Orbital maneuvers** transfer a spacecraft from one orbit to another. Orbital changes can be dramatic, such as the
transfer from a low-earth parking orbit to an interplanetary trajectory. They can also be quite small, as in the final
stages of the rendezvous of one spacecraft with another. Changing orbits requires the firing of onboard rocket engines.
In this module we consider solely *nonimpulsive maneuvers* in which the rockets fire continuously to produce the
required velocity change (delta-v).

📌 **Notes**

In *nonimpulsive orbital maneuvers* the thrust acts over a significant time interval and must be included in the
equations of motion. While the rocket motor is firing, the spacecraft mass decreases, because propellant combustion
products are being discharged into space through the nozzle.

In *low-thrust propulsion*, charged particles or plasmas are accelerated using electrostatic or electromagnetic forces
and ejected at very high exhaust velocities.

📖 **References**

- :cite:`curtis`
    - Chapter 6 *Orbital Maneuvers*

- :cite:`kluever`
    - Chapter 9 *Low-Thrust Transfers*

- :cite:`walter`
    - Chapter 8 *Orbital Maneuvering*
"""

import astropy.time as time
import astropy.units as u
import numpy as np
import typing as ty

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.models.results as sl_results
import spacelab.models.rocket_motor as sl_rocket_motor
import spacelab.n_body_models.lagrange_coefficients as sl_lagrange_coefficients
import spacelab.n_body_models.two_body_problem as sl_two_body_problem
import spacelab.orbit.representation as sl_representation
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

# * curtis

def constant_tangential_thrust_transfer_from_time(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    initial_radius: u.Quantity,
    time_of_flight: u.Quantity,
    direction: sl_enums.SpiralDirection) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Constant tangential thrust transfer from burning time.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param initial_radius: Initial circular orbit radius
    :type initial_radius: u.Quantity
    :param time_of_flight: Time of flight
    :type time_of_flight: u.Quantity
    :param direction: Direction of the spiral
    :type direction: sl_enums.SpiralDirection
    :return: [final radius, propellant mass]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    This maneuver computes the final radius and propellant mass consumed for a *constant tangential thrust transfer*
    given the initial radius and the time of flight. The algorithm assumes a constant tangential thrust applied over
    the specified time interval, resulting in a continuous acceleration that modifies the spacecraf's orbit.
    
    By integrating the equations of motion under constant tangential thrust, the maneuver calculates the final
    orbital radius after the burn and the total propellant mass consumed based on the rocket motor's parameters and
    specific impulse.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.10 *Nonimpulsive orbital maneuvers*
    - :cite:`kluever`
        - Section 9.3 *Coplanar Circle-to-Circle Transfer*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor
    
    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * initial_radius
    
    err_msg = sl_validator.validate_quantity("initial_radius", initial_radius, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * time_of_flight
    
    err_msg = sl_validator.validate_quantity("time_of_flight", time_of_flight, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * direction
    
    err_msg = sl_validator.validate_type("direction", direction, sl_enums.SpiralDirection)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * initial_radius above attractor radius

    attractor_radius: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)

    if initial_radius.to_value(u.km) <= attractor_radius:

        sl_logger.logger.warning("'initial_radius' must be greater than the attractor radius")

        return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    m_0: float = rocket_motor.spacecraft_mass.to_value(u.kg)
    
    r_0: float = initial_radius.to_value(u.km)
    
    tof: float = time_of_flight.to_value(u.s)
    
    # ? 1. Target radius
    
    v_0: float = np.sqrt(mu / r_0) # * Initial circular orbit velocity
    
    c: float = rocket_motor.calc_effective_exhaust_velocity(attractor=attractor).to_value(u.km / u.s)
    
    m_dot: float = rocket_motor.calc_propellant_mass_flow_rate(attractor=attractor).to_value(u.kg / u.s)
    
    sign: float = +1 if direction == sl_enums.SpiralDirection.OUTWARD else -1
    
    r: float = mu / (v_0 + sign * c * np.log(1 - m_dot / m_0 * tof))**2
    
    # ? 2. Propellant mass
    
    m_p: float = m_dot * tof
    
    return [r * u.km, m_p * u.kg]

def constant_tangential_thrust_transfer_from_radius(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    initial_radius: u.Quantity,
    final_radius: u.Quantity,
    earth_shadow: bool = False) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Constant tangential thrust transfer from final radius.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param initial_radius: Initial circular orbit radius
    :type initial_radius: u.Quantity
    :param final_radius: Final circular orbit radius
    :type final_radius: u.Quantity
    :param earth_shadow: Enable/disable the earth shadow effect, defaults to False
    :type earth_shadow: bool, optional
    :return: [time of flight, propellant mass, delta velocity]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    This maneuver computes the time of flight and propellant mass consumed for a *constant tangential thrust transfer*
    given the initial and final radii. The algorithm assumes a constant tangential thrust applied over the transfer,
    resulting in a continuous acceleration that modifies the spacecraft's orbit.
    
    By integrating the equations of motion under constant tangential thrust, the maneuver calculates the time of
    flight required to reach the final radius and the total propellant mass consumed based on the rocket motor's
    parameters and specific impulse.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.10 *Nonimpulsive orbital maneuvers*
    - :cite:`kluever`
        - Section 9.3 *Coplanar Circle-to-Circle Transfer*
        - Section 9.4 *Coplanar Transfer with Earth-Shadow Effects*
    - :cite:`walter`
        - Section 8.4 *Other Transfers*
        - Section 8.4.5 *Continuous Thrust Transfer*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor
    
    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * initial_radius
    
    err_msg = sl_validator.validate_quantity("initial_radius", initial_radius, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * final_radius
    
    err_msg = sl_validator.validate_quantity("final_radius", final_radius, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * initial_radius above attractor radius

    attractor_radius: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)

    if initial_radius.to_value(u.km) <= attractor_radius:

        sl_logger.logger.warning("'initial_radius' must be greater than the attractor radius")

        return None

    # * final_radius above attractor radius

    if final_radius.to_value(u.km) <= attractor_radius:

        sl_logger.logger.warning("'final_radius' must be greater than the attractor radius")

        return None
    
    # * earth_shadow
    
    err_msg = sl_validator.validate_type("earth_shadow", earth_shadow, bool)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    R_E: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)
    
    m_0: float = rocket_motor.spacecraft_mass.to_value(u.kg)
    
    r_0: float = initial_radius.to_value(u.km)
    
    r_f: float = final_radius.to_value(u.km)
    
    # ? 1. Flight time
    
    v_0: float = np.sqrt(mu / r_0) # * Initial circular orbit velocity
    
    v_f: float = np.sqrt(mu / r_f) # * Final circular orbit velocity
    
    dv: float = - np.abs(v_f - v_0)
    
    c: float = rocket_motor.calc_effective_exhaust_velocity(attractor=attractor).to_value(u.km / u.s)
    
    c_tilde: float = dv
    
    if earth_shadow:
        
        coeff: float = np.pi / R_E
        
        c_tilde = np.sqrt(coeff * mu) * (np.arctanh(np.sqrt(coeff * r_f) + 0j) - np.arctanh(np.sqrt(coeff * r_0) + 0j))
    
    m_dot: float = rocket_motor.calc_propellant_mass_flow_rate(attractor=attractor).to_value(u.kg / u.s)
    
    tof: float = m_0 / m_dot * (1 - np.exp(c_tilde.real / c))
    
    # ? 2. Propellant mass
    
    m_p: float = m_dot * tof
    
    return [tof * u.s, m_p * u.kg, dv * u.km / u.s]

def non_impulsive_maneuver( # NOSONAR python:S3776
    attractor: sl_bodies.Attractor, # NOSONAR python:S107
    rocket_motor: sl_rocket_motor.RocketMotor,
    initial_position: u.Quantity,
    initial_velocity: u.Quantity,
    burning_time_guess: u.Quantity,
    time_step: u.Quantity,
    final_position: u.Quantity,
    semi_major_axis_target: bool = False,
    inclination_target: bool = False,
    initial_radius: u.Quantity = 0 * u.km,
    final_radius: u.Quantity = 0 * u.km,
    initial_inclination: u.Quantity = 0 * u.deg,
    final_inclination: u.Quantity = 0 * u.deg,
    thrust_direction: sl_enums.ThrustDirection = sl_enums.ThrustDirection.ALONG_VELOCITY,
    tolerance: float = 1e-0) -> ty.Optional[ty.Tuple[sl_results.NonImpulsiveManeuverResult, sl_results.Result]]:
    """
    Non impulsive maneuver that, starting from an initial position and velocity, computes the final position and
    velocity after a given burning time guess. That guess is adjusted iteratively until the final position is close
    enough to the target position or the semi-major axis.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor object
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param initial_position: Initial position vector
    :type initial_position: u.Quantity
    :param initial_velocity: Initial velocity vector
    :type initial_velocity: u.Quantity
    :param burning_time_guess: Initial burning time guess; must be positive
    :type burning_time_guess: u.Quantity
    :param time_step: Time step for burning time calculation
    :type time_step: u.Quantity
    :param final_position: Final position vector.
    :type final_position: u.Quantity
    :param semi_major_axis_target: Match the final semi-major axis to the target radius. Defaults to ``False``
    :type semi_major_axis_target: bool
    :param inclination_target: Match the final inclination, defaults to ``False``
    :type inclination_target: bool
    :param initial_radius: Initial radius in kilometers, defaults to ``0 km``
    :type initial_radius: u.Quantity
    :param final_radius: Target radius in kilometers, defaults to ``0 km``
    :type final_radius: u.Quantity
    :param initial_inclination: Initial inclination, defaults to ``0 deg``
    :type initial_inclination: u.Quantity
    :param final_inclination: Target inclination, defaults to ``0 deg``
    :type final_inclination: u.Quantity
    :param thrust_direction: Thrust direction, defaults to :attr:`sl_enums.ThrustDirection.ALONG_VELOCITY`
    :type thrust_direction: sl_enums.ThrustDirection
    :param tolerance: Convergence tolerance, defaults to ``1``
    :type tolerance: float
    :return: Maneuver result and integration result, or ``None`` if input validation fails.
    :rtype: ty.Optional[ty.Tuple[sl_results.NonImpulsiveManeuverResult, sl_results.Result]]
    
    📌 **Notes**
    
    If the 'semi_major_axis_target' is set to True, the algorithm will try to match the semi-major axis of the final
    orbit to the norm of the final position vector. Otherwise, it will try to match the final position vector norm
    to the target final position vector norm.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.10 *Nonimpulsive orbital maneuvers*
    """

    # >>> Validation

    validation_errors: ty.List[ty.Optional[str]] = [
        # * attractor
        sl_validator.validate_attractor(attractor),
        # * rocket_motor
        sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor),
        # * initial_position
        sl_validator.validate_quantity_vector("initial_position", initial_position, u.km, 3),
        # * initial_velocity
        sl_validator.validate_quantity_vector("initial_velocity", initial_velocity, u.km / u.s, 3),
        # * burning_time_guess
        sl_validator.validate_quantity("burning_time_guess", burning_time_guess, u.s),
        # * time_step
        sl_validator.validate_quantity("time_step", time_step, u.s),
        # * final_position
        sl_validator.validate_quantity_vector("final_position", final_position, u.km, 3),
        # * semi_major_axis_target
        sl_validator.validate_type("semi_major_axis_target", semi_major_axis_target, bool),
        # * inclination_target
        sl_validator.validate_type("inclination_target", inclination_target, bool),
        # * initial_radius
        sl_validator.validate_quantity("initial_radius", initial_radius, u.km),
        # * final_radius
        sl_validator.validate_quantity("final_radius", final_radius, u.km),
        # * initial_inclination
        sl_validator.validate_quantity_angle("initial_inclination", initial_inclination),
        # * final_inclination
        sl_validator.validate_quantity_angle("final_inclination", final_inclination),
        # * thrust_direction
        sl_validator.validate_type("thrust_direction", thrust_direction, sl_enums.ThrustDirection),
        # * tolerance
        sl_validator.validate_type("tolerance", tolerance, float),
    ]

    err_msg: str | None = next((message for message in validation_errors if message), None)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * supplied radii above attractor radius

    attractor_radius: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)
    initial_radius_km: float = initial_radius.to_value(u.km)
    final_radius_km: float = final_radius.to_value(u.km)

    if initial_radius_km != 0 and initial_radius_km <= attractor_radius:

        sl_logger.logger.warning("A supplied 'initial_radius' must be greater than the attractor radius")

        return None

    if final_radius_km != 0 and final_radius_km <= attractor_radius:

        sl_logger.logger.warning("A supplied 'final_radius' must be greater than the attractor radius")

        return None

    # >>> Algorithm

    if burning_time_guess.to_value(u.s) <= 0:
        
        sl_logger.logger.warning("Initial 'burning_time_guess' must be greater than zero")
        
        return None
    
    t_burn: time.TimeDelta = time.TimeDelta(burning_time_guess.to_value(u.s) * u.s)
    
    prev_epsilon: float = 0.0
    
    maneuver = sl_results.NonImpulsiveManeuverResult()
    
    result = sl_results.Result()
    
    maneuver.burn_time = t_burn.to(u.s)
    
    max_iterations: int = 100
    
    iteration: int = 0
    
    while True:
        
        if iteration > max_iterations:
            
            sl_logger.logger.warning('Reached max iterations')
            
            break
        
        # ? 1. Integrate
        
        orbit = sl_two_body_problem.Orbit()
        
        orbit.from_cartesian(attractor=attractor, position=initial_position, velocity=initial_velocity)
        
        result = orbit.propagate_for(
            delta=t_burn,
            rocket_motor=rocket_motor,
            thrust_direction=thrust_direction,
            initial_radius=initial_radius,
            target_radius=final_radius,
            initial_inclination=initial_inclination,
            target_inclination=final_inclination)
        
        if not result.success:
            
            sl_logger.logger.error('Integration failed')
            
            break
        
        r: u.Quantity = np.array([
            result.position_x[-1].to_value(u.km),
            result.position_y[-1].to_value(u.km),
            result.position_z[-1].to_value(u.km)]) * u.km
        
        v: u.Quantity = np.array([
            result.velocity_x[-1].to_value(u.km / u.s),
            result.velocity_y[-1].to_value(u.km / u.s),
            result.velocity_z[-1].to_value(u.km / u.s)]) * u.km / u.s
        
        m_sc: u.Quantity = result.mass_spacecraft[-1]
        
        # ? 2. Calculate orbital elements
        
        oe: sl_orbital_elements.OrbitalElements =\
            sl_representation.cartesian_to_keplerian(attractor=attractor, position=r, velocity=v)
        
        # ? 3. Update state vector
        
        epsilon: float = 0.0
        
        if semi_major_axis_target:
            
            epsilon = oe.semimajor_axis.to_value(u.km) - np.linalg.norm(final_position.to_value(u.km))

            # * final_inclination not less than initial_inclination

            if final_inclination.to_value(u.deg) < initial_inclination.to_value(u.deg):

                sl_logger.logger.warning("'final_inclination' must not be less than 'initial_inclination'")

                return None
            
            maneuver.position_x = r[0]
            maneuver.position_y = r[1]
            maneuver.position_z = r[2]
            maneuver.velocity_x = v[0]
            maneuver.velocity_y = v[1]
            maneuver.velocity_z = v[2]
            maneuver.spacecraft_mass = m_sc
        
        elif inclination_target:
            
            epsilon = oe.inclination.to_value(u.deg) - final_inclination.to_value(u.deg)
            
            maneuver.position_x = r[0]
            maneuver.position_y = r[1]
            maneuver.position_z = r[2]
            maneuver.velocity_x = v[0]
            maneuver.velocity_y = v[1]
            maneuver.velocity_z = v[2]
            maneuver.spacecraft_mass = m_sc
            
        else:
        
            delta_theta: u.Quantity = u.Quantity(180.0, u.deg) - oe.true_anomaly
        
            l_r_f, l_v_f = sl_lagrange_coefficients.propagate_of_angle(
                attractor=attractor, initial_position=r, initial_velocity=v, delta_true_anomaly=delta_theta)
        
            epsilon: float = np.linalg.norm(l_r_f.to_value(u.km)) - np.linalg.norm(final_position.to_value(u.km))
            
            maneuver.position_x = l_r_f[0]
            maneuver.position_y = l_r_f[1]
            maneuver.position_z = l_r_f[2]
            maneuver.velocity_x = l_v_f[0]
            maneuver.velocity_y = l_v_f[1]
            maneuver.velocity_z = l_v_f[2]
            maneuver.spacecraft_mass = m_sc
        
        # ? 4. Check error
        
        if np.abs(epsilon) < tolerance: break
        
        # ? 5. Update time interval and burn time
        
        if not np.isclose(prev_epsilon, 0.0, rtol=1e-09, atol=1e-09) and prev_epsilon * epsilon < 0:
            
            time_step = time_step / 2.0
        
        if epsilon < 0:
            
            t_burn += time.TimeDelta(time_step.to_value(u.s) * u.s)
            
        else:
            
            t_burn -= time.TimeDelta(time_step.to_value(u.s) * u.s)
        
        maneuver.burn_time = t_burn.to(u.s)
        
        # ? 6. Update error
        
        prev_epsilon = epsilon
        
        iteration += 1
    
    return maneuver, result

# * kluever

def inclination_change_maneuver(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    radius: u.Quantity,
    initial_inclination: u.Quantity,
    final_inclination: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Non-impulsive inclination change maneuver.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor object
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param radius: Circular orbit radius
    :type radius: u.Quantity
    :param initial_inclination: Initial orbital inclination
    :type initial_inclination: u.Quantity
    :param final_inclination: Final orbital inclination
    :type final_inclination: u.Quantity
    :return: [time of flight, propellant mass, delta velocity]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    It is develop as an analytical solutions for a low-thrust maneuver that only changes orbital inclination,
    considering Gauss' variational equation for inclination.
    
    📖 **References**
    
    - :cite:`kluever`
        - Section 9.5 *Inclination-Change Maneuver*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor
    
    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * radius
    
    err_msg = sl_validator.validate_quantity("radius", radius, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * radius above attractor radius

    attractor_radius: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)

    if radius.to_value(u.km) <= attractor_radius:

        sl_logger.logger.warning("'radius' must be greater than the attractor radius")

        return None
    
    # * initial_inclination
    
    err_msg = sl_validator.validate_quantity_angle("initial_inclination", initial_inclination)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * final_inclination
    
    err_msg = sl_validator.validate_quantity_angle("final_inclination", final_inclination)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    m_0: float = rocket_motor.spacecraft_mass.to_value(u.kg)
    
    r: float = radius.to_value(u.km)
    
    i_0: float = initial_inclination.to_value(u.rad)
    
    i_f: float = final_inclination.to_value(u.rad)
    
    # ? 1. Flight time
    
    v: float = np.sqrt(mu / r) # * Circular orbit velocity
    
    d_i: float = np.abs(i_f - i_0)
    
    dv: float = d_i * np.pi * v / 2
    
    c: float = rocket_motor.calc_effective_exhaust_velocity(attractor=attractor).to_value(u.km / u.s)
    
    m_dot: float = rocket_motor.calc_propellant_mass_flow_rate(attractor=attractor).to_value(u.kg / u.s)
    
    tof: float = m_0 / m_dot * (1 - np.exp(- dv / c))
    
    # ? 2. Propellant mass
    
    m_p: float = m_dot * tof
    
    return [tof * u.s, m_p * u.kg, dv * u.km / u.s]

def inclined_circular_orbits_transfer(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    initial_radius: u.Quantity,
    final_radius: u.Quantity,
    initial_inclination: u.Quantity,
    final_inclination: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Non-impulsive transfer between two inclined circular orbits.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor object
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param initial_radius: Initial circular orbit radius
    :type initial_radius: u.Quantity
    :param final_radius: Final circular orbit radius
    :type final_radius: u.Quantity
    :param initial_inclination: Initial orbital inclination
    :type initial_inclination: u.Quantity
    :param final_inclination: Final orbital inclination
    :type final_inclination: u.Quantity
    :return: [time of flight, propellant mass, delta velocity]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    In 1961, T. N. Edelbaum obtained a closed-form solution for the general *three-dimensional low-thrust transfer*
    between inclined circular orbits. Edelbaum utilized optimization theory and the calculus of variations to develop
    the minimum-propellant transfer between circular orbits with a plane change.

    His approach assumed that the out-of-plane thrust acceleration component remained constant over an orbital
    revolution (switching signs at :math:`\\pm 90°` from the nodal crossings) while the in-plane thrust component
    remained aligned with the velocity vector. However, the magnitude of the out-of-plane component varies in an optimal
    fashion so that the majority of the inclination change occurs at higher orbital altitudes. Using inplane tangential
    thrust assures that the orbit transfer retains its quasi-circular "spiral" nature. This thrust-steering strategy
    will cause simultaneous changes in semimajor axis and inclination during the orbit transfer.
    
    📖 **References**
    
    - :cite:`kluever`
        - Section 9.6 *Transfer Between Inclined Circular Orbits*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor
    
    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * initial_radius
    
    err_msg = sl_validator.validate_quantity("initial_radius", initial_radius, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * final_radius
    
    err_msg = sl_validator.validate_quantity("final_radius", final_radius, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * radii above attractor radius

    attractor_radius: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)

    if initial_radius.to_value(u.km) <= attractor_radius:

        sl_logger.logger.warning("Initial circular orbit radius must exceed the attractor radius")

        return None

    if final_radius.to_value(u.km) <= attractor_radius:

        sl_logger.logger.warning("Final circular orbit radius must exceed the attractor radius")

        return None
    
    # * initial_inclination
    
    err_msg = sl_validator.validate_quantity_angle("initial_inclination", initial_inclination)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * final_inclination
    
    err_msg = sl_validator.validate_quantity_angle("final_inclination", final_inclination)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    m_0: float = rocket_motor.spacecraft_mass.to_value(u.kg)
    
    r_0: float = initial_radius.to_value(u.km)
    
    r_f: float = final_radius.to_value(u.km)
    
    i_0: float = initial_inclination.to_value(u.rad)
    
    i_f: float = final_inclination.to_value(u.rad)
    
    # ? 1. Flight time
    
    v_0: float = np.sqrt(mu / r_0) # * Initial circular orbit velocity
    
    v_f: float = np.sqrt(mu / r_f) # * Final circular orbit velocity
    
    d_i: float = i_f - i_0
    
    # * T. N. Edelbaum equation
    
    dv: float = np.sqrt(v_0**2 + v_f**2 - 2 * v_0 * v_f * np.cos(d_i * np.pi / 2))
    
    c: float = rocket_motor.calc_effective_exhaust_velocity(attractor=attractor).to_value(u.km / u.s)
    
    m_dot: float = rocket_motor.calc_propellant_mass_flow_rate(attractor=attractor).to_value(u.kg / u.s)
    
    tof: float = m_0 / m_dot * (1 - np.exp(- dv / c))
    
    # ? 2. Propellant mass
    
    m_p: float = m_dot * tof
    
    return [tof * u.s, m_p * u.kg, dv * u.km / u.s]
