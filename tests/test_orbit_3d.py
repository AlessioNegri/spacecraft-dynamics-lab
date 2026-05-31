import astropy.time as time
import astropy.units as u
import numpy as np

import astro.bodies as bodies
import astro.two_body_problem as tbp
import astro.orbital_position as op
import astro.orbit_3d as o3d

def test_right_ascension_declination():
    """EXAMPLE 4.1"""
    
    r: u.Quantity = np.array([-5368, -1784, 3691]) * u.km
    
    alpha, delta = o3d.Orbit3D.right_ascension_declination(position=r)
    
    assert np.isclose(alpha.to_value(u.deg), 198.4, atol=1e-1)
    assert np.isclose(delta.to_value(u.deg), 33.12, atol=1e-2)

def test_orbital_elements():
    """EXAMPLE 4.3"""
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    r: u.Quantity = np.array([-6045, -3490, 2500]) * u.km
    v: u.Quantity = np.array([-3.457, 6.618, 2.533]) * u.km / u.s
    
    oe = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r, velocity=v)
    
    assert np.isclose(oe.specific_angular_momentum.to_value(u.km**2 / u.s), 58311, atol=1e-0)
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 8788, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.1712, atol=1e-4)
    assert np.isclose(oe.inclination.to_value(u.deg), 153.2, atol=1e-1)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 255.3, atol=1e-1)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 20.07, atol=1e-2)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 28.45, atol=1e-2)

def test_geocentric_equatorial_to_perifocal():
    """EXAMPLE 4.7"""
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    r_GEF: u.Quantity = np.array([-4040, 4815, 3629]) * u.km
    v_GEF: u.Quantity = np.array([-10.39, -4.772, 1.744]) * u.km / u.s
    
    r_PF, v_PF = o3d.Orbit3D.geocentric_equatorial_to_perifocal(attractor, r_GEF, v_GEF)
    
    assert np.allclose(r_PF.to_value(u.km)[0], 6285, atol=1e-0)
    assert np.allclose(r_PF.to_value(u.km)[1], 3628.6, atol=1e-0)
    assert np.allclose(v_PF.to_value(u.km / u.s)[0], -2.4898, atol=1e-4)
    assert np.allclose(v_PF.to_value(u.km / u.s)[1], 11.295, atol=1e-3)
    
def test_perifocal_to_geocentric_equatorial():
    """EXAMPLE 4.7"""
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum = 80_000 * u.km**2 / u.s,
        semimajor_axis = 0 * u.km,
        eccentricity = 1.4 * u.one,
        inclination = 30 * u.deg,
        right_ascension_of_ascending_node = 40 * u.deg,
        argument_of_periapsis = 60 * u.deg,
        true_anomaly = 30 * u.deg
    )
    
    r_GEF, v_GEF = o3d.Orbit3D.keplerian_to_cartesian(attractor, oe)
    
    assert np.allclose(r_GEF.to_value(u.km)[0], -4040, atol=1e-0)
    assert np.allclose(r_GEF.to_value(u.km)[1], 4815, atol=1e-0)
    assert np.allclose(r_GEF.to_value(u.km)[2], 3629, atol=1e-0)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[0], -10.39, atol=1e-2)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[1], -4.772, atol=1e-3)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[2], 1.744, atol=1e-3)
    
def test_planet_oblateness_effect():
    """EXAMPLE 4.8"""
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum = 0 * u.km**2 / u.s,
        semimajor_axis = 6718 * u.km,
        eccentricity = 0.008931 * u.one,
        inclination = 51.43 * u.deg,
        right_ascension_of_ascending_node = 0 * u.deg,
        argument_of_periapsis = 0 * u.deg,
        true_anomaly = 0 * u.deg
    )
    
    d_raan_dt, d_argp_dt = o3d.Orbit3D.planet_oblateness_effect(bodies.Attractor.EARTH, oe)
    
    assert np.isclose(d_raan_dt.to_value(u.deg / u.day), -5.181, atol=1e-3)
    assert np.isclose(d_argp_dt.to_value(u.deg / u.day), 3.920, atol=1e-3)
    
def test_example_4_11():
    """EXAMPLE 4.11"""
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    r_GEF: u.Quantity = np.array([-3670, -3870, 4400]) * u.km
    v_GEF: u.Quantity = np.array([4.7, -7.4, 1]) * u.km / u.s
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor, r_GEF, v_GEF)
    
    assert np.isclose(oe.specific_angular_momentum.to_value(u.km**2 / u.s), 58_926, atol=1e-0)
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 10644, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.42607, atol=1e-5)
    assert np.isclose(oe.inclination.to_value(u.deg), 39.687, atol=1e-3)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 130.32, atol=1e-2)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 42.373, atol=1e-3)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 52.404, atol=1e-3)
    
    parameters: tbp.OrbitParameters = tbp.Orbit.cartesian_to_orbit_parameters(attractor, r_GEF, v_GEF)
    
    assert np.isclose(parameters.period.to_value(u.s), 10_928, atol=1e-0)
    
    n: float = 2 * np.pi / parameters.period.to_value(u.s) # ? Mean motion [rad/s]
    
    t_1: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(oe.true_anomaly, parameters.period, oe.eccentricity)
    
    assert np.isclose(t_1.to_value(u.s), 631.00, atol=1e-0)
    
    t_2: u.Quantity = t_1 + 96 * u.hour
    
    nu_32: u.Quantity = op.OrbitalPosition.elliptical_orbit_true_anomaly(t_2, parameters.period, oe.eccentricity)
    
    assert np.isclose(nu_32.to_value(u.deg), 360-148.75, atol=1e-1)
    
    d_raan_dt, d_argp_dt = o3d.Orbit3D.planet_oblateness_effect(attractor, oe)
    
    oe.right_ascension_of_ascending_node += d_raan_dt.to(u.deg / u.day) * t_2.to(u.day)
    oe.argument_of_periapsis += d_argp_dt.to(u.deg / u.day) * t_2.to(u.day)
    oe.true_anomaly = nu_32
    
    r_GEF, v_GEF = o3d.Orbit3D.keplerian_to_cartesian(attractor, oe)
    
    assert np.allclose(r_GEF.to_value(u.km)[0], 9667, atol=1e-0)
    assert np.allclose(r_GEF.to_value(u.km)[1], 4326, atol=1e-0)
    assert np.allclose(r_GEF.to_value(u.km)[2], -8691, atol=1e-0)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[0], -3.040, atol=1e-2)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[1], 3.330, atol=1e-3)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[2], 0.6327, atol=1e-4)
    
def test_ground_track_propagation():
    """EXAMPLE 4.12"""
    
    attractor: bodies.Attractor = bodies.Attractor.EARTH
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum = 0 * u.km**2 / u.s,
        semimajor_axis = 8350 * u.km,
        eccentricity = 0.19760 * u.one,
        inclination = 60 * u.deg,
        right_ascension_of_ascending_node = 270 * u.deg,
        argument_of_periapsis = 45 * u.deg,
        true_anomaly = 230 * u.deg
    )
    
    alpha, delta = o3d.Orbit3D.ground_track_propagation(attractor, oe, time.TimeDelta(45 * u.minute))
    
    assert np.isclose(alpha.to_value(u.deg), 313.7 - 180, atol=1e-1)
    assert np.isclose(delta.to_value(u.deg), 54.84, atol=1e-2)