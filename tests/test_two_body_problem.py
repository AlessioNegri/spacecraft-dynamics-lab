import astropy.units as u
import numpy as np

from astro.bodies import Attractor
from astro.two_body_problem import OrbitParameters, Orbit

def test_cartesian_to_orbit_parameters_circle():
    """EXAMPLE 2.5"""
    
    r_GEO: float = np.cbrt(398_600 / (72.9217e-6)**2)
    v_GEO: float = np.sqrt(398_600 / r_GEO)
    T_GEO: float = 2 * np.pi * r_GEO**(3/2) / np.sqrt(398_600)
    
    attractor: Attractor = Attractor.EARTH
    r_0: np.ndarray = np.array([r_GEO, 0, 0]) * u.km
    v_0: np.ndarray = np.array([0, v_GEO, 0]) * u.km / u.s

    op: OrbitParameters = Orbit.cartesian_to_orbit_parameters(attractor=attractor, r=r_0, v=v_0)

    assert np.isclose(op.h.to_value(), r_GEO * v_GEO, atol=1e-1)
    assert np.isclose(op.e, 0, atol=1e-4)
    assert np.isclose(op.r_p.to_value(), r_GEO, atol=1e-1)
    assert np.isclose(op.r_a.to_value(), r_GEO, atol=1e-1)
    assert np.isclose(op.a.to_value(), r_GEO, atol=1e-1)
    assert np.isclose(op.b.to_value(), r_GEO, atol=1e-1)
    assert np.isclose(op.T.to_value(), T_GEO, atol=1e-1)
    
def test_cartesian_to_orbit_parameters_ellipse():
    """EXAMPLE 2.7"""
    
    attractor: Attractor = Attractor.EARTH
    r_0: np.ndarray = np.array([6778, 0, 0]) * u.km
    v_0: np.ndarray = np.array([0, 8.435, 0]) * u.km / u.s

    op: OrbitParameters = Orbit.cartesian_to_orbit_parameters(attractor=attractor, r=r_0, v=v_0)

    assert op.conic_type == "ellipse"
    assert np.isclose(op.h.to_value(), 57172, atol=1e-1)
    assert np.isclose(op.e, 0.2098, atol=1e-4)
    assert np.isclose(op.r_p.to_value(), 6778, atol=1e-1)
    assert np.isclose(op.r_a.to_value(), 10378, atol=1e-0)
    assert np.isclose(op.a.to_value(), 8578, atol=1e-0)
    assert np.isclose(op.T.to_value(), 7907, atol=1e-0)
    
def test_cartesian_to_orbit_parameters_parabola():
    """EXAMPLE 2.9"""
    
    attractor: Attractor = Attractor.EARTH
    r_0: np.ndarray = np.array([7000, 0, 0]) * u.km
    v_0: np.ndarray = np.array([0, 74700 / 7000, 0]) * u.km / u.s

    op: OrbitParameters = Orbit.cartesian_to_orbit_parameters(attractor=attractor, r=r_0, v=v_0)
        
    assert np.isclose(op.h.to_value(), 74700, atol=1e-1)
    assert np.isclose(op.e, 1.0, atol=1e-1)
    
def test_cartesian_to_orbit_parameters_hyperbola():
    """EXAMPLE 2.10"""
    
    attractor: Attractor = Attractor.EARTH
    r_0: np.ndarray = np.array([6986, 0, 0]) * u.km
    v_0: np.ndarray = np.array([0, 80708 / 6986, 0]) * u.km / u.s

    op: OrbitParameters = Orbit.cartesian_to_orbit_parameters(attractor=attractor, r=r_0, v=v_0)
    
    assert op.conic_type == "hyperbola"
    assert np.isclose(op.h.to_value(), 80708, atol=1e-1)
    assert np.isclose(op.e, 1.3393, atol=1e-4)
    assert np.isclose(op.r_p.to_value(), 6986, atol=1e-1)
    assert np.isclose(op.a.to_value(), 20590, atol=1e1)
    assert np.isclose(op.v_esc.to_value(), 10.682, atol=1e-3)
    assert np.isclose(op.delta_ta.to_value(), 96.60, atol=1e-1)
    assert np.isclose(op.delta_ar.to_value(), 18340, atol=1e1)
    assert np.isclose(op.v_inf.to_value(), np.sqrt(19.36), atol=1e-0)
    assert np.isclose(op.C_3.to_value(), 19.36, atol=1e-2)