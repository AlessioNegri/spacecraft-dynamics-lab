import astropy.time as time
import numpy as np

import astro.bodies as bodies

def check_attractor(attractor: str) -> None:
    """Check the validity of the attractor

    Args:
        attractor (str): Main attractor

    Raises:
        TypeError: Wrong type
        ValueError: Wrong name
    """
    
    if not isinstance(attractor, str): raise TypeError("'attractor' must be of type 'str'")
        
    if attractor.lower() not in bodies.BODIES: raise ValueError(f"'attractor' must be one of {bodies.BODIES.keys()}")

def check_position_vector(r: np.ndarray) -> None:
    """Check the validity of the position vector

    Args:
        r (np.ndarray): Position vector

    Raises:
        TypeError: Wrong type
        ValueError: Wrong size
    """
    
    if not isinstance(r, np.ndarray): raise TypeError("'r' must be of type 'numpy.ndarray'")
        
    if r.shape != (3,): raise ValueError("'r' must have shape = (3,)")
    
def check_velocity_vector(v: np.ndarray) -> None:
    """Check the validity of the velocity vector

    Args:
        v (np.ndarray): Velocity vector

    Raises:
        TypeError: Wrong type
        ValueError: Wrong size
    """
    
    if not isinstance(v, np.ndarray): raise TypeError("'v' must be of type 'numpy.ndarray'")
        
    if v.shape != (3,): raise ValueError("'v' must have shape = (3,)")
    
def check_time(time_: time.Time) -> None:
    """Check the validity of the time

    Args:
        time_ (time.Time): Time

    Raises:
        TypeError: Wrong type
    """
    
    if not isinstance(time_, time.Time): raise TypeError("'time_' must be of type 'astropy.time.Time'")
    
def check_time_delta(delta: time.TimeDelta) -> None:
    """Check the validity of the delta time

    Args:
        delta (time.TimeDelta): Time

    Raises:
        TypeError: Wrong type
    """
    
    if not isinstance(delta, time.TimeDelta): raise TypeError("'delta' must be of type 'astropy.time.TimeDelta'")
    
def check_keplerian_parameters(a: float, ecc: float, inc: float, raan: float, argp: float, nu: float) -> None:
    """Check the validity of the keplerian parameters

    Args:
        a (float): Semi-major axis
        ecc (float): Eccentricity
        inc (float): Inclination [deg]
        raan (float): Right ascension of the ascending node [deg]
        argp (float): Argument of periapsis [deg]
        nu (float): True anomaly [deg]
        
    Raises:
        TypeError: Wrong type
        ValueError: Wrong value
    """
    
    if not isinstance(a, float): raise TypeError("'a' must be of type 'float'")
        
    if not isinstance(ecc, float): raise TypeError("'ecc' must be of type 'float'")
    
    if not isinstance(inc, float): raise TypeError("'inc' must be of type 'float'")
    
    if not isinstance(raan, float): raise TypeError("'raan' must be of type 'float'")
    
    if not isinstance(argp, float): raise TypeError("'argp' must be of type 'float'")
    
    if not isinstance(nu, float): raise TypeError("'nu' must be of type 'float'")
    
    if ecc < 1 and a < 0: raise ValueError("'a' must be positive for ellitical orbits")
    
    if ecc > 1 and a > 0: raise ValueError("'a' must be negative for hyperbolic orbits")
    
    if ecc < 0: raise ValueError("'e' must be positive")
    
    if not (0 <= inc <= 180): raise ValueError("'inc' must be in [0, 180] deg")
    
    if not (0 <= raan <= 360): raise ValueError("'raan' must be in [0, 360] deg")
    
    if not (0 <= argp <= 360): raise ValueError("'argp' must be in [-180, 180] deg")
    
    if not (-180 <= nu <= 180): raise ValueError("'nu' must be in [-180, 180] deg")
    
def check_angle(angle: float) -> None:
    """Check the validity of the angle

    Args:
        angle (float): Angle [deg]

    Raises:
        TypeError: Wrong type
        ValueError: Wrong value
    """
    
    if not isinstance(angle, float): raise TypeError("'angle' must be of type 'float'")
    
    if not (-360 <= angle <= 360): raise ValueError("'angle' must be in [-360, +360] deg")