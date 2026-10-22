"""
Orbital Perturbations

Implements the orbital perturbations

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 12: Introduction to Orbital Perturbations

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 5: Non-Keplerian Motion
    
- Ulrich Walter, "Astronautics - The Physics of Space Flight"
    - Chapter 12: Orbit Perturbations
"""

import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.integrate as ode
import typing

import spacelab.physical_constants as physical_constants
import spacelab.bodies as bodies
import spacelab.common as common
import spacelab.lagrange_coefficients as lc
import spacelab.orbit_3d as o3d
import spacelab.orbit_determination as od

from spacelab.enums import AtmosphereModel

from spacelab.models.results import ResultOP
from spacelab.models.orbital_elements import OrbitalElements
from spacelab.models.gravity_harmonics import GravityHarmonics

class OrbitalPerturbations():
    """Orbital Perturbations"""
    
    def __init__(self):
        """Constructor"""
        
        self.not_ready_message: str = "Orbital Perturbations object is not ready"
        
        self.ready: bool = False
        
        self.attractor: bodies.Attractor = bodies.Attractor.EARTH
        
        self.julian_day: float = od.OrbitDetermination.J2000
        
        self.position: np.ndarray = np.zeros(3)
        
        self.velocity: np.ndarray = np.zeros(3)
        
        self.ballistic_coefficient: u.Quantity = 0 * u.m**2 / u.kg # ? (C_D * A / m)
        
        self.ballistic_coefficient_srp: u.Quantity = 0 * u.m**2 / u.kg # ? (C_R * A_s / m)
        
        self.use_atmospheric_drag: bool = False
        
        self.use_gravitational_perturbation: bool = False
        
        self.use_solar_radiation_pressure: bool = False
        
        self.use_lunar_gravity: bool = False
        
        self.use_solar_gravity: bool = False
    
    # --- STATIC ---
    
    @staticmethod
    def earth_harmonic_coefficients() -> GravityHarmonics:
        """
        Multipole coefficients of Earth's gravitational potential

        Returns:
            GravityHarmonics: Multipole coefficients
        """
        
        earth_gravity_harmonics: GravityHarmonics = GravityHarmonics(
            C={
                (0,0): 1.0,
                
                (1,0): 0.0,
                (1,1): 0.0,
                
                (2,0): -1.082627e-03,
                (2,1): +0.0,
                (2,2): +1.5745e-06,
                
                (3,0): +2.5326e-06,
                (3,1): -2.1926e-06,
                (3,2): +3.0899e-07,
                (3,3): -1.0055e-07,
                
                (4,0): +1.6196e-06,
                (4,1): +5.0880e-07,
                (4,2): +7.8418e-08,
                (4,3): -5.9210e-08,
                (4,4): -3.9841e-09,
                
                (5,0): -2.2730e-07,
                (5,1): +5.3180e-08,
                (5,2): +1.0559e-07,
                (5,3): +1.4930e-08,
                (5,4): -2.2993e-09,
                (5,5): -4.3082e-10,
            },

            S={
                (0,0): 0.0,
                
                (1,0): 0.0,
                (1,1): 0.0,
                
                (2,0): 0.0,
                (2,1): 0.0,
                (2,2): -9.0380e-07,
                
                (3,0): 0.0,
                (3,1): -2.6843e-07,
                (3,2): -2.1144e-07,
                (3,3): -1.9722e-07,
                
                (4,0): 0.0,
                (4,1): +4.4917e-07,
                (4,2): +1.4818e-07,
                (4,3): +1.2008e-08,
                (4,4): +6.5257e-09,
                
                (5,0): 0,
                (5,1): +8.0859e-08,
                (5,2): -5.2329e-08,
                (5,3): +7.0973e-09,
                (5,4): +3.8671e-10,
                (5,5): +1.6482e-09,
            },

            J={
                (2,0): 1.0826266e-3,
                (3,0): -2.5326e-6,
                (4,0): -1.6196e-6,
                (5,0): -2.2730e-7,
                (6,0):  5.4068e-7,
                (7,0): -3.5236e-7,
                (9,0): -1.2062e-7,
            },
            
            L={
                (2, 2): np.deg2rad(-14.928),
                
                (3, 1): np.deg2rad(-173.01),
                (3, 2): np.deg2rad(-17.192),
                (3, 3): np.deg2rad(-39.005),
                
                (4, 1): np.deg2rad(+41.436),
                (4, 2): np.deg2rad(+31.056),
                (4, 3): np.deg2rad(+56.180),
                (4, 4): np.deg2rad(+30.351),
                
                (5, 1): np.deg2rad(+56.667),
                (5, 2): np.deg2rad(-13.182),
                (5, 3): np.deg2rad(+8.4751),
                (5, 4): np.deg2rad(+42.613),
                (5, 5): np.deg2rad(+20.930),
            }
        )
        
        for (n, m) in earth_gravity_harmonics.C.keys():
            
            if (n, m) not in earth_gravity_harmonics.J:
                
                earth_gravity_harmonics.J[(n, m)] = np.sqrt(
                    earth_gravity_harmonics.C[(n, m)]**2 +
                    earth_gravity_harmonics.S[(n, m)]**2
                )
        
        return earth_gravity_harmonics
    
    @staticmethod
    def earth_reduced_harmonic_coefficients(semimajor_axis: u.Quantity,
                                            eccentricity: u.Quantity) -> typing.Dict[typing.Tuple[int, int], float]:
        """
        Calculate the earth reduced harmonic coefficients j_nm for a given semimajor axis and eccentricity orbit

        Args:
            semimajor_axis (u.Quantity): Semimajor axis
            eccentricity (u.Quantity): Eccentricity

        Returns:
            typing.Dict[typing.Tuple[int, int], float]: Reduced harmonic coefficients j_nm
        """
        
        R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km)
        
        sma: float = semimajor_axis.to_value(u.km)
        
        ecc: float = eccentricity.to_value(u.one)
        
        earth_harmonics: GravityHarmonics = OrbitalPerturbations.earth_harmonic_coefficients()

        semilatus_rectum: float = sma * (1 - ecc**2)
        
        j_nm: typing.Dict[typing.Tuple[int, int], float] =\
            {
                (n, m):
                    3 / 2 * earth_harmonics.J[(n, m)] * (R_E / semilatus_rectum)**n
                    for (n, m) in earth_harmonics.J.keys()
            }
        
        return j_nm
    
    @staticmethod
    def density(altitude: u.Quantity, model: AtmosphereModel = AtmosphereModel.USSA76) -> typing.List[u.Quantity]:
        """
        Calculates the atmospheric density given the altitude above the Earth using one of the following models:
        
        - *USSA76* piecewise exponential model
        - *CIRA-72* piecewise exponential model

        Note
        -----
        The given altitude is located in the values of the altitude ranges. For example, and altitude of 249 km will be
        located in the range 200-250 but uses the value of 200 km reference altitude.
        
        Args:
            altitude (u.Quantity): Altitude
            model (AtmosphereModel, optional): Atmosphere model. Defaults to AtmosphereModel.USSA76.

        Returns:
            typing.List[u.Quantity]: Density and scale height [rho_z, H_z]
        """
        
        z: float = altitude.to_value(u.km)
        
        # >>> 1. Geometric altitudes [km] (1 x 28)
        
        h: np.ndarray = np.array(
            [
                0, 25, 30, 40, 50, 60, 70, 80, 90, 100,
                110, 120, 130, 140, 150, 180, 200, 250, 300, 350,
                400, 450, 500, 600, 700, 800, 900, 1000
            ])
        
        # >>> 2. Corresponding densities [kg / m^3] from USSA76 (1 x 28)
        
        rho_USSA76: np.ndarray = np.array(
            [
                1.225, 4.008e-2, 1.841e-2, 3.996e-3, 1.027e-3,
                3.097e-4, 8.283e-5, 1.846e-5, 3.416e-6, 5.606e-7,
                9.708e-8, 2.222e-8, 8.152e-9, 3.831e-9, 2.076e-9,
                5.194e-10, 2.541e-10, 6.073e-11, 1.916e-11, 7.014e-12,
                2.803e-12, 1.184e-12, 5.215e-13, 1.137e-13, 3.070e-14,
                1.136e-14, 5.759e-15, 3.561e-15
            ])
        
        rho_CIRA: np.ndarray = np.array(
            [
                1.225, 3.899e-2, 1.774e-2, 3.972e-3, 1.057e-3,
                3.206e-4, 8.770e-5, 1.905e-5, 3.396e-6, 5.297e-7,
                9.661e-8, 2.438e-8, 8.484e-9, 3.845e-9, 2.070e-9,
                5.464e-10, 2.789e-10, 7.248e-11, 2.418e-11, 9.518e-12,
                3.725e-12, 1.585e-12, 6.967e-13, 1.454e-13, 3.614e-14,
                1.170e-14, 5.245e-15, 3.019e-15
            ])
        
        # >>> 3. Scale heights [km] (1 x 27)

        H_USSA76: np.ndarray = np.array(
            [
                7.310, 6.427, 6.546, 7.360, 8.342,
                7.583, 6.661, 5.927, 5.533, 5.703,
                6.782, 9.973, 13.243, 16.322, 21.652,
                27.974, 34.934, 43.342, 49.755, 54.513,
                58.019, 60.980, 65.654, 76.377, 100.587,
                147.203, 208.020
            ])
        
        H_CIRA: np.ndarray = np.array(
            [
                7.249, 6.349, 6.682, 7.554, 8.382,
                7.714, 6.549, 5.799, 5.382, 5.877,
                7.263, 9.473, 12.636, 16.149, 22.523,
                29.740, 37.105, 45.546, 53.628, 53.298,
                58.515, 60.828, 63.822, 71.835, 88.667,
                124.64, 181.05, 268.00
            ])
        
        # >>> 4. Handle altitudes outside of the range
        
        if z > h[-1]:
            
            z = h[-1]
            
        elif z < h[0]:
            
            print(f"Warning: altitude is below {h[0]} km, using density at {h[0]} km")
            
            z = h[0]
        
        # >>> 5. Determine the interpolation interval
        
        rho: float = 0.0
        H: float = 0.0
        
        if model == AtmosphereModel.USSA76:
            
            rho = rho_USSA76
            H = H_USSA76
        
        elif model == AtmosphereModel.CIRA72:
            
            rho = rho_CIRA
            H = H_CIRA
        
        else:
            
            print("Warning: model not available")
            
            return [0 * kg / m**3, 0 * u.km]
        
        idx: int = np.searchsorted(h, z) - 1
        
        idx = np.clip(idx, 0, len(H) - 1)
        
        # >>> 6. Exponential interpolation
        
        rho_z: u.Quantity = rho[idx] * np.exp(-(z - h[idx]) / H[idx]) * u.kg / u.m**3
        
        return rho_z, H[idx] * u.km
    
    @staticmethod
    def sun_position(timestamp: time.Time) -> typing.List[u.Quantity]:
        """        
        Given the year, month, day, and universal time, calculate the obliquity of the ecliptic ε, ecliptic longitude of
        the Sun λ, and the geocentric position vector of the Sun r_sun with respect to the Earth based on the
        Astronomical Almanac

        Args:
            timestamp (time.Time): UTC timestamp

        Returns:
            typing.List[u.Quantity]: [Sun position vector in GEF, apparent ecliptic longitude, obliquity]
        """
        
        # >>> 1. Julian day number
        
        JD: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp=timestamp)
        
        # >>> 2. Number of days since J2000
        
        n: float = JD - od.OrbitDetermination.J2000
        
        # >>> 3. Mean anonaly of the Sun (deg)
        
        M: float = common.wrap_angle(357.529 + 0.98560023 * n)
        
        # >>> 4. Mean longitude of the Sun (deg)
        
        L: float = common.wrap_angle(280.459 + 0.98564736 * n)
        
        # >>> 5. Apparent Solar Ecliptic Longitude
        
        lambda_: float = common.wrap_angle(L + 1.915 * np.sin(np.deg2rad(M)) + 0.0200 * np.sin(2 * np.deg2rad(M)))
        
        # >>> 6. Obliquity
        
        epsilon: float = common.wrap_angle(23.439 - 3.56e-7 * n)
        
        # >>> 7. Earth-Sun unit direction vector
        
        u_earth_sun: np.ndarray = np.array([np.cos(np.deg2rad(lambda_)),
                                            np.sin(np.deg2rad(lambda_)) * np.cos(np.deg2rad(epsilon)),
                                            np.sin(np.deg2rad(lambda_)) * np.sin(np.deg2rad(epsilon))])
        
        # >>> 8. Earth-Sun distance
        
        r_earth_sun: float = (1.00014 - 0.01671 * np.cos(np.deg2rad(M)) - 0.000140 * np.cos(2 * np.deg2rad(M)))
        
        # >>> 9. Sun Geocentric position vector
        
        r_sun: u.Quantity = r_earth_sun * u_earth_sun * u.au
        
        return [r_sun, lambda_ * u.deg, epsilon * u.deg]
    
    @staticmethod
    def earth_shadow(spacecraft_position: u.Quantity, sun_position: u.Quantity) -> int:
        """
        Given the position vector of a satellite and the apparent position vector of the sun, both in geocentric
        equatorial frame (GEF), determine the value of the shadow function (0 = shadow, 1 = light)

        Args:
            spacecraft_position (u.Quantity): Spacecraft position vector
            sun_position (u.Quantity): Sun position vector

        Returns:
            int: Shadow function value (0 -> in shadow, 1 -> in light)
        """
        
        r_sc: np.ndarray = spacecraft_position.to_value(u.km)
        
        r_sun: np.ndarray = sun_position.to_value(u.km)
        
        common.check_position_vector(r_sc)
        
        common.check_position_vector(r_sun)
        
        R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km) # ? Earth radius
        
        # >>> 1. Magnitudes
        
        r_sc_norm: float = np.linalg.norm(r_sc)
        
        r_sun_norm: float = np.linalg.norm(r_sun)
        
        # >>> 2. Angle between position vectors
        
        theta: float = np.arccos(np.dot(r_sun, r_sc) / (r_sun_norm * r_sc_norm))
        
        # >>> 3. Inner angles
        
        theta_1: float = np.arccos(R_E / r_sun_norm)
        
        theta_2: float = np.arccos(R_E / r_sc_norm)
        
        # >>> 4. Shadow condition
        
        return 0 if theta_1 + theta_2 <= theta else 1
    
    @staticmethod
    def moon_position(timestamp: time.Time) -> u.Quantity:
        """
        Given the year, month, day, and universal time, calculate the geocentric position vector of the Moon with
        respect to the Earth based on the Astronomical Almanac

        Args:
            timestamp (time.Time): UTC timestamp

        Returns:
            u.Quantity: Moon position vector in GEF
        """
        
        # >>> 0. Coefficients for computing lunar position
        
        # * Longitude lambda_
        
        b_0: float = 218.32
        c_0: float = 481_267.881
        
        a: typing.List[float] = [ 6.29, -1.27, 0.66, 0.21, -0.19, -0.11 ]
        b: typing.List[float] = [ 135.0, 259.3, 235.7, 269.9, 357.5, 106.5 ]
        c: typing.List[float] = [ 477_198.87, -413_335.36, 890_534.22, 954_397.74, 35_999.05, 966_404.03 ]
        
        # * Latitude delta
        
        d: typing.List[float] = [ 5.13, 0.28, -0.28, -0.17 ]
        e: typing.List[float] = [ 93.3, 220.2, 318.3, 217.6 ]
        f: typing.List[float] = [ 483_202.03, 960_400.89, 6_003.15, -407_332.21 ]
        
        # * Horizontal Parallax HP
        
        g_0: float = 0.9508
        
        g: typing.List[float] = [ 0.0518, 0.0095, 0.0078, 0.0028 ]
        h: typing.List[float] = [ 135.0, 259.3, 253.7, 269.9 ]
        k: typing.List[float] = [ 477_198.87, -413_335.38, 890_534.22, 954_397.70 ]
        
        # >>> 1. Julian day number
        
        JD: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp=timestamp)
        
        # >>> 2. Number of Julian centuries since J2000
        
        T_0: float = (JD - od.OrbitDetermination.J2000) / 36_525
        
        # >>> 3. Obliquity
        
        epsilon: float = common.wrap_angle(23.439 - 0.0130042 * T_0)
        
        # >>> 4. Lunar ecliptic longitude
        
        lambda_: float = common.wrap_angle(b_0 + c_0 * T_0 + sum([a[i] * np.sin(np.deg2rad(b[i] + c[i] * T_0)) for i in range(0, 6)]))
        
        # >>> 5. Lunar ecliptic latitude
        
        delta: float = common.wrap_angle(sum([d[i] * np.sin(np.deg2rad(e[i] + f[i] * T_0)) for i in range(0, 4)]))
        
        # >>> 6. Lunar horizontal parallax
        
        HP: float = common.wrap_angle(g_0 + sum([g[i] * np.cos(np.deg2rad(h[i] + k[i] * T_0)) for i in range(0, 4)]), high=180)
        
        # >>> 7. Earth-Moon distance
        
        r_earth_moon: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km) / np.sin(np.deg2rad(HP))
        
        # >>> 8. Earth-Moon unit direction vector
        
        epsilon_rad: float = np.deg2rad(epsilon)
        
        delta_rad: float = np.deg2rad(delta)
        
        lambda_rad: float = np.deg2rad(lambda_)
        
        u_earth_moon: np.ndarray = np.array([
            np.cos(delta_rad) * np.cos(lambda_rad),
            np.cos(epsilon_rad) * np.cos(delta_rad) * np.sin(lambda_rad) - np.sin(epsilon_rad) * np.sin(delta_rad),
            np.sin(epsilon_rad) * np.cos(delta_rad) * np.sin(lambda_rad) + np.cos(epsilon_rad) * np.sin(delta_rad)])
        
        # >>> 9. Moon Geocentric position vector
        
        r_moon: u.Quantity = r_earth_moon * u_earth_moon * u.km
        
        return r_moon
    
    @staticmethod
    def nodal_regression_rate(attractor: bodies.Attractor,
                              orbital_elements: OrbitalElements) -> typing.List[u.Quantity]:
        """
        Calculate the nodal regression rate (right ascension of the ascending node) due to:
        - J2 perturbation
        - Lunar gravity
        - Solar gravity

        Args:
            attractor (bodies.Attractor): Main attractor
            orbital_elements (OrbitalElements): Orbital elements

        Returns:
            typing.List[u.Quantity]: Nodal regression rates [deg / day]
        """
        
        common.check_orbital_elements(orbital_elements)
        
        # >>> Parameters
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        R_E: float = bodies.BODIES[attractor].R_E.to_value(u.km)
        
        J_2: float = bodies.BODIES[attractor].J2.to_value(u.one)
        
        a: float = orbital_elements.semimajor_axis.to_value(u.km)
        
        e: float = orbital_elements.eccentricity.to_value(u.dimensionless_unscaled)
        
        inc: float = orbital_elements.inclination.to_value(u.rad)
        
        period: float = orbital_elements.calc_orbital_period(attractor=attractor).to_value(u.hour)
        
        num_revolutions: float = 24 / period
        
        # >>> Nodal regression rate - gravitational perturbation
        
        if bodies.BODIES[attractor].J2 is None:
            
            dOmega_dt_g: float = 0.0 * u.rad / u.s
        
        else:
        
            coefficient: float = - 3 / 2 * J_2 * np.sqrt(mu) * R_E**2 / (a**(7/2) * (1 - e**2)**2)
        
            dOmega_dt_g: u.Quantity = coefficient * np.cos(inc) * u.rad / u.s
        
        # >>> Nodal regression rate - lunar gravity
        
        dOmega_dt_l: u.Quantity = -0.00338 / num_revolutions * np.cos(inc) * u.deg / u.day
        
        # >>> Nodal regression rate - solar gravity
        
        dOmega_dt_s: u.Quantity = -0.00154 / num_revolutions * np.cos(inc) * u.deg / u.day
        
        return [dOmega_dt_g.to(u.deg / u.day), dOmega_dt_l, dOmega_dt_s]
    
    @staticmethod
    def sun_synchronous_inclination(attractor: bodies.Attractor,
                                    orbital_elements: OrbitalElements,
                                    nodal_regression_rate: u.Quantity) -> u.Quantity:
        """
        Calculate the sun-synchronous inclination for a given semimajor axis and eccentricity

        Args:
            attractor (bodies.Attractor): Main attractor
            orbital_elements (OrbitalElements): Orbital elements
            nodal_regression_rate (u.Quantity): Nodal regression rate
        Returns:
            u.Quantity: Sun-synchronous inclination [deg]
        """
        
        common.check_orbital_elements(orbital_elements)
        
        if bodies.BODIES[attractor].J2 is None: return 0.0 * u.deg
        
        # >>> Parameters
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        R_E: float = bodies.BODIES[attractor].R_E.to_value(u.km)
        
        J_2: float = bodies.BODIES[attractor].J2.to_value(u.one)
        
        a: float = orbital_elements.semimajor_axis.to_value(u.km)
        
        e: float = orbital_elements.eccentricity.to_value(u.dimensionless_unscaled)
        
        dOmega_dt: float = nodal_regression_rate.to_value(u.rad / u.s)
        
        # >>> Sun-synchronous inclination
        
        inc: float = np.arccos(- 2 / 3 * dOmega_dt * (a**(7/2) * (1 - e**2)**2) / (J_2 * np.sqrt(mu) * R_E**2))
        
        return u.Quantity(inc, unit=u.rad).to(u.deg)
    
    @staticmethod
    def apsidal_rotation_rate(attractor: bodies.Attractor,
                              orbital_elements: OrbitalElements) -> typing.List[u.Quantity]:
        """
        Calculate the apsidal rotation rate (argument of periapsis) due to:
        - J2 perturbation
        - Lunar gravity
        - Solar gravity

        Args:
            attractor (bodies.Attractor): Main attractor
            orbital_elements (OrbitalElements): Orbital elements

        Returns:
            typing.List[u.Quantity]: Apsidal rotation rates [deg / day]
        """
        
        common.check_orbital_elements(orbital_elements)
        
        # >>> Parameters
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        R_E: float = bodies.BODIES[attractor].R_E.to_value(u.km)
        
        J_2: float = bodies.BODIES[attractor].J2.to_value(u.one)
        
        a: float = orbital_elements.semimajor_axis.to_value(u.km)
        
        e: float = orbital_elements.eccentricity.to_value(u.dimensionless_unscaled)
        
        inc: float = orbital_elements.inclination.to_value(u.rad)
        
        period: float = orbital_elements.calc_orbital_period(attractor=attractor).to_value(u.hour)
        
        num_revolutions: float = 24 / period
        
        # >>> Apsidal rotation rate - gravitational perturbation
        
        if bodies.BODIES[attractor].J2 is None:
            
             domega_dt_g: u.Quantity = 0.0 * u.rad / u.s
        
        else:
            
            coefficient: float = - 3 / 2 * J_2 * np.sqrt(mu) * R_E**2 / (a**(7/2) * (1 - e**2)**2)
        
            domega_dt_g: u.Quantity = coefficient * (5 / 2 * np.sin(inc)**2 - 2) * u.rad / u.s
        
        # >>> Apsidal rotation rate - lunar gravity
        
        domega_dt_l: u.Quantity = 0.00169 / num_revolutions * (4 - 5 * np.sin(inc)**2) * u.deg / u.day
        
        # >>> Apsidal rotation rate - solar gravity
        
        domega_dt_s: u.Quantity = 0.00077 / num_revolutions * (4 - 5 * np.sin(inc)**2) * u.deg / u.day
        
        return [domega_dt_g.to(u.deg / u.day), domega_dt_l, domega_dt_s]
    
    @staticmethod
    def frozen_orbit_type_1() -> u.Quantity:
        """
        Orbits that aside from a_dot and i_dot = 0 also exhibit the properties e_dot and omega_dot = 0 are
        called *frozen orbits* because the rotation of the apse line is stopped.
        
        If the expression 1 - 5/4 * sin(i)**2 = 0, i.e. if an orbit maintains the critical inclination, the orbit is
        frozen. These are the called **Type I frozen orbits**.

        Returns:
            u.Quantity: Critical inclination
        """
        
        inc_frozen: u.Quantity = np.arcsin(np.sqrt(4/5)) * u.rad # ? Also 180° - inc
        
        return inc_frozen
    
    @staticmethod
    def frozen_orbit_type_2(semimajor_axis: u.Quantity, inclination: u.Quantity) -> typing.List[u.Quantity]:
        """
        Orbits that aside from a_dot and i_dot = 0 also exhibit the properties e_dot and omega_dot = 0 are
        called *frozen orbits* because the rotation of the apse line is stopped.
        
        If we keep omega = 90° / 270°, the orbit is frozen. Because of 0 < e_f << 1 it is always possible to achieve,
        orbits with these conditions are called **Type II frozen orbits**.
        
        Args:
            semimajor_axis (u.Quantity): Semimajor axis
            inclination (u.Quantity): Inclination

        Returns:
            typing.List[u.Quantity]: Eccentricity for vanishing argument of periapsis [e_f_0, e_f]
        """
        
        common.check_angle(inclination)
        
        R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km)
        
        sma: float = semimajor_axis.to_value(u.km)
        inc: float = inclination.to_value(u.rad)
        
        # * Eccentricity for vanishing argument of periapsis
        
        earth_harmonics: GravityHarmonics = OrbitalPerturbations.earth_harmonic_coefficients()
        
        J_2: float = earth_harmonics.J[(2, 0)]
        J_3: float = earth_harmonics.J[(3, 0)]

        e_f_0: float = - 1 / 2 * (J_3 * R_E) / (J_2 * sma) * np.sin(inc)
        
        # * Eccentricity for vanishing argument of periapsis (higher order terms)

        earth_reduced_harmonics: typing.Dict[typing.Tuple[int, int], float] =\
            OrbitalPerturbations.earth_reduced_harmonic_coefficients(
                semimajor_axis=semimajor_axis,
                eccentricity=e_f_0 * u.one
            )
        
        j_2: float = earth_reduced_harmonics[(2, 0)]
        j_3: float = earth_reduced_harmonics[(3, 0)]
        j_5: float = earth_reduced_harmonics[(5, 0)]
        j_7: float = earth_reduced_harmonics[(7, 0)]
        j_9: float = earth_reduced_harmonics[(9, 0)]
        
        e_f: float =\
            np.sin(inc) / (2 * j_2 * ( 1 - 5/4 * np.sin(inc)**2 )) *\
            (\
                - j_3 * ( 1 - 5/4 * np.sin(inc)**2 ) +\
                5/2 * j_5 * ( 1 - 7/2 * np.sin(inc)**2 + 21/8 * np.sin(inc)**4 ) +\
                - 35/8 * j_7 * ( 1 - 27/4 * np.sin(inc)**2 + 99/8 * np.sin(inc)**4 - 429/64 * np.sin(inc)**6 ) +\
                105/16 * j_9 * ( 1 - 11 * np.sin(inc)**2 + 143/4 * np.sin(inc)**4 - 715 / 16 * np.sin(inc)**6 +\
                    2431 / 128 * np.sin(inc)**8 )
            )
        
        return [e_f_0 * u.one, e_f * u.one]
    
    @staticmethod
    def frozen_sun_synchronous_orbit(semimajor_axis: u.Quantity, inclination: u.Quantity) -> typing.List[u.Quantity]:
        """
        Orbits that aside from a_dot and i_dot = 0 also exhibit the properties e_dot and omega_dot = 0 are
        called *frozen orbits* because the rotation of the apse line is stopped.
        
        If we keep omega = 90° / 270°, the orbit is frozen. Imposing also the Sun-synchronous condition,
        we obtain the **Sun-synchronous frozen orbits**
        
        Args:
            semimajor_axis (u.Quantity): Semimajor axis
            inclination (u.Quantity): Inclination

        Returns:
            typing.List[u.Quantity]: Eccentricity for vanishing argument of periapsis [e_f, e_f_sso]
        """
        
        common.check_angle(inclination)
        
        R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km)
        
        sma: float = semimajor_axis.to_value(u.km)
        inc: float = inclination.to_value(u.rad)
        
        # * Eccentricity for vanishing argument of periapsis (higher order terms)
        
        epsilon: float = 0.00978457 * (sma / R_E)**7

        earth_reduced_harmonics: typing.Dict[typing.Tuple[int, int], float] =\
            OrbitalPerturbations.earth_reduced_harmonic_coefficients(
                semimajor_axis=semimajor_axis,
                eccentricity=0 * u.one
            )
        
        j_2: float = earth_reduced_harmonics[(2, 0)]
        j_3: float = earth_reduced_harmonics[(3, 0)]
        j_5: float = earth_reduced_harmonics[(5, 0)]
        j_7: float = earth_reduced_harmonics[(7, 0)]
        j_9: float = earth_reduced_harmonics[(9, 0)]
        
        e_f: float =\
            - np.sin(inc) / (2 * j_2) *\
            (\
                j_3 +\
                5/4 *\
                    (\
                        ( j_5 + 35/32 * j_7 + 147/128 * j_9 ) -\
                        ( 9 * j_5 + 385/16 * j_7 + 5733/128 * j_9 ) * epsilon\
                    )
            )
        
        # * Eccentricity for Sun-synchronous orbit
        
        gamma: float = R_E / sma
        
        e_f_sso: float = 1.170e-3 * gamma * np.sqrt(1 - 0.00978457 * gamma**(-7)) *\
            (\
                1 + 1/8 *\
                    (\
                        (0.8975 * gamma**2 + 1.5217 * gamma**4 + 0.5470 * gamma**6) -\
                        (0.00791 * gamma**(-5) + 0.328 * gamma**(-3) + 0.208 * gamma**(-1))\
                    )\
            )
        
        return [e_f * u.one, e_f_sso * u.one]
    
    @staticmethod
    def draconitic_motion(semimajor_axis: u.Quantity, inclination: u.Quantity) -> typing.List[u.Quantity]:
        """
        As the reference point of recurrence one usually chooses the ascending node in the geocentric equatorial
        reference frame. The orbital period relative to this node is the so-called *draconitic period*.
        
        The **mean draconitic motion** is the mean motion on the orbit between two passes of the (drifting) ascending
        node, while the **draconitic period** is the time between the succeeding passes of the drifting ascending node.
        
        ---
        Note
        ---
        
        It is assumed a circular / near-circular resonant orbit.
        
        Args:
            semimajor_axis (u.Quantity): Semimajor axis
            inclination (u.Quantity): Inclination

        Returns:
            typing.List[u.Quantity]: Mean draconitic motion and period [n_omega, t_omega]
        """
        
        common.check_angle(inclination)
        
        mu: float = bodies.BODIES[bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
        
        sma: float = semimajor_axis.to_value(u.km)
        inc: float = inclination.to_value(u.rad)
        
        n: float = np.sqrt(mu / sma) # ? Mean motion
        
        earth_reduced_harmonics: typing.Dict[typing.Tuple[int, int], float] =\
            OrbitalPerturbations.earth_reduced_harmonic_coefficients(
                semimajor_axis=semimajor_axis,
                eccentricity=0 * u.one
            )
        
        j_2: float = earth_reduced_harmonics[(2, 0)]
        
        # >>> 1. Mean draconitic motion
        
        n_omega: float = n * (1 + j_2 * (3 - 4 * np.sin(inc)**2))
        
        # >>> 2. Draconitic period
        
        t_omega: float = 2 * np.pi / n_omega
        
        return n_omega * u.rad / u.s, t_omega * u.s
    
    @staticmethod
    def commensurate_orbit(inclination: u.Quantity,
                           k_orbital_revolutions: int,
                           l_terrestrial_revolutions: int) -> typing.List[u.Quantity]:
        """
        It provides the semi-major axis of a *k : l* **commensurate orbit** subject to gravitational perturbation, which
        is the key orbital element of a resonant orbit.
        
        ---
        Note
        ---
        
        It is assumed a circular / near-circular resonant orbit.
        
        Args:
            inclination (u.Quantity): Inclination
            k_orbital_revolutions (int): Number of orbital revolutions
            l_terrestrial_revolutions (int): Number of terrestrial revolutions of 360°

        Returns:
            typing.List[u.Quantity]: Commensurate semimajor axis [zeroth order, first order]
        """
        
        common.check_angle(inclination)
        
        mu: float = bodies.BODIES[bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
        R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km)
        omega: float = bodies.BODIES[bodies.Attractor.EARTH].omega.to_value(u.rad / u.s)
        
        inc: float = inclination.to_value(u.rad)
        k: int = k_orbital_revolutions
        l: int = l_terrestrial_revolutions
        
        earth_harmonics: GravityHarmonics = OrbitalPerturbations.earth_harmonic_coefficients()
        
        J_2: float = earth_harmonics.J[(2, 0)]
        
        factor_1: float = 3/2 * J_2 * R_E**2 / (mu / omega**2)**(2/3)
        
        factor_2: float = np.cbrt(mu / omega**2)
        
        a_c_0: float = factor_2 * (l/k)**(2/3) # ? factor_1 = 0
        
        delta: float = factor_1 * (k/l)**(4/3) * (3 - 4 * np.sin(inc)**2 - k/l * np.cos(inc))
        
        a_c: float = factor_2 * (l/k * (1 + delta))**(2/3)
        
        return a_c_0 * u.km, a_c * u.km
    
    @staticmethod
    def gps_orbit(inclination: u.Quantity,
                  longitude_ascending_node: u.Quantity,
                  use_harmonics_32: bool = True,
                  use_harmonics_44: bool = True,
                  use_harmonics_52: bool = True) -> u.Quantity:
        """
        The **GPS** (*Global Positioning System*) is a US space-based global navigation satellite system where between
        24 and 32 (usually 31) active satellites circle Earth equally spaced in six orbital planes (designated A through
        F) starting from a RAAN of 10° and euqally spaced of 60°.
        
        Their specific orbital elements are i = 55°, e = 0.001, and they exhibit a revolutionary period of exactly half
        a sidereal day, i.e., they are in a deep k : l = 2 : 1 resonance with Earth's rotation.
        
        For n < 5 the triples n/m/p = 321, 441, 522 need to be considered.

        Args:
            inclination (u.Quantity): Inclination
            longitude_ascending_node (u.Quantity): Longitude of the ascending node
            use_harmonics_32 (bool, optional): Use 3/2 2/1 harmonic. Defaults to True.
            use_harmonics_44 (bool, optional): Use 4/4 2/1 harmonic. Defaults to True.
            use_harmonics_52 (bool, optional): Use 5/2 2/1 harmonic. Defaults to True.

        Returns:
            typing.List[u.Quantity]: Longitudinal drift rate [ldr]
        """
        
        common.check_angle(inclination)
        common.check_angle(longitude_ascending_node)
                
        inc: float = inclination.to_value(u.rad)
        lambda_omega: float = longitude_ascending_node.to_value(u.rad)
        
        mu: float = bodies.BODIES[bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
        R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km)
        
        earth_harmonics: GravityHarmonics = OrbitalPerturbations.earth_harmonic_coefficients()
        
        J_32: float = earth_harmonics.J[(3, 2)]
        J_44: float = earth_harmonics.J[(4, 4)]
        J_52: float = earth_harmonics.J[(5, 2)]
        
        L_32: float = earth_harmonics.L[(3, 2)]
        L_44: float = earth_harmonics.L[(4, 4)]
        L_52: float = earth_harmonics.L[(5, 2)]
        
        # * GPS orbit data
        
        _, sma_gps = OrbitalPerturbations.commensurate_orbit(
            inclination=55 * u.deg,
            k_orbital_revolutions=2,
            l_terrestrial_revolutions=1)
        
        n_gps: u.Quantity = np.sqrt(mu / sma_gps.to_value(u.km)**3)
        
        ratio: float = R_E / sma_gps.to_value(u.km)
        
        # * Triple 321 441 522
        
        F_321: float = 15/8 * np.sin(inc) * (1 - 2 * np.cos(inc) - 3 * np.cos(inc)**2)
        
        F_441: float = 105/4 * np.sin(inc)**2 * (1 + np.cos(inc))**2
        
        F_522: float =\
            -105/16 * np.sin(inc) * (1 - 2 * np.cos(inc) - 3 * np.cos(inc)**2) +\
            315/32 * np.sin(inc)**3 * (1 - 2 * np.cos(inc) - 5 * np.cos(inc)**2)
        
        omega_lambda: float = n_gps * np.sqrt(3 * J_32 * np.abs(F_321) * ratio**3)
        
        # * Longitudinal drift rate
        
        if not use_harmonics_32:
            
            J_32 = 0
            
        if not use_harmonics_44:
            
            J_44 = 0
            
        if not use_harmonics_52:
            
            J_52 = 0
        
        ldr: float = 3/4 * n_gps**2 *\
            (\
                - 2 * ratio**3 * J_32 * F_321 * np.cos(2 * (lambda_omega - L_32)) +\
                + 4 * ratio**4 * J_44 * F_441 * np.sin(4 * (lambda_omega - L_44)) +\
                - 2 * ratio**5 * J_52 * F_522 * np.cos(2 * (lambda_omega - L_52))
            )

        return ldr / u.s**2
    
    @staticmethod
    def geo_orbit(
        inclination: u.Quantity,
        longitude_ascending_node: u.Quantity,
        use_harmonics_22: bool = True,
        use_harmonics_31: bool = True,
        use_harmonics_33: bool = True
        ) -> u.Quantity:
        """
        A **GEO** (*GEostationary Orbit*) possesses e = i = 0 and is a prime example of a resonant orbit exhibiting
        k = l = 1, i.e., the orbit is in perfect pace with Earth's rotation. Hence a satellite in GEO seems to be at
        rest as seen from any position on Earth.
        
        The relevant harmonics are J_22, J_31, and J_33.

        Args:
            inclination (u.Quantity): Inclination
            longitude_ascending_node (u.Quantity): Longitude of the ascending node
            use_harmonics_22 (bool, optional): Use 2/2 harmonic. Defaults to True.
            use_harmonics_31 (bool, optional): Use 3/1 harmonic. Defaults to True.
            use_harmonics_33 (bool, optional): Use 3/3 harmonic. Defaults to True.

        Returns:
            typing.List[u.Quantity]: Longitudinal drift rate [ldr]
        """
        
        common.check_angle(inclination)
        common.check_angle(longitude_ascending_node)
                
        inc: float = inclination.to_value(u.rad)
        lambda_omega: float = longitude_ascending_node.to_value(u.rad)
        
        mu: float = bodies.BODIES[bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
        R_E: float = bodies.BODIES[bodies.Attractor.EARTH].R_E.to_value(u.km)
        
        earth_harmonics: GravityHarmonics = OrbitalPerturbations.earth_harmonic_coefficients()
        
        J_22: float = earth_harmonics.J[(2, 2)]
        J_31: float = earth_harmonics.J[(3, 1)]
        J_33: float = earth_harmonics.J[(3, 3)]
        
        L_22: float = earth_harmonics.L[(2, 2)]
        L_31: float = earth_harmonics.L[(3, 1)]
        L_33: float = earth_harmonics.L[(3, 3)]
        
        # * GPS orbit data
        
        _, sma_gps = OrbitalPerturbations.commensurate_orbit(
            inclination=0 * u.deg,
            k_orbital_revolutions=1,
            l_terrestrial_revolutions=1)
        
        n_gps: u.Quantity = np.sqrt(mu / sma_gps.to_value(u.km)**3)
        
        ratio: float = R_E / sma_gps.to_value(u.km)
        
        omega_lambda: float = 6 * ratio * n_gps * np.sqrt(J_22)
        
        # * Longitudinal drift rate
        
        if not use_harmonics_22:
            
            J_22 = 0
            
        if not use_harmonics_31:
            
            J_31 = 0
            
        if not use_harmonics_33:
            
            J_33 = 0
        
        ldr: float = 3 * n_gps**2 *\
            (\
                + 6 * ratio**2 * J_22 * np.sin(2 * (lambda_omega - L_22)) +\
                + 3/2 * ratio**3 * J_31 * np.sin(lambda_omega - L_31) +\
                - 45 * ratio**3 * J_33 * np.sin(3 * (lambda_omega - L_33))\
            )

        return ldr / u.s**2
    
    @staticmethod
    def drag_circularization_time(
        semimajor_axis: u.Quantity,
        eccentricity: u.Quantity,
        ballistic_coefficient: u.Quantity
        ) -> u.Quantity:
        """
        King-Hele circularization time for a generic elliptical orbit due to atmospheric drag.

        Args:
            semimajor_axis (u.Quantity): Semimajor axis of the initial orbit
            eccentricity (u.Quantity): Eccentricity of the initial orbit
            ballistic_coefficient (u.Quantity): Ballistic coefficient of the spacecraft (A/m * C_d)

        Returns:
            u.Quantity: Circularization time
        """
        
        sma_0: u.Quantity = semimajor_axis.to(u.km)
        ecc_0: u.Quantity = eccentricity.to(u.one)
        B: u.Quantity = ballistic_coefficient.to(u.km**2 / u.kg)
        
        mu: u.Quantity = bodies.BODIES[bodies.Attractor.EARTH].mu
        R_E: u.Quantity = bodies.BODIES[bodies.Attractor.EARTH].R_E
        
        r_p: u.Quantity = sma_0 * (1 - ecc_0)
        
        rho_p, H_p = OrbitalPerturbations.density(altitude=r_p - R_E, model=AtmosphereModel.CIRA72)
        
        rho_p = rho_p.to(u.kg / u.km**3)
        
        t_circ: u.Quantity = r_p / (B * rho_p) * np.sqrt(2 * np.pi / (mu * H_p)) *\
            (np.arctan(np.sqrt(ecc_0.value)) - np.sqrt(ecc_0) / (1 + ecc_0))
        
        return t_circ
    
    @staticmethod
    def drag_orbit_lifetime(
        semimajor_axis: u.Quantity,
        ballistic_coefficient: u.Quantity
        ) -> u.Quantity:
        """
        Calculates the lifetime of a generic circular orbit due to atmospheric drag.

        Args:
            semimajor_axis (u.Quantity): Semimajor axis of the orbit
            ballistic_coefficient (u.Quantity): Ballistic coefficient of the spacecraft (A/m * C_d)

        Returns:
            u.Quantity: Lifetime of the orbit
        """
        
        sma_0: u.Quantity = semimajor_axis.to(u.km)
        B: u.Quantity = ballistic_coefficient.to(u.km**2 / u.kg)
        
        mu: u.Quantity = bodies.BODIES[bodies.Attractor.EARTH].mu
        R_E: u.Quantity = bodies.BODIES[bodies.Attractor.EARTH].R_E
        
        rho_0, H_0 = OrbitalPerturbations.density(altitude=sma_0 - R_E, model=AtmosphereModel.CIRA72)
        
        rho_0 = rho_0.to(u.kg / u.km**3)
        
        t_l: u.Quantity = H_0 / (B * rho_0 * np.sqrt(mu * sma_0))
        
        return t_l
    
    # --- PUBLIC ---
    
    def init(self,
             attractor: bodies.Attractor,
             position: u.Quantity,
             velocity: u.Quantity,
             julian_day: float = 0,
             ballistic_coefficient: u.Quantity = 0 * u.m**2 / u.kg,
             ballistic_coefficient_srp: u.Quantity = 0 * u.m**2 / u.kg) -> None:
        """
        Initialize the parameters for the propagation

        Args:
            attractor (bodies.Attractor): Main attractor
            position (u.Quantity): Position vector
            velocity (u.Quantity): Velocity vector
            julian_day (float): Julian Day
            ballistic_coefficient (u.Quantity, optional): Ballistic coefficient. Defaults to 0 * u.m**2 / u.kg.
            ballistic_coefficient (u.Quantity, optional): Ballistic coefficient for Solar Radiation Pressure. Defaults to 0 * u.m**2 / u.kg.
        """
        
        common.check_attractor(attractor)
        
        common.check_position_vector(position.to_value(u.km))
        
        common.check_velocity_vector(velocity.to_value(u.km / u.s))
        
        self.ready = True
        
        self.attractor = attractor
        
        self.julian_day = julian_day
        
        self.position = position.to(u.km).to_value()
        
        self.velocity = velocity.to(u.km / u.s).to_value()
        
        self.ballistic_coefficient = ballistic_coefficient
        
        self.ballistic_coefficient_srp = ballistic_coefficient_srp
    
    def choose_perturbations(self,
                             atmospheric_drag: bool = False,
                             gravitational_perturbation: bool = False,
                             solar_radiation_pressure: bool = False,
                             lunar_gravity: bool = False,
                             solar_gravity: bool = False) -> None:
        """
        Select the perturbations to use in the simulation

        Args:
            atmospheric_drag (bool, optional): Activate atmospheric drag perturbation. Defaults to False.
            gravitational_perturbation (bool, optional): Activate gravitational perturbation. Defaults to False.
            solar_radiation_pressure (bool, optional): Activate Solar Radiation Pressure (SRP) perturbation. Defaults to False.
            lunar_gravity (bool, optional): Activate lunar gravity perturbation. Defaults to False.
            solar_gravity (bool, optional): Activate solar gravity perturbation. Defaults to False.
        """
        
        self.use_atmospheric_drag = atmospheric_drag
        
        self.use_gravitational_perturbation = gravitational_perturbation
        
        self.use_solar_radiation_pressure = solar_radiation_pressure
        
        self.use_lunar_gravity = lunar_gravity
        
        self.use_solar_gravity = solar_gravity
    
    def propagate_cowell_for(self, delta: time.TimeDelta) -> ResultOP:
        """
        Propagate the relative motion with perturbations using Cowell's method

        Args:
            delta (time.TimeDelta): Delta time for propagation
        
        Returns:
            ResultOP: Integration result
        """
        
        if not self.ready: raise ValueError(self.not_ready_message)
        
        common.check_time_delta(delta)
        
        result: ResultOP = ResultOP()
        
        solution: dict = ode.solve_ivp(fun=self._cowell_equations_relative_motion,
                                       t_span=[0, delta.to_value(u.s)],
                                       y0=np.concat([self.position, self.velocity]),
                                       method='RK45',
                                       args=(),
                                       rtol=1e-10,
                                       atol=1e-12)
        
        result.success = solution['success']
        result.time = solution['t'] * u.s
        result.position_x = solution['y'][0, :] * u.km
        result.position_y = solution['y'][1, :] * u.km
        result.position_z = solution['y'][2, :] * u.km
        result.velocity_x = solution['y'][3, :] * u.km / u.s
        result.velocity_y = solution['y'][4, :] * u.km / u.s
        result.velocity_z = solution['y'][5, :] * u.km / u.s
        
        return result
    
    def propagate_encke_for(self, delta: time.TimeDelta, step: time.TimeDelta) -> ResultOP:
        """
        Propagate the relative motion with perturbations using Encke's method

        Args:
            delta (time.TimeDelta): Delta time for propagation
            step (time.TimeDelta): Time step between 0 and delta
        
        Returns:
            ResultOP: Integration result
        """
        
        if not self.ready: raise ValueError(self.not_ready_message)
        
        common.check_time_delta(delta)
        
        common.check_time_delta(step)
        
        if step >= delta: raise ValueError("'step' must be smaller than 'delta'")
        
        # >>> 1. Initial conditions
        
        r_0: np.ndarray = self.position
        
        v_0: np.ndarray = self.velocity
        
        dr_0: np.ndarray = np.zeros(shape=(3))
        
        dv_0: np.ndarray = np.zeros(shape=(3))
        
        oe_0: OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=self.attractor,
                                                                   position=r_0 * u.km,
                                                                   velocity=v_0 * u.km / u.s)
        
        max_step: float = oe_0.calc_orbital_period(attractor=self.attractor).to_value(u.s) / 100.0
        
        times: np.ndarray = np.arange(start=step.to_value(u.s), stop=delta.to_value(u.s), step=step.to_value(u.s))
        
        # >>> 2. Compute the first osculating state vector
        
        r_osc, v_osc = lc.LagrangeCoefficients.propagate_position_velocity(attractor=self.attractor,
                                                                           initial_position=r_0 * u.km,
                                                                           initial_velocity=v_0 * u.km / u.s,
                                                                           delta_time=step)
        
        state_vector: typing.List[np.ndarray] = [np.concat([r_0, v_0])]
        
        orbital_elements: typing.List[OrbitalElements] = [oe_0]
        
        #>>> 3. Cycle over the time array
        
        for t in times:
            
            # >>> a. Integrate perturbed motion
            
            solution: dict = ode.solve_ivp(fun=self._encke_equations_relative_motion,
                                           t_span=[t, t + step.to_value(u.s)],
                                           y0=np.concat([dr_0, dv_0]),
                                           method='RK45',
                                           args=(r_osc.to_value(u.km), v_osc.to_value(u.km / u.s)),
                                           rtol=1e-8,
                                           atol=1e-8,
                                           max_step=max_step)
            
            if not solution['success']: raise InterruptedError(solution['message'])
            
            # >>> b. Evaluate new osculating state vector
            
            r_osc, v_osc = lc.LagrangeCoefficients.propagate_position_velocity(attractor=self.attractor,
                                                                               initial_position=r_0 * u.km,
                                                                               initial_velocity=v_0 * u.km / u.s,
                                                                               delta_time=step)
        
            r_0 = r_osc.to_value(u.km) + solution['y'][:3, -1]
            v_0 = v_osc.to_value(u.km / u.s) + solution['y'][3:, -1]
            
            state_vector.append(np.concat([r_0, v_0]))
            
            # >>> c. Calculates osculating orbital elements
            
            oe: OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=self.attractor,
                                                                     position=r_0 * u.km,
                                                                     velocity=v_0 * u.km / u.s)
            
            orbital_elements.append(oe)
        
        result: ResultOP = ResultOP()
        
        result.success = solution['success']
        result.time = times * u.s
        result.position_x = np.array([sv[0] for sv in state_vector]) * u.km
        result.position_y = np.array([sv[1] for sv in state_vector]) * u.km
        result.position_z = np.array([sv[2] for sv in state_vector]) * u.km
        result.velocity_x = np.array([sv[3] for sv in state_vector]) * u.km / u.s
        result.velocity_y = np.array([sv[4] for sv in state_vector]) * u.km / u.s
        result.velocity_z = np.array([sv[5] for sv in state_vector]) * u.km / u.s
        result.orbital_elements = orbital_elements
        
        return result
    
    def propagate_gauss_for(self, delta: time.TimeDelta) -> ResultOP:
        """
        Propagate the relative motion with perturbations using Gauss variational equations

        Args:
            delta (time.TimeDelta): Delta time for propagation
        
        Returns:
            ResultOP: Integration result
        """
        
        if not self.ready: raise ValueError(self.not_ready_message)
        
        common.check_time_delta(delta)
        
        oe_0: OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=self.attractor,
                                                                   position=self.position * u.km,
                                                                   velocity=self.velocity * u.km / u.s)
        
        solution: dict = ode.solve_ivp(fun=self._gauss_variational_eom,
                                       t_span=[0, delta.to_value(u.s)],
                                       y0=np.array([oe_0.specific_angular_momentum.to_value(u.km**2 / u.s),
                                                    oe_0.eccentricity.to_value(u.dimensionless_unscaled),
                                                    oe_0.true_anomaly.to_value(u.rad),
                                                    oe_0.right_ascension_of_ascending_node.to_value(u.rad),
                                                    oe_0.inclination.to_value(u.rad),
                                                    oe_0.argument_of_periapsis.to_value(u.rad)]),
                                       method='RK45',
                                       args=(),
                                       rtol=1e-8,
                                       atol=1e-8)
        
        result: ResultOP = ResultOP()
        
        result.success = solution['success']
        result.time = solution['t'] * u.s
        result.orbital_elements = []
        
        for idx, _ in enumerate(solution['t']):
            
            solution_idx: np.ndarray = solution['y'][:, idx]
            
            oe_idx: OrbitalElements = OrbitalElements(specific_angular_momentum=solution_idx[0] * u.km**2 / u.s,
                                                      semimajor_axis=0.0 * u.km,
                                                      eccentricity=solution_idx[1] * u.dimensionless_unscaled,
                                                      inclination=(solution_idx[4] * u.rad).to(u.deg),
                                                      right_ascension_of_ascending_node=(solution_idx[3] * u.rad).to(u.deg),
                                                      argument_of_periapsis=(solution_idx[5] * u.rad).to(u.deg),
                                                      true_anomaly=(solution_idx[2] * u.rad).to(u.deg))
            
            oe_idx.calc_semimajor_axis(attractor=self.attractor)
            
            result.orbital_elements.append(oe_idx)
        
        return result
    
    # --- PRIVATE ---

    def _cowell_equations_relative_motion(self, t : float, X : np.ndarray) -> np.ndarray:
        """
        Equations of relative motion with perturbations using Cowell's method
        
        This function integrates the full Cartesian equations of motion under a central gravitational field, augmented
        by optional perturbing accelerations.
        
        The state vector is:

            X = [x, y, z, v_x, v_y, v_z]

        The radial distance is:

            r = sqrt(x² + y² + z²)

        The unperturbed (two-body) accelerations are:

            dx/dt   = v_x
            dy/dt   = v_y
            dz/dt   = v_z

            dv_x/dt = - μ * x / r³
            dv_y/dt = - μ * y / r³
            dv_z/dt = - μ * z / r³

        When enabled, the following perturbations are added:

        **1. Atmospheric drag**

            v_rel = v_sc - v_atm
            
            a_drag = -½ ρ ||v_rel|| B v_rel

            where:
                ρ   = atmospheric density at altitude (r - R_E)
                B   = ballistic coefficient
                v_atm = ω × r_sc (rigidly rotating atmosphere)

        **2. J₂ gravitational perturbation**

            a_J2 = (3/2) J₂ μ R_E² / r⁴ · [ x/r (5 z²/r² - 1), y/r (5 z²/r² - 1), z/r (5 z²/r² - 3) ]

        The total perturbing acceleration is:

            p = a_drag + a_J2

        The complete Cowell equations are therefore:

            dx/dt   = v_x
            dy/dt   = v_y
            dz/dt   = v_z

            dv_x/dt = - μ x / r³ + p_x
            dv_y/dt = - μ y / r³ + p_y
            dv_z/dt = - μ z / r³ + p_z
        
        Args:
            t (float): Time (unused, included for ODE solver compatibility)
            X (np.ndarray): State vector [x, y, z, v_x, v_y, v_z]

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        # >>> Parameters
        
        x, y, z, v_x, v_y, v_z = X
        
        r: float = np.sqrt(x**2 + y**2 + z**2)
        
        mu: float = bodies.BODIES[self.attractor].mu.to_value(u.km**3 / u.s**2)
        
        omega: float = bodies.BODIES[self.attractor].omega.to_value(u.rad / u.s)
        
        R_E: float = bodies.BODIES[self.attractor].R_E.to_value(u.km)
        
        J_2: float = bodies.BODIES[self.attractor].J2.to_value(u.one)
        
        # >>> Perturbations
        
        p_atm_drag: np.ndarray = np.zeros(shape=(3))
        
        p_gra_per: np.ndarray = np.zeros(shape=(3))
        
        if self.use_atmospheric_drag:
            
            # * Atmospheric Drag
            
            r_sc: np.ndarray = X[:3] # ? Spacecraft position
            
            v_sc: np.ndarray = X[3:] # ? Spacecraft velocity
            
            v_atm: np.ndarray = np.cross(np.array([0, 0, omega]), r_sc) # ? Atmosphere velocity
            
            v_rel: np.ndarray = v_sc - v_atm # ? Relative velocity w.r.t. atmosphere
            
            rho, _ = self.density((r - R_E) * u.km).to_value(u.kg / u.km**3)
            
            B: float = self.ballistic_coefficient.to_value(u.km**2 / u.kg)
        
            p_atm_drag: np.ndarray = - 0.5 * rho * np.linalg.norm(v_rel) * B * v_rel
            
        if self.use_gravitational_perturbation:
            
            # * Gravitational Perturbation
            
            factor: float = 3 / 2 * J_2 * mu * R_E**2 / r**4
            
            p_gra_per = factor * np.array([x / r * (5 * z**2 / r**2 - 1),
                                           y / r * (5 * z**2 / r**2 - 1),
                                           z / r * (5 * z**2 / r**2 - 3)])
        
        # * Perturbing acceleration
        
        p: np.ndarray = p_atm_drag + p_gra_per
        
        # >>> Equations
        
        dx_dt = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = - (mu / r**3) * x + p[0]
        dx_dt[4] = - (mu / r**3) * y + p[1]
        dx_dt[5] = - (mu / r**3) * z + p[2]
        
        return dx_dt
    
    def _encke_equations_relative_motion(self, t : float, X : np.ndarray,
                                         r_osc : np.ndarray, v_osc : np.ndarray) -> np.ndarray:
        """
        Equations of relative motion with perturbations using Encke's method
        
        Encke's formulation integrates the deviation between the true perturbed trajectory and a reference *osculating*
        two-body orbit. The state vector is:

            X = [dx, dy, dz, dv_x, dv_y, dv_z]

        where:
            dr = [dx, dy, dz] is the position deviation
            dv = [dv_x, dv_y, dv_z] is the velocity deviation

        The osculating (unperturbed) state is provided as:

            r_osc : osculating position vector
            v_osc : osculating velocity vector

        The true spacecraft state is reconstructed as:

            r_sc = r_osc + dr
            v_sc = v_osc + dv

        Let:

            r = ||r_sc||

        The unperturbed two-body acceleration is evaluated at the *osculating* radius:

            a_2body = - μ * r_osc / ||r_osc||³

        Encke's method introduces a correction term to avoid subtracting nearly equal numbers when computing the
        perturbed acceleration. Define:

            q = ( dr · (2 r_sc - dr) ) / r²

            F(q) = (q² - 3q + 3) / (1 + (1 - q)^(3/2)) * q

        The corrected gravitational term becomes:

            a_encke = - μ / ||r_osc||³ * ( dr - F(q) * r_sc )

        Optional perturbations may be added:

        **1. Atmospheric drag**

            v_rel = v_sc - (ω × r_sc)
            
            a_drag = -½ ρ ||v_rel|| B v_rel

            where:
                ρ   = atmospheric density at altitude (r - R_E)
                B   = ballistic coefficient
                v_atm = ω × r_sc (rigidly rotating atmosphere)

        **2. J₂ gravitational perturbation**

            a_J2 = (3/2) J₂ μ R_E² / r⁴ · [ x/r (5 z²/r² - 1), y/r (5 z²/r² - 1), z/r (5 z²/r² - 3) ]

        The total perturbing acceleration is:

            p = a_drag + a_J2

        The complete Encke equations are:

            d(dr)/dt = dv

            d(dv)/dt = a_encke + p

        Args:
            t (float): Time (unused, included for ODE solver compatibility)
            X (np.ndarray): State vector [dx, dy, dz, dv_x, dv_y, dv_z]
            r_osc (np.ndarray): Osculating position vector
            v_osc (np.ndarray): Osculating velocity vector

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        # >>> Parameters
        
        dr, dv = X[:3], X[3:]
        
        mu: float = bodies.BODIES[self.attractor].mu.to_value(u.km**3 / u.s**2)
        
        omega: float = bodies.BODIES[self.attractor].omega.to_value(u.rad / u.s)
        
        R_E: float = bodies.BODIES[self.attractor].R_E.to_value(u.km)
        
        J_2: float = bodies.BODIES[self.attractor].J2.to_value(u.one)
        
        # >>> Osculating state on the perturbed orbit
        
        r_sc: np.ndarray = r_osc + dr # ? Spacecraft position
        
        v_sc: np.ndarray = v_osc + dv # ? Spacecraft velocity
        
        r: float = np.linalg.norm(r_sc)
        
        x, y, z = r_sc
        
        # >>> Perturbations
        
        p_atm_drag: np.ndarray = np.zeros(shape=(3))
        
        p_gra_per: np.ndarray = np.zeros(shape=(3))
        
        if self.use_atmospheric_drag:
            
            # * Atmospheric Drag
            
            v_atm: np.ndarray = np.cross(np.array([0, 0, omega]), r_sc) # ? Atmosphere velocity
            
            v_rel: np.ndarray = v_sc - v_atm # ? Relative velocity w.r.t. atmosphere
            
            rho, _ = self.density((r - R_E) * u.km).to_value(u.kg / u.km**3)
            
            B: float = self.ballistic_coefficient.to_value(u.km**2 / u.kg)
        
            p_atm_drag: np.ndarray = - 0.5 * rho * np.linalg.norm(v_rel) * B * v_rel
            
        if self.use_gravitational_perturbation:
            
            # * Gravitational Perturbation (J2)
            
            factor: float = 3 / 2 * J_2 * mu * R_E**2 / r**4
            
            p_gra_per = factor * np.array([x / r * (5 * z**2 / r**2 - 1),
                                           y / r * (5 * z**2 / r**2 - 1),
                                           z / r * (5 * z**2 / r**2 - 3)])
        
        # * Perturbing acceleration
        
        p: np.ndarray = p_atm_drag + p_gra_per
        
        # >>> Difference between nearly equal numbers
        
        F: callable = lambda q: float((q**2 - 3 * q + 3) / (1 + (1 - q)**(3/2)) * q)
        
        q: float = (np.dot(dr, (2 * r_sc - dr)) / r**2)
        
        # >>> Equations
        
        dx_dt = np.zeros(shape=(6))
        
        dx_dt[0] = dv[0]
        dx_dt[1] = dv[1]
        dx_dt[2] = dv[2]
        dx_dt[3] = - (mu / np.linalg.norm(r_osc)**3) * (dr[0] - F(q) * r_sc[0]) + p[0]
        dx_dt[4] = - (mu / np.linalg.norm(r_osc)**3) * (dr[1] - F(q) * r_sc[1]) + p[1]
        dx_dt[5] = - (mu / np.linalg.norm(r_osc)**3) * (dr[2] - F(q) * r_sc[2]) + p[2]
        
        return dx_dt
    
    def _gauss_variational_eom(self, t : float, X : np.ndarray) -> np.ndarray:
        """
        Equations of relative motion with perturbations using Gauss variational equations
        
        This function integrates the time evolution of the classical orbital elements under the influence of perturbing
        accelerations expressed in the Local-Vertical/Local-Horizontal (LVLH) frame, also known as the RSW frame:

            r̂ : radial unit vector (LV)
            ŝ : along-track / transverse unit vector (LH)
            ŵ : orbit-normal unit vector

        The state vector is:

            X = [h, e, θ, Ω, i, ω]

        where:
            h   = specific angular momentum
            e   = eccentricity
            θ   = true anomaly
            Ω   = right ascension of ascending node (RAAN)
            i   = inclination
            ω   = argument of periapsis

        The radial distance is:

            r = h² / [ μ (1 + e cos θ) ]

        The Gauss variational equations in the RSW frame are:

            dh/dt       = r * S
            de/dt       = (h/μ) sinθ R + (1/(μh)) [(h² + μr) cosθ + μer] S
            dθ/dt       = h/r² + (1/(eh)) [ (h²/μ) cosθ R - (r + h²/μ) sinθ S ]
            dΩ/dt       = r/(h sin i) sin(ω + θ) W
            di/dt       = r/h cos(ω + θ) W
            dω/dt       = - (1/(eh)) [ (h²/μ) cosθ R - (r + h²/μ) sinθ S ] - r/(h tan i) sin(ω + θ) W

        where (R, S, W) are the perturbing accelerations projected onto the RSW frame.

        The following perturbations may be included:

        **1. Atmospheric drag**
        
            v_rel = v_sc - (ω × r_sc)
            
            a_drag projected into (R, S, W) using the flight-path angle γ.

        **2. J₂ gravitational perturbation**
        
            a_J2 = - (3/2) J₂ μ R_E² / r⁴ · f(Ω, i, ω + θ)

            projected analytically into (R, S, W).

        **3. Solar radiation pressure (SRP)**
        
            a_SRP = (S/c) B_SRP · shadow_factor
            
            projected into RSW using the DCM from inertial to RSW.

        **4. Third-body gravity (Moon, Sun)**
        
            a_3B = μ_3B ( r_3B_sc/||r_3B_sc||³ - r_3B/||r_3B||³ )
            
            projected into RSW using (r̂, ŝ, ŵ).

        All angles are wrapped into their canonical domains to avoid numerical drift.
        
        It is used the Local-Vertical/Local-Horizontal (LVLH) frame with unit vectors:
        - r = directed radially outward from the attractor (LV)
        - w = normal to the osculating orbital plane
        - s = w x r

        Args:
            t (float): Time (unused, included for ODE solver compatibility)
            X (np.ndarray): State vector [h, e, θ, Ω, i, ω]

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        # >>> Parameters
        
        h, ecc, ta, raan, inc, argp = X
        
        if ecc < 0: ecc = 0.0
        
        if not np.isfinite(ta): ta = 0.0
        if not np.isfinite(raan): raan = 0.0
        if not np.isfinite(inc): inc = 0.0
        if not np.isfinite(argp): argp = 0.0
        
        ta = common.wrap_angle(angle=ta, low=0, high=2 * np.pi)
        raan = common.wrap_angle(angle=raan, low=0, high=2 * np.pi)
        inc = common.wrap_angle(angle=inc, low=-0.5 * np.pi, high=0.5 * np.pi)
        argp = common.wrap_angle(angle=argp, low=0, high=2 * np.pi)
        
        oe: OrbitalElements = OrbitalElements(specific_angular_momentum=h * u.km ** 2 / u.s,
                                              semimajor_axis=0.0 * u.km,
                                              eccentricity=ecc * u.dimensionless_unscaled,
                                              inclination=inc * u.rad,
                                              right_ascension_of_ascending_node=raan * u.rad,
                                              argument_of_periapsis=argp * u.rad,
                                              true_anomaly=ta * u.rad)
        
        mu: float = bodies.BODIES[self.attractor].mu.to_value(u.km**3 / u.s**2)
        
        omega: float = bodies.BODIES[self.attractor].omega.to_value(u.rad / u.s)
        
        R_E: float = bodies.BODIES[self.attractor].R_E.to_value(u.km)
        
        J_2: float = bodies.BODIES[self.attractor].J2.to_value(u.one)
        
        r: float = h**2 / (mu * (1 + ecc * np.cos(ta)))
        
        # >>> Perturbations (R = radial, S = horizon, W = normal)
        
        p_r: float = 0.0
        p_s: float = 0.0
        p_w: float = 0.0
        
        r_sc, v_sc = o3d.Orbit3D.keplerian_to_cartesian(attractor=self.attractor, orbital_elements=oe) # ? Spacecraft
        
        if self.use_atmospheric_drag:
            
            # * Atmospheric Drag
            
            v_atm: np.ndarray = np.cross(np.array([0, 0, omega]), r_sc.to_value(u.km)) # ? Atmosphere velocity
            
            v_rel: np.ndarray = v_sc.to_value(u.km / u.s) - v_atm # ? Relative velocity w.r.t. atmosphere
            
            rho, _ = self.density((r - R_E) * u.km)
            
            rho = rho.to_value(u.kg / u.km**3)
            
            B: float = self.ballistic_coefficient.to_value(u.km**2 / u.kg)
            
            gamma: float = np.arctan(ecc * np.sin(ta) / ( 1 + ecc * np.cos(ta))) # ? Flight path angle
            
            # ! Projection of the drag acceleration from NTW frame to RSW frame
            
            p_r += - 0.5 * rho * np.linalg.norm(v_rel)**2 * B * np.sin(gamma)
            p_s += - 0.5 * rho * np.linalg.norm(v_rel)**2 * B * np.cos(gamma)
            p_w += 0.0
        
        if self.use_gravitational_perturbation:
            
            # * Gravitational Perturbation (J2)
            
            factor: float = - 3 / 2 * J_2 * mu * R_E**2 / r**4
            
            p_r += factor * (1 - 3 * np.sin(inc)**2 * np.sin(argp + ta)**2)
            p_s += factor * np.sin(inc)**2 * np.sin(2 * (argp + ta))
            p_w += factor * np.sin(2 * inc) * np.sin(argp + ta)
        
        if self.use_solar_radiation_pressure:
            
            # * Solar Radiation Pressure
            
            timestamp_0: time.Time = od.OrbitDetermination.julian_day_2_timestamp(julian_day=self.julian_day)
            
            r_sun, lambda_, epsilon = self.sun_position(timestamp=timestamp_0 + t / 86400)
            
            c: u.Quantity = physical_constants.speed_of_light
            
            S_0: u.Quantity = physical_constants.radiated_power_intensity_photosphere
            
            R_0: u.Quantity = physical_constants.photosphere_radius.to(u.m)
            
            S: u.Quantity = S_0 * (R_0 / np.linalg.norm(r_sun.to(u.m)))**2
            
            B_SRP: u.Quantity = self.ballistic_coefficient_srp
            
            solar_radiation_pressure: u.Quantity = self.earth_shadow(r_sc, r_sun) * S / c * B_SRP
            
            solar_radiation_pressure = solar_radiation_pressure.to_value(u.km / u.s**2)
            
            # ? Direction cosine matrix from XYZ to rsw
            
            dcm_xyz_rsw = np.array(
                [
                    [-np.sin(raan) * np.cos(inc) * np.sin(argp + ta) + np.cos(raan) * np.cos(argp + ta),
                     +np.cos(raan) * np.cos(inc) * np.sin(argp + ta) + np.sin(raan) * np.cos(argp + ta),
                     +np.sin(inc) * np.sin(argp + ta)],
                    
                    [-np.sin(raan) * np.cos(inc) * np.cos(argp + ta) - np.cos(raan) * np.sin(argp + ta),
                     +np.cos(raan) * np.cos(inc) * np.cos(argp + ta) - np.sin(raan) * np.sin(argp + ta),
                     +np.sin(inc) * np.cos(argp + ta)],
                    
                    [+np.sin(raan) * np.sin(inc),
                     -np.cos(raan) * np.sin(inc),
                     +np.cos(inc)]
                ])
            
            # ? Unit vector in rsw frame
            
            u_rsw = np.matmul(dcm_xyz_rsw, np.array([np.cos(lambda_),
                                                     np.sin(lambda_) * np.cos(epsilon),
                                                     np.sin(lambda_) * np.sin(epsilon)]))
            
            p_r += - solar_radiation_pressure * u_rsw[0]
            p_s += - solar_radiation_pressure * u_rsw[1]
            p_w += - solar_radiation_pressure * u_rsw[2]
        
        if self.use_lunar_gravity:
            
            # * Lunar gravity
            
            timestamp_0: time.Time = od.OrbitDetermination.julian_day_2_timestamp(julian_day=self.julian_day)
            
            r_moon: u.Quantity = self.moon_position(timestamp=timestamp_0 + t / 86400)
            
            r_moon_sc: u.Quantity = r_moon - r_sc
            
            mu_moon: u.Quantity = bodies.BODIES[bodies.Attractor.MOON].mu
            
            p_moon: u.Quantity = mu_moon * (r_moon_sc / np.linalg.norm(r_moon_sc)**3 - r_moon / np.linalg.norm(r_moon)**3)
            
            r_hat: u.Quantity = r_sc / np.linalg.norm(r_sc)
            w_hat: u.Quantity = np.cross(r_sc, v_sc) / np.linalg.norm(np.cross(r_sc, v_sc))
            s_hat: u.Quantity = np.cross(w_hat, r_sc) / np.linalg.norm(np.cross(w_hat, r_sc))
            
            p_r += np.dot(p_moon.to_value(u.km / u.s**2), r_hat.to_value())
            p_s += np.dot(p_moon.to_value(u.km / u.s**2), s_hat.to_value())
            p_w += np.dot(p_moon.to_value(u.km / u.s**2), w_hat.to_value())
        
        if self.use_solar_gravity:
            
            # * Solar gravity
            
            timestamp_0: time.Time = od.OrbitDetermination.julian_day_2_timestamp(julian_day=self.julian_day)
            
            r_sun, lambda_, epsilon = self.sun_position(timestamp=timestamp_0 + t / 86400)
            
            r_sun_sc: u.Quantity = r_sun - r_sc
            
            mu_sun: u.Quantity = bodies.BODIES[bodies.Attractor.SUN].mu
            
            p_sun: u.Quantity = mu_sun * (r_sun_sc / np.linalg.norm(r_sun_sc)**3 - r_sun / np.linalg.norm(r_sun)**3)
            
            r_hat: u.Quantity = r_sc / np.linalg.norm(r_sc)
            w_hat: u.Quantity = np.cross(r_sc, v_sc) / np.linalg.norm(np.cross(r_sc, v_sc))
            s_hat: u.Quantity = np.cross(w_hat, r_sc) / np.linalg.norm(np.cross(w_hat, r_sc))
            
            p_r += np.dot(p_sun.to_value(u.km / u.s**2), r_hat.to_value())
            p_s += np.dot(p_sun.to_value(u.km / u.s**2), s_hat.to_value())
            p_w += np.dot(p_sun.to_value(u.km / u.s**2), w_hat.to_value())
        
        # >>> Equations
        
        dh_dt       = r * p_s
        decc_dt     = h / mu * np.sin(ta) * p_r + 1 / (mu * h) * ((h**2 + mu * r) * np.cos(ta) + mu * ecc * r) * p_s
        dnu_dt      = h / r**2 + 1 / (ecc * h) * (h**2 / mu * np.cos(ta) * p_r - (r + h**2 / mu) * np.sin(ta) * p_s)
        draan_dt    = r / (h * np.sin(inc)) * np.sin(argp + ta) * p_w
        dinc_dt     = r / h * np.cos(argp + ta) * p_w
        dargp_dt    = -1 / (ecc * h) * (h**2 / mu * np.cos(ta) * p_r - (r + h**2 / mu) * np.sin(ta) * p_s) - \
                      r * np.sin(argp + ta) / (h * np.tan(inc)) * p_w
        
        dx_dt = np.zeros(shape=(6))
        
        dx_dt[0] = dh_dt
        dx_dt[1] = decc_dt
        dx_dt[2] = dnu_dt
        dx_dt[3] = draan_dt
        dx_dt[4] = dinc_dt
        dx_dt[5] = dargp_dt
        
        return dx_dt
