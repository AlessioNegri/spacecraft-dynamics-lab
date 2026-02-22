"""
Lagrange Coefficients

Implements algorithms for orbital propagation using the classical Lagrange f and g coefficients.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 2: The Two-Body Problem
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import numpy as np

import astro.common as common

class LagrangeCoefficients():
    """Lagrange Coefficients
    """
    
    def __init__(self):
        """Constructor
        """
        
        pass
    
    # --- STATIC ---
    
    @staticmethod
    def propagate_of_angle(attractor: str, r_0 : np.ndarray, v_0 : np.ndarray, delta : float) -> list:
        """Given r_0 and v_0, find r and v after true anomaly changes by delta

        Args:
            r_0 (np.ndarray): Initial position vector [km]
            v_0 (np.ndarray): Initial velocity vector [km/s]
            delta (float): True anomaly variation [deg]

        Returns:
            list: [ r, v ]
        """
        
        common.check_attractor(attractor)
        common.check_position_vector(r_0)
        common.check_velocity_vector(v_0)
        common.check_angle(delta)
        
        mu: float = attractor.mu.to_value() # ? Gravitational constant [km^3 / s^2]
        
        delta = np.deg2rad(delta)
        
        # >>> 1. Magnitudes
        
        r_0_m = np.linalg.norm(r_0)
        v_0_m = np.linalg.norm(v_0)
        
        # >>> 2. Radial Velocity
        
        v_r_0 = np.dot(r_0, v_0) / r_0_m
        
        # >>> 3. Specific Angular momentum
        
        h = r_0_m * np.sqrt(v_0_m**2 - v_r_0**2)
        
        # >>> 4. Radius
        
        r = h**2 / mu * 1 / ( 1 + ( h**2 / (mu * r_0_m) - 1 ) * np.cos(delta) - h * v_r_0 / mu * np.sin(delta) )
        
        # >>> 5. Lagrange coefficients
        
        f = 1 - mu * r / h**2 * (1 - np.cos(delta))
        
        g = r * r_0_m / h * np.sin(delta)
        
        df_dt = mu / h * (1 - np.cos(delta)) / np.sin(delta) * (mu / h**2 * (1 - np.cos(delta)) - 1 / r_0_m - 1 / r)
        
        dg_dt = 1 - mu * r_0_m / h**2 * (1 - np.cos(delta))
        
        return [f * r_0 + g * v_0, df_dt * r_0 + dg_dt * v_0]