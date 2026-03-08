import astropy.time as time
import numpy as np

import astro.bodies as bodies

def check_attractor(attractor: bodies.Attractor) -> None:
    """Check the validity of the attractor

    Args:
        attractor (bodies.Attractor): Main attractor

    Raises:
        TypeError: Wrong type
        ValueError: Wrong name
    """
    
    if not isinstance(attractor, bodies.Attractor): raise TypeError("'attractor' must be of type 'astro.bodies.Attractor'")
        
    if attractor not in bodies.BODIES: raise ValueError(f"'attractor' must be one of {list(bodies.BODIES.keys())}")

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
    
def check_keplerian_parameters(a: float | int,
                               ecc: float | int,
                               inc: float | int,
                               raan: float | int,
                               argp: float | int,
                               nu: float | int) -> None:
    """Check the validity of the keplerian parameters

    Args:
        a (float | int): Semi-major axis
        ecc (float | int): Eccentricity
        inc (float | int): Inclination [deg]
        raan (float | int): Right ascension of the ascending node [deg]
        argp (float | int): Argument of periapsis [deg]
        nu (float | int): True anomaly [deg]
        
    Raises:
        TypeError: Wrong type
        ValueError: Wrong value
    """
    
    if not isinstance(a, float | int): raise TypeError("'a' must be of type 'float' or 'int'")
        
    if not isinstance(ecc, float | int): raise TypeError("'ecc' must be of type 'float' or 'int'")
    
    if not isinstance(inc, float | int): raise TypeError("'inc' must be of type 'float' or 'int'")
    
    if not isinstance(raan, float | int): raise TypeError("'raan' must be of type 'float' or 'int'")
    
    if not isinstance(argp, float | int): raise TypeError("'argp' must be of type 'float' or 'int'")
    
    if not isinstance(nu, float | int): raise TypeError("'nu' must be of type 'float' or 'int'")
    
    if ecc < 1 and a < 0: raise ValueError("'a' must be positive for ellitical orbits")
    
    if ecc > 1 and a > 0: raise ValueError("'a' must be negative for hyperbolic orbits")
    
    if ecc < 0: raise ValueError("'e' must be positive")
    
    if not (0 <= inc <= 180): raise ValueError("'inc' must be in [0, 180] deg")
    
    if not (0 <= raan <= 360): raise ValueError("'raan' must be in [0, 360] deg")
    
    if not (0 <= argp <= 360): raise ValueError("'argp' must be in [-180, 180] deg")
    
    if not (-180 <= nu <= 360): raise ValueError("'nu' must be in [-180, 360] deg")
    
def check_angle(angle: float | int) -> None:
    """Check the validity of the angle

    Args:
        angle (float | int): Angle [deg]

    Raises:
        TypeError: Wrong type
        ValueError: Wrong value
    """
    
    if not isinstance(angle, (float, int)): raise TypeError("'angle' must be of type 'float' or 'int'")
    
    if not (-360 <= angle <= 360): raise ValueError("'angle' must be in [-360, +360] deg")

def wrap_angle(angle: float | int, low: float | int = 0, high: float | int = 360) -> float:
    """Wrap the angle in the range [low, high) deg

    Args:
        low (float | int): Lower bound of the range [deg]
        high (float | int): Upper bound of the range [deg]

    Returns:
        float: Wrapped angle [deg]
    """
    
    if not isinstance(angle, (float, int)): raise TypeError("'angle' must be of type 'float' or 'int'")
    
    wrapped_angle: float = ((angle - low) % (high - low)) + low
    
    return wrapped_angle