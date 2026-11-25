"""
This modules contains the vector representations on the major **coordinate systems** used in space.

📖 **References**

- :cite:`curtis`
    - Chapter 5 *Preliminary Orbit Determination*
- :cite:`kluever`
    - Chapter 3 *Orbit Determination*
"""

import astropy.units as u
import numpy as np
import typing as ty

import spacelab.bodies as sl_bodies
import spacelab.orbit.representation as sl_representation
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

def geocentric_equatorial_position_vector(
    attractor: sl_bodies.Attractor,
    local_sidereal_time: u.Quantity,
    latitude: u.Quantity,
    site_altitude: u.Quantity = 0 * u.km) -> ty.Optional[u.Quantity]:
    """
    **Geocentric Equatorial Frame** (*ECI frame*) position vector of the observer.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param local_sidereal_time: Local sidereal time (theta)
    :type local_sidereal_time: u.Quantity
    :param latitude: Latitude (phi)
    :type latitude: u.Quantity
    :param site_altitude: Ground station elevation above sea level, defaults to 0 * u.km
    :type site_altitude: u.Quantity, optional
    :return: Position vector of the site
    :rtype: ty.Optional[u.Quantity]
    
    📌 **Notes**
    
    As we know, the earth is not a sphere, but a slightly oblate spheroid. The location of the observation site *O* is
    determined by specifying its east longitude :math:`\\lambda` and latitude :math:`\\phi`. East longitude
    :math:`\\lambda` is measured positive eastward from the Greenwhich meridian to the meridian through *O*. The angle
    between the vernal equinox direction (XZ plane) and the meridian of *O* is the local sidereal time :math:`\\theta`.
    Likewise, :math:`\\theta_G` is the Greenwich sidereal time.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.5 *Topocentric coordinate system*
    """
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * local_sidereal_time
    
    err_msg = sl_validator.validate_quantity_angle("local_sidereal_time", local_sidereal_time)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * latitude
    
    err_msg = sl_validator.validate_quantity_angle("latitude", latitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * site_altitude
    
    err_msg = sl_validator.validate_quantity("site_altitude", site_altitude, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    R_E: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)
    
    f: float = sl_bodies.BODIES[attractor].f.to_value(u.one) if sl_bodies.BODIES[attractor].f != None else 0 # * Flattening
    
    theta: float = local_sidereal_time.to_value(u.rad)
    
    phi: float = latitude.to_value(u.rad)
    
    H: float = site_altitude.to_value(u.km)
    
    if H < 0:
        
        sl_logger.logger.warning("'site_altitude' must be >= 0")
        
        return None
    
    A = (R_E / np.sqrt(1 - (2 * f - f**2) * np.sin(phi)**2) + H) * np.cos(phi)
    
    B = (R_E * (1 - f)**2 / np.sqrt(1 - (2 * f - f**2) * np.sin(phi)**2) + H) * np.sin(phi)
    
    R: u.Quantity = np.array([A * np.cos(theta), A * np.sin(theta), B]) * u.km
    
    return R

def topocentric_equatorial_position_vector(
    attractor: sl_bodies.Attractor,
    position: u.Quantity,
    local_sidereal_time: u.Quantity,
    latitude: u.Quantity,
    site_altitude: u.Quantity = 0 * u.km) -> ty.Optional[u.Quantity]:
    """
    Geocentric Equatorial Frame --> **Topocentric Equatorial Frame**.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param position: Geocentric equatorial position vector of the target
    :type position: u.Quantity
    :param local_sidereal_time: Local sidereal time (theta)
    :type local_sidereal_time: u.Quantity
    :param latitude: Latitude (phi)
    :type latitude: u.Quantity
    :param site_altitude: Ground station elevation above sea level, defaults to 0 * u.km
    :type site_altitude: u.Quantity, optional
    :return: Topocentric equatorial position vector of the target
    :rtype: ty.Optional[u.Quantity]
    
    📌 **Notes**
    
    A *topocentric coordinate system* is one which is centered at the observer's location on the surface of the earth.
    Consider a satellite and an observer O on the earth's surface. :math:`\\vec{r}` is the position of the body B
    relative to the center of attraction C; :math:`\\vec{R}` is the position vector of the observer relative to C; and
    :math:`\\vec{\\rho}` is the position of the body B relative to the observer. :math:`\\vec{r}`, :math:`\\vec{R}`
    and :math:`\\vec{\\rho}` comprise the fundamental vector triangle. The relationship among these three vectors is
    :math:`\\vec{r} = \\vec{R} + \\vec{\\rho}`.
    
    The *topocentric equatorial coordinate system* has the origin at point O on the surface of the earth uses a
    non-rotating set of xyz axes through O which coincide with the XYZ axes of the geocentric equatorial frame.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.5 *Topocentric coordinate system*
        - Section 5.6 *Topocentric equatorial coordinate system*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * position
    
    err_msg = sl_validator.validate_quantity_vector("position", position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * local_sidereal_time
    
    err_msg = sl_validator.validate_quantity_angle("local_sidereal_time", local_sidereal_time)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * latitude
    
    err_msg = sl_validator.validate_quantity_angle("latitude", latitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * site_altitude
    
    err_msg = sl_validator.validate_quantity("site_altitude", site_altitude, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    # ? 1. Geocentric position vector of the site
    
    R: ty.Optional[u.Quantity] = geocentric_equatorial_position_vector(
        attractor=attractor, local_sidereal_time=local_sidereal_time, latitude=latitude, site_altitude=site_altitude)
    
    if R is None: return None
    
    # ? 2. Topocentric equatorial position vector
    
    rho: u.Quantity = position.to(u.km) - R
    
    return rho

def topocentric_horizon_position_vector(
    attractor: sl_bodies.Attractor,
    position: u.Quantity,
    local_sidereal_time: u.Quantity,
    latitude: u.Quantity,
    site_altitude: u.Quantity = 0 * u.km) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Geocentric Equatorial Frame --> **Topocentric Horizon Frame**.

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param position: Geocentric equatorial position vector of the target
    :type position: u.Quantity
    :param local_sidereal_time: Local sidereal time (theta)
    :type local_sidereal_time: u.Quantity
    :param latitude: Latitude (phi)
    :type latitude: u.Quantity
    :param site_altitude: Ground station elevation above sea level, defaults to 0 * u.km
    :type site_altitude: u.Quantity, optional
    :return: [Topocentric equatorial position vector of the target :math:`\\rho`, Azimuth :math:`A`, Elevation :math:`a`]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    The *topocentric horizon system* is centered at the observation point O whose position vector is :math:`\\vec{R}`.
    The xy plane is the local horizon, which is the plane tangent to the ellipsoid at point O. The z axis is normal to
    this plane directed outward towards the zenith. The x axis is directed eastward and the y axis points north. Because
    the x axis points east, this may be referred to as an *ENZ* (**East-North-Zenith**) frame. In the *SEZ* topocentric
    reference frame the x axis points towards the south and the y axis towards the east. The SEZ frame is obtained from
    ENZ by a 90° clockwise rotation around the zenith (:math:`\\mathbf{R3}(-90°)`).
    
    The station-based *topocentric-horizon coordinate system* (*SEZ frame*) consists of three orthogonal axes: the
    :math:`\\vec{S}` axis points south along a local meridian, :math:`\\vec{E}` points east along a line of latitude,
    and :math:`\\vec{Z}` points straight up (in the opposite direction of Earth's center). The horizon plane formed by
    the :math:`\\vec{S}` and :math:`\\vec{E}` axes is the fundamental plane.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.7 *Topocentric horizon coordinate system*
    - :cite:`kluever`
        - Section 3.7 *Orbit Determination from One Ground-Based Observation*
        - Section 3.7.1 *Topocentric-Horizon Coordinate System*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * position
    
    err_msg = sl_validator.validate_quantity_vector("position", position, u.km, 3)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * local_sidereal_time
    
    err_msg = sl_validator.validate_quantity_angle("local_sidereal_time", local_sidereal_time)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * latitude
    
    err_msg = sl_validator.validate_quantity_angle("latitude", latitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * site_altitude
    
    err_msg = sl_validator.validate_quantity("site_altitude", site_altitude, u.km)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    # ? 1. Topocentric equatorial position vector
    
    rho: ty.Optional[u.Quantity] = topocentric_equatorial_position_vector(
        attractor=attractor,
        position=position,
        local_sidereal_time=local_sidereal_time,
        latitude=latitude,
        site_altitude=site_altitude)
    
    if rho is None: return None
    
    # ? 2. Topocentric horizon position vector
    
    theta: float = local_sidereal_time.to_value(u.rad)
    
    phi: float = latitude.to_value(u.rad)
    
    # * Matrix of transformation Q_Xx
    
    dcm_ge_th: np.ndarray = np.array( # * dcm_GEF_THF
        [
            [ -np.sin(theta)               , np.cos(theta)                , 0           ],
            [ -np.sin(phi) * np.cos(theta) , -np.sin(phi) * np.sin(theta) , np.cos(phi) ],
            [ np.cos(phi) * np.cos(theta)  , np.cos(phi) * np.sin(theta)  , np.sin(phi) ]
        ])
    
    rho: np.ndarray = np.matmul(dcm_ge_th, rho.to_value(u.km))
    
    # ? 3. Azimuth and Elevation
    
    rho_h: np.ndarray = rho / np.linalg.norm(rho)
    
    a: float = np.arcsin(rho_h[2]) # * Elevation
    
    A: float = np.arctan2(rho_h[0] / np.cos(a), rho_h[1] / np.cos(a)) # * Azimuth
    
    return [rho * u.km, (A * u.rad).to(u.deg), (a * u.rad).to(u.deg)]

def topocentric_equatorial_right_ascension_declination(
    attractor: sl_bodies.Attractor,
    local_sidereal_time: u.Quantity,
    latitude: u.Quantity,
    azimuth: u.Quantity,
    elevation: u.Quantity) -> ty.Optional[ty.List[u.Quantity]]:
    """
    Topocentric Horizon Frame --> **Topocentric Equatorial Frame**

    :param attractor: Main attractor
    :type attractor: sl_bodies.Attractor
    :param local_sidereal_time: Local sidereal time (theta)
    :type local_sidereal_time: u.Quantity
    :param latitude: Latitude (phi)
    :type latitude: u.Quantity
    :param azimuth: Azimuth (A, beta)
    :type azimuth: u.Quantity
    :param elevation: Elevation (a, sigma)
    :type elevation: u.Quantity
    :return: [Topocentric equatorial position vector of the target :math:`\\rho`, Right ascension :math:`\\alpha`, Declination :math:`delta`]
    :rtype: ty.Optional[ty.List[u.Quantity]]
    
    📌 **Notes**
    
    The *topocentric equatorial coordinate system* has the origin at point O on the surface of the earth uses a
    non-rotating set of xyz axes through O which coincide with the XYZ axes of the geocentric equatorial frame.
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.7 *Topocentric horizon coordinate system*
    """
    
    # >>> Validation
    
    # * attractor
    
    err_msg: str | None = sl_validator.validate_attractor(attractor)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * local_sidereal_time
    
    err_msg = sl_validator.validate_quantity_angle("local_sidereal_time", local_sidereal_time)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * latitude
    
    err_msg = sl_validator.validate_quantity_angle("latitude", latitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * azimuth
    
    err_msg = sl_validator.validate_quantity_angle("azimuth", azimuth)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * elevation
    
    err_msg = sl_validator.validate_quantity_angle("elevation", elevation)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    theta: float = local_sidereal_time.to_value(u.rad)
    
    phi: float = latitude.to_value(u.rad)
    
    A: float = azimuth.to_value(u.rad)
    
    a: float = elevation.to_value(u.rad)
    
    # ? 1. Topocentric horizon position vector
    
    # * Matrix of transformation Q_xX
    
    dcm_th_ge: np.ndarray = np.array( # * dcm_THF_GEF
        [
            [ -np.sin(theta) , -np.sin(phi) * np.cos(theta) , np.cos(phi) * np.cos(theta) ],
            [ np.cos(theta)  , -np.sin(phi) * np.sin(theta) , np.cos(phi) * np.sin(theta) ],
            [ 0              , np.cos(phi)                  , np.sin(phi)                 ]
        ])
    
    rho_h: np.ndarray = np.array([np.cos(a) * np.sin(A), np.cos(a) * np.cos(A), np.sin(a)])
    
    # ? 2. Topocentric equatorial position vector
    
    rho: np.ndarray = np.matmul(dcm_th_ge, rho_h)
    
    # ? 3. Right Ascension and Declination
    
    result = sl_representation.right_ascension_declination(position=rho * u.km)
    
    if result is None: return None
    
    alpha, delta = result
    
    return [rho * u.one, alpha, delta]
