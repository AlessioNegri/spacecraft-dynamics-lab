import astropy.time as time
import astropy.units as u
import numpy as np

import spacelab.bodies as sl_bodies
import spacelab.proximity.relative_motion as sl_relative_motion


def test_relative_motion_init_and_linearized_propagation():
    motion = sl_relative_motion.RelativeMotion()

    motion.init(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([7000, 0, 0]) * u.km,
        velocity=np.array([0, 7.5, 0]) * u.km / u.s,
        relative_position=np.array([1, 0.2, 0.1]) * u.km,
        relative_velocity=np.array([0.001, 0.002, 0]) * u.km / u.s,
    )

    assert motion.ready

    result = motion.propagate_for(time.TimeDelta(60 * u.s))

    assert result.success
    assert np.isclose(result.time[-1].to_value(u.s), 60, atol=1e-6)


def test_relative_motion_rejects_invalid_near_circular_eccentricity():
    motion = sl_relative_motion.RelativeMotion()
    motion.init(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([7000, 0, 0]) * u.km,
        velocity=np.array([0, 7.5, 0]) * u.km / u.s,
        relative_position=np.array([1, 0.2, 0.1]) * u.km,
        relative_velocity=np.array([0.001, 0.002, 0]) * u.km / u.s,
    )

    invalid_unit = motion.propagate_near_circular_orbit_for(time.TimeDelta(60 * u.s), 0.01 * u.km)
    negative = motion.propagate_near_circular_orbit_for(time.TimeDelta(60 * u.s), -0.01 * u.one)

    assert not invalid_unit.success
    assert not negative.success


def test_relative_motion_unready_propagation_returns_failure():
    motion = sl_relative_motion.RelativeMotion()

    result = motion.propagate_for(time.TimeDelta(60 * u.s))

    assert not result.success


def test_near_circular_relative_motion_equation_positive_case():
    motion = sl_relative_motion.RelativeMotion()
    motion.init(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([7000, 0, 0]) * u.km,
        velocity=np.array([0, 7.5, 0]) * u.km / u.s,
        relative_position=np.array([1, 0.2, 0.1]) * u.km,
        relative_velocity=np.array([0.001, 0.002, 0]) * u.km / u.s,
    )

    state = np.concat([motion.relative_position, motion.relative_velocity, motion.position, motion.velocity])
    circular_derivative = motion._near_circular_orbit_equations_relative_motion(0, state, 0.0)
    near_circular_derivative = motion._near_circular_orbit_equations_relative_motion(10, state, 0.01)

    assert circular_derivative.shape == (12,)
    assert near_circular_derivative.shape == (12,)
    assert np.all(np.isfinite(circular_derivative))
    assert np.all(np.isfinite(near_circular_derivative))


def test_near_circular_relative_motion_propagation_positive_case():
    motion = sl_relative_motion.RelativeMotion()
    motion.init(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([7000, 0, 0]) * u.km,
        velocity=np.array([0, 7.5, 0]) * u.km / u.s,
        relative_position=np.array([1, 0.2, 0.1]) * u.km,
        relative_velocity=np.array([0.001, 0.002, 0]) * u.km / u.s,
    )

    result = motion.propagate_near_circular_orbit_for(time.TimeDelta(60 * u.s), 0.01 * u.one)

    assert result.success
    assert np.isclose(result.time[-1].to_value(u.s), 60, atol=1e-6)


def test_relative_motion_private_linearized_equation_has_expected_state_size():
    motion = sl_relative_motion.RelativeMotion()
    motion.init(
        attractor=sl_bodies.Attractor.EARTH,
        position=np.array([7000, 0, 0]) * u.km,
        velocity=np.array([0, 7.5, 0]) * u.km / u.s,
        relative_position=np.array([1, 0.2, 0.1]) * u.km,
        relative_velocity=np.array([0.001, 0.002, 0]) * u.km / u.s,
    )

    state = np.concat([motion.relative_position, motion.relative_velocity, motion.position, motion.velocity])
    derivative = motion._linearized_equations_relative_motion(0, state)

    assert derivative.shape == (12,)
    assert np.all(np.isfinite(derivative))
