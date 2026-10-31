import astropy.units as u
import numpy as np
import pytest

from spacelab.bodies import Attractor, BODIES
from spacelab.models.orbital_elements import OrbitalElements


@pytest.fixture
def orbital_elements():
    
    return OrbitalElements(semimajor_axis=7000 * u.km, eccentricity=0.1 * u.one)

def test_calculates_periapsis_and_apoapsis_radii(orbital_elements):
    
    assert orbital_elements.calc_periapsis_radius().to_value(u.km) == pytest.approx(6300)
    assert orbital_elements.calc_apoapsis_radius().to_value(u.km) == pytest.approx(7700)

def test_calculates_semimajor_axis_from_specific_angular_momentum():
    
    semimajor_axis: u.Quantity = 7000 * u.km
    eccentricity: u.Quantity = 0.1 * u.one
    mu: u.Quantity = BODIES[Attractor.EARTH].mu
    angular_momentum: u.Quantity = np.sqrt(mu * semimajor_axis * (1 - eccentricity**2))
    
    elements = OrbitalElements(specific_angular_momentum=angular_momentum, eccentricity=eccentricity)

    result: u.Quantity = elements.calc_semimajor_axis()

    assert result.to_value(u.km) == pytest.approx(semimajor_axis.to_value(u.km))
    assert elements.semimajor_axis == result


def test_calculates_specific_angular_momentum_for_elliptic_orbit(orbital_elements):
    
    mu: u.Quantity = BODIES[Attractor.EARTH].mu
    expected: u.Quantity = np.sqrt(mu * orbital_elements.semimajor_axis * (1 - orbital_elements.eccentricity**2))

    result: u.Quantity = orbital_elements.calc_specific_angular_momentum()

    assert result.to_value(u.km**2 / u.s) == pytest.approx(expected.to_value(u.km**2 / u.s))
    assert orbital_elements.specific_angular_momentum == result


def test_specific_angular_momentum_is_zero_for_non_elliptic_orbit():
    
    elements = OrbitalElements(semimajor_axis=7000 * u.km, eccentricity=1.2 * u.one)

    assert elements.calc_specific_angular_momentum() == 0 * u.km**2 / u.s


def test_calculates_orbital_period_from_semimajor_axis(orbital_elements):
    
    mu: u.Quantity = BODIES[Attractor.EARTH].mu
    expected_period: u.Quantity = 2 * np.pi * np.sqrt(orbital_elements.semimajor_axis**3 / mu)

    result: u.Quantity = orbital_elements.calc_orbital_period()

    assert result.to_value(u.s) == pytest.approx(expected_period.to_value(u.s))


def test_calculates_angular_momentum_when_period_is_requested(orbital_elements):
    
    mu: u.Quantity = BODIES[Attractor.EARTH].mu
    expected_angular_momentum: u.Quantity = np.sqrt(
        mu * orbital_elements.semimajor_axis * (1 - orbital_elements.eccentricity**2)
    )

    assert orbital_elements.specific_angular_momentum == 0 * u.km**2 / u.s

    orbital_elements.calc_orbital_period()

    assert orbital_elements.specific_angular_momentum.to_value(u.km**2 / u.s) == pytest.approx(
        expected_angular_momentum.to_value(u.km**2 / u.s)
    )


def test_orbital_period_is_zero_without_orbit_size_or_momentum():
    
    assert OrbitalElements().calc_orbital_period() == 0 * u.s


@pytest.mark.parametrize("use_angular_momentum", [False, True])
def test_calculates_semilatus_rectum(orbital_elements, use_angular_momentum):
    
    mu: u.Quantity = BODIES[Attractor.EARTH].mu
    expected: u.Quantity = orbital_elements.semimajor_axis * (1 - orbital_elements.eccentricity**2)
    
    if use_angular_momentum:
        
        orbital_elements.specific_angular_momentum = np.sqrt(mu * expected)

    result: u.Quantity = orbital_elements.calc_semilatus_rectum()

    assert result.to_value(u.km) == pytest.approx(expected.to_value(u.km))


def test_updates_elements_from_periapsis_and_apoapsis():
    
    elements = OrbitalElements()

    elements.update_from_periapsis_apoapsis(6300 * u.km, 7700 * u.km)

    assert elements.semimajor_axis.to_value(u.km) == pytest.approx(7000)
    assert elements.eccentricity.to_value(u.one) == pytest.approx(0.1)


def test_update_rejects_invalid_radius_units_without_mutating_elements(orbital_elements):
    
    original_semimajor_axis: u.Quantity = orbital_elements.semimajor_axis
    original_eccentricity: u.Quantity = orbital_elements.eccentricity

    orbital_elements.update_from_periapsis_apoapsis(6300 * u.s, 7700 * u.km)

    assert orbital_elements.semimajor_axis == original_semimajor_axis
    assert orbital_elements.eccentricity == original_eccentricity


def test_calculates_velocity_from_orbital_elements(orbital_elements):
    
    orbital_elements.true_anomaly = 45 * u.deg
    
    mu: u.Quantity = BODIES[Attractor.EARTH].mu
    semimajor_axis: u.Quantity = orbital_elements.semimajor_axis
    eccentricity: u.Quantity = orbital_elements.eccentricity
    radius: u.Quantity = semimajor_axis * (1 - eccentricity**2) / (
        1 + eccentricity * np.cos(orbital_elements.true_anomaly)
    )
    expected_velocity: u.Quantity = np.sqrt(mu * (2 / radius - 1 / semimajor_axis))

    result: u.Quantity = orbital_elements.calc_velocity()

    assert result.to_value(u.km / u.s) == pytest.approx(expected_velocity.to_value(u.km / u.s))


@pytest.mark.parametrize(
    ("method_name", "expected_unit"),
    [
        ("calc_semimajor_axis", u.km),
        ("calc_specific_angular_momentum", u.km**2 / u.s),
        ("calc_orbital_period", u.s),
        ("calc_semilatus_rectum", u.km),
        ("calc_velocity", u.km / u.s),
    ],
)
def test_invalid_attractor_returns_zero_with_expected_unit(orbital_elements, method_name, expected_unit):
    
    result: u.Quantity = getattr(orbital_elements, method_name)(attractor="Earth")

    assert result.unit == expected_unit
    assert result.value == 0
