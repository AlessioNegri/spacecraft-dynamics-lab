"""
Container for enums used in astro library
"""

import astropy.units as u
import enum
import typing

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

class Hemisphere(enum.Enum):
    """Hemisphere region"""
    
    NORTH = "N"
    SOUTH = "S"
    EQUATOR = "EQ"
    EAST = "E"
    WEST = "W"

class AngleHemisphere(typing.NamedTuple):
    """Tuple with angle and hemisphere"""
    
    angle: u.Quantity
    hemisphere: Hemisphere
    
    def to_signed_angle(self) -> u.Quantity:
        
        if self.hemisphere == Hemisphere.NORTH:
            
            return self.angle
        
        elif self.hemisphere == Hemisphere.SOUTH:
            
            return -self.angle

        elif self.hemisphere == Hemisphere.EAST:
                    
            return self.angle
        
        elif self.hemisphere == Hemisphere.WEST:
            
            return -self.angle

        elif self.hemisphere == Hemisphere.EQUATOR:
            
            return 0 * u.deg
        
        else:
            
            return 0 * u.deg

class ClosingApproachStrategy(enum.Enum):
    """Closing approach strategy"""
    
    R_BAR_POS = 0
    R_BAR_NEG = 1
    V_BAR_POS = 2
    V_BAR_NEG = 3

class ClosingApproachTrajectory(enum.Enum):
    """Closing approach trajectory"""
    
    ELLIPTIC    = 0
    CYCLOIDAL   = 1