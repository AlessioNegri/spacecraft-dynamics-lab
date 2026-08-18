import pytest

import astropy.time as time
import astropy.units as u
import copy
import numpy as np

import astro.bodies as bd
import astro.orbit_3d as o3d
import astro.orbital_maneuvers as om
import astro.two_body_problem as tbp

rocket_motor: om.RocketMotor = om.RocketMotor(specific_impulse=300 * u.s,
                                              thrust=400 * u.N,
                                              spacecraft_mass=2000 * u.kg,
                                              propellant_mass=0 * u.kg)

def test_hohmann_transfer_1():
    """EXAMPLE 6.1"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=400 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_p_1: u.Quantity = (6378 + 480) * u.km
    r_a_1: u.Quantity = (6378 + 800) * u.km
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=0 * u.km**2 / u.s,
        semimajor_axis=0.5 * (r_p_1 + r_a_1),
        eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    r_p_2: u.Quantity = (6378 + 16000) * u.km
    r_a_2: u.Quantity = (6378 + 16000) * u.km
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=0 * u.km**2 / u.s,
        semimajor_axis=0.5 * (r_p_2 + r_a_2),
        eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    direction: om.HohmannDirection = om.HohmannDirection.PERICENTER_APOCENTER
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements_1=oe_1,
                                                                       orbital_elements_2=oe_2,
                                                                       direction=direction)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.7225, atol=1e-4)
    assert np.isclose(maneuver.delta_velocity_list[1].to_value(u.km / u.s), 1.3297, atol=1e-4)
    assert np.isclose(maneuver.delta_mass_list[0].to_value(u.kg) + maneuver.delta_mass_list[1].to_value(u.kg), 1291.3, atol=1e-1)
    assert np.isclose(maneuver.orbital_elements_list[0].specific_angular_momentum.to_value(u.km**2 / u.s), 64689.5, atol=1e-1)
    
def test_hohmann_transfer_2():
    """EXAMPLE 6.2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=400 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r: u.Quantity = np.array([-(6378 + 5000), 0, 0]) * u.km
    v: u.Quantity = np.array([0, -10, 0]) * u.km / u.s
    
    oe_1: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r, velocity=v)
    
    r_p_2: u.Quantity = (6378 + 500) * u.km
    r_a_2: u.Quantity = (6378 + 500) * u.km
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=0 * u.km**2 / u.s,
        semimajor_axis=0.5 * (r_p_2 + r_a_2),
        eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    direction: om.HohmannDirection = om.HohmannDirection.PERICENTER_APOCENTER
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements_1=oe_1,
                                                                       orbital_elements_2=oe_2,
                                                                       direction=direction)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s) + maneuver.delta_velocity_list[1].to_value(u.km / u.s), 5.749, atol=1e-3)
    assert np.isclose(maneuver.flight_time_list[0].to_value(u.s), 4339.5, atol=1e-1)
    assert np.isclose((maneuver.delta_mass_list[0].to_value(u.kg) + maneuver.delta_mass_list[1].to_value(u.kg)) / 2000, 0.85, atol=1e-2)

def test_hohmann_transfer_3():
    """EXAMPLE 7.5 - BOOK 2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=318 * u.s,
        thrust=400 * u.N,
        spacecraft_mass=3100 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_p_1: u.Quantity = (6378 + 580) * u.km
    r_a_1: u.Quantity = (6378 + 17350) * u.km
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=0 * u.km**2 / u.s,
        semimajor_axis=0.5 * (r_p_1 + r_a_1),
        eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    r_p_2: u.Quantity = (6378 + 31000) * u.km
    r_a_2: u.Quantity = (6378 + 31000) * u.km
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=0 * u.km**2 / u.s,
        semimajor_axis=0.5 * (r_p_2 + r_a_2),
        eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    direction: om.HohmannDirection = om.HohmannDirection.PERICENTER_APOCENTER
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements_1=oe_1,
                                                                       orbital_elements_2=oe_2,
                                                                       direction=direction)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.4157, atol=1e-4)
    assert np.isclose(maneuver.delta_velocity_list[1].to_value(u.km / u.s), 1.4361, atol=1e-4)
    assert np.isclose(maneuver.delta_mass_list[0].to_value(u.kg), 386.88, atol=1e-2)
    assert np.isclose(maneuver.burn_time_list[0].to_value(u.minute), 50.3, atol=1e-1)

def test_hohmann_transfer_4():
    """EXAMPLE 8.3.2 - BOOK 4"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=(6378 + 400) * u.km)
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=(6378 + 10000) * u.km)
    
    direction: om.HohmannDirection = om.HohmannDirection.PERICENTER_APOCENTER
    
    maneuver_1: om.ManeuverResult = om.OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                         rocket_motor=copy.deepcopy(rocket_motor),
                                                                         orbital_elements_1=oe_1,
                                                                         orbital_elements_2=oe_2,
                                                                         direction=direction)
    
    maneuver_2: om.ManeuverResult = om.OrbitalManeuvers.circular_hohmann_transfer(attractor=attractor,
                                                                                  rocket_motor=copy.deepcopy(rocket_motor),
                                                                                  orbital_elements_1=oe_1,
                                                                                  orbital_elements_2=oe_2,
                                                                                  direction=direction)
    
    dv_1: list = maneuver_1.delta_velocity_list
    dv_2: list = maneuver_2.delta_velocity_list
    
    tof_1: float = maneuver_1.flight_time_list[0].to_value(u.s)
    tof_2: float = maneuver_2.flight_time_list[0].to_value(u.s)
    
    oe_1: o3d.OrbitalElements = maneuver_1.orbital_elements_list[0]
    oe_2: o3d.OrbitalElements = maneuver_2.orbital_elements_list[0]
    
    assert np.isclose(dv_1[0].to_value(u.km / u.s) + dv_1[1].to_value(u.km / u.s), dv_2[0].to_value(u.km / u.s), atol=1e-4)
    assert np.isclose(tof_1, tof_2, atol=1e-4)
    assert np.isclose(oe_1.specific_angular_momentum.to_value(), oe_2.specific_angular_momentum.to_value(), atol=1e-4)
    assert np.isclose(oe_1.semimajor_axis.to_value(u.km), oe_2.semimajor_axis.to_value(u.km), atol=1e-4)
    assert np.isclose(oe_1.eccentricity.to_value(u.one), oe_2.eccentricity.to_value(u.one), atol=1e-4)

def test_bi_elliptic_hohmann_transfer():
    """EXAMPLE 6.3"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=400 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_1: u.Quantity = 7000 * u.km
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=0 * u.km**2 / u.s,
        semimajor_axis=r_1,
        eccentricity=0 * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    r_2: u.Quantity = 105000 * u.km
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=0 * u.km**2 / u.s,
        semimajor_axis=r_2,
        eccentricity=0 * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    r_3: u.Quantity = 210000 * u.km
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.bi_elliptic_hohmann_transfer(attractor=attractor,
                                                                                   rocket_motor=rocket_motor,
                                                                                   orbital_elements_1=oe_1,
                                                                                   orbital_elements_2=oe_2,
                                                                                   apoapsis_radius=r_3)
    
    dv_tot: u.Quantity = maneuver.delta_velocity_list[0] + maneuver.delta_velocity_list[1] + maneuver.delta_velocity_list[2]
    dt_tot: u.Quantity = maneuver.flight_time_list[0] + maneuver.flight_time_list[1]
    
    assert np.isclose(dv_tot.to_value(u.km / u.s), 4.0285, atol=1e-4)
    assert np.isclose(dt_tot.to_value(u.s), 488870, atol=1e0)
    
    hohmann: om.ManeuverResult = om.OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                      rocket_motor=rocket_motor,
                                                                      orbital_elements_1=oe_1,
                                                                      orbital_elements_2=oe_2,
                                                                      direction=om.HohmannDirection.PERICENTER_APOCENTER)
    
    assert np.isclose((hohmann.delta_velocity_list[0] + hohmann.delta_velocity_list[1]).to_value(u.km / u.s), 4.0463, atol=1e-4)
    assert np.isclose((hohmann.flight_time_list[0]).to_value(u.s), 65942, atol=1e0)
    
def test_phasing_maneuver_1():
    """EXAMPLE 6.4"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=0 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_p: u.Quantity = 6800 * u.km
    r_a: u.Quantity = 13600 * u.km
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=60116 * u.km**2 / u.s,
        semimajor_axis=0.5 * (r_p + r_a),
        eccentricity=(r_a - r_p) / (r_a + r_p) * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    nu_target: u.Quantity = 90 * u.deg
    
    num_revolutions: int = 1
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.phasing_maneuver(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements=oe,
                                                                       true_anomaly_target=nu_target,
                                                                       num_revolutions=num_revolutions)
    
    dv_tot: u.Quantity = maneuver.delta_velocity_list[0] + maneuver.delta_velocity_list[1]
    
    assert np.isclose(dv_tot.to_value(u.km / u.s), 0.4970, atol=1e-4)
    
def test_phasing_maneuver_2():
    """EXAMPLE 6.5"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=0 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r: u.Quantity = 42164 * u.km
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=np.sqrt(mu * r.to_value(u.km)) * u.km**2 / u.s,
        semimajor_axis=r,
        eccentricity=0 * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    nu_target: u.Quantity = -12 * u.deg
    
    num_revolutions: int = 3
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.phasing_maneuver(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements=oe,
                                                                       true_anomaly_target=nu_target,
                                                                       num_revolutions=num_revolutions)
    
    dv_tot: u.Quantity = maneuver.delta_velocity_list[0] + maneuver.delta_velocity_list[1]
    
    assert np.isclose(dv_tot.to_value(u.km / u.s), 0.02252, atol=1e-5)
    
def test_non_hohmann_transfer_1():
    """EXAMPLE 6.6"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=400 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_p_1: u.Quantity = 10000 * u.km
    r_a_1: u.Quantity = 20000 * u.km
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=0 * u.km**2 / u.s,
        semimajor_axis=0.5 * (r_p_1 + r_a_1),
        eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=150 * u.deg
    )
    
    r_2: u.Quantity = 6378 * u.km
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(
        specific_angular_momentum=0 * u.km**2 / u.s,
        semimajor_axis=r_2,
        eccentricity=0 * u.one,
        inclination=0 * u.deg,
        right_ascension_of_ascending_node=0 * u.deg,
        argument_of_periapsis=0 * u.deg,
        true_anomaly=0 * u.deg
    )
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.non_hohmann_transfer(attractor=attractor,
                                                                           rocket_motor=rocket_motor,
                                                                           orbital_elements_1=oe_1,
                                                                           orbital_elements_2=oe_2)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.9896, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].specific_angular_momentum.to_value(u.km**2 / u.s), 62711, atol=1e-0)
    assert np.isclose(maneuver.orbital_elements_list[0].eccentricity.to_value(u.dimensionless_unscaled), 0.5469, atol=1e-4)
    assert np.isclose(maneuver.rocket_elevation_angle_list[0].to_value(u.deg), 123.3, atol=1e-1)

def test_non_hohmann_transfer_2():
    """EXAMPLE 6.6"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=400 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=2.5 * 6378 * u.km, true_anomaly=67.55 * u.deg)
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=6 * 6378 * u.km, true_anomaly=139.47 * u.deg)
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.non_hohmann_transfer(attractor=attractor,
                                                                           rocket_motor=rocket_motor,
                                                                           orbital_elements_1=oe_1,
                                                                           orbital_elements_2=oe_2)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 2.693, atol=1e-3)
    assert np.isclose(maneuver.rocket_elevation_angle_list[0].to_value(u.deg), 102.28, atol=1e-2)
    assert np.isclose(maneuver.flight_time_list[0].to_value(u.hour), 2.53, atol=1e-2)

def test_apse_line_rotation_from_eta():
    """EXAMPLE 6.7"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=400 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_p_1: u.Quantity = 8000 * u.km
    r_a_1: u.Quantity = 16000 * u.km
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (r_p_1 + r_a_1),
                                                    eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one)
    
    r_p_2: u.Quantity = 7000 * u.km
    r_a_2: u.Quantity = 21000 * u.km
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (r_p_2 + r_a_2),
                                                    eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one,
                                                    argument_of_periapsis=25 * u.deg)
    
    eta: u.Quantity = 25 * u.deg
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.apse_line_rotation_from_eta(attractor=attractor,
                                                                                  rocket_motor=rocket_motor,
                                                                                  orbital_elements_1=oe_1,
                                                                                  orbital_elements_2=oe_2,
                                                                                  eta=eta)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.503, atol=1e-3)
    assert np.isclose(maneuver.true_anomaly_list[0].to_value(u.deg), 153.04, atol=1e-2)
    assert np.isclose(maneuver.rocket_elevation_angle_list[0].to_value(u.deg), 91.28, atol=1e-2)
    
def test_apse_line_rotation_from_true_anomaly():
    """EXAMPLE 6.8"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=400 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_p: u.Quantity = 7000 * u.km
    r_a: u.Quantity = 17000 * u.km
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (r_p + r_a),
                                                  eccentricity=(r_a - r_p) / (r_a + r_p) * u.one)
    
    dv: u.Quantity = 2 * u.km / u.s
    fpa: u.Quantity = 60 * u.deg
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.apse_line_rotation_from_true_anomaly(attractor=attractor,
                                                                                           rocket_motor=rocket_motor,
                                                                                           orbital_elements=oe,
                                                                                           delta_velocity=dv,
                                                                                           flight_path_angle=fpa)
    
    assert np.isclose(maneuver.orbital_elements_list[0].eccentricity.to_value(u.one), 0.80883, atol=1e-5)
    assert np.isclose(maneuver.orbital_elements_list[0].calc_perigee_radius().to_value(u.km), 6771.1, atol=1e-1)
    assert np.isclose(maneuver.orbital_elements_list[0].calc_apogee_radius().to_value(u.km), 64069, atol=1e-0)
    assert np.isclose(maneuver.orbital_elements_list[0].argument_of_periapsis.to_value(u.deg), -22.05, atol=1e-2)

def test_chase_maneuver():
    """EXAMPLE 6.9"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=400 * u.N,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_p: u.Quantity = 8100 * u.km
    r_a: u.Quantity = 18900 * u.km
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (r_p + r_a),
                                                  eccentricity=(r_a - r_p) / (r_a + r_p) * u.one,
                                                  true_anomaly=45 * u.deg)
    
    ta_T: u.Quantity = 150 * u.deg
    
    dt: time.TimeDelta = time.TimeDelta(u.Quantity(1, u.hour))
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.chase_maneuver(attractor=attractor,
                                                                     rocket_motor=rocket_motor,
                                                                     orbital_elements=oe,
                                                                     true_anomaly_target=ta_T,
                                                                     delta_time=dt)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 4.6755, atol=1e-4)
    assert np.isclose(maneuver.delta_velocity_list[1].to_value(u.km / u.s), 4.7540, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].specific_angular_momentum.to_value(u.km**2 / u.s), 76167, atol=1e-0)
    assert np.isclose(maneuver.orbital_elements_list[0].eccentricity.to_value(u.dimensionless_unscaled), 0.8500, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].semimajor_axis.to_value(u.km), 52445, atol=1e-0)
    assert np.isclose(maneuver.orbital_elements_list[0].true_anomaly.to_value(u.deg), 319.52, atol=1e-2)

def test_launch_azimuth():
    """EXAMPLE 6.10"""
    
    launch_site_latitude: u.Quantity = 34.5 * u.deg
    
    target_orbit_inclination: u.Quantity = 98.43 * u.deg
    
    launch_azimuth: u.Quantity = om.OrbitalManeuvers.launch_azimuth(launch_site_latitude=launch_site_latitude,
                                                                    target_inclination=target_orbit_inclination)
    
    assert np.isclose(launch_azimuth.to_value(u.deg), 349.8, atol=1e-1)

def test_one_impulse_maneuver():
    """EXAMPLE 8.1.6 - BOOK 4"""
    
    oe_LEO: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=6578.14 * u.km,
                                                      inclination=28 * u.deg,
                                                      right_ascension_of_ascending_node=180 * u.deg)
    
    oe_GEO: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=42166 * u.km,
                                                      inclination=3 * u.deg,
                                                      right_ascension_of_ascending_node=280 * u.deg)
    
    oe_GTO: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (6578.14 + 42166) * u.km,
                                                      eccentricity=(42166 - 6578.14) / (42166 + 6578.14) * u.one,
                                                      inclination=3 * u.deg,
                                                      right_ascension_of_ascending_node=180 * u.deg)
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.one_impulse_maneuver(attractor=bd.Attractor.EARTH,
                                                                           rocket_motor=rocket_motor,
                                                                           orbital_elements_1=oe_LEO,
                                                                           orbital_elements_2=oe_GTO)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 4.578, atol=1e-3)
    
    oe_GTO.inclination = 28 * u.deg
    oe_GTO.right_ascension_of_ascending_node = 280 * u.deg
    oe_GTO.true_anomaly = 180 * u.deg
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.one_impulse_maneuver(attractor=bd.Attractor.EARTH,
                                                                           rocket_motor=rocket_motor,
                                                                           orbital_elements_1=oe_GTO,
                                                                           orbital_elements_2=oe_GEO)
        
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.762, atol=1e-3)

def test_inclination_change_maneuver():
    """EXAMPLE 7.7 - BOOK 2"""
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=(6378 + 20180) * u.km, inclination=41 * u.deg)
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=(6378 + 20180) * u.km, inclination=55 * u.deg)
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.inclination_change_maneuver(attractor=bd.Attractor.EARTH,
                                                                                  rocket_motor=rocket_motor,
                                                                                  orbital_elements_1=oe_1,
                                                                                  orbital_elements_2=oe_2)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.944, atol=1e-3)

def test_raan_change_maneuver():
    """EXAMPLE 8.1.6 - BOOK 4"""
    
    oe_GEO: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=42166 * u.km,
                                                      inclination=3 * u.deg,
                                                      right_ascension_of_ascending_node=280 * u.deg)
    
    oe_GTO: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (6578.14 + 42166) * u.km,
                                                      eccentricity=(42166 - 6578.14) / (42166 + 6578.14) * u.one,
                                                      inclination=3 * u.deg,
                                                      right_ascension_of_ascending_node=180 * u.deg,
                                                      true_anomaly=180 * u.deg)
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.raan_change_maneuver(attractor=bd.Attractor.EARTH,
                                                                           rocket_motor=rocket_motor,
                                                                           orbital_elements_1=oe_GTO,
                                                                           orbital_elements_2=oe_GEO)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.128, atol=1e-3)
    
    oe_GTO.inclination = 28 * u.deg
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.raan_change_maneuver(attractor=bd.Attractor.EARTH,
                                                                           rocket_motor=rocket_motor,
                                                                           orbital_elements_1=oe_GTO,
                                                                           orbital_elements_2=oe_GEO)
        
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.149, atol=1e-3)
    
    oe_GEO_minus: o3d.OrbitalElements = copy.deepcopy(oe_GEO)
    
    oe_GEO_minus.right_ascension_of_ascending_node = 180 * u.deg
        
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.raan_change_maneuver(attractor=bd.Attractor.EARTH,
                                                                            rocket_motor=rocket_motor,
                                                                            orbital_elements_1=oe_GEO_minus,
                                                                            orbital_elements_2=oe_GEO)
        
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 0.247, atol=1e-3)
    
def test_plane_change_maneuver_from_dihedral_angle_1():
    """EXAMPLE 6.11"""
    
    r_p_1: u.Quantity = 6678 * u.km
    r_a_1: u.Quantity = 42164 * u.km
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (r_p_1 + r_a_1),
                                                    eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one,
                                                    inclination=28 * u.deg,
                                                    true_anomaly=180 * u.deg)
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=42164 * u.km)
    
    dihedral_angle: u.Quantity = oe_2.inclination - oe_1.inclination
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.plane_change_maneuver_from_dihedral_angle(attractor=bd.Attractor.EARTH,
                                                                                                rocket_motor=rocket_motor,
                                                                                                orbital_elements_1=oe_1,
                                                                                                orbital_elements_2=oe_2,
                                                                                                dihedral_angle=dihedral_angle)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.8191, atol=1e-4)
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=6678 * u.km,
                                                    inclination=28 * u.deg,
                                                    true_anomaly=180 * u.deg)
    
    r_p_2: u.Quantity = 6678 * u.km
    r_a_2: u.Quantity = 42164 * u.km
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (r_p_2 + r_a_2),
                                                    eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one)
    
    dihedral_angle: u.Quantity = oe_2.inclination - oe_1.inclination
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.plane_change_maneuver_from_dihedral_angle(attractor=bd.Attractor.EARTH,
                                                                                                rocket_motor=rocket_motor,
                                                                                                orbital_elements_1=oe_1,
                                                                                                orbital_elements_2=oe_2,
                                                                                                dihedral_angle=dihedral_angle)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 4.9239, atol=1e-4)

def test_plane_change_maneuver_from_dihedral_angle_2():
    """EXAMPLE 6.13"""
    
    r_p_1: u.Quantity = (500 + 6378) * u.km
    r_a_1: u.Quantity = (10000 + 6378) * u.km
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (r_p_1 + r_a_1),
                                                    eccentricity=(r_a_1 - r_p_1) / (r_a_1 + r_p_1) * u.one,
                                                    inclination=15 * u.deg,
                                                    true_anomaly=120 * u.deg)
    
    r_p_2: u.Quantity = (500 + 6378) * u.km
    r_a_2: u.Quantity = (10000 + 6378) * u.km
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(semimajor_axis=0.5 * (r_p_2 + r_a_2),
                                                    eccentricity=(r_a_2 - r_p_2) / (r_a_2 + r_p_2) * u.one,
                                                    true_anomaly=120 * u.deg)
    
    dihedral_angle: u.Quantity = oe_2.inclination - oe_1.inclination
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.plane_change_maneuver_from_dihedral_angle(attractor=bd.Attractor.EARTH,
                                                                                                rocket_motor=rocket_motor,
                                                                                                orbital_elements_1=oe_1,
                                                                                                orbital_elements_2=oe_2,
                                                                                                dihedral_angle=dihedral_angle)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 1.3325, atol=1e-4)
    
    oe_1.true_anomaly = 300 * u.deg
    oe_2.true_anomaly = 300 * u.deg
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.plane_change_maneuver_from_dihedral_angle(attractor=bd.Attractor.EARTH,
                                                                                                rocket_motor=rocket_motor,
                                                                                                orbital_elements_1=oe_1,
                                                                                                orbital_elements_2=oe_2,
                                                                                                dihedral_angle=dihedral_angle)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 2.0165, atol=1e-4)

def test_plane_change_maneuver_from_raan_and_inclination():
    """PROJECT"""
    
    oe_1: o3d.OrbitalElements = o3d.OrbitalElements(
        semimajor_axis=10048 * u.km,
        eccentricity=0.1983 * u.dimensionless_unscaled,
        inclination=2.7794 * u.rad,
        right_ascension_of_ascending_node=1.3915 * u.rad,
        argument_of_periapsis=2.8956 * u.rad,
        true_anomaly=1.3078 * u.rad
    )
    
    oe_2: o3d.OrbitalElements = o3d.OrbitalElements(
        semimajor_axis=10048 * u.km,
        eccentricity=0.1983 * u.dimensionless_unscaled,
        inclination=0.444 * u.rad,
        right_ascension_of_ascending_node=2.5486 * u.rad,
        argument_of_periapsis=3.1052 * u.rad,
        true_anomaly=2.0233 * u.rad
    )
    
    maneuver: om.ManeuverResult = om.OrbitalManeuvers.plane_change_maneuver_from_raan_and_inclination(attractor=bd.Attractor.EARTH,
                                                                                                      rocket_motor=rocket_motor,
                                                                                                      orbital_elements_1=oe_1,
                                                                                                      orbital_elements_2=oe_2)
    
    assert np.isclose(maneuver.delta_velocity_list[0].to_value(u.km / u.s), 9.9574, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].argument_of_periapsis.to_value(u.rad), 3.0316, atol=1e-4)
    assert np.isclose(maneuver.orbital_elements_list[0].true_anomaly.to_value(u.rad), 2.7026, atol=1e-4)

def test_lambert():
    """EXAMPLE 5.2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_1: u.Quantity = np.array([5_000, 10_000, 2_100]) * u.km
    r_2: u.Quantity = np.array([-14_600, 2_500, 7_000]) * u.km
    
    v_1, v_2, ecc, _ = om.OrbitalManeuvers.lambert(attractor=attractor,
                                                departure_position=r_1,
                                                arrival_position=r_2,
                                                delta_time=time.TimeDelta(u.Quantity(1, u.hour)))
    
    assert np.isclose(v_1[0].to_value(u.km / u.s), -5.9925, atol=1e-4)
    assert np.isclose(v_1[1].to_value(u.km / u.s), 1.9254, atol=1e-4)
    assert np.isclose(v_1[2].to_value(u.km / u.s), 3.2456, atol=1e-4)
    
    assert np.isclose(v_2[0].to_value(u.km / u.s), -3.3125, atol=1e-4)
    assert np.isclose(v_2[1].to_value(u.km / u.s), -4.1966, atol=1e-4)
    assert np.isclose(v_2[2].to_value(u.km / u.s), -0.38529, atol=1e-5)
    
    assert np.isclose(ecc.to_value(), 0.4335, atol=1e-4)

def test_super_synchronous_transfer():
    """EXAMPLE 8.4.3 - BOOK 4"""
    
    ssto: om.OrbitalElements = om.OrbitalElements(inclination=25.7 * u.deg,
                                                  right_ascension_of_ascending_node=173.6 * u.deg,
                                                  argument_of_periapsis=179.98 * u.deg)
    
    ssto.update_from_perigee_apogee(periapsis_radius=6563.1 * u.km, apoapsis_radius=129_885 * u.km)
    
    dv_1, dv_2, dv_3 = om.OrbitalManeuvers.super_synchronous_transfer(attractor=bd.Attractor.EARTH,
                                                                      leo_inclination=28.5 * u.deg,
                                                                      geo_inclination=0.6 * u.deg,
                                                                      ssto=ssto)
    
    assert np.isclose(dv_1.to_value(u.km / u.s), 2.993, atol=1e-3)
    assert np.isclose(dv_2.to_value(u.km / u.s), 0.770, atol=1e-3)
    assert np.isclose(dv_3.to_value(u.km / u.s), 0.703, atol=1e-3)

def test_constant_tangential_thrust_transfer_1():
    """EXAMPLE 6.16"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=10000 * u.s,
        thrust=2500e-6 * u.kN,
        spacecraft_mass=1000 * u.kg
    )
    
    r_0: u.Quantity = 6678 * u.km
    
    tof: u.Quantity = 21.03 * u.day
    
    r, m_p = om.OrbitalManeuvers.constant_tangential_thrust_transfer_from_time(attractor=attractor,
                                                                               rocket_motor=rocket_motor,
                                                                               initial_radius=r_0,
                                                                               time_of_flight=tof,
                                                                               direction=om.SpiralDirection.OUTWARD)
    
    assert np.isclose(r.to_value(u.km), 42161, atol=1e-0)
    assert np.isclose(m_p.to_value(u.kg), 46.32, atol=1e-2)
    
    tof, m_p, dv = om.OrbitalManeuvers.constant_tangential_thrust_transfer_from_radius(attractor=attractor,
                                                                                       rocket_motor=rocket_motor,
                                                                                       initial_radius=r_0,
                                                                                       final_radius=r)
    
    assert np.isclose(tof.to_value(u.day), 21.03, atol=1e-2)
    assert np.isclose(m_p.to_value(u.kg), 46.32, atol=1e-2)

def test_constant_tangential_thrust_transfer_2():
    """EXAMPLE 9.1 - BOOK 2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg
    )
    
    r_0: u.Quantity = 6678 * u.km
    
    r_f: u.Quantity = 42161 * u.km
    
    tof, m_p, dv = om.OrbitalManeuvers.constant_tangential_thrust_transfer_from_radius(attractor=attractor,
                                                                                       rocket_motor=rocket_motor,
                                                                                       initial_radius=r_0,
                                                                                       final_radius=r_f)
    
    assert np.isclose(tof.to_value(u.day), 195.73, atol=1e-2)
    assert np.isclose(m_p.to_value(u.kg), 608.6, atol=1e-1)

def test_constant_tangential_thrust_transfer_3():
    """EXAMPLE 9.2 - BOOK 2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=3200 * u.s,
        thrust=0.25 * u.N,
        spacecraft_mass=1200 * u.kg
    )
    
    r_0: u.Quantity = 2 * 6378 * u.km
    
    r_f: u.Quantity = 4 * 6378 * u.km
    
    tof, _, _ = om.OrbitalManeuvers.constant_tangential_thrust_transfer_from_radius(attractor=attractor,
                                                                                    rocket_motor=rocket_motor,
                                                                                    initial_radius=r_0,
                                                                                    final_radius=r_f)
    
    assert np.isclose(tof.to_value(u.day), 88.63, atol=1e-2)
    
    rocket_motor.spacecraft_mass = 2400 * u.kg
    
    tof, _, _ = om.OrbitalManeuvers.constant_tangential_thrust_transfer_from_radius(attractor=attractor,
                                                                                    rocket_motor=rocket_motor,
                                                                                    initial_radius=r_0,
                                                                                    final_radius=r_f)
    
    assert np.isclose(tof.to_value(u.day), 177.25, atol=1e-2)

def test_constant_tangential_thrust_transfer_4():
    """EXAMPLE 9.3 - BOOK 2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg
    )
    
    r_0: u.Quantity = 6678 * u.km
    
    r_f: u.Quantity = 42161 * u.km
    
    tof, _, _ = om.OrbitalManeuvers.constant_tangential_thrust_transfer_from_radius(attractor=attractor,
                                                                                    rocket_motor=rocket_motor,
                                                                                    initial_radius=r_0,
                                                                                    final_radius=r_f,
                                                                                    earth_shadow=True)
    
    assert np.isclose(tof.to_value(u.day), 228.2, atol=1e-1)

def test_non_impulsive_inclination_change_maneuver():
    """EXAMPLE 9.4 - BOOK 2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg
    )
    
    r: u.Quantity = 10000 * u.km
    
    i_0: u.Quantity = 0 * u.deg
    
    i_f: u.Quantity = 20 * u.deg
    
    tof, m_p, dv = om.OrbitalManeuvers.non_impulsive_inclination_change_maneuver(attractor=attractor,
                                                                                 rocket_motor=rocket_motor,
                                                                                 radius=r,
                                                                                 initial_inclination=i_0,
                                                                                 final_inclination=i_f)
    
    assert np.isclose(tof.to_value(u.day), 150.75, atol=1e-2)
    assert np.isclose(m_p.to_value(u.kg), 468.8, atol=1e-1)
    
    r = 30000 * u.km
    
    tof, m_p, dv = om.OrbitalManeuvers.non_impulsive_inclination_change_maneuver(attractor=attractor,
                                                                                 rocket_motor=rocket_motor,
                                                                                 radius=r,
                                                                                 initial_inclination=i_0,
                                                                                 final_inclination=i_f)
    
    assert np.isclose(tof.to_value(u.day), 90.83, atol=1e-2)
    assert np.isclose(m_p.to_value(u.kg), 282.4, atol=1e-1)

def test_non_impulsive_inclined_circular_orbits_transfer():
    """EXAMPLE 9.5 - BOOK 2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg
    )
    
    r_0: u.Quantity = 6678 * u.km
    
    r_f: u.Quantity = 42161 * u.km
    
    i_0: u.Quantity = 28.5 * u.deg
    
    i_f: u.Quantity = 0 * u.deg
    
    tof, m_p, dv = om.OrbitalManeuvers.non_impulsive_inclined_circular_orbits_transfer(attractor=attractor,
                                                                                       rocket_motor=rocket_motor,
                                                                                       initial_radius=r_0,
                                                                                       final_radius=r_f,
                                                                                       initial_inclination=i_0,
                                                                                       final_inclination=i_f)
    
    assert np.isclose(tof.to_value(u.day), 241.3, atol=1e-1)
    assert np.isclose(m_p.to_value(u.kg), 750.5, atol=1e-1)

def test_non_impulsive_maneuver_1():
    """EXAMPLE 6.15"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=10 * u.kN,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_0: u.Quantity = np.array([6858, 0, 0]) * u.km
    
    v_0: u.Quantity = np.array([0, 7.7102, 0]) * u.km / u.s
    
    t_0: u.Quantity = 100 * u.s
    
    dt: u.Quantity = 10 * u.s
    
    r_f: u.Quantity = np.array([-(16000 + 6378), 0, 0]) * u.km
    
    maneuver, _ = om.OrbitalManeuvers.non_impulsive_maneuver(attractor=attractor,
                                                             rocket_motor=rocket_motor,
                                                             initial_position=r_0,
                                                             initial_velocity=v_0,
                                                             burning_time_guess=t_0,
                                                             time_step=dt,
                                                             final_position=r_f,
                                                             tolerance=1e-8)
    
    assert np.isclose(maneuver.burn_time.to_value(u.s), 261.1075, atol=1e-4)
    assert np.isclose(maneuver.spacecraft_mass.to_value(u.kg), 1112.471, atol=1e-3)
    assert np.isclose(maneuver.position_x.to_value(u.km), -22141.57295, atol=1e-5)
    assert np.isclose(maneuver.position_y.to_value(u.km), -3244.5306214, atol=1e-6)
    assert np.isclose(maneuver.position_z.to_value(u.km), 0, atol=1e-0)
    assert np.isclose(maneuver.velocity_x.to_value(u.km / u.s), 0.41938999506, atol=1e-11)
    assert np.isclose(maneuver.velocity_y.to_value(u.km / u.s), -2.8620331423, atol=1e-10)
    assert np.isclose(maneuver.velocity_z.to_value(u.km / u.s), 0, atol=1e-0)
    
    rocket_motor.spacecraft_mass = maneuver.spacecraft_mass
    
    maneuver, _ = om.OrbitalManeuvers.non_impulsive_maneuver(attractor=attractor,
                                                             rocket_motor=rocket_motor,
                                                             initial_position=np.array([
                                                                 maneuver.position_x.to_value(u.km),
                                                                 maneuver.position_y.to_value(u.km),
                                                                 maneuver.position_z.to_value(u.km)]) * u.km,
                                                             initial_velocity=np.array([
                                                                 maneuver.velocity_x.to_value(u.km / u.s),
                                                                 maneuver.velocity_y.to_value(u.km / u.s),
                                                                 maneuver.velocity_z.to_value(u.km / u.s)]) * u.km / u.s,
                                                             burning_time_guess=t_0,
                                                             time_step=dt,
                                                             final_position=r_f,
                                                             semi_major_axis_target=True,
                                                             tolerance=1e-8)
    
    assert np.isclose(maneuver.burn_time.to_value(u.s), 118.88, atol=1e-2)
    assert np.isclose(maneuver.spacecraft_mass.to_value(u.kg), 708.41, atol=1e-2)
    
    r: u.Quantity = np.array([maneuver.position_x.to_value(u.km),
                              maneuver.position_y.to_value(u.km),
                              maneuver.position_z.to_value(u.km)]) * u.km
    
    v: u.Quantity = np.array([maneuver.velocity_x.to_value(u.km / u.s),
                              maneuver.velocity_y.to_value(u.km / u.s),
                              maneuver.velocity_z.to_value(u.km / u.s)]) * u.km / u.s
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r, velocity=v)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 16000 + 6378, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(u.dimensionless_unscaled), 0.00867, atol=1e-5)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 80.85, atol=1e-2)

@pytest.mark.skip(reason="Too long to run")
def test_non_impulsive_maneuver_2():
    """EXAMPLE 6.17"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rocket_motor: om.RocketMotor = om.RocketMotor(
        specific_impulse=10000 * u.s,
        thrust=2500e-6 * u.kN,
        spacecraft_mass=1000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    r_0: u.Quantity = np.array([6678, 0, 0]) * u.km
    
    v_0: u.Quantity = np.array([0, 7.72584, 0]) * u.km / u.s
    
    t_0: u.Quantity = 21.03 * u.day
    
    dt: u.Quantity = 10 * u.s
    
    r_f: u.Quantity = np.array([42164, 0, 0]) * u.km
    
    maneuver, _ = om.OrbitalManeuvers.non_impulsive_maneuver(attractor=attractor,
                                                             rocket_motor=rocket_motor,
                                                             initial_position=r_0,
                                                             initial_velocity=v_0,
                                                             burning_time_guess=t_0,
                                                             time_step=dt,
                                                             final_position=r_f,
                                                             semi_major_axis_target=True,
                                                             tolerance=1e0)
    
    assert np.isclose(maneuver.burn_time.to_value(u.day), 21.0376, atol=1e-4)
    assert np.isclose(rocket_motor.spacecraft_mass.to_value(u.kg) - maneuver.spacecraft_mass.to_value(u.kg), 46.34, atol=1e-2)
    assert np.isclose(maneuver.position_x.to_value(u.km), 37727.275971, atol=1e-6)
    assert np.isclose(maneuver.position_y.to_value(u.km), -20917.194986, atol=1e-6)
    assert np.isclose(maneuver.position_z.to_value(u.km), 0, atol=1e-0)
    assert np.isclose(maneuver.velocity_x.to_value(u.km / u.s), 1.4565649916, atol=1e-10)
    assert np.isclose(maneuver.velocity_y.to_value(u.km / u.s), 2.6271318618, atol=1e-10)
    assert np.isclose(maneuver.velocity_z.to_value(u.km / u.s), 0, atol=1e-0)
    
    r: u.Quantity = np.array([maneuver.position_x.to_value(u.km),
                              maneuver.position_y.to_value(u.km),
                              maneuver.position_z.to_value(u.km)]) * u.km
    
    v: u.Quantity = np.array([maneuver.velocity_x.to_value(u.km / u.s),
                              maneuver.velocity_y.to_value(u.km / u.s),
                              maneuver.velocity_z.to_value(u.km / u.s)]) * u.km / u.s
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor,
                                                           position=r,
                                                           velocity=v)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 42164 - 15, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(u.dimensionless_unscaled), 0.02346, atol=1e-5)
