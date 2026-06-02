"""
Orbital Perturbations

Implements the orbital perturbations

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 12: Introduction to Orbital Perturbations

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 5: Non-Keplerian Motion
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as t
import astropy.units as u
import numpy as np
import scipy.integrate as ode
import typing

import astro.physical_constants as pc
import astro.bodies as bd
import astro.common as cm
import astro.lagrange_coefficients as lc
import astro.orbit_3d as o3d
import astro.orbit_determination as od

class Result:
    """Result of integration
    """
    
    success: bool
    time: u.Quantity
    position_x: u.Quantity
    position_y: u.Quantity
    position_z: u.Quantity
    velocity_x: u.Quantity
    velocity_y: u.Quantity
    velocity_z: u.Quantity
    orbital_elements: typing.List[o3d.OrbitalElements]

class OrbitalPerturbations():
    """Orbital Perturbations
    """
    
    def __init__(self):
        """Constructor
        """
        
        self.not_ready_message: str = "Orbital Perturbations object is not ready"
        
        self.ready: bool = False
        
        self.attractor: bd.Attractor = bd.Attractor.EARTH
        
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
    def density(altitude: u.Quantity) -> u.Quantity:
        """
        Calculate the atmospheric density given the altitude above the Earth with the **USSA76** model

        Args:
            altitude (u.Quantity): Altitude

        Returns:
            u.Quantity: Density
        """
        
        z: float = altitude.to_value(u.km)
        
        # >>> 1. Geometric altitudes [km] (1 x 28)
        
        h: np.ndarray = np.array([0, 25, 30, 40, 50, 60, 70, 80, 90, 100,
                                  110, 120, 130, 140, 150, 180, 200, 250, 300, 350,
                                  400, 450, 500, 600, 700, 800, 900, 1000])
        
        # >>> 2. Corresponding densities [kg / m^3] from USSA76 (1 x 28)
        
        rho: np.ndarray = np.array([1.225, 4.008e-2, 1.841e-2, 3.996e-3, 1.027e-3,
                                    3.097e-4, 8.283e-5, 1.846e-5, 3.416e-6, 5.606e-7,
                                    9.708e-8, 2.222e-8, 8.152e-9, 3.831e-9, 2.076e-9,
                                    5.194e-10, 2.541e-10, 6.073e-11, 1.916e-11, 7.014e-12,
                                    2.803e-12, 1.184e-12, 5.215e-13, 1.137e-13, 3.070e-14,
                                    1.136e-14, 5.759e-15, 3.561e-15])
        
        # >>> 3. Scale heights [km] (1 x 27)

        H: np.ndarray = np.array([7.310, 6.427, 6.546, 7.360, 8.342,
                                  7.583, 6.661, 5.927, 5.533, 5.703,
                                  6.782, 9.973, 13.243, 16.322, 21.652,
                                  27.974, 34.934, 43.342, 49.755, 54.513,
                                  58.019, 60.980, 65.654, 76.377, 100.587,
                                  147.203, 208.020])
        
        # >>> 4. Handle altitudes outside of the range
        
        if z > 1000:
            
            z = 1000
            
        elif z < 0:
            
            print("Warning: altitude is below 0 km, using density at 0 km")
            
            z = 0
        
        # >>> 5. Determine the interpolation interval
        
        idx: int = 0
        
        for j in range(0, H.size):
        
            if z >= h[j] and z < h[j + 1]: idx = j
            
        if z == 1000:
            
            idx = H.size - 1
        
        # >>> 6. Exponential interpolation
        
        rho_z: u.Quantity = rho[idx] * np.exp(-(z - h[idx]) / H[idx]) * u.kg / u.m**3
        
        return rho_z
    
    @staticmethod
    def sun_position(timestamp: t.Time) -> typing.List[u.Quantity]:
        """        
        Given the year, month, day, and universal time, calculate the obliquity of the ecliptic ε, ecliptic longitude of
        the Sun λ, and the geocentric position vector of the Sun r_sun with respect to the Earth based on the
        Astronomical Almanac

        Args:
            timestamp (t.Time): UTC timestamp

        Returns:
            typing.List[u.Quantity]: [Sun position vector in GEF, apparent ecliptic longitude, obliquity]
        """
        
        # >>> 1. Julian day number
        
        JD: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp=timestamp)
        
        # >>> 2. Number of days since J2000
        
        n: float = JD - od.OrbitDetermination.J2000
        
        # >>> 3. Mean anonaly of the Sun (deg)
        
        M: float = cm.wrap_angle(357.529 + 0.98560023 * n)
        
        # >>> 4. Mean longitude of the Sun (deg)
        
        L: float = cm.wrap_angle(280.459 + 0.98564736 * n)
        
        # >>> 5. Apparent Solar Ecliptic Longitude
        
        lambda_: float = cm.wrap_angle(L + 1.915 * np.sin(np.deg2rad(M)) + 0.0200 * np.sin(2 * np.deg2rad(M)))
        
        # >>> 6. Obliquity
        
        epsilon: float = cm.wrap_angle(23.439 - 3.56e-7 * n)
        
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
        
        cm.check_position_vector(r_sc)
        
        cm.check_position_vector(r_sun)
        
        R_E: float = bd.BODIES[bd.Attractor.EARTH].R_E.to_value(u.km) # ? Earth radius
        
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
    def moon_position(timestamp: t.Time) -> u.Quantity:
        """
        Given the year, month, day, and universal time, calculate the geocentric position vector of the Moon with
        respect to the Earth based on the Astronomical Almanac

        Args:
            timestamp (t.Time): UTC timestamp

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
        
        epsilon: float = cm.wrap_angle(23.439 - 0.0130042 * T_0)
        
        # >>> 4. Lunar ecliptic longitude
        
        lambda_: float = cm.wrap_angle(b_0 + c_0 * T_0 + sum([a[i] * np.sin(np.deg2rad(b[i] + c[i] * T_0)) for i in range(0, 6)]))
        
        # >>> 5. Lunar ecliptic latitude
        
        delta: float = cm.wrap_angle(sum([d[i] * np.sin(np.deg2rad(e[i] + f[i] * T_0)) for i in range(0, 4)]))
        
        # >>> 6. Lunar horizontal parallax
        
        HP: float = cm.wrap_angle(g_0 + sum([g[i] * np.cos(np.deg2rad(h[i] + k[i] * T_0)) for i in range(0, 4)]), high=180)
        
        # >>> 7. Earth-Moon distance
        
        r_earth_moon: float = bd.BODIES[bd.Attractor.EARTH].R_E.to_value(u.km) / np.sin(np.deg2rad(HP))
        
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
    def nodal_regression_rate(attractor: bd.Attractor,
                              orbital_elements: o3d.OrbitalElements) -> typing.List[u.Quantity]:
        """
        Calculate the nodal regression rate (right ascension of the ascending node) due to:
        - J2 perturbation
        - Lunar gravity
        - Solar gravity

        Args:
            attractor (bd.Attractor): Main attractor
            orbital_elements (o3d.OrbitalElements): Orbital elements

        Returns:
            typing.List[u.Quantity]: Nodal regression rates [deg / day]
        """
        
        cm.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                      orbital_elements.eccentricity.to_value(),
                                      orbital_elements.inclination.to_value(u.deg),
                                      orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements.true_anomaly.to_value(u.deg))
        
        # >>> Parameters
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        R_E: float = bd.BODIES[attractor].R_E.to_value(u.km)
        
        J_2: float = bd.BODIES[attractor].J2.to_value(u.one)
        
        a: float = orbital_elements.semimajor_axis.to_value(u.km)
        
        e: float = orbital_elements.eccentricity.to_value(u.dimensionless_unscaled)
        
        inc: float = orbital_elements.inclination.to_value(u.rad)
        
        period: float = orbital_elements.calc_orbital_period(attractor=attractor).to_value(u.hour)
        
        num_revolutions: float = 24 / period
        
        # >>> Nodal regression rate - gravitational perturbation
        
        if bd.BODIES[attractor].J2 is None:
            
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
    def sun_synchronous_inclination(attractor: bd.Attractor,
                                    orbital_elements: o3d.OrbitalElements,
                                    nodal_regression_rate: u.Quantity) -> u.Quantity:
        """
        Calculate the sun-synchronous inclination for a given semimajor axis and eccentricity

        Args:
            attractor (bd.Attractor): Main attractor
            orbital_elements (o3d.OrbitalElements): Orbital elements
            nodal_regression_rate (u.Quantity): Nodal regression rate
        Returns:
            u.Quantity: Sun-synchronous inclination [deg]
        """
        
        cm.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                      orbital_elements.eccentricity.to_value(),
                                      orbital_elements.inclination.to_value(u.deg),
                                      orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements.true_anomaly.to_value(u.deg))
        
        if bd.BODIES[attractor].J2 is None: return 0.0 * u.deg
        
        # >>> Parameters
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        R_E: float = bd.BODIES[attractor].R_E.to_value(u.km)
        
        J_2: float = bd.BODIES[attractor].J2.to_value(u.one)
        
        a: float = orbital_elements.semimajor_axis.to_value(u.km)
        
        e: float = orbital_elements.eccentricity.to_value(u.dimensionless_unscaled)
        
        dOmega_dt: float = nodal_regression_rate.to_value(u.rad / u.s)
        
        # >>> Sun-synchronous inclination
        
        inc: float = np.arccos(- 2 / 3 * dOmega_dt * (a**(7/2) * (1 - e**2)**2) / (J_2 * np.sqrt(mu) * R_E**2))
        
        return u.Quantity(inc, unit=u.rad).to(u.deg)
    
    @staticmethod
    def apsidal_rotation_rate(attractor: bd.Attractor,
                              orbital_elements: o3d.OrbitalElements) -> typing.List[u.Quantity]:
        """
        Calculate the apsidal rotation rate (argument of periapsis) due to:
        - J2 perturbation
        - Lunar gravity
        - Solar gravity

        Args:
            attractor (bd.Attractor): Main attractor
            orbital_elements (o3d.OrbitalElements): Orbital elements

        Returns:
            typing.List[u.Quantity]: Apsidal rotation rates [deg / day]
        """
        
        cm.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                      orbital_elements.eccentricity.to_value(),
                                      orbital_elements.inclination.to_value(u.deg),
                                      orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements.true_anomaly.to_value(u.deg))
        
        # >>> Parameters
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        R_E: float = bd.BODIES[attractor].R_E.to_value(u.km)
        
        J_2: float = bd.BODIES[attractor].J2.to_value(u.one)
        
        a: float = orbital_elements.semimajor_axis.to_value(u.km)
        
        e: float = orbital_elements.eccentricity.to_value(u.dimensionless_unscaled)
        
        inc: float = orbital_elements.inclination.to_value(u.rad)
        
        period: float = orbital_elements.calc_orbital_period(attractor=attractor).to_value(u.hour)
        
        num_revolutions: float = 24 / period
        
        # >>> Apsidal rotation rate - gravitational perturbation
        
        if bd.BODIES[attractor].J2 is None:
            
             domega_dt_g: u.Quantity = 0.0 * u.rad / u.s
        
        else:
            
            coefficient: float = - 3 / 2 * J_2 * np.sqrt(mu) * R_E**2 / (a**(7/2) * (1 - e**2)**2)
        
            domega_dt_g: u.Quantity = coefficient * (5 / 2 * np.sin(inc)**2 - 2) * u.rad / u.s
        
        # >>> Apsidal rotation rate - lunar gravity
        
        domega_dt_l: u.Quantity = 0.00169 / num_revolutions * (4 - 5 * np.sin(inc)**2) * u.deg / u.day
        
        # >>> Apsidal rotation rate - solar gravity
        
        domega_dt_s: u.Quantity = 0.00077 / num_revolutions * (4 - 5 * np.sin(inc)**2) * u.deg / u.day
        
        return [domega_dt_g.to(u.deg / u.day), domega_dt_l, domega_dt_s]
    
    # --- PUBLIC ---
    
    def init(self,
             attractor: bd.Attractor,
             position: u.Quantity,
             velocity: u.Quantity,
             julian_day: float = 0,
             ballistic_coefficient: u.Quantity = 0 * u.m**2 / u.kg,
             ballistic_coefficient_srp: u.Quantity = 0 * u.m**2 / u.kg) -> None:
        """
        Initialize the parameters for the propagation

        Args:
            attractor (bd.Attractor): Main attractor
            position (u.Quantity): Position vector
            velocity (u.Quantity): Velocity vector
            julian_day (float): Julian Day
            ballistic_coefficient (u.Quantity, optional): Ballistic coefficient. Defaults to 0 * u.m**2 / u.kg.
            ballistic_coefficient (u.Quantity, optional): Ballistic coefficient for Solar Radiation Pressure. Defaults to 0 * u.m**2 / u.kg.
        """
        
        cm.check_attractor(attractor)
        
        cm.check_position_vector(position.to_value(u.km))
        
        cm.check_velocity_vector(velocity.to_value(u.km / u.s))
        
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
    
    def propagate_cowell_for(self, delta: t.TimeDelta) -> Result:
        """
        Propagate the relative motion with perturbations using Cowell's method

        Args:
            delta (time.TimeDelta): Delta time for propagation
        
        Returns:
            Result: Integration result
        """
        
        if not self.ready: raise ValueError(self.not_ready_message)
        
        cm.check_time_delta(delta)
        
        result: Result = Result()
        
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
    
    def propagate_encke_for(self, delta: t.TimeDelta, step: t.TimeDelta) -> Result:
        """
        Propagate the relative motion with perturbations using Encke's method

        Args:
            delta (time.TimeDelta): Delta time for propagation
            step (time.TimeDelta): Time step between 0 and delta
        
        Returns:
            Result: Integration result
        """
        
        if not self.ready: raise ValueError(self.not_ready_message)
        
        cm.check_time_delta(delta)
        
        cm.check_time_delta(step)
        
        if step >= delta: raise ValueError("'step' must be smaller than 'delta'")
        
        # >>> 1. Initial conditions
        
        r_0: np.ndarray = self.position
        
        v_0: np.ndarray = self.velocity
        
        dr_0: np.ndarray = np.zeros(shape=(3))
        
        dv_0: np.ndarray = np.zeros(shape=(3))
        
        oe_0: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=self.attractor,
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
        
        orbital_elements: typing.List[o3d.OrbitalElements] = [oe_0]
        
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
            
            oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=self.attractor,
                                                                         position=r_0 * u.km,
                                                                         velocity=v_0 * u.km / u.s)
            
            orbital_elements.append(oe)
        
        result: Result = Result()
        
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
    
    def propagate_gauss_for(self, delta: t.TimeDelta) -> Result:
        """
        Propagate the relative motion with perturbations using Gauss variational equations

        Args:
            delta (time.TimeDelta): Delta time for propagation
        
        Returns:
            Result: Integration result
        """
        
        if not self.ready: raise ValueError(self.not_ready_message)
        
        cm.check_time_delta(delta)
        
        oe_0: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=self.attractor,
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
        
        result: Result = Result()
        
        result.success = solution['success']
        result.time = solution['t'] * u.s
        result.orbital_elements = []
        
        for idx, _ in enumerate(solution['t']):
            
            solution_idx: np.ndarray = solution['y'][:, idx]
            
            oe_idx: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=solution_idx[0] * u.km**2 / u.s,
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

        The unperturbed (two‑body) accelerations are:

            dx/dt   = v_x
            dy/dt   = v_y
            dz/dt   = v_z

            dv_x/dt = - μ * x / r³
            dv_y/dt = - μ * y / r³
            dv_z/dt = - μ * z / r³

        When enabled, the following perturbations are added:

        **1. Atmospheric drag**

            v_rel = v_sc − v_atm
            
            a_drag = -½ ρ ||v_rel|| B v_rel

            where:
                ρ   = atmospheric density at altitude (r − R_E)
                B   = ballistic coefficient
                v_atm = ω × r_sc (rigidly rotating atmosphere)

        **2. J₂ gravitational perturbation**

            a_J2 = (3/2) J₂ μ R_E² / r⁴ · [ x/r (5 z²/r² − 1), y/r (5 z²/r² − 1), z/r (5 z²/r² − 3) ]

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
        
        mu: float = bd.BODIES[self.attractor].mu.to_value(u.km**3 / u.s**2)
        
        omega: float = bd.BODIES[self.attractor].omega.to_value(u.rad / u.s)
        
        R_E: float = bd.BODIES[self.attractor].R_E.to_value(u.km)
        
        J_2: float = bd.BODIES[self.attractor].J2.to_value(u.one)
        
        # >>> Perturbations
        
        p_atm_drag: np.ndarray = np.zeros(shape=(3))
        
        p_gra_per: np.ndarray = np.zeros(shape=(3))
        
        if self.use_atmospheric_drag:
            
            # * Atmospheric Drag
            
            r_sc: np.ndarray = X[:3] # ? Spacecraft position
            
            v_sc: np.ndarray = X[3:] # ? Spacecraft velocity
            
            v_atm: np.ndarray = np.cross(np.array([0, 0, omega]), r_sc) # ? Atmosphere velocity
            
            v_rel: np.ndarray = v_sc - v_atm # ? Relative velocity w.r.t. atmosphere
            
            rho: float = self.density((r - R_E) * u.km).to_value(u.kg / u.km**3)
            
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
        two‑body orbit. The state vector is:

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

        The unperturbed two‑body acceleration is evaluated at the *osculating* radius:

            a_2body = - μ * r_osc / ||r_osc||³

        Encke's method introduces a correction term to avoid subtracting nearly equal numbers when computing the
        perturbed acceleration. Define:

            q = ( dr · (2 r_sc − dr) ) / r²

            F(q) = (q² − 3q + 3) / (1 + (1 − q)^(3/2)) * q

        The corrected gravitational term becomes:

            a_encke = - μ / ||r_osc||³ * ( dr − F(q) * r_sc )

        Optional perturbations may be added:

        **1. Atmospheric drag**

            v_rel = v_sc − (ω × r_sc)
            
            a_drag = -½ ρ ||v_rel|| B v_rel

            where:
                ρ   = atmospheric density at altitude (r − R_E)
                B   = ballistic coefficient
                v_atm = ω × r_sc (rigidly rotating atmosphere)

        **2. J₂ gravitational perturbation**

            a_J2 = (3/2) J₂ μ R_E² / r⁴ · [ x/r (5 z²/r² − 1), y/r (5 z²/r² − 1), z/r (5 z²/r² − 3) ]

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
        
        mu: float = bd.BODIES[self.attractor].mu.to_value(u.km**3 / u.s**2)
        
        omega: float = bd.BODIES[self.attractor].omega.to_value(u.rad / u.s)
        
        R_E: float = bd.BODIES[self.attractor].R_E.to_value(u.km)
        
        J_2: float = bd.BODIES[self.attractor].J2.to_value(u.one)
        
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
            
            rho: float = self.density((r - R_E) * u.km).to_value(u.kg / u.km**3)
            
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
            dθ/dt       = h/r² + (1/(eh)) [ (h²/μ) cosθ R − (r + h²/μ) sinθ S ]
            dΩ/dt       = r/(h sin i) sin(ω + θ) W
            di/dt       = r/h cos(ω + θ) W
            dω/dt       = − (1/(eh)) [ (h²/μ) cosθ R − (r + h²/μ) sinθ S ] − r/(h tan i) sin(ω + θ) W

        where (R, S, W) are the perturbing accelerations projected onto the RSW frame.

        The following perturbations may be included:

        **1. Atmospheric drag**
        
            v_rel = v_sc − (ω × r_sc)
            
            a_drag projected into (R, S, W) using the flight‑path angle γ.

        **2. J₂ gravitational perturbation**
        
            a_J2 = −(3/2) J₂ μ R_E² / r⁴ · f(Ω, i, ω + θ)

            projected analytically into (R, S, W).

        **3. Solar radiation pressure (SRP)**
        
            a_SRP = (S/c) B_SRP · shadow_factor
            
            projected into RSW using the DCM from inertial to RSW.

        **4. Third‑body gravity (Moon, Sun)**
        
            a_3B = μ_3B ( r_3B_sc/||r_3B_sc||³ − r_3B/||r_3B||³ )
            
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
        
        ta = cm.wrap_angle(angle=ta, low=0, high=2 * np.pi)
        raan = cm.wrap_angle(angle=raan, low=0, high=2 * np.pi)
        inc = cm.wrap_angle(angle=inc, low=-0.5 * np.pi, high=0.5 * np.pi)
        argp = cm.wrap_angle(angle=argp, low=0, high=2 * np.pi)
        
        oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=h * u.km ** 2 / u.s,
                                                      semimajor_axis=0.0 * u.km,
                                                      eccentricity=ecc * u.dimensionless_unscaled,
                                                      inclination=inc * u.rad,
                                                      right_ascension_of_ascending_node=raan * u.rad,
                                                      argument_of_periapsis=argp * u.rad,
                                                      true_anomaly=ta * u.rad)
        
        mu: float = bd.BODIES[self.attractor].mu.to_value(u.km**3 / u.s**2)
        
        omega: float = bd.BODIES[self.attractor].omega.to_value(u.rad / u.s)
        
        R_E: float = bd.BODIES[self.attractor].R_E.to_value(u.km)
        
        J_2: float = bd.BODIES[self.attractor].J2.to_value(u.one)
        
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
            
            rho: float = self.density((r - R_E) * u.km).to_value(u.kg / u.km**3)
            
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
            
            timestamp_0: t.Time = od.OrbitDetermination.julian_day_2_timestamp(julian_day=self.julian_day)
            
            r_sun, lambda_, epsilon = self.sun_position(timestamp=timestamp_0 + t / 86400)
            
            c: u.Quantity = pc.speed_of_light
            
            S_0: u.Quantity = pc.radiated_power_intensity_photosphere
            
            R_0: u.Quantity = pc.photosphere_radius.to(u.m)
            
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
            
            timestamp_0: t.Time = od.OrbitDetermination.julian_day_2_timestamp(julian_day=self.julian_day)
            
            r_moon: u.Quantity = self.moon_position(timestamp=timestamp_0 + t / 86400)
            
            r_moon_sc: u.Quantity = r_moon - r_sc
            
            mu_moon: u.Quantity = bd.BODIES[bd.Attractor.MOON].mu
            
            p_moon: u.Quantity = mu_moon * (r_moon_sc / np.linalg.norm(r_moon_sc)**3 - r_moon / np.linalg.norm(r_moon)**3)
            
            r_hat: u.Quantity = r_sc / np.linalg.norm(r_sc)
            w_hat: u.Quantity = np.cross(r_sc, v_sc) / np.linalg.norm(np.cross(r_sc, v_sc))
            s_hat: u.Quantity = np.cross(w_hat, r_sc) / np.linalg.norm(np.cross(w_hat, r_sc))
            
            p_r += np.dot(p_moon.to_value(u.km / u.s**2), r_hat.to_value())
            p_s += np.dot(p_moon.to_value(u.km / u.s**2), s_hat.to_value())
            p_w += np.dot(p_moon.to_value(u.km / u.s**2), w_hat.to_value())
        
        if self.use_solar_gravity:
            
            # * Solar gravity
            
            timestamp_0: t.Time = od.OrbitDetermination.julian_day_2_timestamp(julian_day=self.julian_day)
            
            r_sun, lambda_, epsilon = self.sun_position(timestamp=timestamp_0 + t / 86400)
            
            r_sun_sc: u.Quantity = r_sun - r_sc
            
            mu_sun: u.Quantity = bd.BODIES[bd.Attractor.SUN].mu
            
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
