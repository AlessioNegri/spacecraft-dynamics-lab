"""
Interplanetary Trajectories

Implementation of interplanetary trajectories algorithms.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 8: Interplanetary Trajectories
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as time
import astropy.units as u
import dataclasses
import enum
import numpy as np
import typing

import astro.bodies as bd
import astro.common as cm
import astro.orbit_3d as o3d
import astro.orbit_determination as od
import astro.orbital_position as op

@dataclasses.dataclass
class HyperbolaParameters():
    """Hyperbola Parameters
    """
    
    specific_angular_momentum: u.Quantity = 0.0 * u.km**2 / u.s
    eccentricity: u.Quantity = 0.0 * u.dimensionless_unscaled
    periapse_radius: u.Quantity = 0.0 * u.km
    asymptote_angle: u.Quantity = 0.0 * u.rad
    turn_angle: u.Quantity = 0.0 * u.rad
    aiming_radius: u.Quantity = 0.0 * u.km

class FlybySide(enum.IntEnum):
    """Type of fly-by"""
    
    DARK_SIDE = 0
    SUNLIT_SIDE = 1

class InterplanetaryTrajectories():
    """Interplanetary Trajectories
    """
    
    # --- STATIC ---
    
    @staticmethod
    def synodic_period(departure_planet: bd.Attractor, arrival_planet: bd.Attractor) -> u.Quantity:
        """Calculate the **Synodic Period** for an interplanetary transfer

        Args:
            departure_planet (bd.Attractor): Departure planet
            arrival_planet (bd.Attractor): Arrival planet

        Returns:
            u.QUantity: Synodic period
        """
        
        cm.check_attractor(attractor=departure_planet)
        
        cm.check_attractor(attractor=arrival_planet)
        
        departure_period: float = bd.BODIES[departure_planet].T_S.to_value(u.s)
        
        arrival_period: float = bd.BODIES[arrival_planet].T_S.to_value(u.s)
        
        # >>> 1. Mean motions
        
        n_1: float = 2 * np.pi / departure_period
        n_2: float = 2 * np.pi / arrival_period
        
        # >>> 2. Synodic period
        
        T_S: float = 2 * np.pi / np.abs(n_2 - n_1)
        
        return T_S * u.s
    
    @staticmethod
    def wait_time(departure_planet: bd.Attractor, arrival_planet: bd.Attractor) -> typing.List[u.Quantity]:
        """
        Calculate the **wait time** for an interplanetary transfer
        
        It is assumed that the planetary orbits are circular to simplify the calculations

        Args:
            departure_planet (bd.Attractor): Departure planet
            arrival_planet (bd.Attractor): Arrival planet

        Returns:
            typing.List[u.Quantity]: [initial phase angle, final phase angle, wait time]
        """
        
        cm.check_attractor(attractor=departure_planet)
        
        cm.check_attractor(attractor=arrival_planet)
        
        R_1: float = bd.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bd.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        departure_period: float = bd.BODIES[departure_planet].T_S.to_value(u.s)
        
        arrival_period: float = bd.BODIES[arrival_planet].T_S.to_value(u.s)
        
        # >>> 1. Time Of Flight on transfer ellipse of Hohmann transfer between circular orbits
        
        mu_sun: float = bd.BODIES[bd.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        n_1: float = 2 * np.pi / departure_period
        n_2: float = 2 * np.pi / arrival_period
        
        t_12: float = np.pi / np.sqrt(mu_sun) * ((R_1 + R_2) / 2)**(3/2)
        
        # >>> 2. Initial phase angle bewteen planets (departure trip)
        
        phi_0: float = np.pi - n_2 * t_12
        
        # >>> 3. Final phase angle at planet arrival (departure trip)
        
        phi_f: float = np.pi - n_1 * t_12
        
        # >>> 4. Initial phase angle bewteen planets (return trip)
        
        # phi_0_p: float = - phi_f
        
        # >>> 5. Wait time (increase N until the time becomes positive)
        
        t_wait: float = -1
        
        N: int = 0
        
        while t_wait < 0:
            
            if n_1 > n_2:
                
                t_wait = (-2 * phi_f - 2 * np.pi * N) / (n_2 - n_1)
            
            else:
                
                t_wait = (-2 * phi_f + 2 * np.pi * N) / (n_2 - n_1)
            
            N += 1
        
        return [phi_0 * u.rad, phi_f * u.rad, t_wait * u.s]
    
    @staticmethod
    def sphere_of_influence(body: bd.Attractor, main_attractor: bd.Attractor) -> u.Quantity:
        """Calculate the Sphere Of Influence (SOI) of the given body w.r.t. the main attractor

        Args:
            body (bd.Attractor): Planet
            main_attractor (bd.Attractor): Main attractor

        Returns:
            u.Quantity: Sphere Of Influence
        """
        
        cm.check_attractor(attractor=body)
        
        cm.check_attractor(attractor=main_attractor)
        
        R: float = bd.BODIES[body].semi_major_axis.to_value(u.km)
        
        m_body: float = bd.BODIES[body].M.to_value(u.kg)
        
        m_sun: float = bd.BODIES[main_attractor].M.to_value(u.kg)
        
        return R * (m_body / m_sun)**(2/5) * u.km
    
    @staticmethod
    def departure(departure_planet: bd.Attractor,
                  arrival_planet: bd.Attractor,
                  periapse_radius: u.Quantity) -> typing.Tuple[u.Quantity, HyperbolaParameters]:
        """
        Planetary departure hyperbola design
        
        Planet orbits are assumed to be circular and coplanar to simplify the calculations

        Args:
            departurePlanet (CelestialBody): Departure planet
            arrivalPlanet (CelestialBody): Arrival planet
            periapse_radius (u.Quantity): Circular Parking Orbit radius

        Returns:
            typing.Tuple[u.Quantity, HyperbolaParameters]: [dv, params]
        """
        
        cm.check_attractor(attractor=departure_planet)
        
        cm.check_attractor(attractor=arrival_planet)
        
        mu_sun: float = bd.BODIES[bd.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        mu_1: float = bd.BODIES[departure_planet].mu.to_value(u.km**3 / u.s**2)
        
        R_1: float = bd.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bd.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        r_p: float = periapse_radius.to_value(u.km)
        
        # >>> 1. Hyperbolic excess speed of the departure hyperbola (ΔV_DEP = V_SC_DEP - V_PLANET_DEP)
        
        v_inf: float = np.sqrt(mu_sun / R_1) * (np.sqrt(2 * R_2 / (R_1 + R_2)) - 1)
        
        # >>> 2. Hyperbolic trajectory
        
        e: float = 1 + r_p * v_inf**2 / mu_1 # ? Eccentricity
        
        h: float = r_p * np.sqrt(v_inf**2 + 2 * mu_1 / r_p) # ? Specific Angular Momentum
        
        v_p: float = h / r_p # ? Periapse Velocity
        
        asymptote_angle: float = np.arccos(1 / e) # ? Location of periapsis where executing the delta-v maneuver
        
        turn_angle: float = 2 * np.arcsin(1 / e)
        
        aiming_radius: float = h**2 / mu_1 * 1 / np.sqrt(e**2 - 1)
        
        # >>> 3. Circular parking orbit
        
        v_c: float = np.sqrt(mu_1 / r_p)
        
        # >>> 4. Maneuver
        
        dv: float = np.abs(v_p - v_c)
        
        hyperbola_params: HyperbolaParameters = HyperbolaParameters(specific_angular_momentum=h * u.km**2 / u.s,
                                                                    eccentricity=e * u.dimensionless_unscaled,
                                                                    periapse_radius=r_p * u.km,
                                                                    asymptote_angle=asymptote_angle * u.rad,
                                                                    turn_angle=turn_angle * u.rad,
                                                                    aiming_radius=aiming_radius * u.km)
        
        return dv * u.km / u.s, hyperbola_params
    
    @staticmethod
    def rendezvous(departure_planet: bd.Attractor,
                   arrival_planet: bd.Attractor,
                   orbit_period : u.Quantity) -> typing.Tuple[u.Quantity, HyperbolaParameters, o3d.OrbitalElements]:
        """
        Planetary arrival hyperbola design with optimal periapse radius
        
        r_p_opt = (2 * mu_2 / v_inf**2) * (1 - e) / (1 + e)

        Args:
            departure_planet (bd.Attractor): Departure planet
            arrival_planet (bd.Attractor): Arrival planet
            orbit_period (u.Quantity): Elliptical Capture Orbit period

        Returns:
            typing.Tuple[u.Quantity, HyperbolaParameters, o3d.OrbitalElements]: [dv, params, Orbital Elements]
        """
        
        cm.check_attractor(attractor=departure_planet)
        
        cm.check_attractor(attractor=arrival_planet)
        
        mu_sun: float = bd.BODIES[bd.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        mu_2: float = bd.BODIES[arrival_planet].mu.to_value(u.km**3 / u.s**2)
        
        R_1: float = bd.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bd.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        T: float = orbit_period.to_value(u.s)
        
        # >>> 1. Hyperbolic excess speed of the arrival hyperbola (ΔV_ARR = V_PLANET_ARR - V_SC_ARR)
        
        v_inf: float = np.sqrt(mu_sun / R_2) * (1 - np.sqrt(2 * R_1 / (R_1 + R_2)))
        
        # >>> 2. Capture orbit with optimal periapse radius
        
        a: float = (T * np.sqrt(mu_2) / (2 * np.pi))**(2/3) # ? Semi-major axis
        
        e: float = (2 * mu_2) / (a * v_inf**2) - 1 # ? Eccentricity with optimal periapse radius
        
        r_p: float = (2 * mu_2 / v_inf**2) * (1 - e) / (1 + e) # ? Optimal periapse radius
        
        oe_capture: o3d.OrbitalElements = o3d.OrbitalElements(0, a * u.km, e * u.dimensionless_unscaled, 0, 0, 0, 0)
        
        # >>> 3. Hyperbolic trajectory
        
        e_hyp: float = 1 + r_p * v_inf**2 / mu_2 # ? Eccentricity
        
        h_hyp: float = r_p * np.sqrt(v_inf**2 + 2 * mu_2 / r_p) # ? Specific angular momentum
        
        turn_angle: float = 2 * np.arcsin(1 / e_hyp)
        
        asymptote_angle: float = np.arccos(1 / e_hyp) # ? Angle to periapsis
        
        aiming_radius: float = h_hyp**2 / mu_2 * 1 / np.sqrt(e_hyp**2 - 1)
        
        hyperbola_params: HyperbolaParameters = HyperbolaParameters(specific_angular_momentum=h_hyp * u.km**2 / u.s,
                                                                    eccentricity=e_hyp * u.dimensionless_unscaled,
                                                                    periapse_radius=r_p * u.km,
                                                                    asymptote_angle=asymptote_angle * u.rad,
                                                                    turn_angle=turn_angle * u.rad,
                                                                    aiming_radius=aiming_radius * u.km)
        
        # >>> 4. Maneuver
        
        dv: float = v_inf * np.sqrt((1 - e) / 2)
        
        return dv * u.km / u.s, hyperbola_params, oe_capture
    
    @staticmethod
    def flyby(departure_planet: bd.Attractor,
              arrival_planet: bd.Attractor,
              periapse_radius: u.Quantity,
              nu_1: u.Quantity,
              side: FlybySide = FlybySide.DARK_SIDE)\
    -> typing.Tuple[o3d.OrbitalElements, HyperbolaParameters, o3d.OrbitalElements]:
        """
        Planetary flyby hyperbola design
        
        Planet orbits are assumed to be circular and coplanar to simplify the calculations

        Args:
            departure_planet (bd.Attractor): Departure planet
            arrival_planet (bd.Attractor): Arrival planet
            periapse_radius (u.Quantity): Hyperbola periapse radius
            nu_1 (u.Quantity): True anomaly of the incoming trajectory
            side (FlybySide, optional): Side w.r.t. Sun. Defaults to FlybySide.DARK_SIDE.

        Returns:
            typing.Tuple[o3d.OrbitalElements, HyperbolaParameters, o3d.OrbitalElements]:
                [Pre-flyby Orbital Elements, Hyperbola Parameters, Post-flyby Orbital Elements]
        """
        
        cm.check_attractor(attractor=departure_planet)
        
        cm.check_attractor(attractor=arrival_planet)
        
        cm.check_angle(angle=nu_1.to_value(u.deg))
        
        mu_sun: float = bd.BODIES[bd.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        mu_2: float = bd.BODIES[arrival_planet].mu.to_value(u.km**3 / u.s**2)
        
        R_1: float = bd.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bd.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        r_p: float = periapse_radius.to_value(u.km)
        
        nu_1: float = nu_1.to_value(u.rad)
        
        # >>> 1. Preflyby ellipse (orbit 1) - Heliocentric frame
        
        e_1: float = (R_1 - R_2) / (R_1 + R_2 * np.cos(nu_1)) # ? Eccentricity
        
        h_1: float = np.sqrt(mu_sun * R_1 * (1 - e_1)) # ? Specific angular momentum
        
        V_t_1: float = mu_sun / h_1 * (1 + e_1 * np.cos(nu_1)) # ? Transverse velocity
        
        V_r_1: float = mu_sun / h_1 * e_1 * np.sin(nu_1) # ? Radial velocity
        
        oe_1: o3d.OrbitalElements = o3d.OrbitalElements(h_1 * u.km**2 / u.s,
                                                        0 * u.km,
                                                        e_1 * u.dimensionless_unscaled,
                                                        0, 0, 0, 0)
        
        # >>> 2. Flyby hyperbola - Planetocentric frame (u_v, u_s)
        
        V_1_v: np.ndarray = np.array([V_t_1, -V_r_1]) # ? Vehicle velocity in the heliocentric frame at flyby point
        
        V_planet: np.ndarray = np.array([np.sqrt(mu_sun / R_2), 0]) # ? Planet velocity in the heliocentric frame
        
        v_inf_1: np.ndarray = V_1_v - V_planet # ? Hyperbolic excess velocity of the spacecraft
        
        v_inf_1_norm: float = np.linalg.norm(v_inf_1)
        
        e_hyp: float = 1 + r_p * v_inf_1_norm**2 / mu_2 # ? Eccentricity of the flyby hyperbola
        
        h_hyp: float = r_p * np.sqrt(v_inf_1_norm**2 + 2 * mu_2 / r_p) # ? Specific angular momentum
        
        turn_angle: float = 2 * np.arcsin(1 / e_hyp)
        
        asymptote_angle: float = np.arccos(1 / e_hyp)
        
        aiming_radius: float = r_p * np.sqrt((e_hyp + 1) / (e_hyp - 1))
        
        phi_1: float = np.arctan(v_inf_1[1] / v_inf_1[0]) # ? Angle between v_inf_1 and V_planet (inbound)
        
        hyperbola_params: HyperbolaParameters = HyperbolaParameters(specific_angular_momentum=h_hyp * u.km**2 / u.s,
                                                                    eccentricity=e_hyp * u.dimensionless_unscaled,
                                                                    periapse_radius=r_p * u.km,
                                                                    asymptote_angle=asymptote_angle * u.rad,
                                                                    turn_angle=turn_angle * u.rad,
                                                                    aiming_radius=aiming_radius * u.km)
        
        # >>> 3. Approach
        
        phi_2: float = 0.0 # ? Angle between v_inf_2 and V_planet (outbound)
        
        if side == FlybySide.DARK_SIDE:
            
            phi_2 = phi_1 + turn_angle
            
        else:
            
            phi_2 = phi_1 - turn_angle
        
        v_inf_2: np.ndarray = v_inf_1_norm * np.array([np.cos(phi_2), np.sin(phi_2)])
        
        V_2_v: np.ndarray = V_planet + v_inf_2 # ? Vehicle velocity in the heliocentric frame after flyby
        
        V_t_2: float = V_2_v[0] # ? Transverse velocity after flyby
        
        V_r_2: float = - V_2_v[1] # ? Radial velocity after flyby (negative because of the reference frame)
        
        # >>> 4. Postflyby ellipse (orbit 2) - Heliocentric frame
        
        h_2: float = R_2 * V_t_2
        
        e_cos: float = h_2**2 / (mu_sun * R_2) - 1 # ? e_2 * cos(nu_2)
        
        e_sin: float = V_r_2 * h_2 / mu_sun # ? e_2 * sin(nu_2)
        
        nu_2: float = np.arctan2(e_sin, e_cos)
        
        e_2: float = e_sin / np.sin(nu_2)
        
        oe_2: o3d.OrbitalElements = o3d.OrbitalElements(h_2 * u.km**2 / u.s,
                                                        0 * u.km,
                                                        e_2 * u.dimensionless_unscaled,
                                                        0, 0, 0, 0)
        
        # >>> 5. Maneuver
        
        return oe_1, hyperbola_params, oe_2
    
    @staticmethod
    def ephemeris(planet: bd.Attractor, timestamp: time.Time) -> typing.List[u.Quantity]:
        """
        Evaluates the ephemeris for a given planet and timestamp
        
        Determine the state vector of a planet at a given date and time. All angular calculations must be adjusted so
        that they lie in the range 0° - 360° (except for inclination, which must be in the range -90° - 90°).

        Args:
            planet (bd.Attractor): Planet
            timestamp (time.Time): Timestamp

        Returns:
            typing.List[u.Quantity]: [r_HEF, v_HEF] state vector in the Heliocentric Ecliptic Frame (HEF)
        """
        
        mu_sun: float = bd.BODIES[bd.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 1. Julian day number
        
        JD: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp=timestamp)
        
        # >>> 2. Number of Julian centuries between J2000 and the given timestamp
        
        T_0: u.Quantity = (JD - 2_451_545) / 36_525 * bd.julian_century
        
        # >>> 3. Orbital elements
        
        poe, dpoe_dt = bd.get_ephemeris(planet)
        
        semi_major_axis: u.Quantity = (poe.semi_major_axis + dpoe_dt.semi_major_axis * T_0)
        
        eccentricity: u.Quantity = poe.eccentricity + dpoe_dt.eccentricity * T_0
        
        inclination: u.Quantity = cm.wrap_angle(poe.inclination + dpoe_dt.inclination * T_0, low=-90, high=90)
        
        right_ascension_of_ascending_node: u.Quantity = cm.wrap_angle(poe.right_ascension_of_ascending_node + dpoe_dt.right_ascension_of_ascending_node * T_0)
        
        longitude_of_perihelion: u.Quantity = cm.wrap_angle(poe.longitude_of_perihelion + dpoe_dt.longitude_of_perihelion * T_0)
        
        mean_longitude: u.Quantity = cm.wrap_angle(poe.mean_longitude + dpoe_dt.mean_longitude * T_0)
        
        # >>> 4. Angular momentum
        
        h: u.Quantity = np.sqrt(mu_sun * semi_major_axis.to_value(u.km) * (1 - eccentricity.to_value(u.dimensionless_unscaled)**2)) * u.km**2 / u.s
        
        # >>> 5. Argument of Perihelion and Mean Anomaly
        
        argument_of_perihelion: u.Quantity = longitude_of_perihelion - right_ascension_of_ascending_node
        
        mean_anomaly: u.Quantity = mean_longitude - longitude_of_perihelion
        
        # >>> 6. True anomaly
        
        period: u.Quantity = 2 * np.pi * np.sqrt(semi_major_axis.to_value(u.km)**3 / mu_sun) * u.s
        
        t: u.Quantity = mean_anomaly.to(u.rad) * period / (2 * np.pi * u.rad)
        
        nu: u.Quantity = op.OrbitalPosition.elliptical_orbit_true_anomaly(t=t, T=period, e=eccentricity.to_value())
        
        # >>> 7. State vector
        
        oe: o3d.OrbitalElements = o3d.OrbitalElements(h,
                                                      semi_major_axis,
                                                      eccentricity,
                                                      inclination,
                                                      right_ascension_of_ascending_node,
                                                      argument_of_perihelion,
                                                      nu)
        
        r_HEF, v_HEF = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=bd.Attractor.SUN, oe=oe)
        
        return r_HEF, v_HEF
    
    @staticmethod
    def optimal_transfer(departure_planet: bd.Attractor,
                         arrival_planet: bd.Attractor,
                         departure_timestamp: time.Time,
                         arrival_timestamp: time.Time,
                         departure_parking_orbit_radius: u.Quantity,
                         arrival_periapse_radius: u.Quantity,
                         arrival_orbit_period: u.Quantity) -> typing.List[u.Quantity]:
        """"
        Optimal transfer with Lambert arc
        
        Given the departure and arrival dates (and, therefore, the time of flight), determine the trajectory for a
        mission from planet 1 to planet 2.

        Args:
            departure_planet (bd.Attractor): Departure planet
            arrival_planet (bd.Attractor): Arrival planet
            departure_timestamp (time.Time): Departure timestamp
            arrival_timestamp (time.Time): Arrival timestamp
            departure_parking_orbit_radius (u.Quantity): Departure parking orbit radius
            arrival_orbit_period (u.Quantity): Arrival orbit period
            arrival_periapse_radius (u.Quantity): Arrival periapse radius

        Returns:
            typing.List[u.Quantity]: [dv_departure, dv_arrival]
        """
        
        cm.check_attractor(attractor=departure_planet)
        
        cm.check_attractor(attractor=arrival_planet)
        
        time_of_flight: time.TimeDelta = (arrival_timestamp - departure_timestamp)
        
        r_p_departure: float = departure_parking_orbit_radius.to_value(u.km)
        
        period_arrival: float = arrival_orbit_period.to_value(u.s)
        
        r_p_A: float = arrival_periapse_radius.to_value(u.km)
        
        mu_departure: float = bd.BODIES[departure_planet].mu.to_value(u.km**3 / u.s**2)
        
        mu_arrival: float = bd.BODIES[arrival_planet].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 1. Planetary ephemeris
        
        R_1, V_1 = InterplanetaryTrajectories.ephemeris(planet=departure_planet, timestamp=departure_timestamp)
        R_2, V_2 = InterplanetaryTrajectories.ephemeris(planet=arrival_planet, timestamp=arrival_timestamp)
        
        # >>> 2. Lambert problem
        
        V_D_v, V_A_v, _, _ = od.OrbitDetermination.lambert(attractor=bd.Attractor.SUN,
                                                           r_1=R_1,
                                                           r_2=R_2,
                                                           dt=time_of_flight)
        
        # >>> 3. Hyperbolic excess velocities
        
        v_inf_D: np.ndarray = (V_D_v - V_1).to_value(u.km / u.s)
        v_inf_A: np.ndarray = (V_A_v - V_2).to_value(u.km / u.s)
        
        # >>> 4. Departure hyperbola
        
        v_p_D: float = np.sqrt(np.linalg.norm(v_inf_D)**2 + 2 * mu_departure / r_p_departure)
        
        v_c_D: float = np.sqrt(mu_departure / r_p_departure)
        
        dv_departure: float = np.abs(v_p_D - v_c_D)
        
        # >>> 5. Arrival hyperbola and parking orbit
        
        # >>> a. Rendezvous orbit from period
    
        a_A: float = (period_arrival * np.sqrt(mu_arrival) / (2 * np.pi))**(2/3)
        
        e_A: float = 1 - r_p_A / a_A
        
        v_p_A: float = np.sqrt(mu_arrival * (1 + e_A) / r_p_A)
        
        # >>> b. Hyperbola trajectory
        
        v_p_hyp: float = np.sqrt(np.linalg.norm(v_inf_A)**2 + 2 * mu_arrival / r_p_A)
        
        # >>> c. Maneuver
        
        dv_arrival: float = np.abs(v_p_hyp - v_p_A)
        
        return dv_departure * u.km / u.s, dv_arrival * u.km / u.s
