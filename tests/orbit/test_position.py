import astropy.units as u
import numpy as np
import pytest

import spacelab.bodies as sl_bodies
import spacelab.orbit.position as sl_position

def test_circular_orbit_time():
    
    t: u.Quantity = sl_position.circular_orbit_time(true_anomaly=360 * u.deg, period=1000 * u.s)
    
    assert np.isclose(t.to_value(u.s), 1000)

def test_circular_orbit_true_anomaly():
    
    nu: u.Quantity = sl_position.circular_orbit_true_anomaly(time_of_flight=(1000/4) * u.s, period=1000 * u.s)
    
    assert np.isclose(nu.to_value(u.deg), 90)

def test_elliptical_orbit_time_1():
    """:cite:`curtis` EXAMPLE 3.1"""

    t: u.Quantity = sl_position.elliptical_orbit_time(
        true_anomaly=120 * u.deg, period=18834 * u.s, eccentricity=0.37255 * u.one)

    assert np.isclose(t.to_value(u.s), 4077, atol=1e-1)

def test_elliptical_orbit_time_2():
    """EXAMPLE 5.4.1 - BOOK 3"""

    t: u.Quantity = sl_position.elliptical_orbit_time(
        true_anomaly=59.04 * u.deg, period=158 * u.minute, eccentricity=0.3 * u.one)

    assert np.isclose(t.to_value(u.s), 867.6, atol=1e-1)

    t: u.Quantity = sl_position.elliptical_orbit_time(
        true_anomaly=287.0 * u.deg, period=158 * u.minute, eccentricity=0.3 * u.one)

    assert np.isclose(t.to_value(u.s), 8358.56, atol=1e-2)
    
def test_elliptical_orbit_true_anomaly():
    """:cite:`curtis` EXAMPLE 3.2"""

    nu: u.Quantity = sl_position.elliptical_orbit_true_anomaly(
        time_of_flight=3 * u.hour, period=18834 * u.s, eccentricity=0.37255 * u.one)

    assert np.isclose(nu.to_value(u.deg), 193.2, atol=1e-1)


def test_elliptical_orbit_round_trip_after_half_period():
    period = 158 * u.minute
    eccentricity = 0.3 * u.one
    expected_true_anomaly = 287 * u.deg
    time_of_flight = sl_position.elliptical_orbit_time(
        expected_true_anomaly,
        period,
        eccentricity,
    )

    actual_true_anomaly = sl_position.elliptical_orbit_true_anomaly(
        time_of_flight,
        period,
        eccentricity,
    )

    assert np.isclose(actual_true_anomaly.to_value(u.deg), expected_true_anomaly.to_value(u.deg), atol=1e-8)


@pytest.mark.parametrize(
    ("function", "args", "expected_unit"),
    [
        pytest.param(sl_position.circular_orbit_time, (1 * u.s, 1000 * u.s), u.s, id="circular-time-angle-unit"),
        pytest.param(sl_position.circular_orbit_time, (90 * u.deg, 0 * u.s), u.s, id="circular-time-nonpositive-period"),
        pytest.param(sl_position.circular_orbit_true_anomaly, (-1 * u.s, 1000 * u.s), u.deg, id="circular-anomaly-negative-time"),
        pytest.param(sl_position.circular_orbit_true_anomaly, (250 * u.s, 0 * u.s), u.deg, id="circular-anomaly-nonpositive-period"),
    ],
)
def test_circular_orbit_invalid_inputs_return_zero(function, args, expected_unit):
    result = function(*args)

    assert result == 0 * expected_unit


@pytest.mark.parametrize("eccentricity", [-0.1, 1.0])
def test_elliptical_orbit_time_rejects_non_elliptic_eccentricity(eccentricity):
    result = sl_position.elliptical_orbit_time(
        90 * u.deg,
        1000 * u.s,
        eccentricity * u.one,
    )

    assert result == 0 * u.s


@pytest.mark.parametrize("eccentricity", [-0.1, 1.0])
def test_elliptical_orbit_true_anomaly_rejects_non_elliptic_eccentricity(eccentricity):
    result = sl_position.elliptical_orbit_true_anomaly(
        100 * u.s,
        1000 * u.s,
        eccentricity * u.one,
    )

    assert result == 0 * u.deg


def test_elliptical_orbit_true_anomaly_rejects_nonpositive_time_of_flight():
    result = sl_position.elliptical_orbit_true_anomaly(
        0 * u.s,
        1000 * u.s,
        0.3 * u.one,
    )

    assert result == 0 * u.deg
    
def test_parabolic_orbit_time():
    """:cite:`curtis` EXAMPLE 3.4"""

    t: u.Quantity = sl_position.parabolic_orbit_time(
        true_anomaly=144.75447856886476 * u.deg,
        specific_angular_momentum=79720 * u.km**2 / u.s,
        attractor=sl_bodies.Attractor.EARTH)

    assert np.isclose(t.to_value(u.s), 6 * 60 * 60, atol=1e-1)
    
def test_parabolic_orbit_true_anomaly():
    """:cite:`curtis` EXAMPLE 3.4"""

    nu: u.Quantity = sl_position.parabolic_orbit_true_anomaly(
        time_of_flight=6 * u.hour,
        specific_angular_momentum=79720 * u.km**2 / u.s,
        attractor=sl_bodies.Attractor.EARTH)

    assert np.isclose(nu.to_value(u.deg), 144.75, atol=1e-2)


def test_parabolic_orbit_true_anomaly_rejects_nonpositive_time_of_flight():
    nu = sl_position.parabolic_orbit_true_anomaly(
        time_of_flight=0 * u.s,
        specific_angular_momentum=79720 * u.km**2 / u.s,
        attractor=sl_bodies.Attractor.EARTH,
    )

    assert nu == 0 * u.deg

def test_hyperbolic_orbit_time():
    """:cite:`curtis` EXAMPLE 3.5"""

    t: u.Quantity = sl_position.hyperbolic_orbit_time(
        true_anomaly=100 * u.deg,
        specific_angular_momentum=100_170 * u.km**2 / u.s,
        eccentricity=2.7696 * u.one,
        attractor=sl_bodies.Attractor.EARTH)

    assert np.isclose(t.to_value(u.s), 4141.4, atol=1e-1)
    
def test_hyperbolic_orbit_true_anomaly():
    """:cite:`curtis` EXAMPLE 3.5"""

    nu: u.Quantity = sl_position.hyperbolic_orbit_true_anomaly(
        time_of_flight=4141.4 * u.s + 3 * u.hour,
        specific_angular_momentum=100_170 * u.km**2 / u.s,
        eccentricity=2.7696 * u.one,
        attractor=sl_bodies.Attractor.EARTH)

    assert np.isclose(nu.to_value(u.deg), 107.78, atol=1e-2)


def test_hyperbolic_orbit_true_anomaly_invalid_eccentricity_unit_returns_zero():
    nu = sl_position.hyperbolic_orbit_true_anomaly(
        time_of_flight=1000 * u.s,
        specific_angular_momentum=100_170 * u.km**2 / u.s,
        eccentricity=2.0 * u.km,
        attractor=sl_bodies.Attractor.EARTH,
    )

    assert nu == 0 * u.deg


def test_hyperbolic_orbit_true_anomaly_rejects_eccentricity_at_or_below_one():
    nu = sl_position.hyperbolic_orbit_true_anomaly(
        time_of_flight=1000 * u.s,
        specific_angular_momentum=100_170 * u.km**2 / u.s,
        eccentricity=1 * u.one,
        attractor=sl_bodies.Attractor.EARTH,
    )

    assert nu == 0 * u.deg


def test_hyperbolic_orbit_time_rejects_true_anomaly_outside_asymptote():
    t = sl_position.hyperbolic_orbit_time(
        true_anomaly=170 * u.deg,
        specific_angular_momentum=100_170 * u.km**2 / u.s,
        eccentricity=2.7696 * u.one,
        attractor=sl_bodies.Attractor.EARTH,
    )

    assert t == 0 * u.s
