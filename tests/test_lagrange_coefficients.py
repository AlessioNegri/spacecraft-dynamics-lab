import astropy.time as time
import astropy.units as u
import numpy as np

from astro.lagrange_coefficients import LagrangeCoefficients

def test_propagate_of_angle():
    """EXAMPLE 2.13"""
    
    attractor: str = "earth"
    r_0: np.ndarray = np.array([8182.4, -6865.9, 0])
    v_0: np.ndarray = np.array([0.47572, 8.8116, 0])
    delta: float = 120

    r, v = LagrangeCoefficients.propagate_of_angle(attractor=attractor, r_0=r_0, v_0=v_0, delta=delta)

    assert np.allclose(r, [1454.9, 8251.6, 0], atol=1e-1)
    assert np.allclose(v, [-8.1323, 5.6785, 0], atol=1e-4)
    
def test_universal_kepler_solution():
    """EXAMPLE 3.6"""
    
    attractor: str = "earth"
    r_0: float = 10000
    v_r_0: float = 3.0752
    alpha: float = 1 / (-19655) # ? Reciprocal of the semi-major axis [1/km]
    dt: float = time.TimeDelta(u.Quantity(1, u.hour))

    x: float = LagrangeCoefficients.universal_kepler_solution(attractor=attractor, r_0=r_0, v_r_0=v_r_0, alpha=alpha, dt=dt)

    assert np.isclose(x, 128.51, atol=1e-1)
    
def test_propagate_position_velocity():
    """EXAMPLE 3.7"""
    
    attractor: str = "earth"
    r_0: np.ndarray = np.array([7000, -12124, 0])
    v_0: np.ndarray = np.array([2.6679, 4.6210, 0])
    dt: time.TimeDelta = time.TimeDelta(u.Quantity(1, u.hour))
    
    r, v = LagrangeCoefficients.propagate_position_velocity(attractor=attractor, r_0=r_0, v_0=v_0, dt=dt)
    
    assert np.allclose(r, [-3297.8, 7413.3, 0], atol=1e-1)
    assert np.allclose(v, [-8.2977, -0.96309, 0], atol=1e-3)