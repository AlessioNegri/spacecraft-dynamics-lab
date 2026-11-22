import astropy.time as time
import astropy.units as u
import numpy as np

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.models.orbit_parameters as sl_orbit_parameters
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.n_body_models.conversions as sl_conversions
import spacelab.orbit.determination as sl_determination
import spacelab.orbit.position as sl_position
import spacelab.orbit.representation as sl_representation

def test_launch_azimuth_1():
    """:cite:`curtis` EXAMPLE 6.10"""
    
    launch_azimuth: u.Quantity = sl_determination.launch_azimuth(
        launch_site_latitude=34.5 * u.deg,
        target_inclination=98.43 * u.deg)
    
    assert np.isclose(launch_azimuth.to_value(u.deg), 349.8, atol=1e-1)

def test_launch_azimuth_2():
    """:cite:`kluever` EXAMPLE 3.3"""
    
    launch_azimuth: u.Quantity = sl_determination.launch_azimuth(
        launch_site_latitude=28.5 * u.deg,
        target_inclination=51.65 * u.deg,
        direction=sl_enums.LaunchPass.DESCENDING)
    
    assert np.isclose(launch_azimuth.to_value(u.deg), 135.088, atol=1e-3)

def test_gibbs_method_1():
    """:cite:`curtis` EXAMPLE 5.1"""
    
    oe: sl_orbital_elements.OrbitalElements = sl_determination.gibbs_method(
        attractor=sl_bodies.Attractor.EARTH,
        position_1=np.array([-294.32, 4265.1, 5986.7]) * u.km,
        position_2=np.array([-1365.5, 3637.6, 6346.8]) * u.km,
        position_3=np.array([-2940.3, 2473.7, 6555.8]) * u.km)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 8001, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.1, atol=1e-1)
    assert np.isclose(oe.inclination.to_value(u.deg), 60, atol=1e-0)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 40, atol=1e-0)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 30, atol=1e-0)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 50, atol=1e-0)

def test_gibbs_method_2():
    """:cite:`kluever` EXAMPLE 3.6"""
    
    oe: sl_orbital_elements.OrbitalElements = sl_determination.gibbs_method(
        attractor=sl_bodies.Attractor.EARTH,
        position_1=np.array([-11052.902, -12938.738, 8505.244]) * u.km,
        position_2=np.array([-10378.257, -15955.205, 14212.351]) * u.km,
        position_3=np.array([-9336.222, -17747.079, 18337.068]) * u.km)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 26565, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.7411, atol=1e-4)
    assert np.isclose(oe.inclination.to_value(u.deg), 63.4, atol=1e-1)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 270, atol=1e-0)

def test_lambert():
    """:cite:`curtis` EXAMPLE 5.2"""
    
    attractor = sl_bodies.Attractor.EARTH
    
    r_1: u.Quantity = np.array([5_000, 10_000, 2_100]) * u.km
    r_2: u.Quantity = np.array([-14_600, 2_500, 7_000]) * u.km
    
    v_1, v_2, oe, _ = sl_determination.lambert(
        attractor=attractor,
        departure_position=r_1,
        arrival_position=r_2,
        delta_time=time.TimeDelta(u.Quantity(1, u.hour)))
    
    orb_par: sl_orbit_parameters.OrbitParameters =\
        sl_conversions.cartesian_to_orbit_parameters(attractor=attractor, position=r_1, velocity=v_1)
    
    t_1: u.Quantity = sl_position.elliptical_orbit_time(
        true_anomaly=oe.true_anomaly, period=orb_par.period, eccentricity=oe.eccentricity)
    
    assert np.isclose(v_1[0].to_value(u.km / u.s), -5.9925, atol=1e-4)
    assert np.isclose(v_1[1].to_value(u.km / u.s), 1.9254, atol=1e-4)
    assert np.isclose(v_1[2].to_value(u.km / u.s), 3.2456, atol=1e-4)
    
    assert np.isclose(v_2[0].to_value(u.km / u.s), -3.3125, atol=1e-4)
    assert np.isclose(v_2[1].to_value(u.km / u.s), -4.1966, atol=1e-4)
    assert np.isclose(v_2[2].to_value(u.km / u.s), -0.38529, atol=1e-5)
    
    assert np.isclose(oe.specific_angular_momentum.to_value(u.km**2 / u.s), 80_466, atol=1e-0)
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 20_003, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.4335, atol=1e-4)
    assert np.isclose(oe.inclination.to_value(u.deg), 30.19, atol=1e-2)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 44.60, atol=1e-2)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 30.71, atol=1e-2)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 350.8, atol=1e-1)
    
    assert np.isclose((t_1 - orb_par.period).to_value(u.s), -256.1, atol=1e-1)

def test_predict_from_angle_range_1():
    """:cite:`curtis` EXAMPLE 5.10"""
    
    r, v = sl_determination.predict_from_angle_range(
        attractor=sl_bodies.Attractor.EARTH,
        slant_range=2551 * u.km,
        azimuth=90 * u.deg,
        elevation=30 * u.deg,
        range_rate=0 * u.km / u.s,
        azimuth_rate=1.973e-3 * u.rad / u.s,
        elevation_rate=9.864e-4 * u.rad / u.s,
        local_sidereal_time=300 * u.deg,
        latitude=60 * u.deg)
    
    assert np.isclose(r[0].to_value(u.km), 3831, atol=1e-0)
    assert np.isclose(r[1].to_value(u.km), -2216, atol=1e-0)
    assert np.isclose(r[2].to_value(u.km), 6605, atol=1e-0)
    assert np.isclose(v[0].to_value(u.km / u.s), 1.504, atol=1e-3)
    assert np.isclose(v[1].to_value(u.km / u.s), -4.562, atol=1e-3)
    assert np.isclose(v[2].to_value(u.km / u.s), -0.2920, atol=1e-3)
    
    oe: sl_orbital_elements.OrbitalElements =\
        sl_representation.cartesian_to_keplerian(attractor=sl_bodies.Attractor.EARTH, position=r, velocity=v)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 5170, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.6195, atol=1e-4)
    assert np.isclose(oe.inclination.to_value(u.deg), 113.4, atol=1e-1)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 109.8, atol=1e-1)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 309.8, atol=1e-1)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 165.3, atol=1e-1)

def test_predict_from_angle_range_2():
    """:cite:`kluever` EXAMPLE 3.4"""
    
    r, v = sl_determination.predict_from_angle_range(
        attractor=sl_bodies.Attractor.EARTH,
        slant_range=668.3 * u.km,
        azimuth=135.4 * u.deg,
        elevation=62.5 * u.deg,
        range_rate=2.39 * u.km / u.s,
        azimuth_rate=-0.38 * u.deg / u.s,
        elevation_rate=-0.65 * u.deg / u.s,
        local_sidereal_time=240.7 * u.deg,
        latitude=42.9 * u.deg)
    
    assert np.isclose(r[0].to_value(u.km), -2386.828, atol=1e-3)
    assert np.isclose(r[1].to_value(u.km), -4696.030, atol=1e-3)
    assert np.isclose(r[2].to_value(u.km), 4561.938, atol=1e-3)
    assert np.isclose(v[0].to_value(u.km / u.s), 5.5237, atol=1e-4)
    assert np.isclose(v[1].to_value(u.km / u.s), -5.1511, atol=1e-4)
    assert np.isclose(v[2].to_value(u.km / u.s), -3.9706, atol=1e-4)

def test_predict_from_angle_range_3():
    """:cite:`kluever` EXAMPLE 3.5"""
    
    r, v = sl_determination.predict_from_angle_range(
        attractor=sl_bodies.Attractor.EARTH,
        slant_range=668.3 * u.km,
        azimuth=135.4 * u.deg,
        elevation=62.5 * u.deg,
        range_rate=2.39 * u.km / u.s,
        azimuth_rate=-0.38 * u.deg / u.s,
        elevation_rate=-0.65 * u.deg / u.s,
        local_sidereal_time=240.7 * u.deg,
        latitude=42.9 * u.deg,
        site_altitude=390 * u.m)
    
    assert np.isclose(r[0].to_value(u.km), -2386.968, atol=1e-3)
    assert np.isclose(r[1].to_value(u.km), -4696.279, atol=1e-3)
    assert np.isclose(r[2].to_value(u.km), 4562.204, atol=1e-3)
    assert np.isclose(v[0].to_value(u.km / u.s), 5.5237, atol=1e-4)
    assert np.isclose(v[1].to_value(u.km / u.s), -5.1511, atol=1e-4)
    assert np.isclose(v[2].to_value(u.km / u.s), -3.9706, atol=1e-4)

def test_predict_from_gauss_method():
    """:cite:`curtis` EXAMPLE 5.11"""
    
    r, v = sl_determination.predict_from_gauss_method(
        attractor=sl_bodies.Attractor.EARTH,
        latitude=40 * u.deg,
        local_sidereal_time_list=np.array([44.506, 45.000, 45.499]) * u.deg,
        right_ascension_list=np.array([43.537, 54.420, 64.318]) * u.deg,
        declination_list=np.array([-8.7833, -12.074, -15.105]) * u.deg,
        observation_time_list=np.array([0, 118.10, 237.58]) * u.s,
        site_altitude=1 * u.km)
    
    assert np.isclose(r[0].to_value(u.km), 5659.8, atol=1e-1)
    assert np.isclose(r[1].to_value(u.km), 6534.8, atol=1e-1)
    assert np.isclose(r[2].to_value(u.km), 3270.1, atol=1e-1)
    assert np.isclose(v[0].to_value(u.km / u.s), -3.8791, atol=1e-4)
    assert np.isclose(v[1].to_value(u.km / u.s), 5.1196, atol=1e-4)
    assert np.isclose(v[2].to_value(u.km / u.s), -2.2409, atol=1e-4)

def test_herrick_gibbs_method():
    orbit_radius = 7000 * u.km
    angles = np.deg2rad([0, 5, 10])
    positions = np.array([
        [orbit_radius.to_value(u.km) * np.cos(angle), orbit_radius.to_value(u.km) * np.sin(angle), 0]
        for angle in angles
    ]) * u.km

    oe = sl_determination.herrick_gibbs_method(
        attractor=sl_bodies.Attractor.EARTH,
        position_1=positions[0],
        time_1=0 * u.s,
        position_2=positions[1],
        time_2=80 * u.s,
        position_3=positions[2],
        time_3=160 * u.s,
    )

    assert oe is not None
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 7000, atol=200)
    assert oe.eccentricity.to_value() < 0.05


def test_herrick_gibbs_method_invalid_position_shape_returns_none():
    oe = sl_determination.herrick_gibbs_method(
        attractor=sl_bodies.Attractor.EARTH,
        position_1=np.array([7000, 0]) * u.km,
        time_1=0 * u.s,
        position_2=np.array([6900, 600, 0]) * u.km,
        time_2=600 * u.s,
        position_3=np.array([6600, 1200, 0]) * u.km,
        time_3=1200 * u.s,
    )

    assert oe is None


def test_lambert_invalid_direction_returns_none():
    result = sl_determination.lambert(
        attractor=sl_bodies.Attractor.EARTH,
        departure_position=np.array([5000, 10000, 2100]) * u.km,
        arrival_position=np.array([-14600, 2500, 7000]) * u.km,
        delta_time=time.TimeDelta(1 * u.hour),
        direction="prograde",
    )

    assert result is None


def test_predict_from_gauss_method_extended():
    """:cite:`curtis` EXAMPLE 5.12"""
    
    r, v = sl_determination.predict_from_gauss_method_extended(
        attractor=sl_bodies.Attractor.EARTH,
        latitude=40 * u.deg,
        local_sidereal_time_list=np.array([44.506, 45.000, 45.499]) * u.deg,
        right_ascension_list=np.array([43.537, 54.420, 64.318]) * u.deg,
        declination_list=np.array([-8.7833, -12.074, -15.105]) * u.deg,
        observation_time_list=np.array([0, 118.10, 237.58]) * u.s,
        site_altitude=1 * u.km)
    
    assert np.isclose(r[0].to_value(u.km), 5662.8, atol=1e-1)
    assert np.isclose(r[1].to_value(u.km), 6539.0, atol=1e-1)
    assert np.isclose(r[2].to_value(u.km), 3269.0, atol=1e-1)
    assert np.isclose(v[0].to_value(u.km / u.s), -3.8848, atol=1e-4)
    assert np.isclose(v[1].to_value(u.km / u.s), 5.1254, atol=1e-4)
    assert np.isclose(v[2].to_value(u.km / u.s), -2.2446, atol=1e-4)
