import astropy.time as time
import astropy.units as u
import numpy as np
import pytest

from spacelab.bodies import Attractor, BODIES
from spacelab.enums import ThrustDirection
from spacelab.models.rocket_motor import RocketMotor
from spacelab.n_body_models.two_body_problem import Orbit


@pytest.fixture
def orbit():
	epoch = time.Time("2025-01-01T00:00:00", format="isot", scale="utc")
	radius = 7000 * u.km
	orbital_speed = np.sqrt((BODIES[Attractor.EARTH].mu / radius).to_value(u.km**2 / u.s**2))
	instance = Orbit()
	instance.from_cartesian(
		attractor=Attractor.EARTH,
		position=np.array([radius.to_value(u.km), 0, 0]) * u.km,
		velocity=np.array([0, orbital_speed, 0]) * u.km / u.s,
		epoch=epoch,
	)
	return instance


def test_from_cartesian_initializes_and_converts_state_units():
	orbit = Orbit()
	epoch = time.Time("2025-01-01T00:00:00", format="isot", scale="utc")

	orbit.from_cartesian(
		attractor=Attractor.EARTH,
		position=np.array([7_000_000, 0, 0]) * u.m,
		velocity=np.array([0, 7_500, 0]) * u.m / u.s,
		epoch=epoch,
	)

	assert orbit.ready
	assert orbit.attractor == BODIES[Attractor.EARTH]
	np.testing.assert_allclose(orbit.position, [7000, 0, 0])
	np.testing.assert_allclose(orbit.velocity, [0, 7.5, 0])
	assert orbit.epoch == epoch


@pytest.mark.parametrize(
	("attractor", "position", "velocity", "epoch"),
	[
		("Earth", np.array([7000, 0, 0]) * u.km, np.array([0, 7.5, 0]) * u.km / u.s,
		 time.Time("2025-01-01T00:00:00", format="isot", scale="utc")),
		(Attractor.EARTH, np.array([7000, 0, 0]) * u.s, np.array([0, 7.5, 0]) * u.km / u.s,
		 time.Time("2025-01-01T00:00:00", format="isot", scale="utc")),
		(Attractor.EARTH, np.array([7000, 0]) * u.km, np.array([0, 7.5, 0]) * u.km / u.s,
		 time.Time("2025-01-01T00:00:00", format="isot", scale="utc")),
		(Attractor.EARTH, np.array([7000, 0, 0]) * u.km, np.array([0, 7.5, 0]) * u.s,
		 time.Time("2025-01-01T00:00:00", format="isot", scale="utc")),
		(Attractor.EARTH, np.array([7000, 0, 0]) * u.km, np.array([0, 7.5, 0]) * u.km / u.s, "2025-01-01"),
	],
)
def test_from_cartesian_rejects_invalid_inputs(attractor, position, velocity, epoch):
	orbit = Orbit()

	orbit.from_cartesian(attractor, position, velocity, epoch)

	assert not orbit.ready


def test_unthrusted_propagate_for_returns_successful_state(orbit):
	result = orbit.propagate_for(time.TimeDelta(60 * u.s))

	assert result.success
	assert result.time[-1].to_value(u.s) == pytest.approx(60)
	assert result.position_x[-1].to_value(u.km) != pytest.approx(orbit.position[0])
	assert result.velocity_y[-1].to_value(u.km / u.s) > 0


def test_unthrusted_propagate_until_returns_successful_state(orbit):
	end_epoch = orbit.epoch + time.TimeDelta(60 * u.s)

	result = orbit.propagate_until(end_epoch)

	assert result.success
	assert result.time[-1].to_value(u.s) == pytest.approx(60)


def test_thrusted_propagation_tracks_spacecraft_mass(orbit):
	motor = RocketMotor(
		specific_impulse=300 * u.s,
		thrust=100 * u.N,
		spacecraft_mass=1000 * u.kg,
	)

	result = orbit.propagate_for(time.TimeDelta(60 * u.s), rocket_motor=motor)

	assert result.success
	assert result.mass_spacecraft[0].to_value(u.kg) == pytest.approx(1000)
	assert result.mass_spacecraft[-1].to_value(u.kg) < result.mass_spacecraft[0].to_value(u.kg)


@pytest.mark.parametrize("method_name", ["propagate_for", "propagate_until"])
def test_propagation_forwards_thrust_control_parameters(orbit, monkeypatch, method_name):
	motor = RocketMotor(specific_impulse=300 * u.s, thrust=100 * u.N, spacecraft_mass=1000 * u.kg)
	captured = {}

	def capture_parameters(**kwargs):
		captured.update(kwargs)

	monkeypatch.setattr(orbit, "_propagate", capture_parameters)
	parameters = {
		"rocket_motor": motor,
		"thrust_direction": ThrustDirection.ALONG_ANGULAR_MOMENTUM,
		"initial_radius": 7000 * u.m,
		"target_radius": 8000 * u.m,
		"initial_inclination": 10 * u.deg,
		"target_inclination": 20 * u.deg,
	}

	if method_name == "propagate_for":
		getattr(orbit, method_name)(time.TimeDelta(60 * u.s), **parameters)
	else:
		getattr(orbit, method_name)(orbit.epoch + time.TimeDelta(60 * u.s), **parameters)

	assert captured["initial_radius"] == pytest.approx(7)
	assert captured["target_radius"] == pytest.approx(8)
	assert captured["initial_inclination"] == pytest.approx(np.deg2rad(10))
	assert captured["target_inclination"] == pytest.approx(np.deg2rad(20))


def test_propagation_rejects_invalid_orbit_and_arguments(orbit):
	uninitialized = Orbit()
	assert not uninitialized.propagate_for(time.TimeDelta(60 * u.s)).success
	assert not orbit.propagate_for(60 * u.s).success
	assert not orbit.propagate_until(orbit.epoch - time.TimeDelta(1 * u.s)).success
	assert not orbit.propagate_until("2025-01-01").success


def test_equations_relative_motion_returns_central_gravity_acceleration(orbit):
	state = np.array([7000, 0, 0, 0, 7.5, 0])
	mu = BODIES[Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)

	derivative = orbit._equations_relative_motion(0, state)

	np.testing.assert_allclose(derivative[:3], state[3:])
	np.testing.assert_allclose(derivative[3:], [-mu / 7000**2, 0, 0])


@pytest.mark.parametrize(
	("direction", "expected_thrust_acceleration"),
	[
		(ThrustDirection.ALONG_VELOCITY, np.array([0, 0.001, 0])),
		(ThrustDirection.ALONG_ANGULAR_MOMENTUM, np.array([0, 0, 0.001])),
	],
)
def test_equations_with_thrust_include_acceleration_and_mass_flow(
	orbit,
	direction,
	expected_thrust_acceleration,
):
	state = np.array([7000, 0, 0, 0, 7.5, 0, 1000])
	thrust = 1.0
	specific_impulse = 300.0
	gravity = orbit.attractor.g_0.to_value(u.km / u.s**2)
	mu = orbit.attractor.mu.to_value(u.km**3 / u.s**2)

	derivative = orbit._equations_relative_motion_with_thrust(
		t=0,
		X=state,
		thrust=thrust,
		specific_impulse=specific_impulse,
		thrust_direction=direction,
		initial_radius=0,
		target_radius=1,
		initial_inclination=0,
		target_inclination=1,
	)

	expected_acceleration = np.array([-mu / 7000**2, 0, 0]) + expected_thrust_acceleration
	np.testing.assert_allclose(derivative[:3], state[3:6])
	np.testing.assert_allclose(derivative[3:6], expected_acceleration)
	assert derivative[6] == pytest.approx(-thrust / (specific_impulse * gravity))
