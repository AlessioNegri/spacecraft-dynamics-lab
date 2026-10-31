import astropy.units as u
import numpy as np
import pytest

from spacelab.enums import AtmosphereModel
import spacelab.models.atmosphere as atmosphere
import spacelab.physical_constants as constants

def test_thermodynamic_properties_at_zero_altitude():
    
    atm = atmosphere.Atmosphere()

    temperature, pressure, density = atm.thermodynamic_properties(altitude=0 * u.km)

    assert temperature.unit == u.K
    assert pressure.unit == u.Pa
    assert density.unit == u.kg / u.m**3

    assert temperature > 0 * u.K
    assert pressure > 0 * u.Pa
    assert density > 0 * u.kg / u.m**3

def test_thermodynamic_consistency_recomputes_density():
    
    atm = atmosphere.Atmosphere()

    temperature, pressure, density = atm.thermodynamic_properties(altitude=0 * u.km, thermodynamic_consistency=True)

    assert density.unit == u.kg / u.m**3
    
    assert density > 0 * u.kg / u.m**3
    assert temperature > 0 * u.K
    assert pressure > 0 * u.Pa


def test_sample_properties_returns_altitude_grid():
    
    atm = atmosphere.Atmosphere()

    temperatures, pressures, densities = atm.sample_properties([0, 10, 20] * u.km)

    assert len(temperatures) == 3
    assert len(pressures) == 3
    assert len(densities) == 3
    
    assert temperatures[0] > 0
    assert pressures[0] > 0
    assert densities[0] > 0

def test_density():
    
    atm = atmosphere.Atmosphere()
    
    rho, _ = atm.density(altitude=1 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 1.068, atol=1e-3)
    
    rho, _ = atm.density(altitude=3.981 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 7.106e-1, atol=1e-4)
    
    rho, _ = atm.density(altitude=15.849 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 1.401e-1, atol=1e-4)
    
    rho, _ = atm.density(altitude=63.096 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 2.059e-4, atol=1e-7)
    
    rho, _ = atm.density(altitude=251.189 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 5.909e-11, atol=1e-14)
    
    rho, _ = atm.density(altitude=1001.0 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 3.561e-15, atol=1e-18)

@pytest.fixture
def atm():
    return atmosphere.Atmosphere()

@pytest.mark.parametrize("altitude", [None, 1 * u.s, -1 * u.km])
def test_thermodynamic_properties_rejects_invalid_altitude(atm, altitude):
    
    assert atm.thermodynamic_properties(altitude) is None

def test_thermodynamic_properties_rejects_non_boolean_consistency(atm):
    
    assert atm.thermodynamic_properties(0 * u.km, thermodynamic_consistency=1) is None

def test_thermodynamic_properties_consistency_satisfies_gas_law(atm):
    
    temperature, pressure, density = atm.thermodynamic_properties(25 * u.km, thermodynamic_consistency=True)

    expected_density = (pressure / (constants.atmospheric_gas_constant * temperature)).decompose()

    assert density.to_value(u.kg / u.m**3) == pytest.approx(expected_density.to_value(u.kg / u.m**3))

def test_sample_properties_default_grid_returns_1000_samples(atm):
    
    temperatures, pressures, densities = atm.sample_properties()

    assert temperatures.shape == (1000,)
    assert pressures.shape == (1000,)
    assert densities.shape == (1000,)
    assert np.all(np.isfinite(temperatures))
    assert np.all(np.isfinite(pressures))
    assert np.all(np.isfinite(densities))

def test_sample_properties_rejects_negative_altitude_and_invalid_consistency(atm):
    
    assert atm.sample_properties([0 * u.km, -1 * u.km]) is None
    assert atm.sample_properties([0 * u.km], thermodynamic_consistency=1) is None

def test_density_selects_requested_model(atm):
    
    ussa_density, ussa_scale_height = atm.density(1 * u.km, AtmosphereModel.USSA76)
    cira_density, cira_scale_height = atm.density(1 * u.km, AtmosphereModel.CIRA72)

    assert ussa_density.to_value(u.kg / u.m**3) == pytest.approx(1.225 * np.exp(-1 / 7.310))
    assert cira_density.to_value(u.kg / u.m**3) == pytest.approx(1.225 * np.exp(-1 / 7.249))
    assert ussa_scale_height.to_value(u.km) == pytest.approx(7.310)
    assert cira_scale_height.to_value(u.km) == pytest.approx(7.249)
    assert ussa_density != cira_density

def test_density_clamps_altitude_above_model_range(atm):
    
    max_altitude = atm.altitude[-1] * u.km

    at_maximum, scale_height = atm.density(max_altitude)
    above_maximum, above_scale_height = atm.density((atm.altitude[-1] + 100) * u.km)

    assert above_maximum == at_maximum
    assert above_scale_height == scale_height

@pytest.mark.parametrize(
    ("altitude", "model"),
    [
        (1 * u.s, AtmosphereModel.USSA76),
        (-1 * u.km, AtmosphereModel.USSA76),
        (1 * u.km, "USSA76"),
    ],
)
def test_density_rejects_invalid_inputs(atm, altitude, model):
    
    assert atm.density(altitude, model) is None
