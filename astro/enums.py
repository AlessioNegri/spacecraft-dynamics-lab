"""
Container for enums used in astro library
"""

import enum

class OrbitDirection(enum.IntEnum):
    """Orbit direction type"""
    
    PROGRADE    = 0
    RETROGRADE  = 1

class HohmannDirection(enum.IntEnum):
    """List of Hohmann transfer directions"""
    
    PERICENTER_APOCENTER = 0
    APOCENTER_PERICENTER = 1

class SpiralDirection(enum.IntEnum):
    """List of Spiral transfer directions"""
    
    OUTWARD = 0
    INWARD = 1

class ThrustDirection(enum.IntEnum):
    """List of Spiral transfer directions"""
    
    ALONG_VELOCITY = 0
    ALONG_ANGULAR_MOMENTUM = 1

class FlybySide(enum.IntEnum):
    """Type of fly-by"""
    
    DARK_SIDE = 0
    SUNLIT_SIDE = 1
