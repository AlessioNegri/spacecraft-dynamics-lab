import astropy.time as time
import astropy.units as u
import copy as cp
import numpy as np
import pytest
import typing as ty

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.maneuvers.impulsive as sl_impulsive
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.models.results as sl_results
import spacelab.models.rocket_motor as sl_rocket_motor
import spacelab.orbit.representation as sl_representation

rocket_motor = sl_rocket_motor.RocketMotor(
    specific_impulse=300 * u.s, thrust=400 * u.N, spacecraft_mass=2000 * u.kg, propellant_mass=0 * u.kg)

def test_hohmann_transfer_1():
    """:cite:`curtis` EXAMPLE 6.1"""
    
    r_p_1: u.Quantity = (6378 + 480) * u.km
    r_a_1: u.Quantity = (6378 + 800) * u.km
    
    oe_1 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_1 + r_a_1),
        eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one
    )
    
    r_p_2: u.Quantity = (6378 + 16000) * u.km
    r_a_2: u.Quantity = (6378 + 16000) * u.km
    
    oe_2 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_2 + r_a_2),
        eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one
    )
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        direction=sl_enums.HohmannDirection.PERICENTER_APOCENTER)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.7225, atol=1e-4)
    assert np.isclose(maneuver.delta_velocity_list[1].to_value(u.km / u.s), 1.3297, atol=1e-4)
    assert np.isclose(maneuver.delta_mass_list[0].to_value(u.kg) + maneuver.delta_mass_list[1].to_value(u.kg), 1291.3, atol=1e-1)
    assert np.isclose(maneuver.orbital_elements_list[0].specific_angular_momentum.to_value(u.km**2 / u.s), 64689.5, atol=1e-1)
    
def test_hohmann_transfer_2():
    """:cite:`curtis` EXAMPLE 6.2"""
    
    r: u.Quantity = np.array([-(6378 + 5000), 0, 0]) * u.km
    v: u.Quantity = np.array([0, -10, 0]) * u.km / u.s
    
    oe_1: sl_orbital_elements.OrbitalElements =\
        sl_representation.cartesian_to_keplerian(attractor=sl_bodies.Attractor.EARTH, position=r, velocity=v)
    
    r_p_2: u.Quantity = (6378 + 500) * u.km
    r_a_2: u.Quantity = (6378 + 500) * u.km
    
    oe_2 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_2 + r_a_2),
        eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one
    )
    
    direction = sl_enums.HohmannDirection.PERICENTER_APOCENTER
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        direction=direction)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s) + maneuver.delta_velocity_list[1].to_value(u.km / u.s), 5.749, atol=1e-3)
    assert np.isclose(maneuver.flight_time_list[0].to_value(u.s), 4339.5, atol=1e-1)
    assert np.isclose((maneuver.delta_mass_list[0].to_value(u.kg) + maneuver.delta_mass_list[1].to_value(u.kg)) / 2000, 0.85, atol=1e-2)

def test_hohmann_transfer_3():
    """:cite:`kluever` EXAMPLE 7.5"""
    
    rocket_motor = sl_rocket_motor.RocketMotor(specific_impulse=318 * u.s, thrust=400 * u.N, spacecraft_mass=3100 * u.kg)
    
    r_p_1: u.Quantity = (6378 + 580) * u.km
    r_a_1: u.Quantity = (6378 + 17350) * u.km
    
    oe_1 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_1 + r_a_1),
        eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one
    )
    
    r_p_2: u.Quantity = (6378 + 31000) * u.km
    r_a_2: u.Quantity = (6378 + 31000) * u.km
    
    oe_2 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_2 + r_a_2),
        eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one
    )
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        direction=sl_enums.HohmannDirection.PERICENTER_APOCENTER)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.4157, atol=1e-4)
    assert np.isclose(maneuver.delta_velocity_list[1].to_value(u.km / u.s), 1.4361, atol=1e-4)
    assert np.isclose(maneuver.delta_mass_list[0].to_value(u.kg), 386.88, atol=1e-2)
    assert np.isclose(maneuver.burn_time_list[0].to_value(u.minute), 50.3, atol=1e-1)

def test_hohmann_transfer_4():
    """:cite:`walter` EXAMPLE 8.3.2"""
    
    attractor = sl_bodies.Attractor.EARTH
    
    oe_1 = sl_orbital_elements.OrbitalElements(semimajor_axis=(6378 + 400) * u.km)
    oe_2 = sl_orbital_elements.OrbitalElements(semimajor_axis=(6378 + 10000) * u.km)
    
    direction = sl_enums.HohmannDirection.PERICENTER_APOCENTER
    
    maneuver_1: sl_results.ManeuverResult = sl_impulsive.hohmann_transfer(
        attractor=attractor,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        direction=direction)
    
    maneuver_2: sl_results.ManeuverResult = sl_impulsive.circular_hohmann_transfer(
        attractor=attractor,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        direction=direction)
    
    dv_1: ty.List[u.Quantity] = maneuver_1.delta_velocity_list
    dv_2: ty.List[u.Quantity] = maneuver_2.delta_velocity_list
    
    tof_1: float = maneuver_1.flight_time_list[0].to_value(u.s)
    tof_2: float = maneuver_2.flight_time_list[0].to_value(u.s)
    
    oe_1: sl_orbital_elements.OrbitalElements = maneuver_1.orbital_elements_list[0]
    oe_2: sl_orbital_elements.OrbitalElements = maneuver_2.orbital_elements_list[0]
    
    assert np.isclose(dv_1[0].to_value(u.km / u.s) + dv_1[1].to_value(u.km / u.s), dv_2[0].to_value(u.km / u.s), atol=1e-4)
    assert np.isclose(tof_1, tof_2, atol=1e-4)
    assert np.isclose(oe_1.specific_angular_momentum.to_value(), oe_2.specific_angular_momentum.to_value(), atol=1e-4)
    assert np.isclose(oe_1.semimajor_axis.to_value(u.km), oe_2.semimajor_axis.to_value(u.km), atol=1e-4)
    assert np.isclose(oe_1.eccentricity.to_value(u.one), oe_2.eccentricity.to_value(u.one), atol=1e-4)

def test_bi_elliptic_hohmann_transfer():
    """:cite:`curtis` EXAMPLE 6.3"""
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.bi_elliptic_hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=sl_orbital_elements.OrbitalElements(semimajor_axis=7000 * u.km),
        orbital_elements_2=sl_orbital_elements.OrbitalElements(semimajor_axis=105000 * u.km),
        apoapsis_radius=210000 * u.km)
    
    dv_tot: u.Quantity = maneuver.delta_velocity_list[0] + maneuver.delta_velocity_list[1] + maneuver.delta_velocity_list[2]
    dt_tot: u.Quantity = maneuver.flight_time_list[0] + maneuver.flight_time_list[1]
    
    assert np.isclose(dv_tot.to_value(u.km / u.s), 4.0285, atol=1e-4)
    assert np.isclose(dt_tot.to_value(u.s), 488870, atol=1e0)
    
    hohmann: sl_results.ManeuverResult = sl_impulsive.hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=sl_orbital_elements.OrbitalElements(semimajor_axis=7000 * u.km),
        orbital_elements_2=sl_orbital_elements.OrbitalElements(semimajor_axis=105000 * u.km),
        direction=sl_enums.HohmannDirection.PERICENTER_APOCENTER)
    
    assert np.isclose((hohmann.delta_velocity_list[0] + hohmann.delta_velocity_list[1]).to_value(u.km / u.s), 4.0463, atol=1e-4)
    assert np.isclose((hohmann.flight_time_list[0]).to_value(u.s), 65942, atol=1e0)
    
def test_phasing_maneuver_1():
    """:cite:`curtis` EXAMPLE 6.4"""
    
    r_p: u.Quantity = 6800 * u.km
    r_a: u.Quantity = 13600 * u.km
    
    oe = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=60116 * u.km**2 / u.s,
        semimajor_axis=0.5 * (r_p + r_a),
        eccentricity=(r_a - r_p) / (r_a + r_p) * u.one,
    )
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.phasing_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements=oe,
        true_anomaly_target=90 * u.deg,
        num_revolutions=1)
    
    dv_tot: u.Quantity = maneuver.delta_velocity_list[0] + maneuver.delta_velocity_list[1]
    
    assert np.isclose(dv_tot.to_value(u.km / u.s), 0.4970, atol=1e-4)
    
def test_phasing_maneuver_2():
    """:cite:`curtis` EXAMPLE 6.5"""
    
    mu: float = sl_bodies.BODIES[sl_bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
    
    r: u.Quantity = 42164 * u.km
    
    oe = sl_orbital_elements.OrbitalElements(
        specific_angular_momentum=np.sqrt(mu * r.to_value(u.km)) * u.km**2 / u.s,
        semimajor_axis=r
    )
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.phasing_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements=oe,
        true_anomaly_target=-12 * u.deg,
        num_revolutions=3)
    
    dv_tot: u.Quantity = maneuver.delta_velocity_list[0] + maneuver.delta_velocity_list[1]
    
    assert np.isclose(dv_tot.to_value(u.km / u.s), 0.02252, atol=1e-5)
    
def test_non_hohmann_transfer_1():
    """:cite:`curtis` EXAMPLE 6.6"""
    
    r_p_1: u.Quantity = 10000 * u.km
    r_a_1: u.Quantity = 20000 * u.km
    
    oe_1 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_1 + r_a_1),
        eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one,
        true_anomaly=150 * u.deg
    )
    
    oe_2 = sl_orbital_elements.OrbitalElements(semimajor_axis=6378 * u.km)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.non_hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.9896, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].specific_angular_momentum.to_value(u.km**2 / u.s), 62711, atol=1e-0)
    assert np.isclose(maneuver.orbital_elements_list[0].eccentricity.to_value(u.dimensionless_unscaled), 0.5469, atol=1e-4)
    assert np.isclose(maneuver.rocket_elevation_angle_list[0].to_value(u.deg), 123.3, atol=1e-1)

def test_non_hohmann_transfer_2():
    """:cite:`kluever` EXAMPLE 7.6"""
    
    oe_1 = sl_orbital_elements.OrbitalElements(semimajor_axis=2.5 * 6378 * u.km, true_anomaly=67.55 * u.deg)
    
    oe_2 = sl_orbital_elements.OrbitalElements(semimajor_axis=6 * 6378 * u.km, true_anomaly=139.47 * u.deg)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.non_hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 2.693, atol=1e-3)
    assert np.isclose(maneuver.rocket_elevation_angle_list[0].to_value(u.deg), 102.28, atol=1e-2)
    assert np.isclose(maneuver.flight_time_list[0].to_value(u.hour), 2.53, atol=1e-2)

def test_apse_line_rotation_from_eta():
    """:cite:`curtis` EXAMPLE 6.7"""
    
    r_p_1: u.Quantity = 8000 * u.km
    r_a_1: u.Quantity = 16000 * u.km
    
    oe_1 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_1 + r_a_1),
        eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one)
    
    r_p_2: u.Quantity = 7000 * u.km
    r_a_2: u.Quantity = 21000 * u.km
    
    oe_2 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_2 + r_a_2),
        eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one,
        argument_of_periapsis=25 * u.deg)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.apse_line_rotation_from_eta(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        apse_line_rotation_angle=25 * u.deg)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.503, atol=1e-3)
    assert np.isclose(maneuver.true_anomaly_list[0].to_value(u.deg), 153.04, atol=1e-2)
    assert np.isclose(maneuver.rocket_elevation_angle_list[0].to_value(u.deg), 91.28, atol=1e-2)
    
def test_apse_line_rotation_from_true_anomaly():
    """:cite:`curtis` EXAMPLE 6.8"""
    
    r_p: u.Quantity = 7000 * u.km
    r_a: u.Quantity = 17000 * u.km
    
    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p + r_a), eccentricity=(r_a - r_p) / (r_a + r_p) * u.one)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.apse_line_rotation_from_true_anomaly(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements=oe,
        delta_velocity=2 * u.km / u.s,
        flight_path_angle=60 * u.deg)
    
    assert np.isclose(maneuver.orbital_elements_list[0].eccentricity.to_value(u.one), 0.80883, atol=1e-5)
    assert np.isclose(maneuver.orbital_elements_list[0].calc_periapsis_radius().to_value(u.km), 6771.1, atol=1e-1)
    assert np.isclose(maneuver.orbital_elements_list[0].calc_apoapsis_radius().to_value(u.km), 64069, atol=1e-0)
    assert np.isclose(maneuver.orbital_elements_list[0].argument_of_periapsis.to_value(u.deg), -22.05, atol=1e-2)

def test_chase_maneuver():
    """:cite:`curtis` EXAMPLE 6.9"""
    
    r_p: u.Quantity = 8100 * u.km
    r_a: u.Quantity = 18900 * u.km
    
    oe = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p + r_a), eccentricity=(r_a - r_p) / (r_a + r_p) * u.one, true_anomaly=45 * u.deg)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.chase_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements=oe,
        true_anomaly_target=150 * u.deg,
        delta_time=time.TimeDelta(u.Quantity(1, u.hour)))
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 4.6755, atol=1e-4)
    assert np.isclose(maneuver.delta_velocity_list[1].to_value(u.km / u.s), 4.7540, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].specific_angular_momentum.to_value(u.km**2 / u.s), 76167, atol=1e-0)
    assert np.isclose(maneuver.orbital_elements_list[0].eccentricity.to_value(u.dimensionless_unscaled), 0.8500, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].semimajor_axis.to_value(u.km), 52445, atol=1e-0)
    assert np.isclose(maneuver.orbital_elements_list[0].true_anomaly.to_value(u.deg), 319.52, atol=1e-2)

def test_plane_change_maneuver_from_dihedral_angle_1():
    """:cite:`curtis` EXAMPLE 6.11"""
    
    r_p_1: u.Quantity = 6678 * u.km
    r_a_1: u.Quantity = 42164 * u.km
    
    oe_1 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_1 + r_a_1),
        eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one,
        inclination=28 * u.deg,
        true_anomaly=180 * u.deg)
    
    oe_2 = sl_orbital_elements.OrbitalElements(semimajor_axis=42164 * u.km)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.plane_change_maneuver_from_dihedral_angle(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        dihedral_angle=oe_2.inclination - oe_1.inclination)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.8191, atol=1e-4)
    
    oe_1 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=6678 * u.km, inclination=28 * u.deg, true_anomaly=180 * u.deg)
    
    r_p_2: u.Quantity = 6678 * u.km
    r_a_2: u.Quantity = 42164 * u.km
    
    oe_2 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_2 + r_a_2), eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.plane_change_maneuver_from_dihedral_angle(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        dihedral_angle=oe_2.inclination - oe_1.inclination)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 4.9239, atol=1e-4)

def test_plane_change_maneuver_from_dihedral_angle_2():
    """:cite:`curtis` EXAMPLE 6.13"""
    
    r_p_1: u.Quantity = (500 + 6378) * u.km
    r_a_1: u.Quantity = (10000 + 6378) * u.km
    
    oe_1 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_1 + r_a_1),
        eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one,
        inclination=15 * u.deg,
        true_anomaly=120 * u.deg)
    
    r_p_2: u.Quantity = (500 + 6378) * u.km
    r_a_2: u.Quantity = (10000 + 6378) * u.km
    
    oe_2 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (r_p_2 + r_a_2),
        eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one,
        true_anomaly=120 * u.deg)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.plane_change_maneuver_from_dihedral_angle(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        dihedral_angle=oe_2.inclination - oe_1.inclination)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.3325, atol=1e-4)
    
    oe_1.true_anomaly = 300 * u.deg
    oe_2.true_anomaly = 300 * u.deg
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.plane_change_maneuver_from_dihedral_angle(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        dihedral_angle=oe_2.inclination - oe_1.inclination)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 2.0165, atol=1e-4)

def test_plane_change_maneuver_from_raan_and_inclination():
    """UNIVERSITY PROJECT"""
    
    oe_1 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=10048 * u.km,
        eccentricity=0.1983 * u.dimensionless_unscaled,
        inclination=2.7794 * u.rad,
        right_ascension_of_ascending_node=1.3915 * u.rad,
        argument_of_periapsis=2.8956 * u.rad,
        true_anomaly=1.3078 * u.rad
    )
    
    oe_2 = sl_orbital_elements.OrbitalElements(
        semimajor_axis=10048 * u.km,
        eccentricity=0.1983 * u.dimensionless_unscaled,
        inclination=0.444 * u.rad,
        right_ascension_of_ascending_node=2.5486 * u.rad,
        argument_of_periapsis=3.1052 * u.rad,
        true_anomaly=2.0233 * u.rad
    )
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.plane_change_maneuver_from_raan_and_inclination(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 9.9574, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].argument_of_periapsis.to_value(u.rad), 3.0316, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].true_anomaly.to_value(u.rad), 2.7026, atol=1e-4)

def test_inclination_change_maneuver():
    """:cite:`kluever` EXAMPLE 7.7"""
    
    oe_1 = sl_orbital_elements.OrbitalElements(semimajor_axis=(6378 + 20180) * u.km, inclination=41 * u.deg)
    
    oe_2 = sl_orbital_elements.OrbitalElements(semimajor_axis=(6378 + 20180) * u.km, inclination=55 * u.deg)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.inclination_change_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.944, atol=1e-3)

def test_one_impulse_maneuver():
    """:cite:`walter` EXAMPLE 8.1.6"""
    
    oe_LEO = sl_orbital_elements.OrbitalElements(
        semimajor_axis=6578.14 * u.km, inclination=28 * u.deg, right_ascension_of_ascending_node=180 * u.deg)
    
    oe_GEO = sl_orbital_elements.OrbitalElements(
        semimajor_axis=42166 * u.km, inclination=3 * u.deg, right_ascension_of_ascending_node=280 * u.deg)
    
    oe_GTO = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (6578.14 + 42166) * u.km,
        eccentricity=(42166 - 6578.14) / (42166 + 6578.14) * u.one,
        inclination=3 * u.deg,
        right_ascension_of_ascending_node=180 * u.deg)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.one_impulse_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_LEO,
        orbital_elements_2=oe_GTO)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 4.578, atol=1e-3)
    
    oe_GTO.inclination = 28 * u.deg
    oe_GTO.right_ascension_of_ascending_node = 280 * u.deg
    oe_GTO.true_anomaly = 180 * u.deg
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.one_impulse_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_GTO,
        orbital_elements_2=oe_GEO)
        
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.762, atol=1e-3)

def test_raan_change_maneuver():
    """:cite:`walter` EXAMPLE 8.1.6"""
    
    oe_GEO = sl_orbital_elements.OrbitalElements(
        semimajor_axis=42166 * u.km, inclination=3 * u.deg, right_ascension_of_ascending_node=280 * u.deg)
    
    oe_GTO = sl_orbital_elements.OrbitalElements(
        semimajor_axis=0.5 * (6578.14 + 42166) * u.km,
        eccentricity=(42166 - 6578.14) / (42166 + 6578.14) * u.one,
        inclination=3 * u.deg,
        right_ascension_of_ascending_node=180 * u.deg,
        true_anomaly=180 * u.deg)
    
    maneuver: sl_results.ManeuverResult = sl_impulsive.raan_change_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_GTO,
        orbital_elements_2=oe_GEO)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.128, atol=1e-3)
    
    oe_GTO.inclination = 28 * u.deg
    
    maneuver: sl_bodies.ManeuverResult = sl_impulsive.raan_change_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_GTO,
        orbital_elements_2=oe_GEO)
        
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.149, atol=1e-3)
    
    oe_GEO_minus: sl_orbital_elements.OrbitalElements = cp.deepcopy(oe_GEO)
    
    oe_GEO_minus.right_ascension_of_ascending_node = 180 * u.deg
        
    maneuver: sl_results.ManeuverResult = sl_impulsive.raan_change_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_GEO_minus,
        orbital_elements_2=oe_GEO)
        
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.247, atol=1e-3)

def test_lambert():
    """:cite:`curtis` EXAMPLE 5.2"""
    
    v_1, v_2, ecc, _ = sl_impulsive.lambert(
        attractor=sl_bodies.Attractor.EARTH,
        departure_position=np.array([5_000, 10_000, 2_100]) * u.km,
        arrival_position=np.array([-14_600, 2_500, 7_000]) * u.km,
        delta_time=time.TimeDelta(u.Quantity(1, u.hour)))
    
    assert np.isclose(v_1[0].to_value(u.km / u.s), -5.9925, atol=1e-4)
    assert np.isclose(v_1[1].to_value(u.km / u.s), 1.9254, atol=1e-4)
    assert np.isclose(v_1[2].to_value(u.km / u.s), 3.2456, atol=1e-4)
    
    assert np.isclose(v_2[0].to_value(u.km / u.s), -3.3125, atol=1e-4)
    assert np.isclose(v_2[1].to_value(u.km / u.s), -4.1966, atol=1e-4)
    assert np.isclose(v_2[2].to_value(u.km / u.s), -0.38529, atol=1e-5)
    
    assert np.isclose(ecc.to_value(), 0.4335, atol=1e-4)

def test_super_synchronous_transfer():
    """:cite:`walter` EXAMPLE 8.4.3"""
    
    ssto = sl_orbital_elements.OrbitalElements(
        inclination=25.7 * u.deg,
        right_ascension_of_ascending_node=173.6 * u.deg,
        argument_of_periapsis=179.98 * u.deg)
    
    ssto.update_from_periapsis_apoapsis(periapsis_radius=6563.1 * u.km, apoapsis_radius=129_885 * u.km)
    
    dv_1, dv_2, dv_3 = sl_impulsive.super_synchronous_transfer(
        attractor=sl_bodies.Attractor.EARTH, leo_inclination=28.5 * u.deg, geo_inclination=0.6 * u.deg, ssto=ssto)
    
    assert np.isclose(dv_1.to_value(u.km / u.s), 2.993, atol=1e-3)
    assert np.isclose(dv_2.to_value(u.km / u.s), 0.770, atol=1e-3)
    assert np.isclose(dv_3.to_value(u.km / u.s), 0.703, atol=1e-3)

@pytest.mark.parametrize(
    ("attractor", "rocket_motor", "direction"),
    [
        pytest.param("Earth", rocket_motor, sl_enums.HohmannDirection.PERICENTER_APOCENTER, id="invalid-attractor"),
        pytest.param(sl_bodies.Attractor.EARTH, object(), sl_enums.HohmannDirection.PERICENTER_APOCENTER, id="invalid-rocket-motor"),
        pytest.param(sl_bodies.Attractor.EARTH, rocket_motor, "outward", id="invalid-direction"),
    ],
)
def test_hohmann_transfer_invalid_inputs_return_none(attractor, rocket_motor, direction):
    oe_1 = sl_orbital_elements.OrbitalElements(semimajor_axis=7000 * u.km)
    oe_2 = sl_orbital_elements.OrbitalElements(semimajor_axis=8000 * u.km)

    result = sl_impulsive.hohmann_transfer(
        attractor=attractor,
        rocket_motor=rocket_motor,
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        direction=direction,
    )

    assert result is None

def test_hohmann_transfer_apocenter_pericenter_inward_direction():
    oe_1 = sl_orbital_elements.OrbitalElements(semimajor_axis=8000 * u.km)
    oe_2 = sl_orbital_elements.OrbitalElements(semimajor_axis=7000 * u.km)

    inward = sl_impulsive.hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_1,
        orbital_elements_2=oe_2,
        direction=sl_enums.HohmannDirection.APOCENTER_PERICENTER,
    )

    outward = sl_impulsive.hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=oe_2,
        orbital_elements_2=oe_1,
        direction=sl_enums.HohmannDirection.PERICENTER_APOCENTER,
    )

    inward_dv = sum(delta.to_value(u.km / u.s) for delta in inward.delta_velocity_list)
    outward_dv = sum(delta.to_value(u.km / u.s) for delta in outward.delta_velocity_list)

    assert inward is not None
    assert outward is not None
    assert np.isclose(inward_dv, outward_dv, atol=1e-4)

def test_bielliptic_invalid_apoapsis_unit_returns_none():
    result = sl_impulsive.bi_elliptic_hohmann_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        orbital_elements_1=sl_orbital_elements.OrbitalElements(semimajor_axis=7000 * u.km),
        orbital_elements_2=sl_orbital_elements.OrbitalElements(semimajor_axis=105000 * u.km),
        apoapsis_radius=210000 * u.s,
    )

    assert result is None

def test_lambert_invalid_position_shape_returns_none():
    result = sl_impulsive.lambert(
        attractor=sl_bodies.Attractor.EARTH,
        departure_position=np.array([5000, 10000]) * u.km,
        arrival_position=np.array([-14600, 2500, 7000]) * u.km,
        delta_time=time.TimeDelta(1 * u.hour),
    )

    assert result is None
