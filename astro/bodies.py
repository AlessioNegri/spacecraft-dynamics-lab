import astropy.units as u
import dataclasses as dc
import enum
import numpy as np
import typing

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
    T_S     : u.Quantity    # ? Sidereal Orbital Period [terrestrial days]
    semi_major_axis: u.Quantity # ? Semi-Major Axis [km]

@dc.dataclass(frozen=True)
class PlanetaryOrbitalElements:
    semi_major_axis: u.Quantity
    eccentricity: u.Quantity
    inclination: u.Quantity
    right_ascension_of_ascending_node: u.Quantity
    longitude_of_perihelion: u.Quantity # ? argument of perihelion + right ascension of ascending node
    mean_longitude: u.Quantity # ? longitude of perihelion + mean anomaly

@dc.dataclass(frozen=True)
class PlanetaryOrbitalElementsCentennialRates:
    semi_major_axis: u.Quantity
    eccentricity: u.Quantity
    inclination: u.Quantity
    right_ascension_of_ascending_node: u.Quantity
    longitude_of_perihelion: u.Quantity
    mean_longitude: u.Quantity

# --- BODIES ---

BODIES: dict[Attractor, Body] = {}

BODIES[Attractor.SUN] = Body(
    name=Attractor.SUN,
    mu=132712440041.93938 * u.km**3 / u.s**2,
    R_E=695700.0 * u.km,
    J2=None,
    f=None,
    omega=(2 * np.pi / (25.38 * 86400)) * u.rad / u.s,
    M=1.98847e30 * u.kg,
    g_0=274 * u.m / u.s**2,
    T_S=0 * u.day,
    semi_major_axis=0 * u.AU
)

BODIES[Attractor.MERCURY] = Body(
    name=Attractor.MERCURY,
    mu=22031.86855 * u.km**3 / u.s**2,
    R_E=2439.7 * u.km,
    J2=None,
    f=None,
    omega=(2 * np.pi / (58.646 * 86400)) * u.rad / u.s,
    M=3.3011e23 * u.kg,
    g_0=3.7 * u.m / u.s**2,
    T_S=87.969_100_000 * u.day,
    semi_major_axis=0.387_098 * u.AU
)

BODIES[Attractor.VENUS] = Body(
    name=Attractor.VENUS,
    mu=324858.592 * u.km**3 / u.s**2,
    R_E=6051.8 * u.km,
    J2=None,
    f=None,
    omega=(-2 * np.pi / (243.025 * 86400)) * u.rad / u.s,  # ? Retrograde
    M=4.8675e24 * u.kg,
    g_0=8.87 * u.m / u.s**2,
    T_S=224.701_000_000 * u.day,
    semi_major_axis=0.723_332 * u.AU
)

BODIES[Attractor.EARTH] = Body(
    name=Attractor.EARTH,
    mu=398600.4418 * u.km**3 / u.s**2,
    R_E=6378.1363 * u.km,
    J2=1.08262668e-3,
    f=1 / 298.257223563,
    omega=7.2921150e-5 * u.rad / u.s,
    M=5.972168e24 * u.kg,
    g_0=9.80665 * u.m / u.s**2,
    T_S=365.256_363_004 * u.day,
    semi_major_axis=149_598_023 * u.km
)

BODIES[Attractor.MOON] = Body(
    name=Attractor.MOON,
    mu=4902.800066 * u.km**3 / u.s**2,
    R_E=1737.4 * u.km,
    J2=2.03263e-4,
    f=None,
    omega=(2 * np.pi / (27.321661 * 86400)) * u.rad / u.s,
    M=7.34767309e22 * u.kg,
    g_0=1.622 * u.m / u.s**2,
    T_S=27.321_661_000 * u.day,
    semi_major_axis=0.002_570 * u.AU
)

BODIES[Attractor.MARS] = Body(
    name=Attractor.MARS,
    mu=42828.375214 * u.km**3 / u.s**2,
    R_E=3396.19 * u.km,
    J2=1.96045e-3,
    f=1 / 169.8,
    omega=7.0882181e-5 * u.rad / u.s,
    M=6.4171e23 * u.kg,
    g_0=3.72076 * u.m / u.s**2,
    T_S=686.980_000_000 * u.day,
    semi_major_axis=1.523_680_550 * u.AU
)

BODIES[Attractor.JUPITER] = Body(
    name=Attractor.JUPITER,
    mu=126686511.0 * u.km**3 / u.s**2,
    R_E=71492.0 * u.km,
    J2=1.4697e-2,
    f=0.06487,
    omega=1.75853e-4 * u.rad / u.s,
    M=1.8982e27 * u.kg,
    g_0=24.79 * u.m / u.s**2,
    T_S=4_332.590_000_000 * u.day,
    semi_major_axis=5.203_800 * u.AU
)

BODIES[Attractor.SATURN] = Body(
    name=Attractor.SATURN,
    mu=37931207.8 * u.km**3 / u.s**2,
    R_E=60268.0 * u.km,
    J2=1.6298e-2,
    f=0.09796,
    omega=1.63788e-4 * u.rad / u.s,
    M=5.6834e26 * u.kg,
    g_0=10.44 * u.m / u.s**2,
    T_S=10_755.700_000_000 * u.day,
    semi_major_axis=9.582_600 * u.AU
)

BODIES[Attractor.URANUS] = Body(
    name=Attractor.URANUS,
    mu=5793951.0 * u.km**3 / u.s**2,
    R_E=25559.0 * u.km,
    J2=3.34343e-3,
    f=0.02293,
    omega=(-1.01237e-4) * u.rad / u.s,  # ? Retrograde
    M=8.6810e25 * u.kg,
    g_0=8.69 * u.m / u.s**2,
    T_S=30_688.500_000_000 * u.day,
    semi_major_axis=19.191_260 * u.AU
)

BODIES[Attractor.NEPTUNE] = Body(
    name=Attractor.NEPTUNE,
    mu=6836529.0 * u.km**3 / u.s**2,
    R_E=24764.0 * u.km,
    J2=3.411e-3,
    f=0.01708,
    omega=1.08339e-4 * u.rad / u.s,
    M=1.02413e26 * u.kg,
    g_0=11.15 * u.m / u.s**2,
    T_S=60_195.000_000_000 * u.day,
    semi_major_axis=30.070 * u.AU
)

BODIES[Attractor.PLUTO] = Body(
    name=Attractor.PLUTO,
    mu=872.4 * u.km**3 / u.s**2,
    R_E=1188.3 * u.km,
    J2=None,
    f=None,
    omega=(-1.138e-5) * u.rad / u.s,
    M=1.303e22 * u.kg,
    g_0=0.62 * u.m / u.s**2,
    T_S=90_560.000_000_000 * u.day,
    semi_major_axis=39.482 * u.AU
)

def get_body(attractor: Attractor) -> Body: return BODIES[attractor]

# --- EPHEMERIDES ---

julian_century: u.Unit = 36525 * u.day

EPHEMERIDES: typing.Dict[Attractor, typing.Tuple[PlanetaryOrbitalElements, PlanetaryOrbitalElementsCentennialRates]] = {}

EPHEMERIDES[Attractor.MERCURY] = (
    PlanetaryOrbitalElements(
        semi_major_axis=0.38709927 * u.AU,
        eccentricity=0.20563593 * u.dimensionless_unscaled,
        inclination=7.00497902 * u.deg,
        right_ascension_of_ascending_node=48.33076593 * u.deg,
        longitude_of_perihelion=77.45779628 * u.deg,
        mean_longitude=252.25032350 * u.deg
    ),
    PlanetaryOrbitalElementsCentennialRates(
        semi_major_axis=0.00000037 * u.AU / julian_century,
        eccentricity=0.00001906 * u.dimensionless_unscaled / julian_century,
        inclination=-0.00594749 * u.deg / julian_century,
        right_ascension_of_ascending_node=-0.12534081 * u.deg / julian_century,
        longitude_of_perihelion=0.16047689 * u.deg / julian_century,
        mean_longitude=149472.67411175 * u.deg / julian_century
    )
)

EPHEMERIDES[Attractor.VENUS] = (
    PlanetaryOrbitalElements(
        semi_major_axis=0.72333566 * u.AU,
        eccentricity=0.00677672 * u.dimensionless_unscaled,
        inclination=3.39467605 * u.deg,
        right_ascension_of_ascending_node=76.67984255 * u.deg,
        longitude_of_perihelion=131.60246717 * u.deg,
        mean_longitude=181.97909950 * u.deg
    ),
    PlanetaryOrbitalElementsCentennialRates(
        semi_major_axis=0.00000390 * u.AU / julian_century,
        eccentricity=-0.00004107 * u.dimensionless_unscaled / julian_century,
        inclination=-0.00078890 * u.deg / julian_century,
        right_ascension_of_ascending_node=-0.27769418 * u.deg / julian_century,
        longitude_of_perihelion=0.00268329 * u.deg / julian_century,
        mean_longitude=58517.81538729 * u.deg / julian_century
    )
)

EPHEMERIDES[Attractor.EARTH] = (
    PlanetaryOrbitalElements(
        semi_major_axis=1.00000261 * u.AU,
        eccentricity=0.01671123 * u.dimensionless_unscaled,
        inclination=-0.00001531 * u.deg,
        right_ascension_of_ascending_node=0.0 * u.deg,
        longitude_of_perihelion=102.93768193 * u.deg,
        mean_longitude=100.46457166 * u.deg
    ),
    PlanetaryOrbitalElementsCentennialRates(
        semi_major_axis=0.00000562 * u.AU / julian_century,
        eccentricity=-0.00004932 * u.dimensionless_unscaled / julian_century,
        inclination=-0.01294668 * u.deg / julian_century,
        right_ascension_of_ascending_node=0.0 * u.deg / julian_century,
        longitude_of_perihelion=0.32327364 * u.deg / julian_century,
        mean_longitude=35999.37244981 * u.deg / julian_century
    )
)

EPHEMERIDES[Attractor.MARS] = (
    PlanetaryOrbitalElements(
        semi_major_axis=1.52371034 * u.AU,
        eccentricity=0.09339410 * u.dimensionless_unscaled,
        inclination=1.84969142 * u.deg,
        right_ascension_of_ascending_node=49.55953891 * u.deg,
        longitude_of_perihelion=(360 - 23.94362959) * u.deg,
        mean_longitude=(360 - 4.55343205) * u.deg
    ),
    PlanetaryOrbitalElementsCentennialRates(
        semi_major_axis=0.0001847 * u.AU / julian_century,
        eccentricity=0.00007882 * u.dimensionless_unscaled / julian_century,
        inclination=-0.00813131 * u.deg / julian_century,
        right_ascension_of_ascending_node=-0.29257343 * u.deg / julian_century,
        longitude_of_perihelion=0.44441088 * u.deg / julian_century,
        mean_longitude=19140.30268499 * u.deg / julian_century
    )
)

EPHEMERIDES[Attractor.JUPITER] = (
    PlanetaryOrbitalElements(
        semi_major_axis=5.20288700 * u.AU,
        eccentricity=0.04838624 * u.dimensionless_unscaled,
        inclination=1.30439695 * u.deg,
        right_ascension_of_ascending_node=100.47390909 * u.deg,
        longitude_of_perihelion=14.72847983 * u.deg,
        mean_longitude=34.39644501 * u.deg
    ),
    PlanetaryOrbitalElementsCentennialRates(
        semi_major_axis=-0.00011607 * u.AU / julian_century,
        eccentricity=0.00013253 * u.dimensionless_unscaled / julian_century,
        inclination=-0.00183714 * u.deg / julian_century,
        right_ascension_of_ascending_node=0.20469106 * u.deg / julian_century,
        longitude_of_perihelion=0.21252668 * u.deg / julian_century,
        mean_longitude=3034.74612775 * u.deg / julian_century
    )
)

EPHEMERIDES[Attractor.SATURN] = (
    PlanetaryOrbitalElements(
        semi_major_axis=9.53667594 * u.AU,
        eccentricity=0.05386179 * u.dimensionless_unscaled,
        inclination=2.48599187 * u.deg,
        right_ascension_of_ascending_node=113.66242448 * u.deg,
        longitude_of_perihelion=92.59887831 * u.deg,
        mean_longitude=49.95424423 * u.deg
    ),
    PlanetaryOrbitalElementsCentennialRates(
        semi_major_axis=-0.00125060 * u.AU / julian_century,
        eccentricity=-0.00050991 * u.dimensionless_unscaled / julian_century,
        inclination=0.00193609 * u.deg / julian_century,
        right_ascension_of_ascending_node=-0.28867794 * u.deg / julian_century,
        longitude_of_perihelion=-0.41897216 * u.deg / julian_century,
        mean_longitude=1222.49362201 * u.deg / julian_century
    )
)

EPHEMERIDES[Attractor.URANUS] = (
    PlanetaryOrbitalElements(
        semi_major_axis=19.18916464 * u.AU,
        eccentricity=0.04725744 * u.dimensionless_unscaled,
        inclination=0.77263783 * u.deg,
        right_ascension_of_ascending_node=74.01692503 * u.deg,
        longitude_of_perihelion=170.95427630 * u.deg,
        mean_longitude=313.23810451 * u.deg
    ),
    PlanetaryOrbitalElementsCentennialRates(
        semi_major_axis=-0.00196176 * u.AU / julian_century,
        eccentricity=-0.00004397 * u.dimensionless_unscaled / julian_century,
        inclination=-0.00242939 * u.deg / julian_century,
        right_ascension_of_ascending_node=0.04240589 * u.deg / julian_century,
        longitude_of_perihelion=0.40805281 * u.deg / julian_century,
        mean_longitude=424.48202785 * u.deg / julian_century
    )
)

EPHEMERIDES[Attractor.NEPTUNE] = (
    PlanetaryOrbitalElements(
        semi_major_axis=30.06992276 * u.AU,
        eccentricity=0.00859048 * u.dimensionless_unscaled,
        inclination=1.77004347 * u.deg,
        right_ascension_of_ascending_node=131.78422574 * u.deg,
        longitude_of_perihelion=44.96476227 * u.deg,
        mean_longitude=(360 - 55.12002969) * u.deg
    ),
    PlanetaryOrbitalElementsCentennialRates(
        semi_major_axis=0.00026291 * u.AU / julian_century,
        eccentricity=0.00005105 * u.dimensionless_unscaled / julian_century,
        inclination=0.00035372 * u.deg / julian_century,
        right_ascension_of_ascending_node=-0.00508664 * u.deg / julian_century,
        longitude_of_perihelion=-0.32241464 * u.deg / julian_century,
        mean_longitude=218.45945325 * u.deg / julian_century
    )
)

EPHEMERIDES[Attractor.PLUTO] = (
    PlanetaryOrbitalElements(
        semi_major_axis=39.48211675 * u.AU,
        eccentricity=0.24882730 * u.dimensionless_unscaled,
        inclination=17.14001206 * u.deg,
        right_ascension_of_ascending_node=110.30393684 * u.deg,
        longitude_of_perihelion=224.06891629 * u.deg,
        mean_longitude=238.92903833 * u.deg
    ),
    PlanetaryOrbitalElementsCentennialRates(
        semi_major_axis=-0.00031596 * u.AU / julian_century,
        eccentricity=0.00005170 * u.dimensionless_unscaled / julian_century,
        inclination=0.00004818 * u.deg / julian_century,
        right_ascension_of_ascending_node=-0.01183482 * u.deg / julian_century,
        longitude_of_perihelion=-0.04062942 * u.deg / julian_century,
        mean_longitude=145.20780515 * u.deg / julian_century
    )
)

def get_ephemeris(attractor: Attractor) -> typing.Tuple[PlanetaryOrbitalElements, PlanetaryOrbitalElementsCentennialRates]:
    return EPHEMERIDES[attractor]
