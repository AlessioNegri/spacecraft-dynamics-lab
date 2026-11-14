import astropy.time as time
import astropy.units as u
import numpy as np

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.models.orbit_parameters as sl_orbit_parameters
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.n_body_models.conversions as sl_conversions
import spacelab.orbit.position as sl_position
import spacelab.orbit.representation as sl_representation

def test_right_ascension_declination():
    """:cite:`curtis` EXAMPLE 4.1"""
    
    alpha, delta = sl_representation.right_ascension_declination(position=np.array([-5368, -1784, 3691]) * u.km)
    
    assert np.isclose(alpha.to_value(u.deg), 198.4, atol=1e-1)
    assert np.isclose(delta.to_value(u.deg), 33.12, atol=1e-2)

def test_cartesian_to_keplerian_1():
    """:cite:`curtis` EXAMPLE 4.3"""
    
    oe = sl_representation.cartesian_to_keplerian(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([-6045, -3490, 2500]) * u.km,
        velocity=np.array([-3.457, 6.618, 2.533]) * u.km / u.s)
    
    assert np.isclose(oe.specific_angular_momentum.to_value(u.km**2 / u.s), 58311, atol=1e-0)
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 8788, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.1712, atol=1e-4)
    assert np.isclose(oe.inclination.to_value(u.deg), 153.2, atol=1e-1)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 255.3, atol=1e-1)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 20.07, atol=1e-2)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 28.45, atol=1e-2)

def test_cartesian_to_keplerian_2():
    """:cite:`kluever` EXAMPLE 3.1"""
    
    oe = sl_representation.cartesian_to_keplerian(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([9031.5, -5316.9, -1647.2]) * u.km,
        velocity=np.array([-2.8640, 5.1112, -5.0805]) * u.km / u.s)
    
    assert np.isclose(oe.specific_angular_momentum.to_value(u.km**2 / u.s), np.sqrt(35432**2 + 50602**2 + 30934**2), atol=1e-0)
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 26563.6, atol=1e-1)
    assert np.isclose(oe.eccentricity.to_value(), 0.7411, atol=1e-4)
    assert np.isclose(oe.inclination.to_value(u.deg), 63.4, atol=1e-1)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 145, atol=1e-0)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 270, atol=1e-0)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 280, atol=1e-0)

def test_geocentric_equatorial_to_perifocal_1():
    """:cite:`curtis` EXAMPLE 4.7"""
    
    r_PF, v_PF = sl_representation.geocentric_equatorial_to_perifocal(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([-4040, 4815, 3629]) * u.km,
        velocity=np.array([-10.39, -4.772, 1.744]) * u.km / u.s)
    
    assert np.allclose(r_PF.to_value(u.km)[0], 6285, atol=1e-0)
    assert np.allclose(r_PF.to_value(u.km)[1], 3628.6, atol=1e-0)
    assert np.allclose(v_PF.to_value(u.km / u.s)[0], -2.4898, atol=1e-4)
    assert np.allclose(v_PF.to_value(u.km / u.s)[1], 11.295, atol=1e-3)
    
def test_perifocal_to_geocentric_equatorial_2():
    """:cite:`kluever` EXAMPLE 3.2"""
    
    oe = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum = 0 * u.km**2 / u.s,
        semimajor_axis = 26564 * u.km,
        eccentricity = 0.7411 * u.one,
        inclination = 63.4 * u.deg,
        right_ascension_of_ascending_node = 200 * u.deg,
        argument_of_periapsis = -90 * u.deg,
        true_anomaly = 30 * u.deg
    )
    
    r_GEF, v_GEF = sl_representation.keplerian_to_cartesian(attractor=sl_bodies.Attractor.EARTH, orbital_elements=oe)
    
    assert np.allclose(r_GEF.to_value(u.km)[0], -4394.0, atol=1e-1)
    assert np.allclose(r_GEF.to_value(u.km)[1], 1410.3, atol=1e-1)
    assert np.allclose(r_GEF.to_value(u.km)[2], -5647.7, atol=1e-1)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[0], -8.2715, atol=1e-4)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[1], -4.3852, atol=1e-4)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[2], 2.5794, atol=1e-4)

def test_perifocal_to_geocentric_equatorial():
    """:cite:`curtis` EXAMPLE 4.7"""
    
    oe = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum = 80_000 * u.km**2 / u.s,
        semimajor_axis = 0 * u.km,
        eccentricity = 1.4 * u.one,
        inclination = 30 * u.deg,
        right_ascension_of_ascending_node = 40 * u.deg,
        argument_of_periapsis = 60 * u.deg,
        true_anomaly = 30 * u.deg
    )
    
    r_GEF, v_GEF = sl_representation.keplerian_to_cartesian(attractor=sl_bodies.Attractor.EARTH, orbital_elements=oe)
    
    assert np.allclose(r_GEF.to_value(u.km)[0], -4040, atol=1e-0)
    assert np.allclose(r_GEF.to_value(u.km)[1], 4815, atol=1e-0)
    assert np.allclose(r_GEF.to_value(u.km)[2], 3629, atol=1e-0)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[0], -10.39, atol=1e-2)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[1], -4.772, atol=1e-3)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[2], 1.744, atol=1e-3)
    
def test_keplerian_to_equinoctial():
    """:cite:`walter` EXAMPLE 7.3.5"""

    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=8350 * u.km,
        eccentricity=0.19760 * u.one,
        inclination=60 * u.deg,
        right_ascension_of_ascending_node=270 * u.deg,
        argument_of_periapsis=45 * u.deg,
        true_anomaly=230 * u.deg)

    eq = sl_representation.keplerian_to_equinoctial(oe)

    assert np.isclose(eq.semimajor_axis.to_value(u.km), 8350, atol=1e-6)
    assert np.isclose(eq.eccentricity_vector_h.to_value(u.one), -0.139685, atol=1e-4)
    assert np.isclose(eq.eccentricity_vector_k.to_value(u.one), 0.139685, atol=1e-4)
    assert np.isclose(eq.ascending_node_vector_p.to_value(u.one), -0.577350, atol=1e-4)
    assert np.isclose(eq.ascending_node_vector_q.to_value(u.one), 0.0, atol=1e-6)
    assert np.isclose(eq.periapsis_location.to_value(u.deg), 545.0, atol=1e-6)

def test_planet_oblateness_effect():
    """:cite:`curtis` EXAMPLE 4.8"""
    
    oe = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum = 0 * u.km**2 / u.s,
        semimajor_axis = 6718 * u.km,
        eccentricity = 0.008931 * u.one,
        inclination = 51.43 * u.deg,
        right_ascension_of_ascending_node = 0 * u.deg,
        argument_of_periapsis = 0 * u.deg,
        true_anomaly = 0 * u.deg
    )
    
    d_raan_dt, d_argp_dt = sl_representation.planet_oblateness_effect(
        attractor=sl_bodies.Attractor.EARTH, orbital_elements=oe)
    
    assert np.isclose(d_raan_dt.to_value(u.deg / u.day), -5.181, atol=1e-3)
    assert np.isclose(d_argp_dt.to_value(u.deg / u.day), 3.920, atol=1e-3)
    
def test_example_4_11():
    """:cite:`curtis` EXAMPLE 4.11"""
    
    attractor = sl_bodies.Attractor.EARTH
    
    r_GEF: u.Quantity = np.array([-3670, -3870, 4400]) * u.km
    v_GEF: u.Quantity = np.array([4.7, -7.4, 1]) * u.km / u.s
    
    oe: sl_orbital_elements.OrbitalElements =\
        sl_representation.cartesian_to_keplerian(attractor=attractor, position=r_GEF, velocity=v_GEF)
    
    assert np.isclose(oe.specific_angular_momentum.to_value(u.km**2 / u.s), 58_926, atol=1e-0)
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 10644, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.42607, atol=1e-5)
    assert np.isclose(oe.inclination.to_value(u.deg), 39.687, atol=1e-3)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 130.32, atol=1e-2)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 42.373, atol=1e-3)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 52.404, atol=1e-3)
    
    parameters: sl_orbit_parameters.OrbitParameters =\
        sl_conversions.cartesian_to_orbit_parameters(attractor=attractor, position=r_GEF, velocity=v_GEF)
    
    assert np.isclose(parameters.period.to_value(u.s), 10_928, atol=1e-0)
    
    n: float = 2 * np.pi / parameters.period.to_value(u.s) # ? Mean motion [rad/s]
    
    t_1: u.Quantity = sl_position.elliptical_orbit_time(
        true_anomaly=oe.true_anomaly, period=parameters.period, eccentricity=oe.eccentricity)
    
    assert np.isclose(t_1.to_value(u.s), 631.00, atol=1e-0)
    
    t_2: u.Quantity = t_1 + 96 * u.hour
    
    nu_32: u.Quantity = sl_position.elliptical_orbit_true_anomaly(
        time_of_flight=t_2, period=parameters.period, eccentricity=oe.eccentricity)
    
    assert np.isclose(nu_32.to_value(u.deg), 360-148.75, atol=1e-1)
    
    d_raan_dt, d_argp_dt = sl_representation.planet_oblateness_effect(attractor=attractor, orbital_elements=oe)
    
    oe.right_ascension_of_ascending_node += d_raan_dt.to(u.deg / u.day) * t_2.to(u.day)
    oe.argument_of_periapsis += d_argp_dt.to(u.deg / u.day) * t_2.to(u.day)
    oe.true_anomaly = nu_32
    
    r_GEF, v_GEF = sl_representation.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe)
    
    assert np.allclose(r_GEF.to_value(u.km)[0], 9667, atol=1e-0)
    assert np.allclose(r_GEF.to_value(u.km)[1], 4326, atol=1e-0)
    assert np.allclose(r_GEF.to_value(u.km)[2], -8691, atol=1e-0)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[0], -3.040, atol=1e-2)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[1], 3.330, atol=1e-3)
    assert np.allclose(v_GEF.to_value(u.km / u.s)[2], 0.6327, atol=1e-4)

def test_latitude():
    """:cite:`sforza` EXAMPLE 5.4.2"""
    
    latitude, hemisphere = sl_representation.latitude(inclination=30 * u.deg, true_anomaly=59.04 * u.deg)
    
    assert np.isclose(latitude.to_value(u.deg), 25.38, atol=1e-2)
    assert hemisphere == sl_enums.Hemisphere.NORTH
    
    latitude, hemisphere = sl_representation.latitude(inclination=30 * u.deg, true_anomaly=287.0 * u.deg)
        
    assert np.isclose(latitude.to_value(u.deg), 28.56, atol=1e-2)
    assert hemisphere == sl_enums.Hemisphere.SOUTH

def test_longitude():
    """:cite:`sforza` EXAMPLE 5.4.7"""
    
    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=9684 * u.km,
        eccentricity=0.3 * u.one,
        inclination=30 * u.deg,
        right_ascension_of_ascending_node=210 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=59.04 * u.deg)
    
    latitude: sl_enums.AngleHemisphere = sl_representation.latitude(inclination=30 * u.deg, true_anomaly=59.04 * u.deg)
    
    epoch = time.Time("2000-01-01 12:00:00", scale="utc")
    
    longitude: sl_enums.AngleHemisphere = sl_representation.longitude(
        orbital_elements=oe, latitude=latitude, epoch=epoch, orbit_time=488.5 * u.minute)
    
    assert np.isclose(longitude.angle.to_value(u.deg), 154.3, atol=1e-1)
    assert longitude.hemisphere == sl_enums.Hemisphere.EAST
    
    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=9684 * u.km,
        eccentricity=0.3 * u.one,
        inclination=30 * u.deg,
        right_ascension_of_ascending_node=210 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=287 * u.deg)
    
    latitude: sl_enums.AngleHemisphere = sl_representation.latitude(inclination=30 * u.deg, true_anomaly=287 * u.deg)
    
    longitude: sl_enums.AngleHemisphere = sl_representation.longitude(
        orbital_elements=oe, latitude=latitude, epoch=epoch, orbit_time=613.2 * u.minute)
    
    assert np.isclose(longitude.angle.to_value(u.deg), 0.5, atol=1e-1)
    assert longitude.hemisphere == sl_enums.Hemisphere.EAST

def test_horizon_footprint():
    """EXAMPLE 5.5 - BOOK 3"""
    
    c_f, beta, delta, _ = sl_representation.horizon_footprint(attractor=sl_bodies.Attractor.EARTH, altitude=400 * u.km)
    
    assert np.isclose(c_f.to_value(u.km), 4404, atol=1e-0)
    assert np.isclose(beta.to_value(u.deg), 19.78, atol=1e-2)
    assert np.isclose(delta.to_value(u.deg), 70.22, atol=1e-2)

def test_ground_track_propagation():
    """:cite:`curtis` EXAMPLE 4.12"""
    
    oe = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum = 0 * u.km**2 / u.s,
        semimajor_axis = 8350 * u.km,
        eccentricity = 0.19760 * u.one,
        inclination = 60 * u.deg,
        right_ascension_of_ascending_node = 270 * u.deg,
        argument_of_periapsis = 45 * u.deg,
        true_anomaly = 230 * u.deg
    )
    
    alpha, delta = sl_representation.ground_track_propagation(
        attractor=sl_bodies.Attractor.EARTH, orbital_elements=oe, time_step=time.TimeDelta(45 * u.minute))
    
    assert np.isclose(alpha.to_value(u.deg), 313.7 - 180, atol=1e-1)
    assert np.isclose(delta.to_value(u.deg), 54.84, atol=1e-2)

def test_eclipse_duration():
    """:cite:`walter` EXAMPLE 14.1.1"""
    
    beta, eclipse, t_e, hot_case = sl_representation.eclipse_duration(
        attractor=sl_bodies.Attractor.EARTH,
        circular_orbit_radius=42166 * u.km,
        inclination=0 * u.deg,
        right_ascension_ascending_node=0 * u.deg,
        right_ascension_sun=0 * u.deg)
    
    assert np.isclose(beta.to_value(u.deg), 0, atol=1e-1)
    assert eclipse
    assert np.isclose(t_e.to_value(u.minute), 69.4, atol=1e-1)
    assert hot_case


def test_rotation_matrix_is_orthogonal_with_unit_determinant():
    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=8350 * u.km,
        eccentricity=0.19760 * u.one,
        inclination=60 * u.deg,
        right_ascension_of_ascending_node=270 * u.deg,
        argument_of_periapsis=45 * u.deg,
        true_anomaly=230 * u.deg,
    )

    rotation = sl_representation.rotation_matrix_ijk_to_pqw(oe)

    assert np.allclose(rotation @ rotation.T, np.identity(3), atol=1e-12)
    assert np.isclose(np.linalg.det(rotation), 1, atol=1e-12)


def test_perifocal_position_conversion_matches_keplerian_state():
    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=8350 * u.km,
        eccentricity=0.19760 * u.one,
        inclination=60 * u.deg,
        right_ascension_of_ascending_node=270 * u.deg,
        argument_of_periapsis=45 * u.deg,
        true_anomaly=230 * u.deg,
    )
    semilatus_rectum = oe.calc_semilatus_rectum(attractor=sl_bodies.Attractor.EARTH)
    true_anomaly = oe.true_anomaly.to_value(u.rad)
    perifocal_position = semilatus_rectum / (1 + oe.eccentricity * np.cos(true_anomaly)) * np.array(
        [np.cos(true_anomaly), np.sin(true_anomaly), 0]
    )

    expected_position, _ = sl_representation.keplerian_to_cartesian(
        sl_bodies.Attractor.EARTH,
        oe,
    )
    actual_position = sl_representation.perifocal_to_geocentric_equatorial_position_vector(
        oe,
        perifocal_position,
    )

    assert np.allclose(actual_position.to_value(u.km), expected_position.to_value(u.km), atol=1e-9)


def test_position_vector_representations_preserve_magnitude_and_frame_components():
    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=8350 * u.km,
        eccentricity=0.19760 * u.one,
        inclination=60 * u.deg,
        right_ascension_of_ascending_node=270 * u.deg,
        argument_of_periapsis=45 * u.deg,
        true_anomaly=230 * u.deg,
    )
    magnitude = 7000 * u.km
    flight_path_angle = 20 * u.deg

    r_ijk, r_pqw, r_ntw, r_rsw = sl_representation.position_vector_representations(
        oe,
        flight_path_angle,
        magnitude,
    )

    for vector in (r_ijk, r_pqw, r_ntw, r_rsw):
        assert np.isclose(np.linalg.norm(vector.to_value(u.km)), magnitude.to_value(u.km))
    assert np.allclose(
        r_pqw.to_value(u.km),
        magnitude.to_value(u.km) * np.array([np.cos(oe.true_anomaly.to_value(u.rad)), np.sin(oe.true_anomaly.to_value(u.rad)), 0]),
    )
    assert np.allclose(
        r_ntw.to_value(u.km),
        magnitude.to_value(u.km) * np.array([np.cos(flight_path_angle.to_value(u.rad)), np.sin(flight_path_angle.to_value(u.rad)), 0]),
    )
    assert np.allclose(r_rsw.to_value(u.km), [magnitude.to_value(u.km), 0, 0])


def test_velocity_vector_representations_preserve_magnitude_and_local_components():
    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=8350 * u.km,
        eccentricity=0.19760 * u.one,
        inclination=60 * u.deg,
        right_ascension_of_ascending_node=270 * u.deg,
        argument_of_periapsis=45 * u.deg,
        true_anomaly=230 * u.deg,
    )
    magnitude = 7.5 * u.km / u.s
    flight_path_angle = 20 * u.deg

    v_ijk, v_pqw, v_rsw, v_ntw = sl_representation.velocity_vector_representations(
        oe,
        flight_path_angle,
        magnitude,
    )

    for vector in (v_ijk, v_pqw, v_rsw, v_ntw):
        assert np.isclose(np.linalg.norm(vector.to_value(u.km / u.s)), magnitude.to_value(u.km / u.s))
    assert np.allclose(v_ntw.to_value(u.km / u.s), [0, magnitude.to_value(u.km / u.s), 0])
    assert np.allclose(
        v_rsw.to_value(u.km / u.s),
        magnitude.to_value(u.km / u.s) * np.array([np.sin(flight_path_angle.to_value(u.rad)), np.cos(flight_path_angle.to_value(u.rad)), 0]),
    )


def test_perifocal_position_conversion_invalid_vector_returns_zero():
    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=8350 * u.km,
        eccentricity=0.19760 * u.one,
        inclination=60 * u.deg,
        right_ascension_of_ascending_node=270 * u.deg,
        argument_of_periapsis=45 * u.deg,
        true_anomaly=230 * u.deg,
    )

    result = sl_representation.perifocal_to_geocentric_equatorial_position_vector(
        oe,
        np.array([1, 0, 0]) * u.s,
    )

    assert np.array_equal(result.to_value(u.km), np.zeros(3))


def test_eclipse_duration_returns_no_eclipse_for_polar_sun_geometry():
    beta, eclipse, eclipse_duration, _ = sl_representation.eclipse_duration(
        attractor=sl_bodies.Attractor.EARTH,
        circular_orbit_radius=42166 * u.km,
        inclination=90 * u.deg,
        right_ascension_ascending_node=90 * u.deg,
        right_ascension_sun=0 * u.deg,
    )

    assert np.isclose(beta.to_value(u.deg), 90, atol=1e-10)
    assert not eclipse
    assert eclipse_duration == 0 * u.s


def test_right_ascension_declination_invalid_position_returns_zero_angles():
    right_ascension, declination = sl_representation.right_ascension_declination(
        np.array([1, 2]) * u.km,
    )

    assert right_ascension == 0 * u.deg
    assert declination == 0 * u.deg


def test_cartesian_to_keplerian_invalid_attractor_returns_default_elements():
    oe = sl_representation.cartesian_to_keplerian(
        attractor="Earth",
        position=np.array([7000, 0, 0]) * u.km,
        velocity=np.array([0, 7.5, 0]) * u.km / u.s,
    )

    assert isinstance(oe, sl_orbital_elements.OrbitalElements)
    assert oe.semimajor_axis == 0 * u.km
    assert oe.eccentricity == 0 * u.one


def test_horizon_footprint_rejects_nonpositive_altitude():
    footprint, tangent_angle, line_of_sight_angle, access_area = sl_representation.horizon_footprint(
        sl_bodies.Attractor.EARTH,
        0 * u.km,
    )

    assert footprint == 0 * u.km
    assert tangent_angle == 0 * u.rad
    assert line_of_sight_angle == 0 * u.rad
    assert access_area == 0 * u.rad


def test_ground_track_rejects_hyperbolic_orbit():
    oe = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=80_000 * u.km**2 / u.s,
        semimajor_axis=-10_000 * u.km,
        eccentricity=1.4 * u.one,
        inclination=30 * u.deg,
        right_ascension_of_ascending_node=40 * u.deg,
        argument_of_periapsis=60 * u.deg,
        true_anomaly=30 * u.deg,
    )

    right_ascension, declination = sl_representation.ground_track_propagation(
        sl_bodies.Attractor.EARTH,
        oe,
        time.TimeDelta(60 * u.s),
    )

    assert right_ascension == 0 * u.deg
    assert declination == 0 * u.deg
