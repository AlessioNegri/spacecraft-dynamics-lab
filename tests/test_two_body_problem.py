import astropy.units as u
import numpy as np

from astro.bodies import Attractor
from astro.two_body_problem import OrbitParameters, Orbit

def test_cartesian_to_orbit_parameters_circle():
    """EXAMPLE 2.5"""
    
    r_geo: float = np.cbrt(398_600 / (72.9217e-6)**2)
    v_geo: float = np.sqrt(398_600 / r_geo)
    period_geo: float = 2 * np.pi * r_geo**(3/2) / np.sqrt(398_600)
    
    attractor: Attractor = Attractor.EARTH
    r_0: np.ndarray = np.array([r_geo, 0, 0]) * u.km
    v_0: np.ndarray = np.array([0, v_geo, 0]) * u.km / u.s

    op: OrbitParameters = Orbit.cartesian_to_orbit_parameters(attractor=attractor, position=r_0, velocity=v_0)
    
    assert op.conic_type == "circle"
    assert np.isclose(op.specific_angular_momentum.to_value(), r_geo * v_geo, atol=1e-1)
    assert np.isclose(op.eccentricity, 0, atol=1e-4)
    assert np.isclose(op.periapsis_radius.to_value(), r_geo, atol=1e-1)
    assert np.isclose(op.apoapsis_radius.to_value(), r_geo, atol=1e-1)
    assert np.isclose(op.semimajor_axis.to_value(), r_geo, atol=1e-1)
    assert np.isclose(op.semiminor_axis.to_value(), r_geo, atol=1e-1)
    assert np.isclose(op.period.to_value(), period_geo, atol=1e-1)
    
def test_cartesian_to_orbit_parameters_ellipse():
    """EXAMPLE 2.7"""
    
    attractor: Attractor = Attractor.EARTH
    r_0: np.ndarray = np.array([6778, 0, 0]) * u.km
    v_0: np.ndarray = np.array([0, 8.435, 0]) * u.km / u.s

    op: OrbitParameters = Orbit.cartesian_to_orbit_parameters(attractor=attractor, position=r_0, velocity=v_0)

    assert op.conic_type == "ellipse"
    assert np.isclose(op.specific_angular_momentum.to_value(), 57172, atol=1e-1)
    assert np.isclose(op.eccentricity, 0.2098, atol=1e-4)
    assert np.isclose(op.periapsis_radius.to_value(), 6778, atol=1e-1)
    assert np.isclose(op.apoapsis_radius.to_value(), 10378, atol=1e-0)
    assert np.isclose(op.semimajor_axis.to_value(), 8578, atol=1e-0)
    assert np.isclose(op.period.to_value(), 7907, atol=1e-0)
    
def test_cartesian_to_orbit_parameters_parabola():
    """EXAMPLE 2.9"""
    
    attractor: Attractor = Attractor.EARTH
    r_0: np.ndarray = np.array([7000, 0, 0]) * u.km
    v_0: np.ndarray = np.array([0, 74700 / 7000, 0]) * u.km / u.s

    op: OrbitParameters = Orbit.cartesian_to_orbit_parameters(attractor=attractor, position=r_0, velocity=v_0)
    
    assert op.conic_type == "parabola"
    assert np.isclose(op.specific_angular_momentum.to_value(), 74700, atol=1e-1)
    assert np.isclose(op.eccentricity, 1.0, atol=1e-1)
    
def test_cartesian_to_orbit_parameters_hyperbola():
    """EXAMPLE 2.10"""
    
    attractor: Attractor = Attractor.EARTH
    r_0: np.ndarray = np.array([6986, 0, 0]) * u.km
    v_0: np.ndarray = np.array([0, 80708 / 6986, 0]) * u.km / u.s

    op: OrbitParameters = Orbit.cartesian_to_orbit_parameters(attractor=attractor, position=r_0, velocity=v_0)
    
    assert op.conic_type == "hyperbola"
    assert np.isclose(op.specific_angular_momentum.to_value(), 80708, atol=1e-1)
    assert np.isclose(op.eccentricity, 1.3393, atol=1e-4)
    assert np.isclose(op.periapsis_radius.to_value(), 6986, atol=1e-1)
    assert np.isclose(op.semimajor_axis.to_value(), -20590, atol=1e1)
    assert np.isclose(op.escape_velocity.to_value(), 10.682, atol=1e-3)
    assert np.isclose(op.turning_angle.to_value(), 96.60, atol=1e-1)
    assert np.isclose(op.aiming_radius.to_value(), 18340, atol=1e1)
    assert np.isclose(op.hyperbolic_excess_speed.to_value(), np.sqrt(19.36), atol=1e-0)
    assert np.isclose(op.characteristic_energy.to_value(), 19.36, atol=1e-2)

def test_cartesian_to_orbit_parameters_line():
    """EXAMPLE 2.7"""
    
    attractor: Attractor = Attractor.EARTH
    r_0: np.ndarray = np.array([6778, 0, 0]) * u.km
    v_0: np.ndarray = np.array([8.435, 0 , 0]) * u.km / u.s

    op: OrbitParameters = Orbit.cartesian_to_orbit_parameters(attractor=attractor, position=r_0, velocity=v_0)

    assert op.conic_type == "line"