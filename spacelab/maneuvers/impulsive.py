"""
**Orbital maneuvers** transfer a spacecraft from one orbit to another. Orbital changes can be dramatic, such as the
transfer from a low-earth parking orbit to an interplanetary trajectory. They can also be quite small, as in the final
stages of the rendezvous of one spacecraft with another. Changing orbits requires the firing of onboard rocket engines.
In this module we consider solely *impulsive maneuvers* in which the rockets fire in relatively short bursts to produce
the required velocity change (delta-v).

📌 **Notes**

*Impulsive maneuvers* are those in which brief firings of onboard rocket motors change the magnitude and direction of
the velocity vector instantaneously. During an impulsive maneuver, the position of the spacecraft is considered to be
fixed; only the velocity changes. The impulsive maneuver is an idealization by means of which we can avoid having to
solve the equations of motion with the rocket thrust included. The idealization is satisfactory for those cases in which
the position of the spacecraft changes only slightly during the time that the maneuvering rockets fire. This is true for
high-thrust rockets with burn times short compared with the coasting time of the vehicle.

📖 **References**

- :cite:`curtis`
    - Chapter 6 *Orbital Maneuvers*

- :cite:`kluever`
    - Chapter 7 *Impulsive Orbital Maneuvers*

- :cite:`sforza`
    - Chapter 5 *ORBITAL MECHANICS*

- :cite:`walter`
    - Chapter 8 *Orbital Maneuvering*
"""

import astropy.time as time
import astropy.units as u
import copy as cp
import numpy as np
import scipy.optimize as optimize
import typing as ty

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.models.results as sl_results
import spacelab.models.rocket_motor as sl_rocket_motor
import spacelab.orbit.determination as sl_determination
import spacelab.orbit.position as sl_position
import spacelab.orbit.representation as sl_representation
import spacelab.physical_constants as sl_physical_constants
import spacelab.utils.angle as sl_angle
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

# * curtis

def hohmann_transfer( # NOSONAR python:S3776
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements,
    direction: sl_enums.HohmannDirection) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Hohmann transfer maneuver.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :param direction: Direction of the transfer
    :type direction: sl_enums.HohmannDirection
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    The **Hohmann transfer** (Walter Hohmann, 1925) is the most energy efficient two-impulse orbital maneuver used to
    transfer a spacecraft between two coplanar, elliptical or circular orbits sharing a common focus. It is a widely
    used approximation for transfers between low-eccentricity orbits. The Hohmann transfer is an elliptical orbit
    tangent to both circles at its apse line.
            
    This implementation generalizes the classical Hohmann transfer to allow transfers between arbitrary coplanar 
    elliptical orbits, using one of two possible geometric configurations:
    
    - pericenter -> apocenter
    - apocenter -> pericenter
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.3 *Hohmann transfer*
    - :cite:`kluever`
        - Section 7.3 *Hohmann Transfer*
    - :cite:`sforza`
        - Section 5.1.5 *IN-PLANE ORBITAL TRANSFER: NONINTERSECTING ORBITS*
    - :cite:`walter`
        - Section 8.3 *Hohmann Transfer*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor
    
    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_1
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_2
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * direction
    
    err_msg = sl_validator.validate_type("direction", direction, sl_enums.HohmannDirection)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    # ? 0. Pericenter/Apocenter radii
    
    r_p_1: float = orbital_elements_1.calc_periapsis_radius().to_value(u.km)
    r_a_1: float = orbital_elements_1.calc_apoapsis_radius().to_value(u.km)
    
    r_p_2: float = orbital_elements_2.calc_periapsis_radius().to_value(u.km)
    r_a_2: float = orbital_elements_2.calc_apoapsis_radius().to_value(u.km)
    
    # ? 1. Orbit 1 (Specific Angular Momentum, Velocity at Pericenter and Apocenter)
    
    v_p_1: float = orbital_elements_1.calc_periapsis_velocity().to_value(u.km / u.s)
    
    v_a_1: float = orbital_elements_1.calc_apoapsis_velocity().to_value(u.km / u.s)
    
    # ? 2. Orbit 2 (Specific Angular Momentum, Velocity at Pericenter and Apocenter)
    
    v_p_2: float = orbital_elements_2.calc_periapsis_velocity().to_value(u.km / u.s)
    
    v_a_2: float = orbital_elements_2.calc_apoapsis_velocity().to_value(u.km / u.s)
    
    # ? 3. Transfer Orbit
    
    r_p_t: float = 0.0
    r_a_t: float = 0.0
    
    swap: bool = False
    
    if direction == sl_enums.HohmannDirection.PERICENTER_APOCENTER:
        
        r_p_t: float = min(r_p_1, r_a_2)
        r_a_t: float = max(r_p_1, r_a_2)
        
        swap = r_p_1 > r_a_2
        
    elif direction == sl_enums.HohmannDirection.APOCENTER_PERICENTER:
        
        r_p_t: float = min(r_p_2, r_a_1)
        r_a_t: float = max(r_p_2, r_a_1)
        
        swap = r_p_2 > r_a_1
        
    a_t: float = 0.5 * (r_p_t + r_a_t)
    
    e_t: float = (r_a_t - r_p_t) / (r_a_t + r_p_t)

    h_t: float = np.sqrt(2 * mu) * np.sqrt(r_a_t * r_p_t / (r_a_t + r_p_t))
    
    v_p_t: float = h_t / r_p_t
    
    v_a_t: float = h_t / r_a_t
    
    t_t: float = 2 * np.pi / float(np.sqrt(mu)) * a_t**(3/2) # ? Orbital Period
    
    # ? 4. Delta-V Calculations
    
    dv_1: float = 0.0
    dv_2: float = 0.0
    ta_1: float = 0.0 # * True anomaly at first maneuver point
    ta_t: float = 0.0 # * True anomaly at second maneuver point
    
    if direction == sl_enums.HohmannDirection.PERICENTER_APOCENTER:
        
        dv_1 = abs(v_p_t - (v_p_1 if not swap else v_a_2))
        
        dv_2 = abs((v_a_2 if not swap else v_p_1) - v_a_t)
        
        ta_1 = 0.0
        
        ta_t = 0.0 if not swap else 180.0
    
    elif direction == sl_enums.HohmannDirection.APOCENTER_PERICENTER:
        
        dv_1 = abs(v_a_t - (v_a_1 if not swap else v_p_2))
        
        dv_2 = abs((v_p_2 if not swap else v_a_1) - v_p_t)
        
        ta_1 = 180.0
        
        ta_t = 180.0 if not swap else 0.0
    
    argp_t: float = orbital_elements_1.argument_of_periapsis.to_value(u.deg)
    
    if swap:
        
        argp_t = sl_angle.wrap_angle((argp_t + 180.0) * u.deg, -180.0 * u.deg, +180.0 * u.deg).to_value(u.deg)
    
    # ? 5. Result
    
    dm_1: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_1 * u.km / u.s, attractor=attractor)
    
    t_burn_1: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_1, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm_1
    
    dm_2: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_2 * u.km / u.s, attractor=attractor)

    t_burn_2: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_2, attractor=attractor)

    rocket_motor.spacecraft_mass -= dm_2
    
    oe_t = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=h_t * u.km**2 / u.s,
        semimajor_axis=a_t * u.km,
        eccentricity=e_t * u.one,
        inclination=orbital_elements_1.inclination,
        right_ascension_of_ascending_node=orbital_elements_1.right_ascension_of_ascending_node,
        argument_of_periapsis=argp_t * u.deg,
        true_anomaly=ta_t * u.deg)
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list=[dv_1 * u.km / u.s, dv_2 * u.km / u.s]
    maneuver.flight_time_list=[0.5 * t_t * u.s]
    maneuver.delta_mass_list=[dm_1, dm_2]
    maneuver.burn_time_list=[t_burn_1, t_burn_2]
    maneuver.orbital_elements_list=[oe_t]
    maneuver.true_anomaly_list=[ta_1 * u.deg]
    maneuver.rocket_elevation_angle_list=[0 * u.deg, 0 * u.deg]
    
    return maneuver

def bi_elliptic_hohmann_transfer(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements,
    apoapsis_radius: u.Quantity) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Bi-Elliptic Hohmann transfer maneuver.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :param apoapsis_radius: Apoapsis of intermediate orbit
    :type apoapsis_radius: u.Quantity
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    The **bi-elliptic Hohmann transfer** is a three-impulse orbital maneuver used to transfer a spacecraft between two
    coplanar orbits when the ratio between the final and initial orbital radii is sufficiently large.
    Unlike the classical Hohmann transfer, which uses a single transfer ellipse, the bi-elliptic transfer introduces
    an intermediate apoapsis :math:`r_3`, allowing the spacecraft to perform part of the maneuver at a very low velocity.
    This can reduce the total :math:`\\Delta v` when the target orbit is much larger than the initial one.

    This implementation generalizes the bi-elliptic transfer to elliptical orbits by computing the maneuver at the
    appropriate pericenter or apoapsis radii of the initial and final orbits.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.4 *Bi-elliptic Hohmann transfer*
    - :cite:`walter`
        - Section 8.4 *Other Transfers*
        - Section 8.4.2 *Bi-elliptic Transfer*
    """

    # >>> Validation

    # * attractor

    err_msg: str | None = sl_validator.validate_attractor(attractor)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * rocket_motor

    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * orbital_elements_1

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * orbital_elements_2

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * apoapsis_radius

    err_msg = sl_validator.validate_quantity("apoapsis_radius", apoapsis_radius, u.km)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # >>> Algorithm
    
    # ? 1. First transfer

    oe_t_1: sl_orbital_elements.OrbitalElements = cp.deepcopy(orbital_elements_1)
    
    oe_t_1.update_from_periapsis_apoapsis(
        periapsis_radius=orbital_elements_1.calc_periapsis_radius(),
        apoapsis_radius=apoapsis_radius)

    maneuver_1: ty.Optional[sl_results.ManeuverResult] = hohmann_transfer(
        attractor=attractor,
        rocket_motor=rocket_motor,
        orbital_elements_1=orbital_elements_1,
        orbital_elements_2=oe_t_1,
        direction=sl_enums.HohmannDirection.PERICENTER_APOCENTER)

    if maneuver_1 is None: return None

    oe_t_2: sl_orbital_elements.OrbitalElements = cp.deepcopy(orbital_elements_2)
    
    oe_t_2.update_from_periapsis_apoapsis(periapsis_radius=orbital_elements_2.calc_periapsis_radius(),
                                        apoapsis_radius=apoapsis_radius)
    
    # ? 2. Intermediate transfer

    maneuver_2: ty.Optional[sl_results.ManeuverResult] = hohmann_transfer(
        attractor=attractor,
        rocket_motor=rocket_motor,
        orbital_elements_1=oe_t_1,
        orbital_elements_2=oe_t_2,
        direction=sl_enums.HohmannDirection.APOCENTER_PERICENTER)

    if maneuver_2 is None: return None
    
    # ? 3. Second transfer

    maneuver_3: ty.Optional[sl_results.ManeuverResult] = hohmann_transfer(
        attractor=attractor,
        rocket_motor=rocket_motor,
        orbital_elements_1=oe_t_2,
        orbital_elements_2=orbital_elements_2,
        direction=sl_enums.HohmannDirection.APOCENTER_PERICENTER)

    if maneuver_3 is None: return None
    
    # ? 4. Result

    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list=[
        maneuver_1.delta_velocity_list[0], maneuver_2.delta_velocity_list[0], maneuver_3.delta_velocity_list[1]]
    
    maneuver.flight_time_list=[maneuver_1.flight_time_list[0], maneuver_2.flight_time_list[0]]
    
    maneuver.delta_mass_list=[
        maneuver_1.delta_mass_list[0], maneuver_2.delta_mass_list[0], maneuver_3.delta_mass_list[1]]
    
    maneuver.burn_time_list=[
        maneuver_1.burn_time_list[0], maneuver_2.burn_time_list[0], maneuver_3.burn_time_list[1]]
    
    maneuver.orbital_elements_list=[maneuver_1.orbital_elements_list[0], maneuver_2.orbital_elements_list[0]]
    
    maneuver.true_anomaly_list=[
        maneuver_1.true_anomaly_list[0], maneuver_2.true_anomaly_list[0], maneuver_3.true_anomaly_list[0]]
    
    maneuver.rocket_elevation_angle_list=[
        maneuver_1.rocket_elevation_angle_list[0],
        maneuver_2.rocket_elevation_angle_list[0],
        maneuver_3.rocket_elevation_angle_list[1]]
    
    return maneuver

def phasing_maneuver(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements: sl_orbital_elements.OrbitalElements,
    true_anomaly_target: u.Quantity,
    num_revolutions: int = 1) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Phasing maneuver from *chaser* A to *target* B.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements: Orbital elements of chaser A
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :param true_anomaly_target: True anomaly of target B
    :type true_anomaly_target: u.Quantity
    :param num_revolutions: Number of revolutions on phasing orbit, defaults to 1
    :type num_revolutions: int, optional
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    A **phasing maneuver** is a two-impulse Hohmann transfer from and back to the same orbit. The Hohmann transfer
    ellipse is the phasing orbit with a period selected to return the spacecraft to the main orbit within a specified
    time. Phasing maneuvers are used to change the position of a spacecraft in its orbit. If two spacecraft, destined to
    rendezvous, are at different locations in the same orbit, then one of them may perform a phasing maneuver in order
    to catch the other one. Communications and weather satellites in geostationary earth orbit use phasing maneuvers to
    move to new locations above the equator. In that case, the rendezvous is with an empty point in space rather than
    with a physical target.
    
    A **phasing maneuver** is a two-impulse orbital strategy used to synchronize the position of a chaser spacecraft (A)
    with a target spacecraft (B) located on the same orbital plane. The goal is to adjust the orbital period of the
    chaser so that, after completing a specified number of revolutions on a temporary “phasing orbit”, it arrives at
    the same true anomaly as the target.
    
    This maneuver is commonly used for rendezvous, formation flying, and constellation maintenance.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.5 *Phasing maneuver*
    """
    
    # >>> Validation

    # * attractor

    err_msg: str | None = sl_validator.validate_attractor(attractor)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * rocket_motor

    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * orbital_elements

    err_msg = sl_validator.validate_orbital_elements(orbital_elements)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * true_anomaly_target

    err_msg = sl_validator.validate_quantity_angle("true_anomaly_target", true_anomaly_target)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # * num_revolutions

    err_msg = sl_validator.validate_type("num_revolutions", num_revolutions, int)

    if err_msg: sl_logger.logger.warning(err_msg); return None

    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    # ? 1. Chaser Orbit period and velocity at pericenter
    
    T_1: float = orbital_elements.calc_orbital_period(attractor=attractor).to_value(u.s)
    
    r_p_1: float = orbital_elements.calc_periapsis_radius().to_value(u.km)
    
    v_p_1: float = orbital_elements.calc_periapsis_velocity().to_value(u.km / u.s)
    
    # ? 2. Time from A (pericenter - chaser) to B (target) placed at true_anomaly_target w.r.t. A
    
    t_ab: u.Quantity = sl_position.elliptical_orbit_time(
        true_anomaly=true_anomaly_target, period=T_1 * u.s, eccentricity=orbital_elements.eccentricity)
    
    # ? 3. Orbit 2 (Phasing Orbit with kick at pericenter)
    
    T_2: float = T_1 - t_ab.to_value(u.s) / num_revolutions
    
    a_2: float = (np.sqrt(mu) * T_2 / (2 * np.pi))**(2/3)
    
    r_a: float = r_p_1 # * Maneuver point is the pericenter of the chaser orbit
    
    r_d: float = 2 * a_2 - r_a # * Opposite point of the phasing orbit
    
    h_2: float = np.sqrt(2 * mu) * np.sqrt(r_a * r_d / (r_a + r_d))
    
    v_p_a: float = h_2 / r_a
    
    # ? 4. Delta-V Calculations
    
    dv_1: float = np.abs(v_p_a - v_p_1)
    
    dv_2: float = np.abs(v_p_1 - v_p_a)
    
    # ? 5. Result
    
    dm_1: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_1 * u.km / u.s, attractor=attractor)
    
    t_burn_1: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_1, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm_1
    
    dm_2: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_2 * u.km / u.s, attractor=attractor)
    
    t_burn_2: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_2, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm_2
    
    oe_t = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=h_2 * u.km**2 / u.s,
        semimajor_axis=a_2 * u.km,
        eccentricity=(r_d - r_a) / (r_d + r_a) * u.one,
        inclination=orbital_elements.inclination,
        right_ascension_of_ascending_node=orbital_elements.right_ascension_of_ascending_node,
        argument_of_periapsis=orbital_elements.argument_of_periapsis,
        true_anomaly=0 * u.deg)
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list=[dv_1 * u.km / u.s, dv_2 * u.km / u.s]
    maneuver.flight_time_list=[num_revolutions * T_2 * u.s]
    maneuver.delta_mass_list=[dm_1, dm_2]
    maneuver.burn_time_list=[t_burn_1, t_burn_2]
    maneuver.orbital_elements_list=[oe_t]
    maneuver.rocket_elevation_angle_list=[0 * u.deg, 0 * u.deg]
    
    return maneuver

def non_hohmann_transfer(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Non-Hohmann transfer between coaxial elliptical orbits.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    A **non-Hohmann transfer** is a general two-impulse maneuver used to move a spacecraft from an initial elliptical
    orbit to a target point located at a specified radius and true anomaly on a second coaxial (same-focus) orbit.
    Unlike the classical Hohmann transfer, which is constrained to pericenter-to-apocenter geometry, the non-Hohmann
    transfer allows the spacecraft to intercept the target at an arbitrary true anomaly. This makes it suitable for
    rendezvous, phasing, and transfers between elliptical orbits where the target point is not aligned with the
    apsides.
    
    This maneuver computes a single transfer ellipse that connects:
    
    - the spacecraft's current position on the initial orbit
    - the desired target position on the final orbit, defined by the specified radius and true anomaly.
    
    The transfer is completed with two tangential burns: one to enter the transfer ellipse and one to match the
    target orbit at the interception point.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.6 *Non-Hohmann transfers with a common apse line*
    - :cite:`kluever`
        - Section 7.4 *General Coplanar Transfer*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor
    
    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_1
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_2
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    # ? 1. Orbit 1 (Starting Orbit)
    
    ta_1: float = orbital_elements_1.true_anomaly.to_value(u.rad)
    
    r_1: float = orbital_elements_1.calc_position(attractor=attractor).to_value(u.km) # * Radius
    
    v_1: float = orbital_elements_1.calc_velocity(attractor=attractor).to_value(u.km / u.s) # * Velocity
    
    fpa_1: float = orbital_elements_1.calc_flight_path_angle(attractor=attractor).to_value(u.rad) # * Flight path angle
    
    # ? 2. Orbit 2 (Target Orbit)
    
    ta_2: float = orbital_elements_2.true_anomaly.to_value(u.rad)
    
    r_2: float = orbital_elements_2.calc_position(attractor=attractor).to_value(u.km) # * Radius
    
    v_2: float = orbital_elements_2.calc_velocity(attractor=attractor).to_value(u.km / u.s) # * Velocity
    
    fpa_2: float = orbital_elements_2.calc_flight_path_angle(attractor=attractor).to_value(u.rad) # * Flight path angle
    
    # ? 3. Transfer Orbit
    
    # ? ta_1 and ta_2 are the true anomalies of the transfer orbit at the maneuver point and at the target point,
    # ? respectively. Since the transfer orbit is coaxial with the initial orbit, ta_1 is equal to the true anomaly
    # ? of the initial orbit at the maneuver point, same for ta_2 on target orbit.
    
    e_t: float = - (r_2 - r_1) / (r_2 * np.cos(ta_2) - r_1 * np.cos(ta_1))
    
    h_t: float = np.sqrt(mu * r_1 * r_2) * np.sqrt((np.cos(ta_2) - np.cos(ta_1)) /\
        (r_2 * np.cos(ta_2) - r_1 * np.cos(ta_1)))
    
    r_p_t: float = h_t**2 / mu * 1 / (1 + e_t)
    
    r_a_t: float = h_t**2 / mu * 1 / (1 - e_t)
    
    a_t: float = 0.5 * (r_p_t + r_a_t) if e_t < 1 else 0
    
    period_t: float = 2 * np.pi / float(np.sqrt(mu)) * a_t**(3/2) if e_t < 1 else 0
    
    # ? 3. Starting point of the transfer orbit (maneuver point)
    
    v_t_t_1: float = h_t / r_1
    
    v_r_t_1: float = mu / h_t * e_t * np.sin(ta_1)
    
    v_t_1: float = np.sqrt(v_r_t_1**2 + v_t_t_1**2)
    
    fpa_t_1: float = np.arctan(v_r_t_1 / v_t_t_1)
    
    # ? 4. Target point of the transfer orbit (interception point)
    
    v_t_t_2: float = h_t / r_2
    
    v_r_t_2: float = mu / h_t * e_t * np.sin(ta_2)
    
    v_t_2: float = np.sqrt(v_r_t_2**2 + v_t_t_2**2)
    
    fpa_t_2: float = np.arctan(v_r_t_2 / v_t_t_2)
    
    # ? 4. Result
    
    delta_fpa_1: float = (fpa_t_1 - fpa_1)
    delta_fpa_2: float = (fpa_t_2 - fpa_2)
    
    dv_1: float = np.sqrt(v_1**2 + v_t_1**2 - 2 * v_1 * v_t_1 * np.cos(delta_fpa_1))
    dv_2: float = np.sqrt(v_2**2 + v_t_2**2 - 2 * v_2 * v_t_2 * np.cos(delta_fpa_2))
    
    #phi_1: float = np.arctan2((v_r_t_1 - v_r_1), (v_t_t_1 - v_t_1))
    #phi_2: float = np.arctan2((v_r_2 - v_r_t_2), (v_t_2 - v_t_t_2))
    
    phi_1: float = np.pi - np.arcsin(v_t_1 / dv_1 * np.sin(delta_fpa_1)) + fpa_1
    phi_2: float = np.pi - np.arcsin(v_t_2 / dv_2 * np.sin(delta_fpa_2)) + fpa_2
    
    if (phi_1 < 0): phi_1 += np.pi
    if (phi_2 < 0): phi_2 += np.pi
    
    if e_t < 1:
        
        t_1: u.Quantity = sl_position.elliptical_orbit_time(
            true_anomaly=orbital_elements_1.true_anomaly,
            period=period_t * u.s,
            eccentricity=e_t * u.one)
    
    else:
        
        t_1: u.Quantity = sl_position.hyperbolic_orbit_time(
            true_anomaly=orbital_elements_1.true_anomaly,
            specific_angular_momentum=h_t * u.km**2 / u.s,
            eccentricity=e_t * u.one,
            attractor=attractor)
    
    dm_1: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_1 * u.km / u.s, attractor=attractor)
    
    t_burn_1: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_1, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm_1
    
    if e_t < 1:
        
        t_2: u.Quantity = sl_position.elliptical_orbit_time(
            true_anomaly=orbital_elements_2.true_anomaly,
            period=period_t * u.s,
            eccentricity=e_t * u.one)
        
    else:
        
        t_2: u.Quantity = sl_position.hyperbolic_orbit_time(
            true_anomaly=orbital_elements_2.true_anomaly,
            specific_angular_momentum=h_t * u.km**2 / u.s,
            eccentricity=e_t * u.one,
            attractor=attractor)
    
    dm_2: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_2 * u.km / u.s, attractor=attractor)
    
    t_burn_2: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_2, attractor=attractor)
    
    oe_t = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=h_t * u.km**2 / u.s,
        semimajor_axis=a_t * u.km,
        eccentricity=e_t * u.dimensionless_unscaled,
        inclination=orbital_elements_1.inclination,
        right_ascension_of_ascending_node=orbital_elements_1.right_ascension_of_ascending_node,
        argument_of_periapsis=orbital_elements_1.argument_of_periapsis,
        true_anomaly=orbital_elements_1.true_anomaly)
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list = [dv_1 * u.km / u.s, dv_2 * u.km / u.s]
    maneuver.flight_time_list = [t_2 - t_1]
    maneuver.delta_mass_list = [dm_1, dm_2]
    maneuver.burn_time_list=[t_burn_1, t_burn_2]
    maneuver.orbital_elements_list = [oe_t]
    maneuver.true_anomaly_list=[orbital_elements_1.true_anomaly, orbital_elements_2.true_anomaly]
    maneuver.rocket_elevation_angle_list=[phi_1 * u.rad, phi_2 * u.rad]
    
    return maneuver

def apse_line_rotation_from_eta(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements,
    apse_line_rotation_angle: u.Quantity,
    second_intersection_point: bool = False) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Apse line rotation from angle variation :math:`\\eta`.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :param apse_line_rotation_angle: Apse line rotation angle
    :type apse_line_rotation_angle: u.Quantity
    :param second_intersection_point: True for using the second intersection point, defaults to False
    :type second_intersection_point: bool, optional
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    An **apse-line rotation maneuver** is a two-impulse orbital maneuver used to rotate the line of apsides (the line
    connecting pericenter and apocenter) of an elliptical orbit by a specified angle :math:`\\eta`, without changing the
    orbital energy or inclination. This maneuver is required when the spacecraft must realign its argument of
    perigee to match a target orbit or to achieve a specific geometric configuration for rendezvous, phasing, or
    mission design.
    
    The maneuver exploits the fact that two coaxial elliptical orbits with different arguments of perigee intersect
    at two points. By performing impulsive burns at one of these intersection points, the spacecraft can transition
    from the initial orbit to the target orbit while rotating the apse line by the desired angle.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.7 *Apse line rotation*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor
    
    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_1
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_2
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * apse_line_rotation_angle
    
    err_msg = sl_validator.validate_quantity_angle("apse_line_rotation_angle", apse_line_rotation_angle)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * second_intersection_point
    
    err_msg = sl_validator.validate_type("second_intersection_point", second_intersection_point, bool)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    eta: float = apse_line_rotation_angle.to_value(u.rad)
    
    # ? 1. Orbit parameters
    
    e_1: float = orbital_elements_1.eccentricity.to_value()
    
    h_1: float = orbital_elements_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
    
    e_2: float = orbital_elements_2.eccentricity.to_value()
    
    h_2: float = orbital_elements_2.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
    
    # ? 2. Coefficients a, b, c of the quadratic equation for the true anomaly at the intersection point
    
    a: float = e_1 * h_2**2 - e_2 * h_1**2 * np.cos(eta)
    
    b: float = - e_2 * h_1**2 * np.sin(eta)
    
    c: float = h_1**2 - h_2**2
    
    phi: float = np.arctan(b / a)
    
    sign: int = 1 if not second_intersection_point else -1
    
    ta_1: float = phi + sign * np.arccos(c / a * np.cos(phi))
    
    if ta_1 < 0: ta_1 = 2 * np.pi + ta_1
    
    r: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(ta_1))
    
    # ? 3. Orbit 1
    
    v_t_1: float = h_1 / r
    
    v_r_1: float = mu / h_1 * e_1 * np.sin(ta_1)
    
    v_1: float = np.sqrt(v_r_1**2 + v_t_1**2)
    
    fpa_1: float = np.arctan(v_r_1 / v_t_1)
    
    # ? 4. Orbit 2
    
    v_t_2: float = h_2 / r
    
    v_r_2: float = mu / h_2 * e_2 * np.sin(ta_1 - eta)
    
    v_2: float = np.sqrt(v_r_2**2 + v_t_2**2)
    
    fpa_2: float = np.arctan(v_r_2 / v_t_2)
    
    # ? 5. Result
    
    delta_fpa: float = fpa_2 - fpa_1
    
    dv: float = np.sqrt(v_1**2 + v_2**2 - 2 * v_1 * v_2 * np.cos(delta_fpa))
    
    phi: float = 0.0
    #phi: float = np.pi - np.arcsin(v_2 / dv * np.sin(delta_fpa)) + fpa_1
    
    if np.abs(v_t_2 - v_t_1) < 1e-6:
        
        phi = np.pi if v_r_2 - v_r_1 > 0 else -np.pi
        
    else:
        
        phi = np.arctan((v_r_2 - v_r_1) / (v_t_2 - v_t_1))
        
    if (phi < 0): phi += np.pi
    
    dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, attractor=attractor)
    
    t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm
    
    # TODO: check if I should deepcopy orbital_elements_2
    oe_t = sl_orbital_elements.OrbitalElements(true_anomaly=((ta_1 - eta) * u.rad).to(u.deg))
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list = [dv * u.km / u.s]
    maneuver.flight_time_list = [0 * u.s]
    maneuver.delta_mass_list = [dm]
    maneuver.burn_time_list=[t_burn]
    maneuver.orbital_elements_list = [oe_t]
    maneuver.true_anomaly_list=[(ta_1 * u.rad).to(u.deg)]
    maneuver.rocket_elevation_angle_list = [(phi * u.rad).to(u.deg)]
    
    return maneuver

def apse_line_rotation_from_true_anomaly(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements: sl_orbital_elements.OrbitalElements,
    delta_velocity: u.Quantity,
    flight_path_angle: u.Quantity) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Apse line rotation from true anomaly.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements: Orbital elements of the initial orbit
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :param delta_velocity: Delta velocity
    :type delta_velocity: u.Quantity
    :param flight_path_angle: Flight path angle of delta velocity
    :type flight_path_angle: u.Quantity
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    This maneuver computes the rotation of the line of apsides (argument of perigee change) produced by a single,
    finite-magnitude impulse applied at a given true anomaly on an elliptical orbit. Unlike apse-line rotation
    maneuvers defined by a desired angle between two orbits, this formulation starts from a prescribed
    :math:`\\Delta \\mathbf{v}` vector (magnitude and flight-path angle) and determines the resulting change in the
    orbit's geometry.
    
    The algorithm assumes:
    
    - coplanar motion around a central body
    - an impulsive burn applied at the current position of the spacecraft
    - the burn direction defined in the local orbital frame by a flight path angle relative to the local velocity
    direction
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.7 *Apse line rotation*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor
    
    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * delta_velocity
    
    err_msg = sl_validator.validate_quantity("delta_velocity", delta_velocity, u.km / u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * flight_path_angle
    
    err_msg = sl_validator.validate_quantity_angle("flight_path_angle", flight_path_angle)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    # ? 1. Orbit 1
    
    e_1: float = orbital_elements.eccentricity.to_value()
    
    h_1: float = orbital_elements.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
    
    ta_1: float = orbital_elements.true_anomaly.to_value(u.rad)
    
    r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(ta_1))
    
    v_t_1: float = h_1 / r_1
    
    v_r_1: float = mu / h_1 * e_1 * np.sin(ta_1)
    
    # ? 2. Delta v
    
    dv_t: float = delta_velocity.to_value(u.km / u.s) * np.cos(flight_path_angle.to_value(u.rad))
    
    dv_r: float = delta_velocity.to_value(u.km / u.s) * np.sin(flight_path_angle.to_value(u.rad))
    
    # ? 3. Orbit 2
    
    h_2: float = h_1 + r_1 * dv_t
    
    numerator: float = (v_t_1 + dv_t) * (v_r_1 + dv_r) * v_t_1**2 * 1 / (mu / r_1)
    
    denominator: float = (v_t_1 + dv_t)**2 * e_1 * np.cos(ta_1) + (2 * v_t_1 + dv_t) * dv_t
    
    ta_2: float = np.arctan(numerator / denominator)
    
    eta: float = ta_1 - ta_2
    
    e_2: float = ((h_1 + r_1 * dv_t)**2 * e_1 * np.cos(ta_1) + (2 * h_1 + r_1 * dv_t) * r_1 * dv_t) /\
        (h_1**2 * np.cos(ta_2))
    
    r_p_2: float = h_2**2 / mu * 1 / (1 + e_2)
    
    r_a_2: float = h_2**2 / mu * 1 / (1 - e_2)
    
    # ? 4. Result
    
    dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=delta_velocity, attractor=attractor)
    
    t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm
    
    oe_t = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=h_2 * u.km**2 / u.s,
        semimajor_axis=0.5 * (r_p_2 + r_a_2) * u.km,
        eccentricity=e_2 * u.one,
        inclination=orbital_elements.inclination,
        right_ascension_of_ascending_node=orbital_elements.right_ascension_of_ascending_node,
        argument_of_periapsis=(orbital_elements.argument_of_periapsis.to_value(u.rad) + eta) * u.rad,
        true_anomaly=ta_2 * u.rad)
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list = [delta_velocity]
    maneuver.flight_time_list = [0 * u.s]
    maneuver.delta_mass_list = [dm]
    maneuver.burn_time_list=[t_burn]
    maneuver.orbital_elements_list = [oe_t]
    maneuver.true_anomaly_list=[(ta_1 * u.rad).to(u.deg)]
    maneuver.rocket_elevation_angle_list = [flight_path_angle]
    
    return maneuver

def chase_maneuver(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements: sl_orbital_elements.OrbitalElements,
    true_anomaly_target: u.Quantity,
    delta_time: time.TimeDelta) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Chase maneuver from Chaser C to Target T.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements: Orbital elements of the initial orbit
    :type orbital_elements: sl_orbital_elements.OrbitalElements
    :param true_anomaly_target: True anomaly of Target
    :type true_anomaly_target: u.Quantity
    :param delta_time: Delta time for the interception
    :type delta_time: time.TimeDelta
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    A **chase maneuver** is a two-impulse orbital maneuver used to intercept a target spacecraft located at a known true
    anomaly after a specified time interval. Unlike a phasing maneuver, which adjusts the orbital period to achieve
    alignment after several revolutions, the chase maneuver computes a single transfer ellipse that brings the
    chaser to the target's position exactly after a prescribed time of flight :math:`\\Delta t`.
    
    This maneuver is essential for time-critical rendezvous operations, interception trajectories, and short-arc
    pursuit strategies.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.8 *Chase maneuvers*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor
    
    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * true_anomaly_target
    
    err_msg = sl_validator.validate_quantity_angle("true_anomaly_target", true_anomaly_target)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * delta_time
    
    err_msg = sl_validator.validate_time_delta("delta_time", delta_time)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    # ? 1. Parameters of the chaser and target orbits
    
    h: float = orbital_elements.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
    
    T: float = orbital_elements.calc_orbital_period(attractor=attractor).to_value(u.s)
    
    # ? 2. Perifocal Frame state vector for Chaser C
    
    e: float = orbital_elements.eccentricity.to_value()
    
    ta_c: float = orbital_elements.true_anomaly.to_value(u.rad)
    
    r_c: np.ndarray = h**2 / mu * 1 / (1 + e * np.cos(ta_c)) * np.array([np.cos(ta_c), np.sin(ta_c), 0])
    
    v_c: np.ndarray = mu / h * np.array([-np.sin(ta_c), (e + np.cos(ta_c)), 0])
    
    # ? 3. New Perifocal Frame state vector for Target T after dt
    
    t_t: float = sl_position.elliptical_orbit_time(
        true_anomaly=true_anomaly_target, period=T * u.s, eccentricity=e * u.one).to_value(u.s)
    
    t_t_new: float = t_t + delta_time.to_value(u.s)
    
    ta_t_new: float = sl_position.elliptical_orbit_true_anomaly(
        time_of_flight=t_t_new * u.s, period=T * u.s, eccentricity=e * u.one).to_value(u.rad)
    
    r_t: np.ndarray = h**2 / mu * 1 / (1 + e * np.cos(ta_t_new)) * np.array([np.cos(ta_t_new), np.sin(ta_t_new), 0])
    
    v_t: np.ndarray = mu / h * np.array([-np.sin(ta_t_new), (e + np.cos(ta_t_new)), 0])
    
    # ? 4. Lambert problem solution for the transfer from C to T in time dt
    
    r_c: u.Quantity = sl_representation.perifocal_to_geocentric_equatorial_position_vector(
        orbital_elements=orbital_elements, perifocal_position=r_c * u.km)
    
    r_t: u.Quantity = sl_representation.perifocal_to_geocentric_equatorial_position_vector(
        orbital_elements=orbital_elements, perifocal_position=r_t * u.km)
    
    if orbital_elements.inclination <= 90.0 * u.deg:
        
        direction = sl_enums.OrbitDirection.PROGRADE
        
    else:
        
        direction = sl_enums.OrbitDirection.RETROGRADE
    
    lambert_res: ty.Optional[ty.Tuple[u.Quantity, u.Quantity, sl_orbital_elements.OrbitalElements, u.Quantity]] =\
        sl_determination.lambert(
            attractor=attractor,
            departure_position=r_c,
            arrival_position=r_t,
            delta_time=delta_time,
            direction=direction)
    
    if lambert_res == None: return None
    
    v_t_c, v_t_t, oe_t, ta_t_2 = lambert_res
    
    oe_t_2: sl_orbital_elements.OrbitalElements = cp.deepcopy(oe_t)
    
    oe_t_2.true_anomaly = ta_t_2
    
    # ? 5. Result
    
    dv_1: u.Quantity = np.linalg.norm(v_t_c.to_value(u.km / u.s) - v_c) * u.km / u.s
    
    dv_2: u.Quantity = np.linalg.norm(v_t - v_t_t.to_value(u.km / u.s)) * u.km / u.s
    
    dm_1: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_1, attractor=attractor)
    
    t_burn_1: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_1, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm_1
    
    dm_2: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_2, attractor=attractor)
    
    t_burn_2: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_2, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm_2
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list = [dv_1, dv_2]
    maneuver.flight_time_list = [delta_time.to_value(u.s) * u.s]
    maneuver.delta_mass_list = [dm_1, dm_2]
    maneuver.burn_time_list=[t_burn_1, t_burn_2]
    maneuver.orbital_elements_list = [oe_t, oe_t_2]
    
    return maneuver

def plane_change_maneuver_from_dihedral_angle(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements,
    dihedral_angle: u.Quantity) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Plane change maneuver from dihedral angle between orbital planes.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :param dihedral_angle: Dihedral angle between the two orbital planes in degrees
    :type dihedral_angle: u.Quantity
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    A **plane change maneuver** is a single-impulse orbital maneuver used to change the inclination and/or the right
    ascension of the ascending node (RAAN) of a spacecraft's orbit. When two orbits have different orientations, 
    the angle between their orbital planes is called the *dihedral angle*.
    
    This maneuver computes the :math:`\\Delta v` required to rotate the spacecraft's velocity vector by the dihedral
    angle at a specific point in the orbit, typically at the intersection of the two planes, to achieve the desired
    plane change. The algorithm calculates the velocity components in the initial and target orbits at the maneuver
    point and determines the required :math:`\\Delta v` to transition between the two planes while minimizing fuel
    consumption.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 6.9 *Plane change maneuvers*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor

    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_1

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_2

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * dihedral_angle
    
    err_msg = sl_validator.validate_quantity_angle("dihedral_angle", dihedral_angle)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    dihedral_angle: float = dihedral_angle.to_value(u.rad)
    
    # ? 1. Orbit 1
    
    e_1: float = orbital_elements_1.eccentricity.to_value()
    
    ta_1: float = orbital_elements_1.true_anomaly.to_value(u.rad)
    
    h_1: float = orbital_elements_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
    
    r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(ta_1))
    
    v_t_1: float = h_1 / r_1
    
    v_r_1: float = mu / h_1 * e_1 * np.sin(ta_1)
    
    # ? 2. Orbit 2
    
    e_2: float = orbital_elements_2.eccentricity.to_value()
    
    ta_2: float = orbital_elements_2.true_anomaly.to_value(u.rad)
    
    h_2: float = orbital_elements_2.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
    
    r_2: float = h_2**2 / mu * 1 / (1 + e_2 * np.cos(ta_2))
    
    v_t_2: float = h_2 / r_2
    
    v_r_2: float = mu / h_2 * e_2 * np.sin(ta_2)
    
    # ? 3. Result
    
    dv: float = np.sqrt((v_r_2 - v_r_1)**2 + v_t_1**2 + v_t_2**2 - 2 * v_t_1 * v_t_2 * np.cos(dihedral_angle))
    
    dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, attractor=attractor)
    
    t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list = [dv * u.km / u.s]
    maneuver.flight_time_list = [0 * u.s]
    maneuver.delta_mass_list = [dm]
    maneuver.burn_time_list=[t_burn]
    maneuver.orbital_elements_list = []
    
    return maneuver

def plane_change_maneuver_from_raan_and_inclination(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Plane change maneuver from RAAN and inclination differences.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    This maneuver computes the **plane change** required to transition between two orbits with different orientations
    by analyzing the differences in their right ascension of the ascending node (RAAN) and inclination.
    By determining the dihedral angle between the orbital planes from these angular differences, the maneuver
    calculates the necessary :math:`\\Delta v` to achieve the desired plane change while minimizing fuel consumption.
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor

    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_1

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_2

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    inc_1: float = orbital_elements_1.inclination.to_value(u.rad)
    inc_2: float = orbital_elements_2.inclination.to_value(u.rad)
    
    raan_1: float = orbital_elements_1.right_ascension_of_ascending_node.to_value(u.rad)
    raan_2: float = orbital_elements_2.right_ascension_of_ascending_node.to_value(u.rad)
    
    argp_1: float = orbital_elements_1.argument_of_periapsis.to_value(u.rad)
    argp_2: float = 0.0
    
    # ? 1. Differences
    
    delta_raan: float = raan_2 - raan_1
    
    delta_inc: float = inc_2 - inc_1
    
    # ? 2. Plane Change (spherical trigonometry)
    
    if delta_raan * delta_inc > 0:
        
        delta: float = np.arccos(np.cos(inc_1) * np.cos(inc_2) + np.sin(inc_1) * np.sin(inc_2) * np.cos(delta_raan))
        
        cos_u_1: float = (-np.cos(inc_2) + np.cos(delta) * np.cos(inc_1)) / (np.sin(delta) * np.sin(inc_1))
        cos_u_2: float = (+np.cos(inc_1) - np.cos(delta) * np.cos(inc_2)) / (np.sin(delta) * np.sin(inc_2))
        sin_u_1: float = np.sin(delta_raan) * np.sin(inc_2) / np.sin(delta)
        sin_u_2: float = np.sin(delta_raan) * np.sin(inc_1) / np.sin(delta)
        
        u_1: float = np.arctan2(sin_u_1, cos_u_1)
        u_2: float = np.arctan2(sin_u_2, cos_u_2)
        
        ta_1: float = u_1 - argp_1
        
        argp_2: float = ta_1 + u_2
    
    else:
        
        delta: float = np.arccos(np.cos(inc_1) * np.cos(inc_2) + np.sin(inc_1) * np.sin(inc_2) * np.cos(delta_raan))
        
        cos_u_1: float = (+np.cos(inc_2) - np.cos(delta) * np.cos(inc_1)) / (np.sin(delta) * np.sin(inc_1))
        cos_u_2: float = (-np.cos(inc_1) + np.cos(delta) * np.cos(inc_2)) / (np.sin(delta) * np.sin(inc_2))
        sin_u_1: float = np.sin(delta_raan) * np.sin(inc_2) / np.sin(delta)
        sin_u_2: float = np.sin(delta_raan) * np.sin(inc_1) / np.sin(delta)
        
        u_1: float = np.arctan2(sin_u_1, cos_u_1)
        u_2: float = np.arctan2(sin_u_2, cos_u_2)
        
        ta_1: float = 2 * np.pi - u_1 - argp_1
        
        argp_2: float = 2 * np.pi - u_2 - ta_1
    
    # ? 3. Orbit 1 at the maneuver point
    
    e_1: float = orbital_elements_1.eccentricity.to_value()
    
    h_1: float = orbital_elements_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
    
    r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(ta_1))
    
    v_t_1: float = h_1 / r_1
    
    # ? 4. Result
    
    dv: float = 2 * v_t_1 * np.sin(delta / 2)
    
    dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, attractor=attractor)
    
    t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm
    
    oe_t = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=orbital_elements_1.specific_angular_momentum,
        semimajor_axis=orbital_elements_1.semimajor_axis,
        eccentricity=orbital_elements_1.eccentricity,
        inclination=inc_2 * u.rad,
        right_ascension_of_ascending_node=raan_2 * u.rad,
        argument_of_periapsis=argp_2 * u.rad,
        true_anomaly=ta_1 * u.rad)
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list = [dv * u.km / u.s]
    maneuver.flight_time_list = [0 * u.s]
    maneuver.delta_mass_list = [dm]
    maneuver.burn_time_list=[t_burn]
    maneuver.orbital_elements_list = [oe_t]
    
    return maneuver

# * kluever

def inclination_change_maneuver(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements) -> ty.Optional[sl_results.ManeuverResult]:
    """
    [Genuine] Inclination change maneuver on line on nodes.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    A velocity increment with a component normal to the plane of the orbit will change the orientation of the orbital
    plane. To change inclination only, the velocity increment must be applied at the nodal crossing (i.e., the
    equatorial plane crossing).
    
    - *Ascending node*. The orbit-normal component of :math:`\\Delta \\mathbf{v}` is in the opposite direction as the
    angular momentum vector.
    - *Descending node*. The orbit-normal component of :math:`\\Delta \\mathbf{v}` is in the same direction as the
    angular momentum vector.

    The maneuver rotates the velocity vector "downward" (south) to the equatorial plane without changing its magnitude
    (also the angular momentum vector is rotated).
    
    📖 **References**
    
    - :cite:`kluever`
        - Section 7.5 *Inclination-Change Maneuver*
    - :cite:`walter`
        - Section 8.1 *One-Impulse Maneuvers*
        - Section 8.1.5 *Genuine Plane Change Maneuvers*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor

    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_1

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_2

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    delta_inc: float = (orbital_elements_2.inclination.to_value(u.rad) - orbital_elements_1.inclination.to_value(u.rad))
    
    # ? 1. Orbit 1
    
    omega: u.Quantity = orbital_elements_1.argument_of_periapsis.to(u.deg)
    
    ta_current: u.Quantity = sl_angle.wrap_angle(orbital_elements_1.true_anomaly.to(u.deg))

    ta_an: u.Quantity = sl_angle.wrap_angle(-omega) # * True anomaly of Ascending Node
    
    ta_dn: u.Quantity = sl_angle.wrap_angle(180 * u.deg - omega) # * True anomaly of Descending Node
    
    ta_1: u.Quantity = ta_dn if (ta_an < ta_current < ta_dn) else ta_an
    
    oe_1: sl_orbital_elements.OrbitalElements = cp.deepcopy(orbital_elements_1)
    
    oe_1.true_anomaly = ta_1
    
    v_1: float = oe_1.calc_velocity(attractor=attractor).to_value(u.km / u.s)
    
    fpa_1: float = oe_1.calc_flight_path_angle(attractor=attractor).to_value(u.rad)
    
    # ? 2. Result
    
    dv: float = np.abs(2 * v_1 * np.cos(fpa_1) * np.sin(delta_inc / 2))
    
    dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, attractor=attractor)
    
    t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list=[dv * u.km / u.s]
    maneuver.flight_time_list=[0 * u.s]
    maneuver.delta_mass_list=[dm]
    maneuver.burn_time_list=[t_burn]
    maneuver.true_anomaly_list=[ta_1]
    
    return maneuver

# * walter

def circular_hohmann_transfer( # NOSONAR python:S3776
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements,
    direction: sl_enums.HohmannDirection) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Hohmann transfer maneuver between circular orbits.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :param direction: Direction of the transfer
    :type direction: sl_enums.HohmannDirection
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    The **Hohmann transfer** (Hohmann, 1925) is the most energy efficient two-impulse orbital maneuver used to transfer
    a spacecraft between two coplanar, elliptical or circular orbits sharing a common focus. It is a widely used
    approximation for transfers between low-eccentricity orbits. The Hohmann transfer is an elliptical orbit tangent to
    both circles at its apse line.
            
    This implementation generalizes the classical Hohmann transfer to allow transfers between arbitrary coplanar 
    elliptical orbits, using one of two possible geometric configurations:
    
    - pericenter -> apocenter
    - apocenter -> pericenter
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.3 *Hohmann Transfer*
        - Section 8.3.2 *Transfer Between Circular Orbits*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor

    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_1

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    if not np.isclose(orbital_elements_1.eccentricity.to_value(u.one), 0.0, rtol=0.0, atol=1e-12):

        sl_logger.logger.warning("'orbital_elements_1' must describe a circular orbit")

        return None
    
    # * orbital_elements_2

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    if not np.isclose(orbital_elements_2.eccentricity.to_value(u.one), 0.0, rtol=0.0, atol=1e-12):

        sl_logger.logger.warning("'orbital_elements_2' must describe a circular orbit")

        return None
    
    # * direction

    err_msg = sl_validator.validate_type("direction", direction, sl_enums.HohmannDirection)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    # ? 0. Orbit radii
    
    r_1: float = orbital_elements_1.semimajor_axis.to_value(u.km)
    r_2: float = orbital_elements_2.semimajor_axis.to_value(u.km)
    
    # ? 1. Inner/Outer orbits
    
    r_inn: float = min(r_1, r_2)
    r_out: float = max(r_1, r_2)
    
    v_inn: float = np.sqrt(mu / r_inn)
    v_out: float = np.sqrt(mu / r_out)
    
    # ? 2. Transfer orbit
    
    swap: bool = False
    
    if direction == sl_enums.HohmannDirection.PERICENTER_APOCENTER:
        
        swap = r_inn > r_out
        
    elif direction == sl_enums.HohmannDirection.APOCENTER_PERICENTER:
        
        swap = r_out > r_inn
    
    a_t: float = 0.5 * (r_inn + r_out)
    
    e_t: float = (r_out - r_inn) / (r_out + r_inn)
    
    h_t: float = np.sqrt(2 * mu) * np.sqrt(r_out * r_inn / (r_out + r_inn))
    
    t_t: float = 2 * np.pi * np.sqrt(a_t**3 / mu) # ? Orbital Period
    
    # ? 3. Delta-V Calculation
    
    dv: float = (v_inn - v_out) * ( (np.sqrt(r_inn) + np.sqrt(r_out)) / np.sqrt(a_t) - 1 )
    
    ta_1: float = 0.0 # ? True anomaly at first maneuver point
    ta_t: float = 0.0 # ? True anomaly at second maneuver point
    
    if direction == sl_enums.HohmannDirection.PERICENTER_APOCENTER:
        
        ta_1 = 0.0
        
        ta_t = 0.0 if not swap else 180.0
    
    elif direction == sl_enums.HohmannDirection.APOCENTER_PERICENTER:
        
        ta_1 = 180.0
        
        ta_t = 180.0 if not swap else 0.0
    
    argp_t: float = orbital_elements_1.argument_of_periapsis.to_value(u.deg)
    
    if swap:
        
        argp_t = sl_angle.wrap_angle((argp_t + 180.0) * u.deg, -180.0 * u.deg, +180.0 * u.deg).to_value(u.deg)
    
    # ? 4. Result
    
    dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, attractor=attractor)
    
    t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm
    
    oe_t = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=h_t * u.km**2 / u.s,
        semimajor_axis=a_t * u.km,
        eccentricity=e_t * u.one,
        inclination=orbital_elements_1.inclination,
        right_ascension_of_ascending_node=orbital_elements_1.right_ascension_of_ascending_node,
        argument_of_periapsis=argp_t * u.deg,
        true_anomaly=ta_t * u.deg)

    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list=[dv * u.km / u.s]
    maneuver.flight_time_list=[0.5 * t_t * u.s]
    maneuver.delta_mass_list=[dm]
    maneuver.burn_time_list=[t_burn]
    maneuver.orbital_elements_list=[oe_t]
    maneuver.true_anomaly_list=[ta_1 * u.deg]
    maneuver.rocket_elevation_angle_list=[0 * u.deg, 0 * u.deg]
    
    return maneuver

def one_impulse_maneuver(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements) -> ty.Optional[sl_results.ManeuverResult]:
    """
    Generic one-impulse maneuver.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    The **one-impulse maneuver** is the foundation of any maneuvering in space. It ideally is a finite thrust firing
    with vanishingly short duration, a so-called boost, kick-burn or just burn for short, causing a certain
    :math:`\\Delta v`.
    
    The boost :math:`\\Delta v` to achieve :math:`\\Delta v'` is minimal at the lowest orbital radius and hence
    highest velocity of the orbit. This unexpected effect is called the *Oberth effect*, after Hermann Oberth, an
    Austro-Hungarian-born rocket scientist who discovered this effect in 1929.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.1 *One-Impulse Maneuvers*
        - Section 8.1.3 *General Maneuvers*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor

    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_1

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_2

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    # ? 1. Orbit 1
    
    inc_1: float = orbital_elements_1.inclination.to_value(u.rad)
    
    raan_1: float = orbital_elements_1.right_ascension_of_ascending_node.to_value(u.rad)
    
    v_1: float = orbital_elements_1.calc_velocity(attractor=attractor).to_value(u.km / u.s)
    
    # ? 2. Orbit 2
    
    inc_2: float = orbital_elements_2.inclination.to_value(u.rad)
    
    raan_2: float = orbital_elements_2.right_ascension_of_ascending_node.to_value(u.rad)
    
    v_2: float = orbital_elements_2.calc_velocity(attractor=attractor).to_value(u.km / u.s)
    
    # ? 3. Result
    
    delta_inc: float = (inc_2 - inc_1)
    
    delta_raan: float = (raan_2 - raan_1)
    
    sin_phi_2: float = np.sin(delta_inc / 2)**2 + np.sin(inc_1) * np.sin(inc_2) * np.sin(delta_raan / 2)**2
    
    dv: float = np.sqrt( (v_1 - v_2)**2 + 4 * v_1 * v_2 * sin_phi_2 )
    
    dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, attractor=attractor)

    t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, attractor=attractor)

    rocket_motor.spacecraft_mass -= dm
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list=[dv * u.km / u.s]
    maneuver.flight_time_list=[0 * u.s]
    maneuver.delta_mass_list=[dm]
    maneuver.burn_time_list=[t_burn]
    maneuver.true_anomaly_list=[orbital_elements_1.true_anomaly.to(u.deg)]
    
    return maneuver

def raan_change_maneuver(
    attractor: sl_bodies.Attractor,
    rocket_motor: sl_rocket_motor.RocketMotor,
    orbital_elements_1: sl_orbital_elements.OrbitalElements,
    orbital_elements_2: sl_orbital_elements.OrbitalElements) -> ty.Optional[sl_results.ManeuverResult]:
    """
    [Genuine] Right Ascension of Ascending Node (RAAN) change maneuver.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param rocket_motor: Rocket motor parameters
    :type rocket_motor: sl_rocket_motor.RocketMotor
    :param orbital_elements_1: Orbital elements of the initial orbit
    :type orbital_elements_1: sl_orbital_elements.OrbitalElements
    :param orbital_elements_2: Orbital elements of the target orbit
    :type orbital_elements_2: sl_orbital_elements.OrbitalElements
    :return: Maneuver result
    :rtype: ty.Optional[sl_results.ManeuverResult]
    
    📌 **Notes**
    
    The rotation is achieved for a :math:`\\Delta \\mathbf{v}` that lies in either plane tangent to the two points at
    90° abeam from the nodes of the initial orbit with the reference plane. Obviously, a RAAN change by
    :math:`\\Delta\\Omega = 180°` is identical to an inclination change by :math:`\\Delta i = 2 i`.
    
    Adjust RAAN at the lowest inclination and/or orbital velocity possible.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.1 *One-Impulse Maneuvers*
        - Section 8.1.5 *Genuine Plane Change Maneuvers*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * rocket_motor

    err_msg = sl_validator.validate_type("rocket_motor", rocket_motor, sl_rocket_motor.RocketMotor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_1

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_1)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_2

    err_msg = sl_validator.validate_orbital_elements(orbital_elements_2)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    inc: u.Quantity = orbital_elements_1.inclination.to(u.deg)
    
    raan_1: float = orbital_elements_1.right_ascension_of_ascending_node.to_value(u.rad)
    
    raan_2: float = orbital_elements_2.right_ascension_of_ascending_node.to_value(u.rad)
    
    delta_raan: float = (raan_2 - raan_1)
    
    # ? 1. Orbit 1
    
    omega: u.Quantity = orbital_elements_1.argument_of_periapsis.to(u.deg)
    
    ta_current: u.Quantity = sl_angle.wrap_angle(orbital_elements_1.true_anomaly.to(u.deg))

    ta_an: u.Quantity = sl_angle.wrap_angle(-omega + 90 * u.deg) # * Orthogonal to Node (+ 90°)
    
    ta_dn: u.Quantity = sl_angle.wrap_angle(-omega - 90 * u.deg) # * Orthogonal Node (- 90°)
    
    ta_1: u.Quantity = ta_dn if (ta_an < ta_current < ta_dn) else ta_an
    
    ta_1 += 90 * u.deg - inc if inc <= 90 * u.deg else 180 * u.deg - inc
    
    # TODO: why am I assigning the current value???
    ta_1 = ta_current
    
    oe_1: sl_orbital_elements.OrbitalElements = cp.deepcopy(orbital_elements_1)
    
    oe_1.true_anomaly = ta_1
    
    v_1: float = oe_1.calc_velocity(attractor=attractor).to_value(u.km / u.s)
    
    fpa_1: float = oe_1.calc_flight_path_angle(attractor=attractor).to_value(u.rad)
    
    # ? 2. Result
    
    dv: float = np.abs(2 * v_1 * np.cos(fpa_1) * np.sin(inc.to_value(u.rad)) * np.sin(delta_raan / 2))
    
    dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, attractor=attractor)
    
    t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, attractor=attractor)
    
    rocket_motor.spacecraft_mass -= dm
    
    maneuver = sl_results.ManeuverResult()
    
    maneuver.delta_velocity_list=[dv * u.km / u.s]
    maneuver.flight_time_list=[0 * u.s]
    maneuver.delta_mass_list=[dm]
    maneuver.burn_time_list=[t_burn]
    maneuver.true_anomaly_list=[ta_1]
    
    return maneuver

def _lambert_equation(x: float, dtau: float, s_minus: float, s_plus: float) -> float:
    """
    Universal-variable Lambert's equation.

    :param x: Variable
    :type x: float
    :param dtau: Normalized delta time
    :type dtau: float
    :param s_minus: s minus variable
    :type s_minus: float
    :param s_plus: s plus variable
    :type s_plus: float
    :return: Result
    :rtype: float
    
    📌 **Notes**
    
    The transfer time of a body moving between two points in a conic trajectory is a function only of the sum of the
    distances of the two points from the origin of force, the length of the chord joining these two points, and the
    semi-major axis of the conic.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.2 *Lambert Transfer*
        - Section 8.2.3 *Lambert's Problem*
    """
    
    c_minus: float = np.sqrt(1 - x * s_minus**2)
    
    c_plus: float = np.sqrt(1 - x * s_plus**2)
    
    u_: float = x * (s_plus * c_minus - s_minus * c_plus)**2
    
    L: float = 0 # * Universal L-function
    
    if np.abs(u_) < 1e-12: # * Parabola
        
        L = 1
        
    elif u_ >= 0 and u_ <= 1: # * Ellipse
        
        L = np.arcsin(np.sqrt(u_)) / np.sqrt(u_)
    
    elif u_ < 0: # * Hyperbola
        
        L = np.arcsinh(np.sqrt(-u_)) / np.sqrt(-u_)
    
    return 0.5 * dtau * x + s_plus * c_plus - s_minus * c_minus - (s_plus * c_minus - s_minus * c_plus) * L

def lambert(
    attractor: sl_bodies.Attractor,
    departure_position: u.Quantity,
    arrival_position: u.Quantity,
    delta_time: time.TimeDelta) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Solves **Lambert**'s problem.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param departure_position: Position vector at departure
    :type departure_position: u.Quantity
    :param arrival_position: Position vector at arrival
    :type arrival_position: u.Quantity
    :param delta_time: Time of flight between `departure_position` and `arrival_position`
    :type delta_time: time.TimeDelta
    :return: (velocity at departure, velocity at arrival, Lambert transfer eccentricity, Lambert transfer semi-latus rectum)
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    Calculation scheme for an Universal Solution to Lambert's problem.
    
    The problem to find the according transfer orbit is called Lambert's problem (Lambert 1761). It can be stated as
    follows: *the determination of an orbit, having a specified transfer time and connecting two position vectors*, or
    in other words *to solve for the trajectory connecting two position vectors with a given time of flight*.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.2 *Lambert Transfer*
        - Section 8.2.3 *Lambert's Problem*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * departure_position
    
    err_msg = sl_validator.validate_quantity_vector("departure_position", departure_position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * arrival_position
    
    err_msg = sl_validator.validate_quantity_vector("arrival_position", arrival_position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * delta_time
    
    err_msg = sl_validator.validate_time_delta("delta_time", delta_time)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    # ? 0. Data
    
    r_1: np.ndarray = departure_position.to_value(u.km)
    r_2: np.ndarray = arrival_position.to_value(u.km)
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    dt: float = delta_time.to_value(u.s)
    
    # ? 1. Dimensionless numbers
    
    r_1_m : float = np.linalg.norm(r_1)
    r_2_m: float = np.linalg.norm(r_2)
    
    c: float = np.sqrt(r_1_m**2 + r_2_m**2 - 2 * np.dot(r_1, r_2)) # * Chord
    
    dtau: float = dt * np.sqrt(mu / c**3)
    
    s_plus: float = 0.5 * np.sqrt( (r_1_m + r_2_m) / c + 1 )
    
    s_minus: float = 0.5 * np.sqrt( (r_1_m + r_2_m) / c - 1 )
    
    # ? 2. Equation solver
    
    # ? x = c / a --> x < 0 => hyperbola, x == 0 => parabola, x > 0 => ellipse
    
    # * Battin's robust initial guess
    
    theta: float = np.arccos(np.clip(np.dot(r_1, r_2) / (r_1_m * r_2_m), -1.0, 1.0))

    x_0: float = 1.0 / (1.0 + (2.0 / np.pi) * ((dtau / (1.0 + np.sin(theta / 2))) - 1.0))
    
    x: float = 0.0
    
    try:
        
        x = optimize.newton(func=_lambert_equation, x0=x_0, args=(dtau, s_minus, s_plus))
    
    except Exception:
                
        x = 0.0
    
    # ? 3. Dimensionless numbers
    
    c_minus: float = np.sqrt(1 - x * s_minus**2)
    
    c_plus: float = np.sqrt(1 - x * s_plus**2)
    
    lambda_: float = 2 * (s_plus * c_minus + s_minus * c_plus)**2
    
    rho_1: np.ndarray = r_1 / c
    
    rho_1_m: float = np.linalg.vector_norm(rho_1)
    
    rho_1_hat: np.ndarray = rho_1 / rho_1_m
    
    rho_2: np.ndarray = r_2 / c
    
    rho_2_m: float = np.linalg.vector_norm(rho_2)
    
    rho_2_hat: np.ndarray = rho_2 / rho_2_m
    
    rho: float = rho_1_m * rho_2_m - np.dot(rho_1, rho_2)
    
    # ? 4. Result
    
    coeff: float = np.sqrt(mu / c) * (np.sqrt(rho * lambda_)) / np.linalg.vector_norm(np.cross(rho_1, rho_2))
    
    v_1_plus: np.ndarray = coeff * (rho_2 - rho_1 + rho_1_hat / lambda_)
    
    v_2_minus: np.ndarray = coeff * (rho_2 - rho_1 - rho_2_hat / lambda_)
    
    e: np.ndarray = (1 - x * rho_1_m) * rho_1_hat - c / mu * np.dot(rho_1, v_1_plus) * v_1_plus
    
    p: float = c * rho * lambda_
    
    return [v_1_plus * u.km / u.s, v_2_minus * u.km / u.s, np.linalg.vector_norm(e) * u.one, p * u.km]

def super_synchronous_transfer(
    attractor: sl_bodies.Attractor,
    leo_inclination: u.Quantity,
    geo_inclination: u.Quantity,
    ssto: sl_orbital_elements.OrbitalElements) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Super-synchronous transfer maneuver.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param leo_inclination: Low Earth Orbit (LEO) inclination
    :type leo_inclination: u.Quantity
    :param geo_inclination: Geostationary Orbit (GEO) inclination
    :type geo_inclination: u.Quantity
    :param ssto: Super-synchronous Transfer Orbit (SSTO) orbital elements
    :type ssto: sl_orbital_elements.OrbitalElements
    :return: [delta-v for first burn, delta-v for second burn, delta-v for third burn]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    This maneuver computes the delta-v required for a **super-synchronous transfer** from a *low Earth orbit* (LEO) to a
    *geostationary orbit* (GEO) via a *super-synchronous transfer orbit* (SSTO). The algorithm calculates the necessary
    velocity changes at each stage of the transfer, taking into account the inclination differences between the
    orbits. The maneuver consists of three main burns: the first burn to enter the SSTO, the second burn to adjust
    the inclination and enter the *interim transfer orbit* (ITO), and the third burn to circularize the orbit at GEO.
    The resulting delta-v values for each burn are returned as a list.
    
    The first burn is performed by the launch vehicle to enter the SSTO.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.4 *Other Transfers*
        - Section 8.4.3 *Super-Synchronous Transfer Orbits*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * leo_inclination

    err_msg = sl_validator.validate_quantity_angle("leo_inclination", leo_inclination)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * geo_inclination

    err_msg = sl_validator.validate_quantity_angle("geo_inclination", geo_inclination)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * ssto

    err_msg = sl_validator.validate_orbital_elements(ssto)

    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    inc_leo: float = leo_inclination.to_value(u.rad)
    inc_geo: float = geo_inclination.to_value(u.rad)
    
    r_geo: float = sl_physical_constants.geocentric_equatorial_radius
    
    # ? 0.1 Extract SSTO orbit parameters
    
    h_ssto: float = ssto.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
    
    r_per_ssto: float = ssto.calc_periapsis_radius().to_value(u.km)
    r_apo_ssto: float = ssto.calc_apoapsis_radius().to_value(u.km)
    
    inc_ssto: float = ssto.inclination.to_value(u.rad)
    
    # ? 0.2 Create ITO orbit parameters
    
    r_per_ito: float = r_geo
    r_apo_ito: float = r_apo_ssto
    
    h_ito: float = np.sqrt(2 * mu) * np.sqrt(r_apo_ito * r_per_ito / (r_apo_ito + r_per_ito))
    
    # ? 1. First kick-burn to SSTO (from launch vehicle with small plane change)
    
    v_leo_m: float = np.sqrt(mu / r_per_ssto) # ? LEO -
    v_leo_p: float = h_ssto / r_per_ssto # ? LEO +
    
    dv_1: float = np.sqrt(v_leo_m**2 + v_leo_p**2 - 2 * v_leo_m * v_leo_p * np.cos(inc_leo - inc_ssto))
    
    # ? 2. Second kick-burn to ITO (with plane change)
    
    v_ito_m: float = h_ssto / r_apo_ssto # ? ITO -
    v_ito_p: float = h_ito / r_apo_ssto # ? ITO +
    
    dv_2: float = np.sqrt(v_ito_m**2 + v_ito_p**2 - 2 * v_ito_m * v_ito_p * np.cos(inc_ssto - inc_geo))
    
    # ? 3. Third kick-burn to GEO
    
    v_geo_m: float = h_ito / r_geo # ? GEO -
    v_geo_p: float = np.sqrt(mu / r_geo) # ? GEO +
    
    dv_3: float = v_geo_m - v_geo_p
    
    # ? 4. Result
    
    return [dv_1 * u.km / u.s, dv_2 * u.km / u.s, dv_3 * u.km / u.s]
