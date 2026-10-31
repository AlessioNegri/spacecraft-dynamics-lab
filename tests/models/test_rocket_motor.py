import astropy.units as u
import numpy as np
import pytest

from spacelab.bodies import Attractor, BODIES
from spacelab.models.rocket_motor import RocketMotor

@pytest.fixture
def rocket_motor():
    
	return RocketMotor(specific_impulse=300 * u.s, thrust=400 * u.N, spacecraft_mass=2000 * u.kg)

def test_calc_propellant_mass():
    """Example 6.1 | Space Flight Dynamics | Section 6.3 The Rocket Equation"""
    
    rocket_motor = RocketMotor(specific_impulse=296 * u.s, thrust=400 * u.N, spacecraft_mass=12500 * u.kg)

    dv: u.Quantity = 1.7089 * u.km / u.s

    m_p: u.Quantity = rocket_motor.calc_propellant_mass(dv)

    assert m_p.unit == u.kg
    assert m_p.to_value(u.kg) == pytest.approx(5562, abs=1e-1)
    assert rocket_motor.propellant_mass == m_p

def test_propellant_mass_rejects_invalid_inputs(rocket_motor: RocketMotor):
    
	assert rocket_motor.calc_propellant_mass(2.5 * u.kg) == 0 * u.kg
	assert rocket_motor.calc_propellant_mass(2.5 * u.km / u.s, attractor="Earth") == 0 * u.kg

def test_propellant_mass_returns_zero_for_nonpositive_specific_impulse(rocket_motor: RocketMotor):
    
	rocket_motor.specific_impulse = 0 * u.s

	assert rocket_motor.calc_propellant_mass(2.5 * u.km / u.s) == 0 * u.kg

def test_calc_burn_time():
    
    rocket_motor = RocketMotor(specific_impulse=280 * u.s, thrust=67 * u.kN, spacecraft_mass=2500 * u.kg)

    t_b: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=1720.5 * u.kg)

    assert t_b.unit == u.s
    assert t_b.to_value(u.s) == pytest.approx(70.511, abs=1e-3)

@pytest.mark.parametrize(
	("specific_impulse", "thrust"),
	[
		(0 * u.s, 400 * u.N),
		(300 * u.s, 0 * u.N),
	],
)
def test_burn_time_returns_zero_for_invalid_engine_parameters(specific_impulse: u.Quantity, thrust: u.Quantity):
    
	motor = RocketMotor(specific_impulse=specific_impulse, thrust=thrust, spacecraft_mass=2000 * u.kg)

	assert motor.calc_burn_time(100 * u.kg) == 0 * u.s

def test_burn_time_rejects_invalid_inputs(rocket_motor: RocketMotor):
    
	assert rocket_motor.calc_burn_time(100 * u.m) == 0 * u.s
	assert rocket_motor.calc_burn_time(100 * u.kg, attractor="Earth") == 0 * u.s


def test_calc_effective_exhaust_velocity(rocket_motor: RocketMotor):
    
    gravity: float = BODIES[Attractor.EARTH].g_0.to_value(u.m / u.s**2)
    expected_velocity: float = rocket_motor.specific_impulse.to_value(u.s) * gravity

    exhaust_velocity: u.Quantity = rocket_motor.calc_effective_exhaust_velocity()

    assert exhaust_velocity.unit == u.m / u.s
    assert exhaust_velocity.to_value(u.m / u.s) == pytest.approx(expected_velocity, abs=1e-3)
    assert rocket_motor.calc_effective_exhaust_velocity(attractor="Earth") == 0 * u.m / u.s


def test_calc_propellant_mass_flow_rate(rocket_motor: RocketMotor):
    
	expected_flow_rate: u.Quantity = rocket_motor.thrust / rocket_motor.calc_effective_exhaust_velocity()

	mass_flow_rate: u.Quantity = rocket_motor.calc_propellant_mass_flow_rate()

	assert mass_flow_rate.unit == u.kg / u.s
	assert mass_flow_rate.to_value(u.kg / u.s) == pytest.approx(expected_flow_rate.to_value(u.kg / u.s), abs=1e-3)

def test_mass_flow_rate_returns_zero_for_invalid_attractor_or_exhaust_velocity(rocket_motor: RocketMotor):
    
    assert rocket_motor.calc_propellant_mass_flow_rate(attractor="Earth") == 0 * u.kg / u.s

    rocket_motor.specific_impulse = 0 * u.s

    assert rocket_motor.calc_propellant_mass_flow_rate() == 0 * u.kg / u.s
