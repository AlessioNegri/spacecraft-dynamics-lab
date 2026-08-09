import astropy.units as u

import astro.atmosphere as atmosphere

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
