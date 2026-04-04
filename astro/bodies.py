import astropy.units as u
import dataclasses as dc
import enum
import numpy as np

class Attractor(enum.Enum):
    SUN     = "sun"
    MERCURY = "mercury"
    VENUS   = "venus"
    EARTH   = "earth"
    MOON    = "moon"
    MARS    = "mars"
    JUPITER  = "jupiter"
    SATURN   = "saturn"
    URANUS   = "uranus"
    NEPTUNE  = "neptune"
    PLUTO    = "pluto"

@dc.dataclass(frozen=True)
class Body:
    
    name    : str           # ? Name
    mu      : u.Quantity    # ? Gravitational constant [km^3 / s^2]
    R_E     : u.Quantity    # ? Equatorial radius [km]
    J2      : float | None  # ? J2 []
    f       : float | None  # ? Flattening []
    omega   : u.Quantity    # ? Rotation rate [rad/s]
    M       : u.Quantity    # ? Mass [kg]
    g_0     : u.Quantity    # ? Standard gravity [m/s^2]

BODIES: dict[Attractor, Body] = {}

BODIES[Attractor.SUN] = Body(
    name=Attractor.SUN,
    mu=132712440041.93938 * u.km**3 / u.s**2,
    R_E=695700.0 * u.km,
    J2=None,
    f=None,
    omega=(2 * np.pi / (25.38 * 86400)) * u.rad / u.s,
    M=1.98847e30 * u.kg,
    g_0=274 * u.m / u.s**2
)

BODIES[Attractor.MERCURY] = Body(
    name=Attractor.MERCURY,
    mu=22031.86855 * u.km**3 / u.s**2,
    R_E=2439.7 * u.km,
    J2=None,
    f=None,
    omega=(2 * np.pi / (58.646 * 86400)) * u.rad / u.s,
    M=3.3011e23 * u.kg,
    g_0=3.7 * u.m / u.s**2
)

BODIES[Attractor.VENUS] = Body(
    name=Attractor.VENUS,
    mu=324858.592 * u.km**3 / u.s**2,
    R_E=6051.8 * u.km,
    J2=None,
    f=None,
    omega=(-2 * np.pi / (243.025 * 86400)) * u.rad / u.s,  # ? Retrograde
    M=4.8675e24 * u.kg,
    g_0=8.87 * u.m / u.s**2
)

BODIES[Attractor.EARTH] = Body(
    name=Attractor.EARTH,
    mu=398600.4418 * u.km**3 / u.s**2,
    R_E=6378.1363 * u.km,
    J2=1.08262668e-3,
    f=1 / 298.257223563,
    omega=7.2921150e-5 * u.rad / u.s,
    M=5.972168e24 * u.kg,
    g_0=9.80665 * u.m / u.s**2
)

BODIES[Attractor.MOON] = Body(
    name=Attractor.MOON,
    mu=4902.800066 * u.km**3 / u.s**2,
    R_E=1737.4 * u.km,
    J2=2.03263e-4,
    f=None,
    omega=(2 * np.pi / (27.321661 * 86400)) * u.rad / u.s,
    M=7.34767309e22 * u.kg,
    g_0=1.622 * u.m / u.s**2
)

BODIES[Attractor.MARS] = Body(
    name=Attractor.MARS,
    mu=42828.375214 * u.km**3 / u.s**2,
    R_E=3396.19 * u.km,
    J2=1.96045e-3,
    f=1 / 169.8,
    omega=7.0882181e-5 * u.rad / u.s,
    M=6.4171e23 * u.kg,
    g_0=3.72076 * u.m / u.s**2
)

BODIES[Attractor.JUPITER] = Body(
    name=Attractor.JUPITER,
    mu=126686511.0 * u.km**3 / u.s**2,
    R_E=71492.0 * u.km,
    J2=1.4697e-2,
    f=0.06487,
    omega=1.75853e-4 * u.rad / u.s,
    M=1.8982e27 * u.kg,
    g_0=24.79 * u.m / u.s**2
)

BODIES[Attractor.SATURN] = Body(
    name=Attractor.SATURN,

    mu=37931207.8 * u.km**3 / u.s**2,
    R_E=60268.0 * u.km,
    J2=1.6298e-2,
    f=0.09796,
    omega=1.63788e-4 * u.rad / u.s,
    M=5.6834e26 * u.kg,
    g_0=10.44 * u.m / u.s**2
)

BODIES[Attractor.URANUS] = Body(
    name=Attractor.URANUS,
    mu=5793951.0 * u.km**3 / u.s**2,
    R_E=25559.0 * u.km,
    J2=3.34343e-3,
    f=0.02293,
    omega=(-1.01237e-4) * u.rad / u.s,  # ? Retrograde
    M=8.6810e25 * u.kg,
    g_0=8.69 * u.m / u.s**2
)

BODIES[Attractor.NEPTUNE] = Body(
    name=Attractor.NEPTUNE,
    mu=6836529.0 * u.km**3 / u.s**2,
    R_E=24764.0 * u.km,
    J2=3.411e-3,
    f=0.01708,
    omega=1.08339e-4 * u.rad / u.s,
    M=1.02413e26 * u.kg,
    g_0=11.15 * u.m / u.s**2
)

BODIES[Attractor.PLUTO] = Body(
    name=Attractor.PLUTO,
    mu=872.4 * u.km**3 / u.s**2,
    R_E=1188.3 * u.km,
    J2=None,
    f=None,
    omega=(-1.138e-5) * u.rad / u.s,
    M=1.303e22 * u.kg,
    g_0=0.62 * u.m / u.s**2
)

def get_body(attractor: Attractor) -> Body: return BODIES[attractor]