import astropy.time as time
import astropy.units as u
import numpy as np
import pytest

import spacelab.bodies as sl_bodies
from spacelab.bodies import Attractor
from spacelab.enums import AngleType
from spacelab.n_body_models.lagrange_coefficients import LagrangeCoefficients

def test_propagate_of_angle_true_anomaly():
    """:cite:`curtis` EXAMPLE 2.13"""

    r, v = LagrangeCoefficients.propagate_of_angle(
        attractor=Attractor.EARTH,
        initial_position=np.array([8182.4, -6865.9, 0]) * u.km,
        initial_velocity=np.array([0.47572, 8.8116, 0]) * u.km / u.s,
        delta_true_anomaly=120 * u.deg)
    
    assert np.allclose(r.to_value(u.km), [1454.9, 8251.6, 0], atol=1e-1)
    assert np.allclose(v.to_value(u.km / u.s), [-8.1323, 5.6785, 0], atol=1e-4)

def test_propagate_of_angle_eccentric_anomaly():
    """:cite:`curtis` EXAMPLE 2.13"""

    r, v = LagrangeCoefficients.propagate_of_angle(
        attractor=Attractor.EARTH,
        initial_position=np.array([-15634, 4689, 7407]) * u.km,
        initial_velocity=np.array([-4.6954, -2.3777, 0.6497]) * u.km / u.s,
        delta_true_anomaly=80 * u.deg,
        true_anomalies=[120 * u.deg, 200 * u.deg],
        angle_type=AngleType.ECCENTRIC_ANOMALY)
    
    assert np.allclose(r.to_value(u.km), [-19093, -30245, -5918], atol=1e-0)
    assert np.allclose(v.to_value(u.km / u.s), [2.2512, 0.4661, -0.5918], atol=1e-4)


@pytest.mark.parametrize(
    ("true_anomalies", "angle_type"),
    [
        pytest.param(None, AngleType.ECCENTRIC_ANOMALY, id="missing-anomalies"),
        pytest.param([120 * u.deg], AngleType.ECCENTRIC_ANOMALY, id="wrong-anomaly-count"),
        pytest.param([120 * u.s, 200 * u.deg], AngleType.ECCENTRIC_ANOMALY, id="invalid-anomaly-unit"),
        pytest.param([200 * u.deg, 120 * u.deg], AngleType.ECCENTRIC_ANOMALY, id="decreasing-anomalies"),
        pytest.param([120 * u.deg, 201 * u.deg], AngleType.ECCENTRIC_ANOMALY, id="anomaly-delta-mismatch"),
        pytest.param(None, "true", id="invalid-angle-type"),
    ],
)
def test_propagate_of_angle_invalid_anomaly_options_return_zero_state(true_anomalies, angle_type):
    result = LagrangeCoefficients.propagate_of_angle(
        attractor=Attractor.EARTH,
        initial_position=np.array([-15634, 4689, 7407]) * u.km,
        initial_velocity=np.array([-4.6954, -2.3777, 0.6497]) * u.km / u.s,
        delta_true_anomaly=80 * u.deg,
        true_anomalies=true_anomalies,
        angle_type=angle_type,
    )

    assert len(result) == 2
    assert result[0] == 0 * u.km
    assert result[1] == 0 * u.km / u.s

def test_universal_kepler_solution():
    """:cite:`curtis` EXAMPLE 3.6"""

    x: u.Quantity = LagrangeCoefficients.universal_kepler_solution(
        attractor=Attractor.EARTH,
        initial_position=10000 * u.km,
        initial_radial_velocity=3.0752 * u.km / u.s,
        alpha=1 / (-19655) * 1 / u.km, # ? Reciprocal of the semi-major axis [1/km]
        delta_time=time.TimeDelta(u.Quantity(1, u.hour)))

    assert np.isclose(x.to_value(u.km**0.5), 128.51, atol=1e-1)
    
def test_propagate_position_velocity():
    """:cite:`curtis` EXAMPLE 3.7"""
    
    r, v = LagrangeCoefficients.propagate_position_velocity(
        attractor=Attractor.EARTH,
        initial_position=np.array([7000, -12124, 0]) * u.km,
        initial_velocity=np.array([2.6679, 4.6210, 0]) * u.km / u.s,
        delta_time=time.TimeDelta(u.Quantity(1, u.hour)))
    
    assert np.allclose(r.to_value(u.km), [-3297.8, 7413.3, 0], atol=1e-1)
    assert np.allclose(v.to_value(u.km / u.s), [-8.2977, -0.96309, 0], atol=1e-3)


def test_stumpff_functions_special_cases_and_signs():
    assert np.isclose(LagrangeCoefficients.S(0), 1/6)
    assert np.isclose(LagrangeCoefficients.C(0), 1/2)
    assert np.isclose(LagrangeCoefficients.S(1), 1 - np.sin(1), atol=1e-12)
    assert np.isclose(LagrangeCoefficients.C(1), 1 - np.cos(1), atol=1e-12)
    assert np.isclose(LagrangeCoefficients.S(-1), np.sinh(1) - 1, atol=1e-12)
    assert np.isclose(LagrangeCoefficients.C(-1), np.cosh(1) - 1, atol=1e-12)


def test_lagrange_coefficients_match_universal_variable_formulation():
    r_0 = np.array([7000, -12124, 0]) * u.km
    v_0 = np.array([2.6679, 4.6210, 0]) * u.km / u.s
    dt = time.TimeDelta(1 * u.hour)
    mu = sl_bodies.BODIES[Attractor.EARTH].mu

    r_0_m = np.linalg.norm(r_0)
    v_0_m = np.linalg.norm(v_0)
    v_r_0 = np.dot(r_0.value, v_0.value) / r_0_m.value
    alpha = 2 / r_0_m.to_value(u.km) - v_0_m.to_value(u.km / u.s)**2 / mu.to_value(u.km**3 / u.s**2)

    chi = LagrangeCoefficients.universal_kepler_solution(
        attractor=Attractor.EARTH,
        initial_position=r_0_m,
        initial_radial_velocity=v_r_0 * u.km / u.s,
        alpha=alpha * 1 / u.km,
        delta_time=dt,
    )

    f, g = LagrangeCoefficients.lagrange_coefficients(
        attractor=Attractor.EARTH,
        initial_position=r_0_m,
        alpha=alpha * 1 / u.km,
        delta_time=dt,
        universal_anomaly=chi,
    )

    z = alpha * chi.to_value(u.km**0.5)**2
    expected_f = 1 - chi.to_value(u.km**0.5)**2 / r_0_m.to_value(u.km) * LagrangeCoefficients.C(z)
    expected_g = dt.to_value(u.s) - 1 / np.sqrt(mu.to_value(u.km**3 / u.s**2)) * chi.to_value(u.km**0.5)**3 * LagrangeCoefficients.S(z)

    assert np.isclose(f.to_value(u.one), expected_f, atol=1e-10)
    assert np.isclose(g.to_value(u.s), expected_g, atol=1e-10)


@pytest.mark.parametrize(
    ("attractor", "position", "alpha", "delta_time", "universal_anomaly"),
    [
        pytest.param("Earth", 10000 * u.km, 1 / (10000 * u.km), 1 * u.hour, 10 * u.km**0.5, id="invalid-attractor"),
        pytest.param(Attractor.EARTH, 10000 * u.s, 1 / (10000 * u.km), 1 * u.hour, 10 * u.km**0.5, id="invalid-position-unit"),
        pytest.param(Attractor.EARTH, 10000 * u.km, 1 / (10000 * u.s), 1 * u.hour, 10 * u.km**0.5, id="invalid-alpha-unit"),
        pytest.param(Attractor.EARTH, 10000 * u.km, 1 / (10000 * u.km), 1 * u.km, 10 * u.km**0.5, id="invalid-delta-time-unit"),
        pytest.param(Attractor.EARTH, 10000 * u.km, 1 / (10000 * u.km), 1 * u.hour, 10 * u.s, id="invalid-universal-anomaly-unit"),
    ],
)
def test_lagrange_coefficients_invalid_inputs_return_none(attractor, position, alpha, delta_time, universal_anomaly):
    result = LagrangeCoefficients.lagrange_coefficients(
        attractor=attractor,
        initial_position=position,
        alpha=alpha,
        delta_time=delta_time,
        universal_anomaly=universal_anomaly,
    )

    assert result is None
