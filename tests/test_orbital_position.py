import numpy as np

from astro.orbital_position import OrbitalPosition

def test_circular_orbit_time():
    
    T: float = 1000
    t: float = OrbitalPosition.circular_orbit_time(nu=360, T=T)
    
    assert np.isclose(t, T)

def test_circular_orbit_true_anomaly():
    
    T: float = 1000
    nu: float = OrbitalPosition.circular_orbit_true_anomaly(t=T/4, T=T)
    
    assert np.isclose(nu, 90)

def test_elliptical_orbit_time():
    """EXAMPLE 3.1"""
    
    T: float = 18834
    e: float = 0.37255
    nu: float = 120

    t: float = OrbitalPosition.elliptical_orbit_time(nu=nu, T=T, e=e)

    assert np.isclose(t, 4077, atol=1e-1)
    
def test_elliptical_orbit_true_anomaly():
    """EXAMPLE 3.2"""
    
    T: float = 18834
    e: float = 0.37255
    t: float = 3 * 60 * 60

    nu: float = OrbitalPosition.elliptical_orbit_true_anomaly(t=t, T=T, e=e)

    assert np.isclose(nu, 193.2, atol=1e-1)
    
def test_parabolic_orbit_time():
    """EXAMPLE 3.4"""
    
    h: float = 79720
    nu: float = 144.75447856886476
    attractor: str = "earth"

    t: float = OrbitalPosition.parabolic_orbit_time(nu=nu, h=h, attractor=attractor)

    assert np.isclose(t, 6 * 60 * 60, atol=1e-1)
    
def test_parabolic_orbit_true_anomaly():
    """EXAMPLE 3.4"""
    
    h: float = 79720
    t: float = 6 * 60 * 60
    attractor: str = "earth"

    nu: float = OrbitalPosition.parabolic_orbit_true_anomaly(t=t, h=h, attractor=attractor)

    assert np.isclose(nu, 144.75, atol=1e-2)

def test_hyperbolic_orbit_time():
    """EXAMPLE 3.5"""
    
    h: float = 100_170
    e: float = 2.7696
    nu: float = 100
    attractor: str = "earth"

    t: float = OrbitalPosition.hyperbolic_orbit_time(nu=nu, h=h, e=e, attractor=attractor)

    assert np.isclose(t, 4141.4, atol=1e-1)
    
def test_hyperbolic_orbit_true_anomaly():
    """EXAMPLE 3.5"""
    
    h: float = 100_170
    e: float = 2.7696
    t: float = 4141.4 + 3 * 60 * 60
    attractor: str = "earth"

    nu: float = OrbitalPosition.hyperbolic_orbit_true_anomaly(t=t, h=h, e=e, attractor=attractor)

    assert np.isclose(nu, 107.78, atol=1e-2)