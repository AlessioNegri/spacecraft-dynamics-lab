import astropy.units as u
import numpy as np
import pytest

import spacelab.bodies as sl_bodies
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.orbit.representation as sl_representation
import spacelab.proximity.kinematics as sl_kinematics

def test_local_vertical_local_horizontal_kinematics_and_geocentric_equatorial_kinematics():
    """:cite:`curtis` EXAMPLE 7.1"""
    
    attractor = sl_bodies.Attractor.EARTH
    
    oe_target = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=52059 * u.km**2 / u.s,
        eccentricity=0.025724 * u.one,
        inclination=60 * u.deg,
        right_ascension_of_ascending_node=40 * u.deg,
        argument_of_periapsis=30 * u.deg,
        true_anomaly=40 * u.deg)
    
    r_target, v_target = sl_representation.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_target)
    
    oe_chaser = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=52362 * u.km**2 / u.s,
        eccentricity=0.0072696 * u.one,
        inclination=50 * u.deg,
        right_ascension_of_ascending_node=40 * u.deg,
        argument_of_periapsis=120 * u.deg,
        true_anomaly=40 * u.deg)
    
    r_chaser, v_chaser = sl_representation.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_chaser)
    
    kinematics = sl_kinematics.local_vertical_local_horizontal_kinematics(
        attractor=attractor, orbital_elements_target=oe_target, orbital_elements_chaser=oe_chaser)
    
    r_rel_lvlh: u.Quantity = kinematics[0]
    v_rel_lvlh: u.Quantity = kinematics[1]
    a_rel_lvlh: u.Quantity = kinematics[2]
    
    assert np.isclose(r_rel_lvlh[0].to_value(u.km), -6701.20, atol=1e-2)
    assert np.isclose(r_rel_lvlh[1].to_value(u.km), +6828.30, atol=1e-2)
    assert np.isclose(r_rel_lvlh[2].to_value(u.km), -0406.26, atol=1e-2)
    
    assert np.isclose(v_rel_lvlh[0].to_value(u.km / u.s), 0.31667, atol=1e-5)
    assert np.isclose(v_rel_lvlh[1].to_value(u.km / u.s), 0.11199, atol=1e-5)
    assert np.isclose(v_rel_lvlh[2].to_value(u.km / u.s), 1.24696, atol=1e-5)
    
    assert np.isclose(a_rel_lvlh[0].to_value(u.km / u.s**2), -0.00022222, atol=1e-8)
    assert np.isclose(a_rel_lvlh[1].to_value(u.km / u.s**2), -0.00018074, atol=1e-8)
    assert np.isclose(a_rel_lvlh[2].to_value(u.km / u.s**2), +0.00050593, atol=1e-8)
    
    kinematics = sl_kinematics.geocentric_equatorial_kinematics(
        position_target=r_target,
        velocity_target=v_target,
        position_rel_lvlh=r_rel_lvlh,
        velocity_rel_lvlh=v_rel_lvlh)
    
    assert np.isclose(kinematics[0][0].to_value(u.km), r_chaser[0].to_value(u.km), atol=1e-2)
    assert np.isclose(kinematics[0][1].to_value(u.km), r_chaser[1].to_value(u.km), atol=1e-2)
    assert np.isclose(kinematics[0][2].to_value(u.km), r_chaser[2].to_value(u.km), atol=1e-2)
    
    assert np.isclose(kinematics[1][0].to_value(u.km / u.s), v_chaser[0].to_value(u.km / u.s), atol=1e-2)
    assert np.isclose(kinematics[1][1].to_value(u.km / u.s), v_chaser[1].to_value(u.km / u.s), atol=1e-2)
    assert np.isclose(kinematics[1][2].to_value(u.km / u.s), v_chaser[2].to_value(u.km / u.s), atol=1e-2)


def test_geocentric_equatorial_kinematics_invalid_velocity_shape_returns_none():
    result = sl_kinematics.geocentric_equatorial_kinematics(
        position_target=np.array([7000, 0, 0]) * u.km,
        velocity_target=np.array([0, 7.5]) * u.km / u.s,
        position_rel_lvlh=np.array([1, 0, 0]) * u.km,
        velocity_rel_lvlh=np.array([0, 0.1, 0]) * u.km / u.s,
    )

    assert result is None


def test_lvlh_simulation_positive_case():
    target = sl_orbital_elements.OrbitalElements(
        semimajor_axis=7000 * u.km,
        eccentricity=0 * u.one,
    )
    chaser = sl_orbital_elements.OrbitalElements(
        semimajor_axis=7100 * u.km,
        eccentricity=0 * u.one,
    )

    result = sl_kinematics.simulate_local_vertical_local_horizontal_kinematics(
        attractor=sl_bodies.Attractor.EARTH,
        orbital_elements_target=target,
        orbital_elements_chaser=chaser,
        target_period_multiplier=1,
        points_number=10,
    )

    assert result is not None
    assert len(result) == 3
    assert all(len(axis) == 10 for axis in result)
    assert all(np.all(np.isfinite(axis)) for axis in result)


@pytest.mark.parametrize("points_number", [-1, 0])
def test_lvlh_simulation_rejects_nonpositive_points(points_number):
    target = sl_orbital_elements.OrbitalElements(
        semimajor_axis=7000 * u.km,
        eccentricity=0 * u.one,
    )
    chaser = sl_orbital_elements.OrbitalElements(
        semimajor_axis=7100 * u.km,
        eccentricity=0 * u.one,
    )

    result = sl_kinematics.simulate_local_vertical_local_horizontal_kinematics(
        attractor=sl_bodies.Attractor.EARTH,
        orbital_elements_target=target,
        orbital_elements_chaser=chaser,
        target_period_multiplier=1,
        points_number=points_number,
    )

    assert result is None
