import astropy.units as u
import numpy as np

import spacelab.bodies as sl_bodies
import spacelab.orbit.frames as sl_frames
import spacelab.orbit.representation as sl_representation

def test_geocentric_equatorial_position_vector():
    """:cite:`curtis` EXAMPLE 5.7"""
    
    R: u.Quantity = sl_frames.geocentric_equatorial_position_vector(
        attractor=sl_bodies.Attractor.EARTH,
        local_sidereal_time=186.7 * u.deg,
        latitude=20 * u.deg)
    
    assert np.isclose(R[0].to_value(u.km), -5955, 1e-0)
    assert np.isclose(R[1].to_value(u.km), -699.5, 1e-1)
    assert np.isclose(R[2].to_value(u.km), 2168, 1e-0)

def test_topocentric_equatorial_position_vector():
    """:cite:`curtis` EXAMPLE 5.7"""
    
    rho: u.Quantity = sl_frames.topocentric_equatorial_position_vector(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([-5368, -1784, 3691]) * u.km,
        local_sidereal_time=186.7 * u.deg,
        latitude=20 * u.deg)
    
    assert np.isclose(rho[0].to_value(u.km), 586.8, 1e-1)
    assert np.isclose(rho[1].to_value(u.km), -1084, 1e-0)
    assert np.isclose(rho[2].to_value(u.km), 1523, 1e-0)
    
    alpha, delta = sl_representation.right_ascension_declination(position=rho)
    
    assert np.isclose(alpha.to_value(u.deg), 298.4, 1e-1)
    assert np.isclose(delta.to_value(u.deg), 51.01, 1e-2)

def test_topocentric_horizon_position_vector():
    """:cite:`curtis` EXAMPLE 5.9"""
    
    rho, A, a = sl_frames.topocentric_horizon_position_vector(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([-2032.4, 4591.2, -4544.8]) * u.km,
        local_sidereal_time=110 * u.deg,
        latitude=-40 * u.deg)
    
    assert np.isclose(rho[0].to_value(u.km), 339.5, 1e-1)
    assert np.isclose(rho[1].to_value(u.km), -282.6, 1e-1)
    assert np.isclose(rho[2].to_value(u.km), 389.6, 1e-1)
    assert np.isclose(A.to_value(u.deg), 129.8, 1e-1)
    assert np.isclose(a.to_value(u.deg), 41.41, 1e-2)

def test_geocentric_equatorial_position_vector_altitude_and_negative_fallback():
    base = sl_frames.geocentric_equatorial_position_vector(
        attractor=sl_bodies.Attractor.EARTH,
        local_sidereal_time=0 * u.deg,
        latitude=0 * u.deg,
    )
    elevated = sl_frames.geocentric_equatorial_position_vector(
        attractor=sl_bodies.Attractor.EARTH,
        local_sidereal_time=0 * u.deg,
        latitude=0 * u.deg,
        site_altitude=390 * u.m,
    )

    assert elevated is not None
    assert np.isclose(elevated[0].to_value(u.km), base[0].to_value(u.km) + 0.390, atol=1e-9)

    assert sl_frames.geocentric_equatorial_position_vector(
        attractor=sl_bodies.Attractor.EARTH,
        local_sidereal_time=0 * u.deg,
        latitude=0 * u.deg,
        site_altitude=-1 * u.km,
    ) is None


def test_frame_helpers_reject_invalid_altitude_unit():
    assert sl_frames.topocentric_equatorial_position_vector(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([7000, 0, 0]) * u.km,
        local_sidereal_time=0 * u.deg,
        latitude=0 * u.deg,
        site_altitude=390 * u.s,
    ) is None


def test_topocentric_equatorial_right_ascension_declination():
    """:cite:`curtis` EXAMPLE 5.8"""
    
    rho, alpha, delta = sl_frames.topocentric_equatorial_right_ascension_declination(
        attractor=sl_bodies.Attractor.EARTH,
        local_sidereal_time=215.1 * u.deg,
        latitude=38 * u.deg,
        azimuth=214.3 * u.deg,
        elevation=43 * u.deg)
    
    assert np.isclose(rho[0].to_value(), -0.9810, 1e-4)
    assert np.isclose(rho[1].to_value(), -0.1857, 1e-4)
    assert np.isclose(rho[2].to_value(), -0.05621, atol=1e-5)
    assert np.isclose(alpha.to_value(u.deg), 190.7, 1e-1)
    assert np.isclose(delta.to_value(u.deg), -3.222, 1e-3)
