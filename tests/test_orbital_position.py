import astropy.units as u
import numpy as np

import astro.bodies as bodies
from astro.orbital_position import OrbitalPosition

def test_circular_orbit_time():
    
    T: u.Quantity = 1000 * u.s
    t: u.Quantity = OrbitalPosition.circular_orbit_time(nu=360 * u.deg, T=T)
    
    assert np.isclose(t.to_value(u.s), T.to_value(u.s))

def test_circular_orbit_true_anomaly():
    
    T: u.Quantity = 1000 * u.s
    nu: u.Quantity = OrbitalPosition.circular_orbit_true_anomaly(t=T/4, T=T)
    
    assert np.isclose(nu.to_value(u.deg), 90)

def test_elliptical_orbit_time():
    """EXAMPLE 3.1"""
    
    T: u.Quantity = 18834 * u.s
    e: float = 0.37255
    nu: u.Quantity = 120 * u.deg

    t: u.Quantity = OrbitalPosition.elliptical_orbit_time(nu=nu, T=T, e=e)

    assert np.isclose(t.to_value(u.s), 4077, atol=1e-1)
    
def test_elliptical_orbit_true_anomaly():
    """EXAMPLE 3.2"""
    
    T: u.Quantity = 18834 * u.s
    e: float = 0.37255
    t: u.Quantity = 3 * u.hour

    nu: u.Quantity = OrbitalPosition.elliptical_orbit_true_anomaly(t=t, T=T, e=e)

    assert np.isclose(nu.to_value(u.deg), 193.2, atol=1e-1)
    
def test_parabolic_orbit_time():
    """EXAMPLE 3.4"""
    
    h: u.Quantity = 79720 * u.km**2 / u.s
    nu: u.Quantity = 144.75447856886476 * u.deg
    attractor: bodies.Attractor = bodies.Attractor.EARTH

    t: u.Quantity = OrbitalPosition.parabolic_orbit_time(nu=nu, h=h, attractor=attractor)

    assert np.isclose(t.to_value(u.s), 6 * 60 * 60, atol=1e-1)
    
def test_parabolic_orbit_true_anomaly():
    """EXAMPLE 3.4"""
    
    h: u.Quantity = 79720 * u.km**2 / u.s
    t: u.Quantity = 6 * u.hour
    attractor: bodies.Attractor = bodies.Attractor.EARTH

    nu: u.Quantity = OrbitalPosition.parabolic_orbit_true_anomaly(t=t, h=h, attractor=attractor)

    assert np.isclose(nu.to_value(u.deg), 144.75, atol=1e-2)

def test_hyperbolic_orbit_time():
    """EXAMPLE 3.5"""
    
    h: u.Quantity = 100_170 * u.km**2 / u.s
    e: float = 2.7696
    nu: u.Quantity = 100 * u.deg
    attractor: bodies.Attractor = bodies.Attractor.EARTH

    t: u.Quantity = OrbitalPosition.hyperbolic_orbit_time(nu=nu, h=h, e=e, attractor=attractor)

    assert np.isclose(t.to_value(u.s), 4141.4, atol=1e-1)
    
def test_hyperbolic_orbit_true_anomaly():
    """EXAMPLE 3.5"""
    
    h: u.Quantity = 100_170 * u.km**2 / u.s
    e: float = 2.7696
    t: u.Quantity = 4141.4 * u.s + 3 * u.hour
    attractor: bodies.Attractor = bodies.Attractor.EARTH

    nu: u.Quantity = OrbitalPosition.hyperbolic_orbit_true_anomaly(t=t, h=h, e=e, attractor=attractor)

    assert np.isclose(nu.to_value(u.deg), 107.78, atol=1e-2)