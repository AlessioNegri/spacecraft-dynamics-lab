import astropy.units as u
import numpy as np
import pytest

import spacelab.bodies as bd
import spacelab.models.gravitational_multipoles as gm

@pytest.fixture
def multipoles():
    
    previous = gm.GravitationalMultipoles._instances.pop(gm.GravitationalMultipoles, None)
    instance = gm.GravitationalMultipoles()

    yield instance

    gm.GravitationalMultipoles._instances.pop(gm.GravitationalMultipoles, None)
    
    if previous is not None:
        
        gm.GravitationalMultipoles._instances[gm.GravitationalMultipoles] = previous

def test_loads_earth_harmonic_coefficients(multipoles: gm.GravitationalMultipoles):
    
	assert multipoles.C[(2, 2)] == pytest.approx(1.5745e-6)
	assert multipoles.S[(2, 2)] == pytest.approx(-9.0380e-7)
	assert multipoles.J[(2, 0)] == pytest.approx(1.0826266e-3)
	assert multipoles.J[(2, 2)] == pytest.approx(np.hypot(multipoles.C[(2, 2)], multipoles.S[(2, 2)]))
	assert multipoles.L[(2, 2)] == pytest.approx(np.deg2rad(-14.928))

def test_calc_reduced_harmonic_coefficients(multipoles: gm.GravitationalMultipoles):
    
    multipoles.J = {(2, 0): 1.0e-3, (3, 1): -2.0e-6}

    sma: u.Quantity = 7000 * u.km
    ecc: u.Quantity = 0.1 * u.one
    r_e: float = bd.BODIES[bd.Attractor.EARTH].R_E.to_value(u.km)
    p: float = sma.to_value(u.km) * (1 - ecc.value**2)

    assert multipoles.calc_earth_reduced_harmonic_coefficients(sma, ecc)

    assert multipoles.j == pytest.approx({ k: 1.5 * c * (r_e / p) ** k[0] for k, c in multipoles.J.items() })

@pytest.mark.parametrize(
	("semimajor_axis", "eccentricity"),
	[
        (7000, 0.1),
        (7000 * u.km, 0.1),
		(7000 * u.s, 0.1 * u.one),
		(7000 * u.km, 0.1 * u.km),
		(6000 * u.km, 0.1 * u.one),
	]
)
def test_rejects_invalid_inputs(multipoles, semimajor_axis, eccentricity):
    
	assert not multipoles.calc_earth_reduced_harmonic_coefficients(semimajor_axis, eccentricity)
