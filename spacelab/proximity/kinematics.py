"""
This modules contains the kinematics representations on the major **coordinate systems** used in proximity operations.

📖 **References**

- :cite:`curtis`
    - Chapter 7 *Relative Motion and Rendezvous*
"""

import astropy.time as time
import astropy.units as u
import numpy as np
import typing as ty

import spacelab.bodies as sl_bodies
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.n_body_models.lagrange_coefficients as sl_lagrange_coefficients
import spacelab.orbit.position as sl_position
import spacelab.orbit.representation as sl_representation
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

def local_vertical_local_horizontal_kinematics(
    attractor: sl_bodies.Attractor,
    orbital_elements_target: sl_orbital_elements.OrbitalElements,
    orbital_elements_chaser: sl_orbital_elements.OrbitalElements) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Given the state vectors (:math:`\\vec{r}_T`, :math:`\\vec{v}_T`) of the **target spacecraft** and
    (:math:`\\vec{r}_C`, :math:`\\vec{v}_C`) of the **chaser spacecraft**, find the position, velocity, and acceleration
    of Chaser relative to Target along the **Local Vertical Local Horizontal** (*LVLH*) axes attached to the Target.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param orbital_elements_target: Target orbital elements
    :type orbital_elements_target: sl_orbital_elements.OrbitalElements
    :param orbital_elements_chaser: Chaser orbital elements
    :type orbital_elements_chaser: sl_orbital_elements.OrbitalElements
    :return: Relative [position, velocity, acceleration, angular velocity] LVLH
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    A rendezvous maneuver usually involves a target vehicle, which is passive and nonmaneuvering, and a chase vehicle
    which is active and performs the maneuvers required to bring itself alongside the target. The position vector of
    the target in the *geocentric equatorial frame* is :math:`\\vec{r}_0`. This outward radial is sometimes called
    'r-bar'. The moving frame of reference has its origin at the target. The :math:`x` axis is directed along
    :math:`\\vec{r}_0`, the outward radial to the target. The :math:`y` axis is perpendicular to :math:`\\vec{r}_0` and
    points in the direction of the target satellite's local horizon. The x and y axes therefore lie in the target's
    orbital plane, and the :math:`z` axis is normal to that plane.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 7.2 *Relative motion in orbit*
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
    
    # >>> Algorithm
    
    r_target, v_target = sl_representation.keplerian_to_cartesian(
        attractor=attractor, orbital_elements=orbital_elements_target)
    
    r_chaser, v_chaser = sl_representation.keplerian_to_cartesian(
        attractor=attractor, orbital_elements=orbital_elements_chaser)
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    r_target: np.ndarray = r_target.to_value(u.km)
    r_chaser: np.ndarray = r_chaser.to_value(u.km)
    
    v_target: np.ndarray = v_target.to_value(u.km / u.s)
    v_chaser: np.ndarray = v_chaser.to_value(u.km / u.s)
    
    # ? 1. Angular momentum of the Target
    
    h_target: np.ndarray = np.cross(r_target, v_target)
    
    # ? 2. Unit vectors of the comoving frame of the target (x)
    
    i: np.ndarray = r_target / np.linalg.norm(r_target)
    k: np.ndarray = h_target / np.linalg.norm(h_target)
    j: np.ndarray = np.cross(k, i)
    
    # ? 3. Orthogonal trasformation matrix Q_Xx (direction cosines matrix)
    
    dcm: np.ndarray = np.vstack((i, j, k))
    
    # ? 4. Angular velocity Ω and acceleration dΩ / dt of the comoving frame of the target
    
    omega: np.ndarray = h_target / np.linalg.norm(r_target)**2
    
    d_omega_dt: np.ndarray = - 2 * np.dot(v_target, r_target) / np.linalg.norm(r_target)**2 * omega
    
    # ? 5. Absolute accelerations of Target and Chaser
    
    a_target: np.ndarray = - mu / np.linalg.norm(r_target)**3 * r_target
    a_chaser: np.ndarray = - mu / np.linalg.norm(r_chaser)**3 * r_chaser
    
    # ? 6. Relative position in Geocentric Equatioral Frame (X)
    
    r_rel: np.ndarray = r_chaser - r_target
    
    # ? 7. Relative velocity in Geocentric Equatioral Frame (X)
    
    v_rel: np.ndarray = v_chaser - v_target - np.cross(omega, r_rel)
    
    # ? 8. Relative acceleration in Geocentric Equatioral Frame (X)
    
    a_rel: np.ndarray = a_chaser - a_target - np.cross(d_omega_dt, r_rel) - \
        np.cross(omega, np.cross(omega, r_rel)) - 2 * np.cross(omega, v_rel)
    
    # ? 9. LVLH kinematics (x)
    
    r_rel_lvlh: u.Quantity = np.matmul(dcm, r_rel) * u.km
    v_rel_lvlh: u.Quantity = np.matmul(dcm, v_rel) * u.km / u.s
    a_rel_lvlh: u.Quantity = np.matmul(dcm, a_rel) * u.km / u.s**2
    omega_lvlh: u.Quantity = np.matmul(dcm, omega) * u.rad / u.s
    
    return [r_rel_lvlh, v_rel_lvlh, a_rel_lvlh, omega_lvlh]

def geocentric_equatorial_kinematics(
    position_target: u.Quantity,
    velocity_target: u.Quantity,
    position_rel_lvlh: u.Quantity,
    velocity_rel_lvlh: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Given the state vectors (:math:`\\vec{r}_T`, :math:`\\vec{v}_T`) of the **target spacecraft** and
    (:math:`\\vec{r}_lvlh`, :math:`\\vec{v}_lvlh`) of the **chaser spacecraft** relative to Target along the
    **Local Vertical Local Horizontal** (*LVLH*) axes attached to the Target, find the position and velocity of
    Chaser in the Geocentric Equatorial frame.

    :param position_target: Target position vector
    :type position_target: u.Quantity
    :param velocity_target: Target velocity vector
    :type velocity_target: u.Quantity
    :param position_rel_lvlh: Relative position vector
    :type position_rel_lvlh: u.Quantity
    :param velocity_rel_lvlh: Relative velocity vector
    :type velocity_rel_lvlh: u.Quantity
    :return: Chaser [position, velocity] GEF
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    A rendezvous maneuver usually involves a target vehicle, which is passive and nonmaneuvering, and a chase vehicle
    which is active and performs the maneuvers required to bring itself alongside the target. The position vector of
    the target in the *geocentric equatorial frame* is :math:`\\vec{r}_0`. This outward radial is sometimes called
    'r-bar'. The moving frame of reference has its origin at the target. The :math:`x` axis is directed along
    :math:`\\vec{r}_0`, the outward radial to the target. The :math:`y` axis is perpendicular to :math:`\\vec{r}_0` and
    points in the direction of the target satellite's local horizon. The x and y axes therefore lie in the target's
    orbital plane, and the :math:`z` axis is normal to that plane.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 7.2 *Relative motion in orbit*
    """
    
    # >>> Validation
    
    # * position_target
    
    err_msg: str | None = sl_validator.validate_quantity_vector("position_target", position_target, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * velocity_target
    
    err_msg = sl_validator.validate_quantity_vector("velocity_target", velocity_target, u.km / u.s, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * position_rel_lvlh
    
    err_msg = sl_validator.validate_quantity_vector("position_rel_lvlh", position_rel_lvlh, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * velocity_target
    
    err_msg = sl_validator.validate_quantity_vector("velocity_target", velocity_target, u.km / u.s, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    r_target: np.ndarray = position_target.to_value(u.km)
    r_rel_lvlh: np.ndarray = position_rel_lvlh.to_value(u.km)
    
    v_target: np.ndarray = velocity_target.to_value(u.km / u.s)
    v_rel_lvlh: np.ndarray = velocity_rel_lvlh.to_value(u.km / u.s)
    
    # ? 1. Angular momentum of the Target
    
    h_target: np.ndarray = np.cross(r_target, v_target)
    
    # ? 2. Unit vectors of the comoving frame of the target (x)
    
    i: np.ndarray = r_target / np.linalg.norm(r_target)
    k: np.ndarray = h_target / np.linalg.norm(h_target)
    j: np.ndarray = np.cross(k, i)
    
    # ? 3. Orthogonal trasformation matrix Q_Xx (direction cosines matrix)
    
    dcm: np.ndarray = np.vstack((i, j, k))
    
    # ? 4. Relative position-velocity in Geocentric Equatioral Frame (X)
    
    r_rel: np.ndarray = np.matmul(np.linalg.inv(dcm), r_rel_lvlh)
    v_rel: np.ndarray = np.matmul(np.linalg.inv(dcm), v_rel_lvlh)
    
    # ? 5. Angular velocity Ω of the comoving frame of the target
    
    omega: np.ndarray = h_target / np.linalg.norm(r_target)**2
    
    # ? 6. Chaser position in Geocentric Equatioral Frame (X)
    
    r_chaser: u.Quantity  = (r_target + r_rel) * u.km
    
    # ? 7. Chaser velocity in Geocentric Equatioral Frame (X)
    
    v_chaser: u.Quantity = (v_target + v_rel + np.cross(omega, r_rel)) * u.km / u.s
    
    return [r_chaser, v_chaser]

def simulate_local_vertical_local_horizontal_kinematics(
    attractor: sl_bodies.Attractor,
    orbital_elements_target: sl_orbital_elements.OrbitalElements,
    orbital_elements_chaser: sl_orbital_elements.OrbitalElements,
    target_period_multiplier: int = 60,
    points_number: int = 1000) -> ty.Optional[list]:
    """
    Simulates the motion of the Target w.r.t. the Chaser in the LVLH frame.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param orbital_elements_target: Target orbital elements
    :type orbital_elements_target: sl_orbital_elements.OrbitalElements
    :param orbital_elements_chaser: Chaser orbital elements
    :type orbital_elements_chaser: sl_orbital_elements.OrbitalElements
    :param target_period_multiplier: Multiple of the Target period, defaults to 60
    :type target_period_multiplier: int, optional
    :param points_number: Number of points to simulate, defaults to 1000
    :type points_number: int, optional
    :return: [x, y, z] coordinates
    :rtype: ty.Optional[list]
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 7.2 *Relative motion in orbit*
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
    
    # * target_period_multiplier
    
    err_msg = sl_validator.validate_type("target_period_multiplier", target_period_multiplier, int)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * points_number
    
    err_msg = sl_validator.validate_type("points_number", points_number, int)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    if target_period_multiplier < 0:
        
        sl_logger.logger.warning("'target_period_multiplier' must be positive")
    
        return None
    
    if points_number <= 0:
        
        sl_logger.logger.warning("'points_number' must be positive")
        
        return None
    
    # ? 1. Calculate state vectors from orbital elements
    
    orbital_elements_target.calc_semimajor_axis(attractor=attractor)
    
    orbital_elements_chaser.calc_semimajor_axis(attractor=attractor)
    
    r_target, v_target = sl_representation.keplerian_to_cartesian(
        attractor=attractor, orbital_elements=orbital_elements_target)
    
    r_chaser, v_chaser = sl_representation.keplerian_to_cartesian(
        attractor=attractor, orbital_elements=orbital_elements_chaser)
    
    # ? 2. Target period
    
    t_target: u.Quantity = orbital_elements_target.calc_orbital_period(attractor=attractor)
    
    # ? 3. Target initial time
    
    t_0: u.Quantity = sl_position.elliptical_orbit_time(
        true_anomaly=orbital_elements_target.true_anomaly,
        period=t_target,
        eccentricity=orbital_elements_target.eccentricity)
    
    # ? 4. Final time
    
    t_f: u.Quantity = t_0 + target_period_multiplier * t_target
    
    # ? 5. Time step
    
    dt: float = (t_f.to_value(u.s) - t_0.to_value(u.s)) / float(points_number)
    
    # ? 6. Cycle
    
    times: np.ndarray = np.linspace(t_0, t_f, points_number)
    
    x: list = []
    y: list = []
    z: list = []
    
    for _ in times:
        
        # ? a. LVLH quantities
    
        r_rel_lvlh, _, _, _ = local_vertical_local_horizontal_kinematics(
            attractor=attractor,
            orbital_elements_target=orbital_elements_target,
            orbital_elements_chaser=orbital_elements_chaser)
        
        x.append(r_rel_lvlh[0].to_value(u.km))
        y.append(r_rel_lvlh[1].to_value(u.km))
        z.append(r_rel_lvlh[2].to_value(u.km))
        
        # ? b. Update Target-Chaser vectors
        
        r_target, v_target = sl_lagrange_coefficients.propagate_position_velocity(
            attractor=attractor,
            initial_position=r_target,
            initial_velocity=v_target,
            delta_time=time.TimeDelta(dt * u.s))
        
        r_chaser, v_chaser = sl_lagrange_coefficients.propagate_position_velocity(
            attractor=attractor,
            initial_position=r_chaser,
            initial_velocity=v_chaser,
            delta_time=time.TimeDelta(dt * u.s))
        
        # ? c. Update Target-Chaser orbital elements
        
        orbital_elements_target = sl_representation.cartesian_to_keplerian(
            attractor=attractor, position=r_target, velocity=v_target)
        
        orbital_elements_chaser = sl_representation.cartesian_to_keplerian(
            attractor=attractor, position=r_chaser, velocity=v_chaser)
    
    # ? 6. Result
    
    return [x, y, z]
