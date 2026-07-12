"""
Container for enums used in astro library
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import enum

class ThrustDirection(enum.IntEnum):
    """List of Spiral transfer directions"""
    
    ALONG_VELOCITY = 0
    ALONG_ANGULAR_MOMENTUM = 1