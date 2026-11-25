import astropy.time as time
import astropy.units as u
import numpy as np
import pytest

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.orbit.representation as sl_representation
import spacelab.proximity.kinematics as sl_kinematics
import spacelab.proximity.rendezvous as sl_rendezvous

def test_clohessy_wiltshire_matrices():
    """:cite:`curtis` EXAMPLE 7.5"""
    
    phi_rr, phi_rv, phi_vr, phi_vv = sl_rendezvous.clohessy_wiltshire_matrices(
        mean_motion=0.0011569 * u.rad / u.s, final_time=1.49 * u.hour)
    
    assert np.isclose(phi_rr[0,0], +1.0090, atol=1e-4)
    assert np.isclose(phi_rr[0,1], +0.0000, atol=1e-4)
    assert np.isclose(phi_rr[1,0], -37.699, atol=1e-3)
    assert np.isclose(phi_rr[1,1], +1.0000, atol=1e-4)
    assert np.isclose(phi_rr[2,2], +0.9970, atol=1e-4)
    
    assert np.isclose(phi_rv[0,0], -66.986, atol=1e-3)
    assert np.isclose(phi_rv[0,1], +5.1989, atol=1e-4)
    assert np.isclose(phi_rv[1,0], -5.1989, atol=1e-4)
    assert np.isclose(phi_rv[1,1], -16360., atol=1e-0)
    assert np.isclose(phi_rv[2,2], -66.986, atol=1e-3)
    
    assert np.isclose(phi_vr[0,0], -2.6897e-4, atol=1e-8)
    assert np.isclose(phi_vr[0,1], +0.0000, atol=1e-4)
    assert np.isclose(phi_vr[1,0], -2.0875e-5, atol=1e-9)
    assert np.isclose(phi_vr[1,1], +0.0000, atol=1e-4)
    assert np.isclose(phi_vr[2,2], +8.9655e-5, atol=1e-9)
    
    assert np.isclose(phi_vv[0,0], +0.9970, atol=1e-4)
    assert np.isclose(phi_vv[0,1], -0.1549, atol=1e-4)
    assert np.isclose(phi_vv[1,0], +0.1549, atol=1e-4)
    assert np.isclose(phi_vv[1,1], +0.98798, atol=1e-5)
    assert np.isclose(phi_vv[2,2], +0.9970, atol=1e-4)

def test_clohessy_wiltshire_equations_1():
    """:cite:`kluever` EXAMPLE 8.1"""
    
    dr, dv = sl_rendezvous.clohessy_wiltshire_equations(
        relative_position_0=np.array([-10, -300.2, 0]) * u.km,
        relative_velocity_0=np.array([0, 0.011874, 0]) * u.km / u.s,
        mean_motion=7.9163e-4 * u.rad/ u.s,
        final_time=30 * u.minute)
    
    assert np.isclose(dr[0].to_value(u.km), -10, atol=1e-0)
    assert np.isclose(dr[1].to_value(u.km), -278.8, atol=1e-1)
    assert np.isclose(dv[0].to_value(u.km / u.s), 0, atol=1e-0)
    assert np.isclose(dv[1].to_value(u.km / u.s), 0.011874, atol=1e-5)

def test_clohessy_wiltshire_equations_2():
    """:cite:`kluever` EXAMPLE 8.2"""
    
    dr, dv = sl_rendezvous.clohessy_wiltshire_equations(
        relative_position_0=np.array([0, 0, 0]) * u.km,
        relative_velocity_0=np.array([0.04, 0, 0]) * u.km / u.s,
        mean_motion=1.1517e-3 * u.rad/ u.s,
        final_time=90.9 * u.minute)
    
    assert np.isclose(dr[0].to_value(u.km), 0, atol=1e-0)
    assert np.isclose(dr[1].to_value(u.km), 0, atol=1e-0)
    assert np.isclose(dv[0].to_value(u.km / u.s), 0.04, atol=1e-2)
    assert np.isclose(dv[1].to_value(u.km / u.s), 0, atol=1e-0)

def test_two_impulsive_rendezvous_maneuver_1():
    """:cite:`curtis` EXAMPLE 7.4"""
    
    radius: float = sl_bodies.BODIES[sl_bodies.Attractor.EARTH].R_E.to_value(u.km)
    
    oe_target = sl_orbital_elements.OrbitalElements(
        inclination=40 * u.deg,
        right_ascension_of_ascending_node=20 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=60 * u.deg)
    
    oe_target.update_from_periapsis_apoapsis(
        periapsis_radius=(radius + 300) * u.km, apoapsis_radius=(radius + 300) * u.km)
    
    oe_chaser = sl_orbital_elements.OrbitalElements(
        inclination=40.130 * u.deg,
        right_ascension_of_ascending_node=19.819 * u.deg,
        argument_of_periapsis=70.662 * u.deg,
        true_anomaly=349.65 * u.deg)
    
    oe_chaser.update_from_periapsis_apoapsis(
        periapsis_radius=(radius + 320.06) * u.km, apoapsis_radius=(radius + 513.86) * u.km)
    
    dv_tot, _, _, _ = sl_rendezvous.two_impulsive_rendezvous_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        orbital_elements_target=oe_target,
        orbital_elements_chaser=oe_chaser,
        maneuver_time=8 * u.hour)
    
    assert np.isclose(dv_tot.to_value(u.m / u.s), 111.24, atol=1e-2)

def test_two_impulsive_rendezvous_maneuver_2():
    """:cite:`kluever` EXAMPLE 8.4"""
    
    attractor = sl_bodies.Attractor.EARTH
    
    radius: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)
    
    oe_target = sl_orbital_elements.OrbitalElements()
    
    oe_target.update_from_periapsis_apoapsis(
        periapsis_radius=(radius + 300) * u.km, apoapsis_radius=(radius + 300) * u.km)
    
    r_target, v_target = sl_representation.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_target)
    
    mu: float = sl_bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    y_dot: float = np.sqrt(mu / (radius + 320)) - np.sqrt(mu / (radius + 300))
    
    r_chaser, v_chaser = sl_kinematics.geocentric_equatorial_kinematics(
        position_target=r_target,
        velocity_target=v_target,
        position_rel_lvlh=np.array([20, 40, 0]) * u.km,
        velocity_rel_lvlh=np.array([0, y_dot, 0]) * u.km / u.s)
    
    oe_chaser: sl_orbital_elements.OrbitalElements = sl_representation.cartesian_to_keplerian(
        attractor=attractor, position=r_chaser, velocity=v_chaser)
    
    dv_tot, _, _, _ = sl_rendezvous.two_impulsive_rendezvous_maneuver(
        attractor=attractor,
        orbital_elements_target=oe_target,
        orbital_elements_chaser=oe_chaser,
        maneuver_time=22.63 * u.minute)
    
    assert np.isclose(dv_tot.to_value(u.m / u.s), 57.87, atol=1e-2)

def test_two_impulsive_rendezvous_maneuver_3():
    """:cite:`kluever` EXAMPLE 8.5"""
    
    attractor = sl_bodies.Attractor.EARTH
    
    radius: float = sl_bodies.BODIES[attractor].R_E.to_value(u.km)
    
    oe_target = sl_orbital_elements.OrbitalElements()
    
    oe_target.update_from_periapsis_apoapsis(
        periapsis_radius=(radius + 350) * u.km, apoapsis_radius=(radius + 350) * u.km)
    
    r_target, v_target = sl_representation.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_target)
    
    r_chaser, v_chaser = sl_kinematics.geocentric_equatorial_kinematics(
        position_target=r_target,
        velocity_target=v_target,
        position_rel_lvlh=np.array([0, 587.13, 0]) * u.km,
        velocity_rel_lvlh=np.array([0, 0, 0]) * u.km / u.s)
    
    oe_chaser: sl_orbital_elements.OrbitalElements = sl_representation.cartesian_to_keplerian(
        attractor=attractor, position=r_chaser, velocity=v_chaser)
    
    dv_tot, _, _, _ = sl_rendezvous.two_impulsive_rendezvous_maneuver(
        attractor=attractor,
        orbital_elements_target=oe_target,
        orbital_elements_chaser=oe_chaser,
        maneuver_time=250 * u.minute)
    
    assert np.isclose(dv_tot.to_value(u.m / u.s), 54.73, atol=1e-2)

def test_clohessy_wiltshire_matrices_at_zero_time_are_identity():
    phi_rr, phi_rv, phi_vr, phi_vv = sl_rendezvous.clohessy_wiltshire_matrices(
        mean_motion=0.001 * u.rad / u.s,
        final_time=0 * u.s,
    )

    assert np.allclose(phi_rr, np.identity(3))
    assert np.allclose(phi_rv, np.zeros((3, 3)))
    assert np.allclose(phi_vr, np.zeros((3, 3)))
    assert np.allclose(phi_vv, np.identity(3))


def test_clohessy_wiltshire_equations_at_zero_time_preserve_state():
    relative_position = np.array([10, -20, 3]) * u.km
    relative_velocity = np.array([0.01, -0.02, 0.005]) * u.km / u.s

    final_position, final_velocity = sl_rendezvous.clohessy_wiltshire_equations(
        relative_position_0=relative_position,
        relative_velocity_0=relative_velocity,
        mean_motion=0.001 * u.rad / u.s,
        final_time=0 * u.s,
    )

    assert np.allclose(final_position.to_value(u.km), relative_position.to_value(u.km))
    assert np.allclose(final_velocity.to_value(u.km / u.s), relative_velocity.to_value(u.km / u.s))


@pytest.mark.parametrize(
    ("relative_position", "relative_velocity", "mean_motion", "final_time"),
    [
        pytest.param(np.array([10, 0]) * u.km, np.zeros(3) * u.km / u.s, 0.001 * u.rad / u.s, 60 * u.s, id="position-shape"),
        pytest.param(np.zeros(3) * u.km, np.array([0, 0.1]) * u.km / u.s, 0.001 * u.rad / u.s, 60 * u.s, id="velocity-shape"),
        pytest.param(np.zeros(3) * u.km, np.zeros(3) * u.km / u.s, 1 * u.Hz, 60 * u.s, id="mean-motion-unit"),
        pytest.param(np.zeros(3) * u.km, np.zeros(3) * u.km / u.s, 0.001 * u.rad / u.s, 60 * u.km, id="time-unit"),
    ],
)
def test_clohessy_wiltshire_equations_invalid_inputs_return_none(relative_position, relative_velocity, mean_motion, final_time):
    result = sl_rendezvous.clohessy_wiltshire_equations(
        relative_position_0=relative_position,
        relative_velocity_0=relative_velocity,
        mean_motion=mean_motion,
        final_time=final_time,
    )

    assert result is None


def test_circular_orbit_rendezvous_formula():
    relative_position = np.array([10, -20, 3]) * u.km

    velocity = sl_rendezvous.circular_orbit_rendezvous_maneuver(
        relative_position_0=relative_position,
        mean_motion=0.001 * u.rad / u.s,
        final_time=60 * u.s,
    )

    assert len(velocity) == 3
    assert np.isclose(velocity[0].to_value(u.km / u.s), -10 / 60 + 0.001 * (-20), atol=1e-10)
    assert np.isclose(velocity[1].to_value(u.km / u.s), -(-20) / 60 - 0.001 * 10, atol=1e-10)
    assert np.isclose(velocity[2].to_value(u.km / u.s), -3 / 60, atol=1e-10)


def test_launch_phase_positive_case():
    launch_times = sl_rendezvous.launch_phase(
        timestamp=time.Time("2024-05-16 00:00:00", scale="utc"),
        launch_site_latitude=28.5 * u.deg,
        launch_site_longitude=-80.6 * u.deg,
        target_inclination=51.6 * u.deg,
        target_right_ascension_ascending_node=20 * u.deg,
    )

    assert launch_times is not None
    assert len(launch_times) == 2
    assert all(np.isfinite(time_value.to_value(u.s)) for time_value in launch_times)


def test_launch_phase_rejects_target_inclination_below_site_latitude():
    launch_times = sl_rendezvous.launch_phase(
        timestamp=time.Time("2024-05-16 00:00:00", scale="utc"),
        launch_site_latitude=50 * u.deg,
        launch_site_longitude=0 * u.deg,
        target_inclination=40 * u.deg,
        target_right_ascension_ascending_node=20 * u.deg,
    )

    assert launch_times is None


def test_final_approach_positive_cases():
    v_bar = sl_rendezvous.final_approach(
        semimajor_axis_target=6728 * u.km,
        distance=1 * u.km,
        time=60 * u.s,
        strategy=sl_enums.ClosingApproachStrategy.V_BAR_POS,
    )
    r_bar = sl_rendezvous.final_approach(
        semimajor_axis_target=6728 * u.km,
        distance=1 * u.km,
        time=60 * u.s,
        strategy=sl_enums.ClosingApproachStrategy.R_BAR_POS,
    )

    assert v_bar is not None
    assert r_bar is not None
    assert v_bar.to_value(u.m / u.s) > 0
    assert r_bar.to_value(u.m / u.s) > 0


def test_final_approach_invalid_strategy_returns_none():
    result = sl_rendezvous.final_approach(
        semimajor_axis_target=6728 * u.km,
        distance=1 * u.km,
        time=60 * u.s,
        strategy="v-bar",
    )

    assert result is None


def test_rendezvous():
    """:cite:`walter` EXAMPLE 8.6"""
    
    dtheta, dx = sl_rendezvous.phasing(
        semimajor_axis_chaser=(6378 + 340) * u.km, semimajor_axis_target=(6378 + 350) * u.km)
    
    theta_i, dv = sl_rendezvous.homing_phase(
        semimajor_axis_chaser=(6378 + 340) * u.km, semimajor_axis_target=(6378 + 350) * u.km)
    
    assert np.isclose(theta_i.to_value(u.rad) * (6378 + 350), 33.6, atol=1e-1)
    assert np.isclose(theta_i.to_value(u.deg), 0.286, atol=1e-3)
    assert np.isclose(dv.to_value(u.m / u.s), 5.72, atol=1e-2)
    
    dv: u.Quantity = sl_rendezvous.closing_phase(
        semimajor_axis_target=(6378 + 350) * u.km,
        distance=1 * u.km,
        strategy=sl_enums.ClosingApproachStrategy.V_BAR_POS,
        trajectory=sl_enums.ClosingApproachTrajectory.ELLIPTIC)
    
    assert np.isclose(dv.to_value(u.m / u.s) * 0.5, 0.286, atol=1e-3)
    
    dv: u.Quantity = sl_rendezvous.closing_phase(
        semimajor_axis_target=(6378 + 350) * u.km,
        distance=1 * u.km,
        strategy=sl_enums.ClosingApproachStrategy.V_BAR_POS,
        trajectory=sl_enums.ClosingApproachTrajectory.CYCLOIDAL)

    assert np.isclose(dv.to_value(u.m / u.s) * 0.5, 0.286 / 4.7, atol=1e-3)
