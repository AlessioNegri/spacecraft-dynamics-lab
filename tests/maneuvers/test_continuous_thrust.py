import astropy.units as u
import copy as cp
import numpy as np
import pytest

import spacelab.bodies as sl_bodies
import spacelab.enums as sl_enums
import spacelab.maneuvers.continuous_thrust as sl_continuous_thrust
import spacelab.models.orbital_elements as sl_orbital_elements
import spacelab.models.rocket_motor as sl_rocket_motor
import spacelab.orbit.representation as sl_representation

def test_constant_tangential_thrust_transfer_1():
    """:cite:`curtis` EXAMPLE 6.16"""
    
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=10000 * u.s,
        thrust=2500e-6 * u.kN,
        spacecraft_mass=1000 * u.kg
    )
    
    r, m_p = sl_continuous_thrust.constant_tangential_thrust_transfer_from_time(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        initial_radius=6678 * u.km,
        time_of_flight=21.03 * u.day,
        direction=sl_enums.SpiralDirection.OUTWARD)
    
    assert np.isclose(r.to_value(u.km), 42161, atol=1e-0)
    assert np.isclose(m_p.to_value(u.kg), 46.32, atol=1e-2)
    
    tof, m_p, _ = sl_continuous_thrust.constant_tangential_thrust_transfer_from_radius(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        initial_radius=6678 * u.km,
        final_radius=r)
    
    assert np.isclose(tof.to_value(u.day), 21.03, atol=1e-2)
    assert np.isclose(m_p.to_value(u.kg), 46.32, atol=1e-2)

def test_constant_tangential_thrust_transfer_2():
    """:cite:`kluever` EXAMPLE 9.1"""
    
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg
    )
    
    tof, m_p, _ = sl_continuous_thrust.constant_tangential_thrust_transfer_from_radius(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        initial_radius=6678 * u.km,
        final_radius=42161 * u.km)
    
    assert np.isclose(tof.to_value(u.day), 195.73, atol=1e-2)
    assert np.isclose(m_p.to_value(u.kg), 608.6, atol=1e-1)

def test_constant_tangential_thrust_transfer_3():
    """:cite:`kluever` EXAMPLE 9.2"""
    
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=3200 * u.s,
        thrust=0.25 * u.N,
        spacecraft_mass=1200 * u.kg
    )
    
    tof, _, _ = sl_continuous_thrust.constant_tangential_thrust_transfer_from_radius(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        initial_radius=2 * 6378 * u.km,
        final_radius=4 * 6378 * u.km)
    
    assert np.isclose(tof.to_value(u.day), 88.63, atol=1e-2)
    
    rocket_motor.spacecraft_mass = 2400 * u.kg
    
    tof, _, _ = sl_continuous_thrust.constant_tangential_thrust_transfer_from_radius(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        initial_radius=2 * 6378 * u.km,
        final_radius=4 * 6378 * u.km)
    
    assert np.isclose(tof.to_value(u.day), 177.25, atol=1e-2)

def test_constant_tangential_thrust_transfer_4():
    """:cite:`kluever` EXAMPLE 9.3"""
    
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg
    )
    
    tof, _, _ = sl_continuous_thrust.constant_tangential_thrust_transfer_from_radius(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        initial_radius=6678 * u.km,
        final_radius=42161 * u.km,
        earth_shadow=True)
    
    assert np.isclose(tof.to_value(u.day), 228.2, atol=1e-1)

def test_constant_tangential_thrust_transfer_5():
    """:cite:`walter` EXAMPLE 8.4.5"""
    
    c: u.Quantity = 10_000 * u.m / u.s
    
    m_dot: u.Quantity = (2000 * u.kg) / c * (1e-3 * u.m / u.s**2)
    
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=c /sl_bodies.BODIES[sl_bodies.Attractor.EARTH].g_0,
        thrust=m_dot * c,
        spacecraft_mass=2000 * u.kg
    )
    
    tof, _, _ = sl_continuous_thrust.constant_tangential_thrust_transfer_from_radius(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        initial_radius=6678 * u.km,
        final_radius=42161 * u.km)
    
    assert np.isclose(tof.to_value(u.day), 43.05, atol=1e-2)

def test_inclination_change_maneuver():
    """:cite:`kluever` EXAMPLE 9.4"""
    
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg
    )
    
    tof, m_p, _ = sl_continuous_thrust.inclination_change_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        radius=10000 * u.km,
        initial_inclination=0 * u.deg,
        final_inclination=20 * u.deg)
    
    assert np.isclose(tof.to_value(u.day), 150.75, atol=1e-2)
    assert np.isclose(m_p.to_value(u.kg), 468.8, atol=1e-1)
    
    tof, m_p, _ = sl_continuous_thrust.inclination_change_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        radius=30000 * u.km,
        initial_inclination=0 * u.deg,
        final_inclination=20 * u.deg)
    
    assert np.isclose(tof.to_value(u.day), 90.83, atol=1e-2)
    assert np.isclose(m_p.to_value(u.kg), 282.4, atol=1e-1)

def test_inclined_circular_orbits_transfer():
    """:cite:`kluever` EXAMPLE 9.5"""
    
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg
    )
    
    tof, m_p, _ = sl_continuous_thrust.inclined_circular_orbits_transfer(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        initial_radius=6678 * u.km,
        final_radius=42161 * u.km,
        initial_inclination=28.5 * u.deg,
        final_inclination=0 * u.deg)
    
    assert np.isclose(tof.to_value(u.day), 241.3, atol=1e-1)
    assert np.isclose(m_p.to_value(u.kg), 750.5, atol=1e-1)

def test_non_impulsive_maneuver_1():
    """:cite:`curtis` EXAMPLE 6.15"""
    
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=300 * u.s,
        thrust=10 * u.kN,
        spacecraft_mass=2000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    maneuver, _ = sl_continuous_thrust.non_impulsive_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        initial_position=np.array([6858, 0, 0]) * u.km,
        initial_velocity=np.array([0, 7.7102, 0]) * u.km / u.s,
        burning_time_guess=100 * u.s,
        time_step=10 * u.s,
        final_position=np.array([-(16000 + 6378), 0, 0]) * u.km,
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
    
    maneuver, _ = sl_continuous_thrust.non_impulsive_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        initial_position=np.array([
            maneuver.position_x.to_value(u.km),
            maneuver.position_y.to_value(u.km),
            maneuver.position_z.to_value(u.km)]) * u.km,
        initial_velocity=np.array([
            maneuver.velocity_x.to_value(u.km / u.s),
            maneuver.velocity_y.to_value(u.km / u.s),
            maneuver.velocity_z.to_value(u.km / u.s)]) * u.km / u.s,
        burning_time_guess=100 * u.s,
        time_step=10 * u.s,
        final_position=np.array([-(16000 + 6378), 0, 0]) * u.km,
        semi_major_axis_target=True,
        tolerance=1e-8)
    
    assert np.isclose(maneuver.burn_time.to_value(u.s), 118.88, atol=1e-2)
    assert np.isclose(maneuver.spacecraft_mass.to_value(u.kg), 708.41, atol=1e-2)
    
    r: u.Quantity = np.array([
        maneuver.position_x.to_value(u.km),
        maneuver.position_y.to_value(u.km),
        maneuver.position_z.to_value(u.km)]) * u.km
    
    v: u.Quantity = np.array([
        maneuver.velocity_x.to_value(u.km / u.s),
        maneuver.velocity_y.to_value(u.km / u.s),
        maneuver.velocity_z.to_value(u.km / u.s)]) * u.km / u.s
    
    oe: sl_orbital_elements.OrbitalElements =\
        sl_representation.cartesian_to_keplerian(attractor=sl_bodies.Attractor.EARTH, position=r, velocity=v)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 16000 + 6378, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(u.dimensionless_unscaled), 0.00867, atol=1e-5)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 80.85, atol=1e-2)

@pytest.mark.skip(reason="Too long to run (0:07:55)")
def test_non_impulsive_maneuver_2():
    """:cite:`curtis` EXAMPLE 6.17"""
    
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=10000 * u.s,
        thrust=2500e-6 * u.kN,
        spacecraft_mass=1000 * u.kg,
        propellant_mass=0 * u.kg
    )
    
    maneuver, _ = sl_continuous_thrust.non_impulsive_maneuver(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        initial_position=np.array([6678, 0, 0]) * u.km,
        initial_velocity=np.array([0, 7.72584, 0]) * u.km / u.s,
        burning_time_guess=21.03 * u.day,
        time_step=10 * u.s,
        final_position=np.array([42164, 0, 0]) * u.km,
        semi_major_axis_target=True,
        tolerance=1e0)
    
    assert np.isclose(maneuver.burn_time.to_value(u.day), 21.0376, atol=1e-4) # 21.041689814814816
    assert np.isclose(rocket_motor.spacecraft_mass.to_value(u.kg) - maneuver.spacecraft_mass.to_value(u.kg), 46.34, atol=1e-2)
    assert np.isclose(maneuver.position_x.to_value(u.km), 37727.275971, atol=1e-6)
    assert np.isclose(maneuver.position_y.to_value(u.km), -20917.194986, atol=1e-6)
    assert np.isclose(maneuver.position_z.to_value(u.km), 0, atol=1e-0)
    assert np.isclose(maneuver.velocity_x.to_value(u.km / u.s), 1.4565649916, atol=1e-10)
    assert np.isclose(maneuver.velocity_y.to_value(u.km / u.s), 2.6271318618, atol=1e-10)
    assert np.isclose(maneuver.velocity_z.to_value(u.km / u.s), 0, atol=1e-0)
    
    r: u.Quantity = np.array([
        maneuver.position_x.to_value(u.km),
        maneuver.position_y.to_value(u.km),
        maneuver.position_z.to_value(u.km)]) * u.km
    
    v: u.Quantity = np.array([
        maneuver.velocity_x.to_value(u.km / u.s),
        maneuver.velocity_y.to_value(u.km / u.s),
        maneuver.velocity_z.to_value(u.km / u.s)]) * u.km / u.s
    
    oe: sl_orbital_elements.OrbitalElements =\
        sl_representation.cartesian_to_keplerian(attractor=sl_bodies.Attractor.EARTH, position=r, velocity=v)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 42164 - 15, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(u.dimensionless_unscaled), 0.02346, atol=1e-5)

def test_constant_tangential_thrust_from_time_direction_changes_radius():
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=10000 * u.s,
        thrust=2500e-6 * u.kN,
        spacecraft_mass=1000 * u.kg,
    )

    outward_radius, outward_propellant = sl_continuous_thrust.constant_tangential_thrust_transfer_from_time(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        initial_radius=6678 * u.km,
        time_of_flight=21 * u.day,
        direction=sl_enums.SpiralDirection.OUTWARD,
    )

    inward_radius, inward_propellant = sl_continuous_thrust.constant_tangential_thrust_transfer_from_time(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=cp.deepcopy(rocket_motor),
        initial_radius=6678 * u.km,
        time_of_flight=21 * u.day,
        direction=sl_enums.SpiralDirection.INWARD,
    )

    assert outward_radius > 6678 * u.km
    assert inward_radius < 6678 * u.km
    assert np.isclose(outward_propellant.to_value(u.kg), inward_propellant.to_value(u.kg))

def test_constant_tangential_thrust_same_radius_is_zero_transfer():
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg,
    )

    tof, propellant_mass, delta_velocity = sl_continuous_thrust.constant_tangential_thrust_transfer_from_radius(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        initial_radius=6678 * u.km,
        final_radius=6678 * u.km,
    )

    assert tof == 0 * u.s
    assert propellant_mass == 0 * u.kg
    assert delta_velocity == 0 * u.km / u.s

@pytest.mark.parametrize("initial_radius", [6378 * u.km, 6378 * u.km - 1 * u.km])
def test_constant_tangential_thrust_rejects_radius_at_or_below_earth(initial_radius):
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg,
    )

    result = sl_continuous_thrust.constant_tangential_thrust_transfer_from_radius(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        initial_radius=initial_radius,
        final_radius=7000 * u.km,
    )

    assert result is None

def test_constant_tangential_thrust_rejects_invalid_direction():
    rocket_motor = sl_rocket_motor.RocketMotor(
        specific_impulse=1700 * u.s,
        thrust=0.6 * u.N,
        spacecraft_mass=2500 * u.kg,
    )

    result = sl_continuous_thrust.constant_tangential_thrust_transfer_from_time(
        attractor=sl_bodies.Attractor.EARTH,
        rocket_motor=rocket_motor,
        initial_radius=6678 * u.km,
        time_of_flight=20 * u.day,
        direction="outward",
    )

    assert result is None
