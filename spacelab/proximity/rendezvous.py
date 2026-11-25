"""
This modules contains the **rendezvous** utilities used in proximity operations.

We should emphasize that the Clohessy-Wiltshire equations are an approximation of the twobody dynamics, and, like all
linearized systems, this approximation is only accurate for "small" deviations from the reference state.

📖 **References**

- :cite:`curtis`
    - Chapter 7 *Relative Motion and Rendezvous*
- :cite:`kluever`
    - Chapter 8 *Relative Motion and Orbital Rendezvous*
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
import spacelab.orbit.time as sl_time
import spacelab.proximity.kinematics as sl_kinematics
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

# * curtis

def clohessy_wiltshire_matrices(mean_motion: u.Quantity, final_time: u.Quantity) -> ty.Optional[ty.List[np.ndarray]]:
    """
    Clohessy-Wiltshire matrices.

    :param mean_motion: Target orbit mean motion
    :type mean_motion: u.Quantity
    :param final_time: Final time
    :type final_time: u.Quantity
    :return: [phi_rr, phi_rv, phi_vr, phi_vv]
    :rtype: ty.Optional[ty.List[np.ndarray]]
    
    📌 **Notes**
    
    The **Clohessy-Wiltshire** matrices are used to describe relative motion with circular orbits.
    
    .. math::
    
        \\begin{aligned}
        
        \\delta r(t) &= \\Phi_{rr} \\delta r_0 + \\Phi_{rv} \\delta v_0
        
        \\delta v(t) &= \\Phi_{vr} \\delta r_0 + \\Phi_{vv} \\delta v_0
        
        \\end{aligned}
    
    In rendezvous analysis, all kinematic quantities are relative to the Clohessy-Wiltshire (CW) frame.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 7.4 *Clohessy-Wiltshire equations*
    - :cite:`kluever`
        - Section 8.2 *Linear Clohessy-Wiltshire Equations*
        - Section 8.3 *Homogeneous Solution of the Clohessy-Wiltshire Equations*
    - :cite:`walter`
        - Section 8.5 *Relative Orbits*
        - Section 8.5.2 *Circular Orbits*
    """
    
    # >>> Validation
    
    # * mean_motion
    
    err_msg: str | None = sl_validator.validate_quantity("mean_motion", mean_motion, u.rad / u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * final_time
    
    err_msg = sl_validator.validate_quantity("final_time", final_time, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    n: float = mean_motion.to_value(u.rad / u.s)
    t: float = final_time.to_value(u.s)
    
    phi_rr: np.ndarray = np.array(
        [
            [ 4 - 3 * np.cos(n * t)       , 0 , 0             ],
            [ 6 * (np.sin(n * t) - n * t) , 1 , 0             ],
            [ 0                           , 0 , np.cos(n * t) ]
        ])
    
    phi_rv: np.ndarray = np.array(
        [
            [ 1 / n * np.sin(n * t)       , 2 / n * (1 - np.cos(n * t))             , 0                     ],
            [ 2 / n * (np.cos(n * t) - 1) , 1 / n * (4 * np.sin(n * t) - 3 * n * t) , 0                     ],
            [ 0                           , 0                                       , 1 / n * np.sin(n * t) ]
        ])
    
    phi_vr: np.ndarray = np.array(
        [
            [ 3 * n * np.sin(n * t)       , 0 , 0                   ],
            [ 6 * n * (np.cos(n * t) - 1) , 0 , 0                   ],
            [ 0                           , 0 , - n * np.sin(n * t) ]
        ])
    
    phi_vv: np.ndarray = np.array(
        [
            [ np.cos(n * t)       , 2 * np.sin(n * t)     , 0             ],
            [ - 2 * np.sin(n * t) , 4 * np.cos(n * t) - 3 , 0             ],
            [ 0                   , 0                     , np.cos(n * t) ]
        ])
    
    return [phi_rr, phi_rv, phi_vr, phi_vv]

def clohessy_wiltshire_equations(
    relative_position_0: u.Quantity,
    relative_velocity_0: u.Quantity,
    mean_motion: u.Quantity,
    final_time: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Clohessy-Wiltshire equations.

    :param relative_position_0: Initial relative position vector
    :type relative_position_0: u.Quantity
    :param relative_velocity_0: Initial relative velocity vector
    :type relative_velocity_0: u.Quantity
    :param mean_motion: Target orbit mean motion
    :type mean_motion: u.Quantity
    :param final_time: Final time
    :type final_time: u.Quantity
    :return: Final [dr, dv]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    The **Clohessy-Wiltshire** equations are used to describe relative motion with circular orbits.
    
    .. math::
    
        \\begin{aligned}
        
        \\delta r(t) &= \\Phi_{rr} \\delta r_0 + \\Phi_{rv} \\delta v_0
        
        \\delta v(t) &= \\Phi_{vr} \\delta r_0 + \\Phi_{vv} \\delta v_0
        
        \\end{aligned}
    
    In rendezvous analysis, all kinematic quantities are relative to the Clohessy-Wiltshire (CW) frame.
    
    Hill first derived these relative-motion equations in 1878; Clohessy and Wiltshire rediscovered them in a 1960 study
    on orbital rendezvous.
    
    These equations are a set of coupled, linear, time-invariant differential equations that describe the planar motion
    of a satellite relative to a reference circular orbit. We may think of the x, y, and z coordinates as the radial,
    along-track, and cross-track displacements of the satellite relative to the target moving in a reference circular
    orbit.
    
    We developed the homogeneous solution of the CW equations with zero thrust acceleration.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 7.4 *Clohessy-Wiltshire equations*
    - :cite:`kluever`
        - Section 8.2 *Linear Clohessy-Wiltshire Equations*
        - Section 8.3 *Homogeneous Solution of the Clohessy-Wiltshire Equations*
    - :cite:`walter`
        - Section 8.5 *Relative Orbits*
        - Section 8.5.2 *Circular Orbits*
    """
    
    # >>> Validation
    
    # * relative_position_0
    
    err_msg: str | None = sl_validator.validate_quantity_vector("relative_position_0", relative_position_0, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * relative_velocity_0
    
    err_msg = sl_validator.validate_quantity_vector("relative_velocity_0", relative_velocity_0, u.km / u.s, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * mean_motion
    
    err_msg = sl_validator.validate_quantity("mean_motion", mean_motion, u.rad / u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * final_time
    
    err_msg = sl_validator.validate_quantity("final_time", final_time, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    dr_0: np.ndarray = relative_position_0.to_value(u.km)
    
    dv_0: np.ndarray = relative_velocity_0.to_value(u.km / u.s)
    
    phi_rr, phi_rv, phi_vr, phi_vv = clohessy_wiltshire_matrices(mean_motion=mean_motion, final_time=final_time)
    
    dr: u.Quantity = (np.matmul(phi_rr, dr_0) + np.matmul(phi_rv, dv_0)) * u.km
    dv: u.Quantity = (np.matmul(phi_vr, dr_0) + np.matmul(phi_vv, dv_0)) * u.km / u.s
    
    return [dr, dv]

def two_impulsive_rendezvous_maneuver(
    attractor: sl_bodies.Attractor,
    orbital_elements_target: sl_orbital_elements.OrbitalElements,
    orbital_elements_chaser: sl_orbital_elements.OrbitalElements,
    maneuver_time: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Two-Impulse Rendezvous maneuver.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param orbital_elements_target: Target orbital elements
    :type orbital_elements_target: sl_orbital_elements.OrbitalElements
    :param orbital_elements_chaser: Chaser orbital elements
    :type orbital_elements_chaser: sl_orbital_elements.OrbitalElements
    :param maneuver_time: Maneuver time
    :type maneuver_time: u.Quantity
    :return: [Total delta velocity, dx coordinates, dy coordinates, dz coordinates]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    We consider the determination of an orbit transfer from an arbitrary initial state,
    :math:`(\\delta \\mathbf{r}_0, \\delta \\mathbf{v}_0)`, to the origin of the CW frame with a prescribed transfer
    time :math:`t`. Such a maneuver might represent an orbital insertion into a "slot" in a target orbit or orbital
    rendezvous with another satellite such as a space station.
    
    The first impulse is done at initial position to move closer to the target. The second impulse is done once the
    target is reached to nullify the relative velocity.
    
    When the transfer time is an exact multiple of the period of the reference orbit, the matrix :math:`\\Phi_{rv}`
    becomes singular.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 7.5 *Two-impulse rendezvous maneuvers*
    - :cite:`kluever`
        - Section 8.4 *Orbital Rendezvous Using the Clohessy-Wiltshire Equations*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_target
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements_target)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * orbital_elements_chaser
    
    err_msg = sl_validator.validate_orbital_elements(orbital_elements_chaser)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * maneuver_time
    
    err_msg = sl_validator.validate_quantity("maneuver_time", maneuver_time, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    if orbital_elements_target.eccentricity != 0:
        
        sl_logger.logger.warning("Target orbit must be a circle")
    
        return None
    
    # ? 1. LVLH kinematics at the beginning of the rendezvous
    
    dr_0, dv_0_minus, _, omega = sl_kinematics.local_vertical_local_horizontal_kinematics(
        attractor=attractor,
        orbital_elements_target=orbital_elements_target,
        orbital_elements_chaser=orbital_elements_chaser)
    
    n: u.Quantity = np.linalg.norm(omega.to_value(u.rad / u.s)) * u.rad / u.s # * Mean motion
    
    # ? 2. Clohessy-Wiltshire solution for the maneuver (when reached the target => dr = 0, dv = 0)
    
    phi_rr, phi_rv, _, _ = clohessy_wiltshire_matrices(mean_motion=n, final_time=maneuver_time)
    
    dv_0_plus: np.ndarray = - np.matmul(np.matmul(np.linalg.inv(phi_rv), phi_rr), dr_0.to_value(u.km))
    
    _, dv_f_minus = clohessy_wiltshire_equations(
        relative_position_0=dr_0, relative_velocity_0=dv_0_plus * u.km / u.s, mean_motion=n, final_time=maneuver_time)
    
    dv_f_plus: np.ndarray = np.zeros(shape=(3))
    
    # ? 3. Maneuver result
    
    dv_tot: float = np.linalg.norm(dv_0_plus - dv_0_minus.to_value(u.km / u.s)) + \
                    np.linalg.norm(dv_f_plus - dv_f_minus.to_value(u.km / u.s))
    
    dx: list = []
    dy: list = []
    dz: list = []
    
    # * Iterate on the maneuver time to obtain the rendezvous trajectory
    
    for t in np.linspace(0, maneuver_time.to_value(u.s), 1000):
        
        dr, _ = clohessy_wiltshire_equations(
            relative_position_0=dr_0, relative_velocity_0=dv_0_plus * u.km / u.s, mean_motion=n, final_time=t * u.s)
        
        dx.append(dr[0].to_value(u.km))
        dy.append(dr[1].to_value(u.km))
        dz.append(dr[2].to_value(u.km))
    
    return [dv_tot * u.km / u.s, np.array(dx) * u.km, np.array(dy) * u.km, np.array(dz) * u.km]

# * walter

def circular_orbit_rendezvous_maneuver(
    relative_position_0: u.Quantity,
    mean_motion: u.Quantity,
    final_time: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Circular orbit rendezvous maneuver.

    :param relative_position_0: Initial relative position vector
    :type relative_position_0: u.Quantity
    :param mean_motion: Mean motion of the target orbit
    :type mean_motion: u.Quantity
    :param final_time: Final time of the rendezvous maneuver
    :type final_time: u.Quantity
    :return: Initial relative velocity vector
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    If we consider the most common situation where the target is in a circular orbit, we can derive the
    **Hill's equations** (a.k.a. Clohessy-Wiltshire equations) governing the motion of a S/C, not being subject to
    external forces. By solving these equations we derive the CW matrices, that can be applied to orbital rendezvous,
    obtaining as solution:
    
    .. math::

        \\begin{aligned}
        
        \\frac{d(\\delta x_0)}{dt} &= -\\frac{\\delta x_0}{t} + n\\,\\delta y_0

        \\frac{d(\\delta y_0)}{dt} &= -\\frac{\\delta y_0}{t} - n\\,\\delta x_0

        \\frac{d(\\delta z_0)}{dt} &= -\\frac{\\delta z_0}{t}
        
        \\end{aligned}
    
    If at time :math:`t_0 = 0` a S/C is at an initial point
    :math:`\\mathbf{r}_0 = (\\delta x_0, \\delta y_0, \\delta z_0)` find the initial velocity
    :math:`\\mathbf{v}_0 = (\\dot{\\delta x}_0, \\dot{\\delta y}_0, \\dot{\\delta z}_0)` to meet after time :math:`t` a
    given target point :math:`\\mathbf{r} = (\\delta x, \\delta y, \\delta z) = (0, 0, 0)`.
    
    The solution is valid for :math:`(n \\cdot t)^2 << 1 \\implies t < 0.02 \\cdot T_{orbit}`.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 7.6 *Relative motion in close-proximity circular orbits*
    - :cite:`walter`
        - Section 8.5 *Relative Orbits*
        - Section 8.5.2 *Circular Orbits*
    """
    
    # >>> Validation
    
    # * relative_position_0
    
    err_msg: str | None = sl_validator.validate_quantity_vector("relative_position_0", relative_position_0, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * mean_motion
    
    err_msg = sl_validator.validate_quantity("mean_motion", mean_motion, u.rad / u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * final_time
    
    err_msg = sl_validator.validate_quantity("final_time", final_time, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    dx0: float = relative_position_0[0].to_value(u.km)
    dy0: float = relative_position_0[1].to_value(u.km)
    dz0: float = relative_position_0[2].to_value(u.km)
    
    n: float = mean_motion.to_value(u.rad / u.s)
    t: float = final_time.to_value(u.s)

    dx0_dt: float = - dx0 / t + n * dy0
    dy0_dt: float = - dy0 / t - n * dx0
    dz0_dt: float = - dz0 / t
    
    return [dx0_dt * u.km / u.s, dy0_dt * u.km / u.s, dz0_dt * u.km / u.s]

# ? Orbital Rendezvous mission phases

def launch_phase(
    timestamp: time.Time,
    launch_site_latitude: u.Quantity,
    launch_site_longitude: u.Quantity,
    target_inclination: u.Quantity,
    target_right_ascension_ascending_node: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Calculates the launch phase for a given timestamp and orbital parameters.

    :param timestamp: Timestamp
    :type timestamp: time.Time
    :param launch_site_latitude: Latitude of the launch site
    :type launch_site_latitude: u.Quantity
    :param launch_site_longitude: Longitude of the launch site
    :type launch_site_longitude: u.Quantity
    :param target_inclination: Inclination of the target orbit
    :type target_inclination: u.Quantity
    :param target_right_ascension_ascending_node: Right ascension of the ascending node of the target orbit
    :type target_right_ascension_ascending_node: u.Quantity
    :return: Universal times of launch [ascending pass, descending pass]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    The **launch phase** comprises the injection of the chaser (interceptor) into the orbital plane of the target, as
    well as achieving stable orbital conditions. To directly meet the plane of the target, the interceptor must be
    launched inside a narrow launch window.
    
    The **Universal Time of launch**, :math:`T_{UT}`, defines the moment in time when the launch site is in the plane of
    the International Space Station's orbit, the so-called *in-plane time*.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.6 *Orbital Rendezvous*
        - Section 8.6.1 *Launch Phase*
    """
    
    # >>> Validation
    
    # * timestamp
    
    err_msg: str | None = sl_validator.validate_time("timestamp", timestamp)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * launch_site_latitude
    
    err_msg = sl_validator.validate_quantity_angle("launch_site_latitude", launch_site_latitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * launch_site_longitude
    
    err_msg = sl_validator.validate_quantity_angle("launch_site_longitude", launch_site_longitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * target_inclination
    
    err_msg = sl_validator.validate_quantity_angle("target_inclination", target_inclination)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * target_right_ascension_ascending_node
    
    err_msg = sl_validator.validate_quantity_angle("target_right_ascension_ascending_node", target_right_ascension_ascending_node)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    beta: float = launch_site_latitude.to_value(u.rad)
    lambda_: float = launch_site_longitude.to_value(u.rad)
    inc: float = target_inclination.to_value(u.rad)
    raan: float = target_right_ascension_ascending_node.to_value(u.rad)
    
    # ? 1. Azimuth
    
    if (inc < abs(beta)):
        
        sl_logger.logger.error("target_inclination < ||launch_site_latitude||")
    
        return None
    
    if (inc > np.pi - abs(beta)):
        
        sl_logger.logger.error("target_inclination > 180° - ||launch_site_latitude||")
        
        return None
    
    azimuth_ascending_pass: u.Quantity = np.arcsin(np.cos(inc) / np.cos(beta)) * u.rad
    
    azimuth_descending_pass: u.Quantity = (np.pi - np.arcsin(np.cos(inc) / np.cos(beta))) * u.rad
    
    # ? 2. Universal Time of launch / in-plane time / launch time
    
    omega: float = sl_bodies.BODIES[sl_bodies.Attractor.EARTH].omega.to_value(u.rad / u.s) # * Earth’s sidereal rotation rate
    
    theta: ty.Optional[u.Quantity] = sl_time.local_sidereal_time(timestamp=timestamp, longitude=lambda_ * u.rad)
    
    if theta == None: return None
    
    theta = theta.to_value(u.rad)
    
    # ! θ = θ_G_MST_0 + λ
    
    lambda_u: float = np.arccos(np.cos(azimuth_ascending_pass.to_value(u.rad)) / np.sin(inc))
    
    universal_time_ascending_pass: u.Quantity = (raan + lambda_u - theta) / omega * u.s
    
    lambda_u = np.arccos(np.cos(azimuth_descending_pass.to_value(u.rad)) / np.sin(inc))
    
    universal_time_descending_pass: u.Quantity = (raan + lambda_u - theta) / omega * u.s
    
    return [universal_time_ascending_pass, universal_time_descending_pass]

def phasing(semimajor_axis_chaser: u.Quantity, semimajor_axis_target: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    After successful completion of the launch phase, the interceptor spacecraft achieves a stable orbit within the
    same plane as the target. The two orbits are thus coplanar and typically near circular.

    :param semimajor_axis_chaser: Semimajor axis of the chaser orbit
    :type semimajor_axis_chaser: u.Quantity
    :param semimajor_axis_target: Semimajor axis of the target orbit
    :type semimajor_axis_target: u.Quantity
    :return: [phase angle, closing distance]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    Since the target might be anywhere on its orbit, the first part of the target rendezvous, the so-called
    **far range rendezvous**, requires first a reduction in the distance to the target, until it can be acquired by the
    sensors of the interceptor, and then a transfer to a stable holding point on the trailing side of the target.
    
    This first part of far range rendezvous phase is called **phasing** because it is to reduce the so-called
    (orbital) phase angle :math:`\\theta`, which is the difference in true anomaly as measured in the flight direction
    from the target to the interceptor.
    
    Assumptions:
    
    - Assume small differences in the semi-major axes
    
    - Chaser semi-major axis < Target semi-major axis
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.6 *Orbital Rendezvous*
        - Section 8.6.2 *Phasing*
    """
    
    # >>> Validation
    
    # * semimajor_axis_chaser
    
    err_msg: str | None = sl_validator.validate_quantity("semimajor_axis_chaser", semimajor_axis_chaser, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * semimajor_axis_target
    
    err_msg = sl_validator.validate_quantity("semimajor_axis_target", semimajor_axis_target, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    a_chaser: float = semimajor_axis_chaser.to_value(u.km)
    a_target: float = semimajor_axis_target.to_value(u.km)
    
    # ? 1. Phase angle reduction per orbit revolution
    
    dtheta: float = 3 * np.pi * (a_chaser - a_target) / a_target
    
    # ? 2. Closing distance
    
    dx: float = dtheta * a_target
    
    return [np.abs(dtheta) * u.rad, np.abs(dx) * u.km]

def homing_phase(
    semimajor_axis_chaser: u.Quantity,
    semimajor_axis_target: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    The objective of the homing transfer, the second part of the far range rendezvous, is to transfer the
    interceptor to a stable holding and aiming point in the vicinity of the target. A prerequisite of the transfer
    is that the target must be acquired by the relative navigation sensors of the interceptor.

    :param semimajor_axis_chaser: Semimajor axis of the chaser orbit
    :type semimajor_axis_chaser: u.Quantity
    :param semimajor_axis_target: Semimajor axis of the target orbit
    :type semimajor_axis_target: u.Quantity
    :return: [Initial phase angle, Delta velocity for the Hohmann transfer]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    The **homing transfer** is a classical Hohmann transfer, where the orbits have a radial distance of typically only
    about 10 km. Owing to this, the phase angle at the beginning of the Hohmann maneuver is practically zero while
    its complement to 180°, the so-called lead angle, is :math:`\\alpha_L = 180 - \\theta \\sim 180°`.
    
    :math:`\\theta_i` is the initial phase angle and :math:`\\theta_f` is the final phase angle behind the target.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.6 *Orbital Rendezvous*
        - Section 8.6.3 *Homing Phase*
    """
    
    # >>> Validation
    
    # * semimajor_axis_chaser
    
    err_msg: str | None = sl_validator.validate_quantity("semimajor_axis_chaser", semimajor_axis_chaser, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * semimajor_axis_target
    
    err_msg = sl_validator.validate_quantity("semimajor_axis_target", semimajor_axis_target, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    a_chaser: float = semimajor_axis_chaser.to_value(u.km)
    a_target: float = semimajor_axis_target.to_value(u.km)
    
    mu: float = sl_bodies.BODIES[sl_bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
    
    v_target: float = np.sqrt(mu / a_target) # * Target orbit velocity
    
    r: float = (a_chaser - a_target) / a_target # * Relative difference in semi-major axes
    
    theta_f: float = np.rad2deg(np.abs(r)) # * Final phase angle behind the target
    
    theta_i: float = theta_f - 135 * r # * Initial phase angle (deg)
    
    dv: float = v_target * (np.sqrt(1 - r) - 1) # * Delta-v for the Hohmann transfer
    
    return [theta_i * u.deg, dv * u.km / u.s]

def closing_phase(
    semimajor_axis_target: u.Quantity,
    distance: u.Quantity,
    strategy: sl_enums.ClosingApproachStrategy,
    trajectory: sl_enums.ClosingApproachTrajectory = sl_enums.ClosingApproachTrajectory.ELLIPTIC,
    cycloidal_revolutions: int = 1,
    initial_velocity: u.Quantity = 0 * u.km / u.s) -> ty.Optional[u.Quantity]:
    """
    The target now is within range of the interceptor sensors and thus relative navigation can commence. This
    station-keeping point is essential to assess the situation and plan the upcoming closing maneuver.

    :param semimajor_axis_target: Semimajor axis of the target orbit
    :type semimajor_axis_target: u.Quantity
    :param distance: Distance to the target
    :type distance: u.Quantity
    :param strategy: Closing approach strategy
    :type strategy: sl_enums.ClosingApproachStrategy
    :param trajectory: Closing approach trajectory, defaults to sl_enums.ClosingApproachTrajectory.ELLIPTIC
    :type trajectory: sl_enums.ClosingApproachTrajectory, optional
    :param cycloidal_revolutions: Number of cycloidal revolutions, defaults to 1
    :type cycloidal_revolutions: int, optional
    :param initial_velocity: Initial velocity, defaults to 0 * u.km / u.s
    :type initial_velocity: u.Quantity, optional
    :return: Delta-v for the closing maneuver
    :rtype: ty.Optional[u.Quantity]
    
    📌 **Notes**
    
    The **closing maneuver** depends on the type of final approach (R-bar or V-bar) and we ingress the
    *Approach Ellipsoid*.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.6 *Orbital Rendezvous*
        - Section 8.6.4 *Closing Phase*
    """
    
    # >>> Validation
    
    # * semimajor_axis_target
    
    err_msg: str | None = sl_validator.validate_quantity("semimajor_axis_target", semimajor_axis_target, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * distance
    
    err_msg = sl_validator.validate_quantity("distance", distance, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * strategy
    
    err_msg = sl_validator.validate_type("strategy", strategy, sl_enums.ClosingApproachStrategy)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * trajectory
    
    err_msg = sl_validator.validate_type("trajectory", trajectory, sl_enums.ClosingApproachTrajectory)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * cycloidal_revolutions
    
    err_msg = sl_validator.validate_type("cycloidal_revolutions", cycloidal_revolutions, int)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * initial_velocity
    
    err_msg = sl_validator.validate_quantity("initial_velocity", initial_velocity, u.km / u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    a: float = semimajor_axis_target.to_value(u.km)
    v_0: float = initial_velocity.to_value(u.km / u.s)
    
    mu: float = sl_bodies.BODIES[sl_bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
    
    n: float = np.sqrt(mu / a**3) # * Target orbit mean motion
    
    dv: float = 0.0
    
    if strategy == sl_enums.ClosingApproachStrategy.V_BAR_POS or strategy == sl_enums.ClosingApproachStrategy.V_BAR_NEG:
        
        dx: float = distance.to_value(u.km)
        
        if trajectory == sl_enums.ClosingApproachTrajectory.ELLIPTIC: # * Safer
            
            dv = 2 * dx / 4 * n
        
        elif trajectory == sl_enums.ClosingApproachTrajectory.CYCLOIDAL: # * Efficient
            
            dv = 2 * dx / (6 * np.pi * cycloidal_revolutions) * n
    
    elif strategy == sl_enums.ClosingApproachStrategy.R_BAR_POS or strategy == sl_enums.ClosingApproachStrategy.R_BAR_NEG:
        
        dr: float = distance.to_value(u.km)
        
        dv_i: float = dr / 4 * n
        
        dv_f: float = - 5 * v_0
        
        dv = np.abs(dv_i) + np.abs(dv_f)
    
    return (dv * u.km / u.s).to(u.m / u.s)

def final_approach(
    semimajor_axis_target: u.Quantity,
    distance: u.Quantity,
    time: u.Quantity,
    strategy: sl_enums.ClosingApproachStrategy) -> ty.Optional[u.Quantity]:
    """
    In the final approach (a.k.a. proximity operations or terminal phase), the trajectories now are more or less
    straight to directly intercept the target and therefore are on "collision course" with it. The interceptor is
    now on the waiting point just outside of the Keep-Out Sphere (a.k.a. KOS).

    :param semimajor_axis_target: Semimajor axis of the target orbit
    :type semimajor_axis_target: u.Quantity
    :param distance: Distance to the target
    :type distance: u.Quantity
    :param time: Time to reach the waiting point
    :type time: u.Quantity
    :param strategy: Closing approach strategy
    :type strategy: sl_enums.ClosingApproachStrategy
    :return: Delta velocity for the final approach maneuver
    :rtype: ty.Optional[u.Quantity]
    
    📌 **Notes**
    
    The **final approach** ends at a distance of a few meters upfront.
    
    📖 **References**
    
    - :cite:`walter`
        - Section 8.6 *Orbital Rendezvous*
        - Section 8.6.5 *Final Approach*
    """
    
    # >>> Validation
    
    # * semimajor_axis_target
    
    err_msg: str | None = sl_validator.validate_quantity("semimajor_axis_target", semimajor_axis_target, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * distance
    
    err_msg = sl_validator.validate_quantity("distance", distance, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * time
    
    err_msg = sl_validator.validate_quantity("time", time, u.s)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * strategy
    
    err_msg = sl_validator.validate_type("strategy", strategy, sl_enums.ClosingApproachStrategy)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    a: float = semimajor_axis_target.to_value(u.km)
    t: float = time.to_value(u.s)
    
    mu: float = sl_bodies.BODIES[sl_bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
    
    n: float = np.sqrt(mu / a**3) # * Target orbit mean motion
    
    dv: float
    
    if strategy == sl_enums.ClosingApproachStrategy.V_BAR_POS or strategy == sl_enums.ClosingApproachStrategy.V_BAR_NEG:
        
        dx: float = distance.to_value(u.km)
        
        dv = 2 * (dx / t + n * dx)
    
    elif strategy == sl_enums.ClosingApproachStrategy.R_BAR_POS or strategy == sl_enums.ClosingApproachStrategy.R_BAR_NEG:
        
        dz: float = distance.to_value(u.km)
        
        dv = 2 * (dz / t + n * dz)
    
    return (dv * u.km / u.s).to(u.m / u.s)
