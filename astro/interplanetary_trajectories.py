"""
Interplanetary Trajectories

Implementation of interplanetary trajectories algorithms.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 8: Interplanetary Trajectories

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 10: Interplanetary Trajectories

- Ulrich Walter, "Astronautics - The Physics of Space Flight"
    - Chapter 9: Interplanetary Flight
"""

import astropy.time as time
import astropy.units as u
import numpy as np
import typing

import astro.bodies as bodies
import astro.common as common
import astro.orbit_3d as o3d
import astro.orbit_determination as od
import astro.orbital_position as op

from astro.enums import FlybySide

from astro.models.orbit_parameters import HyperbolaParameters
from astro.models.orbital_elements import OrbitalElements

class InterplanetaryTrajectories():
    """Interplanetary Trajectories"""
    
    # --- STATIC ---
    
    @staticmethod
    def synodic_period(departure_planet: bodies.Attractor, arrival_planet: bodies.Attractor) -> u.Quantity:
        """
        Calculate the **Synodic Period** for an interplanetary transfer

        Args:
            departure_planet (bodies.Attractor): Departure planet
            arrival_planet (bodies.Attractor): Arrival planet

        Returns:
            u.QUantity: Synodic period
        """
        
        common.check_attractor(attractor=departure_planet)
        
        common.check_attractor(attractor=arrival_planet)
        
        departure_period: float = bodies.BODIES[departure_planet].T_S.to_value(u.s)
        
        arrival_period: float = bodies.BODIES[arrival_planet].T_S.to_value(u.s)
        
        # >>> 1. Mean motions
        
        n_1: float = 2 * np.pi / departure_period
        n_2: float = 2 * np.pi / arrival_period
        
        # >>> 2. Synodic period
        
        T_S: float = 2 * np.pi / np.abs(n_2 - n_1)
        
        return T_S * u.s
    
    @staticmethod
    def wait_time(departure_planet: bodies.Attractor, arrival_planet: bodies.Attractor) -> typing.List[u.Quantity]:
        """
        Calculate the **wait time** for an interplanetary transfer
        
        It is assumed that the planetary orbits are circular to simplify the calculations

        Args:
            departure_planet (bodies.Attractor): Departure planet
            arrival_planet (bodies.Attractor): Arrival planet

        Returns:
            typing.List[u.Quantity]: [initial phase angle, final phase angle, wait time]
        """
        
        common.check_attractor(attractor=departure_planet)
        
        common.check_attractor(attractor=arrival_planet)
        
        T_1: float = bodies.BODIES[departure_planet].T_S.to_value(u.s)
        
        R_1: float = bodies.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bodies.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        departure_period: float = bodies.BODIES[departure_planet].T_S.to_value(u.s)
        
        arrival_period: float = bodies.BODIES[arrival_planet].T_S.to_value(u.s)
        
        # >>> 1. Time Of Flight on transfer ellipse of Hohmann transfer between circular orbits
        
        mu_sun: float = bodies.BODIES[bodies.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
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
        
        # * Alternative formula
        
        t_wait_2: float = -1
        
        k: int = 0
        
        T_syn: u.Quantity = InterplanetaryTrajectories.synodic_period(departure_planet=departure_planet,
                                                                      arrival_planet=arrival_planet)
        
        while t_wait_2 < 0:
            
            t_wait_2 = T_syn.to_value(u.s) * (k - np.abs(1 - 2 * t_12 / T_1))
            
            k += 1
        
        return [phi_0 * u.rad, phi_f * u.rad, t_wait * u.s]
    
    @staticmethod
    def sphere_of_influence(body: bodies.Attractor,
                            main_attractor: bodies.Attractor,
                            approximation: bool = True) -> u.Quantity:
        """
        Calculate the Sphere Of Influence (SOI) of the given body w.r.t. the main attractor

        Args:
            body (bodies.Attractor): Planet / Moon
            main_attractor (bodies.Attractor): Main attractor
            approximation (bool, optional): Use the approximated formula. Defaults to True.

        Returns:
            u.Quantity: Sphere Of Influence
        """
        
        common.check_attractor(attractor=body)
        
        common.check_attractor(attractor=main_attractor)
        
        R: float = bodies.BODIES[body].semi_major_axis.to_value(u.km)
        
        m_body: float = bodies.BODIES[body].M.to_value(u.kg)
        
        m_main_attractor: float = bodies.BODIES[main_attractor].M.to_value(u.kg)
        
        if approximation:
            
            return R * (m_body / m_main_attractor)**(2/5) * u.km
        
        else:
            
            return R / ((m_body / m_main_attractor)**(-2/5) + 1) * u.km
    
    @staticmethod
    def departure(departure_planet: bodies.Attractor,
                  arrival_planet: bodies.Attractor,
                  periapse_radius: u.Quantity) -> typing.Tuple[u.Quantity, HyperbolaParameters]:
        """
        Planetary departure hyperbola design
        
        Planet orbits are assumed to be circular and coplanar to simplify the calculations

        Args:
            departure_planet (bodies.Attractor): Departure planet
            arrival_planet (bodies.Attractor): Arrival planet
            periapse_radius (u.Quantity): Circular Parking Orbit radius

        Returns:
            typing.Tuple[u.Quantity, HyperbolaParameters]: [dv, params]
        """
        
        common.check_attractor(attractor=departure_planet)
        
        common.check_attractor(attractor=arrival_planet)
        
        mu_sun: float = bodies.BODIES[bodies.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        mu_1: float = bodies.BODIES[departure_planet].mu.to_value(u.km**3 / u.s**2)
        
        R_1: float = bodies.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bodies.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        r_p: float = periapse_radius.to_value(u.km)
        
        # >>> 1. Hyperbolic excess speed of the departure hyperbola (ΔV_DEP = V_SC_DEP - V_PLANET_DEP)
        
        v_inf: float = np.sqrt(mu_sun / R_1) * np.abs((np.sqrt(2 * R_2 / (R_1 + R_2)) - 1))
        
        # >>> 2. Hyperbolic trajectory
        
        e: float = 1 + r_p * v_inf**2 / mu_1 # ? Eccentricity
        
        h: float = r_p * np.sqrt(v_inf**2 + 2 * mu_1 / r_p) # ? Specific Angular Momentum
        
        v_p: float = h / r_p # ? Periapse Velocity
        
        asymptote_angle: float = np.arccos(1 / e) # ? Location of periapsis where executing the delta-v maneuver
        
        turn_angle: float = 2 * np.arcsin(1 / e)
        
        aiming_radius: float = h**2 / mu_1 * 1 / np.sqrt(e**2 - 1)
        
        p: float = h**2 / mu_1
        
        r_soi: u.Quantity = InterplanetaryTrajectories.sphere_of_influence(body=departure_planet,
                                                                           main_attractor=bodies.Attractor.SUN)
        
        theta: float = np.arccos((p / r_soi.to_value(u.km) - 1) / e)
        
        tof: u.Quantity = op.OrbitalPosition.hyperbolic_orbit_time(true_anomaly=theta * u.rad,
                                                                   specific_angular_momentum=h * u.km**2 / u.s,
                                                                   eccentricity=e * u.one,
                                                                   attractor=departure_planet)
        
        # >>> 3. Circular parking orbit
        
        v_c: float = np.sqrt(mu_1 / r_p)
        
        # >>> 4. Maneuver
        
        dv: float = np.abs(v_p - v_c)
        
        hyperbola_params: HyperbolaParameters = HyperbolaParameters(specific_angular_momentum=h * u.km**2 / u.s,
                                                                    eccentricity=e * u.one,
                                                                    periapsis_radius=r_p * u.km,
                                                                    asymptote_angle=asymptote_angle * u.rad,
                                                                    turning_angle=turn_angle * u.rad,
                                                                    aiming_radius=aiming_radius * u.km,
                                                                    specific_energy=(v_inf * u.km / u.s)**2 / 2,
                                                                    hyperbolic_excess_speed=v_inf * u.km / u.s,
                                                                    characteristic_energy=(v_inf * u.km / u.s)**2,
                                                                    time_of_flight=tof)
        
        return dv * u.km / u.s, hyperbola_params
    
    @staticmethod
    def non_hohmann_transfer(departure_planet: bodies.Attractor,
                             arrival_planet: bodies.Attractor,
                             hyperbolic_excess_velocity: u.Quantity)\
                                 -> typing.Tuple[u.Quantity, u.Quantity, u.Quantity, u.Quantity]:
        """
        Calculate the time of flight and true anomaly at arrival for a non-Hohmann transfer.
        
        Hohmann orbits may be the most favorable transfer orbits from an energetic point o view, but they are very
        sensitive to initial thrust errors, and take the longest time. So just a little more thrust would make sure that,
        with small thrust errors, the transfer orbit still intersects the target orbit, while transition time drastically
        decreases.
        
        But how does the crossing point and with it the transition time change with some transfer excess velocity in the
        initial parking orbit?

        Args:
            departure_planet (bodies.Attractor): Departure planet
            arrival_planet (bodies.Attractor): Arrival planet
            hyperbolic_excess_velocity (u.Quantity): Hyperbolic excess velocity

        Returns:
            typing.Tuple[u.Quantity, u.Quantity, u.Quantity, u.Quantity]: [time of flight, true anomaly at arrival, approximate time of flight, approximate true anomaly at arrival]
        """
        
        common.check_attractor(attractor=departure_planet)
        common.check_attractor(attractor=arrival_planet)
        
        mu_sun: float = bodies.BODIES[bodies.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        R_1: float = bodies.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bodies.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        v_inf: float = hyperbolic_excess_velocity.to_value(u.km / u.s)
        
        # >>> 1. Parking orbit velocity
        
        v_planet: float = np.sqrt(mu_sun / R_1)
        
        # >>> 2. Hyperbolic excess velocity and TOF for an Hohmann transfer
        
        v_inf_H: float = np.sqrt(mu_sun / R_1) * np.abs((np.sqrt(2 * R_2 / (R_1 + R_2)) - 1))
        
        tof_H: float = np.pi / np.sqrt(mu_sun) * ((R_1 + R_2) / 2)**(3/2)
        
        # >>> 3. Alpha parameter (inner / outer)
        
        alpha: float = R_1 / R_2 if R_1 <= R_2 else R_2 / R_1
        
        # >>> 4. Time of flight (always first intersection point of the transfer ellipse => -)
        
        sign: float = +1 if R_1 <= R_2 else -1
        
        tof_approx: float = (tof_H * u.s).to_value(u.day) * ( 1 -\
            4 * np.sqrt(2) / (np.pi * np.sqrt(alpha * (1 - alpha**2))) *\
            np.sqrt(np.abs(v_inf_H - v_inf) / (v_planet + sign * v_inf)) )
        
        # >>> 5. True anomaly (always first intersection point of the transfer ellipse => -)
        
        ta_approx: float = 180 * ( 1 -\
            2 * np.sqrt(2) / np.pi * np.sqrt((1 + alpha) / (1 - alpha)) *\
            np.sqrt(np.abs(v_inf_H - v_inf) / (v_planet + sign * v_inf)) )
        
        # >>> 6. Exact solution
        
        v_inf_prime: float = v_planet + v_inf
        
        e: float = R_1 * v_inf_prime**2 / mu_sun - 1 # ? Eccentricity
        
        if e < 0 or e > 1:
            
            print(f"e = {e} is not valid!")
            
            return 0 * u.s, 0 * u.rad, 0 * u.day, 0 * u.deg
        
        a: float = R_1 / (1 - e) # ? Semimajor axis
        
        factor: float = 1 / e * (alpha * (1 + e) - 1)
        
        factor = np.min([np.max([-1, factor]), 1])
        
        ta_exact: float = np.arccos(factor)
        
        # ? Eccentric anomaly for elliptical orbit
        E: float = 2 * np.arctan2(np.sqrt(1 - e) * np.sin(ta_exact / 2), np.sqrt(1 + e) * np.cos(ta_exact / 2))
        
        tof_exact: float = np.sqrt(a**3 / mu_sun) * (E - e * np.sin(E))
        
        return tof_exact * u.s, ta_exact * u.rad, tof_approx * u.day, ta_approx * u.deg
    
    @staticmethod
    def rendezvous_with_optimal_periapsis_radius(departure_planet: bodies.Attractor,
                                                 arrival_planet: bodies.Attractor,
                                                 orbit_period: u.Quantity)\
                                                -> typing.Tuple[u.Quantity, HyperbolaParameters, OrbitalElements]:
        """
        Planetary arrival hyperbola design with optimal periapsis radius
        
        r_p_opt = (2 * mu_2 / v_inf**2) * (1 - e) / (1 + e)

        Args:
            departure_planet (bodies.Attractor): Departure planet
            arrival_planet (bodies.Attractor): Arrival planet
            orbit_period (u.Quantity): Elliptical Capture Orbit period

        Returns:
            typing.Tuple[u.Quantity, HyperbolaParameters, OrbitalElements]: [dv, params, Orbital Elements]
        """
        
        common.check_attractor(attractor=departure_planet)
        
        common.check_attractor(attractor=arrival_planet)
        
        mu_sun: float = bodies.BODIES[bodies.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        mu_2: float = bodies.BODIES[arrival_planet].mu.to_value(u.km**3 / u.s**2)
        
        R_1: float = bodies.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bodies.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        R_E_2: float = bodies.BODIES[arrival_planet].R_E.to_value(u.km)
        
        T: float = orbit_period.to_value(u.s)
        
        # >>> 1. Hyperbolic excess speed of the arrival hyperbola (ΔV_ARR = V_PLANET_ARR - V_SC_ARR)
        
        v_inf: float = np.sqrt(mu_sun / R_2) * (1 - np.sqrt(2 * R_1 / (R_1 + R_2)))
        
        # >>> 2. Capture orbit with optimal periapsis radius
        
        a: float = (T * np.sqrt(mu_2) / (2 * np.pi))**(2/3) # ? Semi-major axis
        
        e: float = (2 * mu_2) / (a * v_inf**2) - 1 # ? Eccentricity with optimal periapsis radius
        
        if e < 0 or e > 1:
            
            print(f"e = {e} is not valid!")
            
            return 0 * u.km / u.s, HyperbolaParameters(), OrbitalElements()
        
        r_p: float = (2 * mu_2 / v_inf**2) * (1 - e) / (1 + e) # ? Optimal periapsis radius
        
        if r_p <= R_E_2:
            
            print(f"r_p = {r_p} <= R_planet = {R_E_2} is not valid!")
            
            return 0 * u.km / u.s, HyperbolaParameters(), OrbitalElements()
        
        oe_capture: OrbitalElements = OrbitalElements(semimajor_axis=a * u.km, eccentricity=e * u.one)
        
        # >>> 3. Hyperbolic trajectory
        
        e_hyp: float = 1 + r_p * v_inf**2 / mu_2 # ? Eccentricity
        
        h_hyp: float = r_p * np.sqrt(v_inf**2 + 2 * mu_2 / r_p) # ? Specific angular momentum
        
        turn_angle: float = 2 * np.arcsin(1 / e_hyp)
        
        asymptote_angle: float = np.arccos(1 / e_hyp) # ? Angle to periapsis
        
        aiming_radius: float = h_hyp**2 / mu_2 * 1 / np.sqrt(e_hyp**2 - 1)
        
        # aiming_radius: float = 2 * np.sqrt(2) * np.sqrt(1 - e) / (1 + e) * mu_2 / v_inf**2
        
        p: float = h_hyp**2 / mu_2
        
        r_soi: u.Quantity = InterplanetaryTrajectories.sphere_of_influence(body=arrival_planet,
                                                                           main_attractor=bodies.Attractor.SUN)
        
        theta_hyp: float = np.arccos((p / r_soi.to_value(u.km) - 1) / e_hyp)
        
        tof: u.Quantity = op.OrbitalPosition.hyperbolic_orbit_time(true_anomaly=theta_hyp * u.rad,
                                                                   specific_angular_momentum=h_hyp * u.km**2 / u.s,
                                                                   eccentricity=e_hyp * u.one,
                                                                   attractor=arrival_planet)
        
        hyperbola_params: HyperbolaParameters = HyperbolaParameters(specific_angular_momentum=h_hyp * u.km**2 / u.s,
                                                                    eccentricity=e_hyp * u.one,
                                                                    periapsis_radius=r_p * u.km,
                                                                    asymptote_angle=asymptote_angle * u.rad,
                                                                    turning_angle=turn_angle * u.rad,
                                                                    aiming_radius=aiming_radius * u.km,
                                                                    specific_energy=(v_inf * u.km / u.s)**2 / 2,
                                                                    hyperbolic_excess_speed=v_inf * u.km / u.s,
                                                                    characteristic_energy=(v_inf * u.km / u.s)**2,
                                                                    time_of_flight=tof)
        
        # >>> 4. Maneuver
        
        dv: float = v_inf * np.sqrt((1 - e) / 2)
        
        return dv * u.km / u.s, hyperbola_params, oe_capture
    
    @staticmethod
    def rendezvous_with_circular_orbit(departure_planet: bodies.Attractor,
                                       arrival_planet: bodies.Attractor,
                                       radius: u.Quantity)\
                                        -> typing.Tuple[u.Quantity, HyperbolaParameters, OrbitalElements]:
        """
        Planetary arrival hyperbola design with circular orbit

        Args:
            departure_planet (bodies.Attractor): Departure planet
            arrival_planet (bodies.Attractor): Arrival planet
            radius (u.Quantity): Circular Orbit radius

        Returns:
            typing.Tuple[u.Quantity, HyperbolaParameters, OrbitalElements]: [dv, params, Orbital Elements]
        """
        
        common.check_attractor(attractor=departure_planet)
        
        common.check_attractor(attractor=arrival_planet)
        
        mu_sun: float = bodies.BODIES[bodies.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        mu_2: float = bodies.BODIES[arrival_planet].mu.to_value(u.km**3 / u.s**2)
        
        R_1: float = bodies.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bodies.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        r_p: float = radius.to_value(u.km)
        
        # >>> 1. Hyperbolic excess speed of the arrival hyperbola (ΔV_ARR = V_PLANET_ARR - V_SC_ARR)
        
        v_inf: float = np.sqrt(mu_sun / R_2) * (1 - np.sqrt(2 * R_1 / (R_1 + R_2)))
        
        # >>> 2. Capture circular orbit
        
        oe_capture: OrbitalElements = OrbitalElements(semimajor_axis=radius)
        
        # >>> 3. Hyperbolic trajectory
        
        e_hyp: float = 1 + r_p * v_inf**2 / mu_2 # ? Eccentricity
        
        h_hyp: float = r_p * np.sqrt(v_inf**2 + 2 * mu_2 / r_p) # ? Specific angular momentum
        
        turn_angle: float = 2 * np.arcsin(1 / e_hyp)
        
        asymptote_angle: float = np.arccos(1 / e_hyp) # ? Angle to periapsis
        
        aiming_radius: float = r_p / v_inf * np.sqrt(v_inf**2 + 2 * mu_2 / r_p)
        
        p: float = h_hyp**2 / mu_2
        
        r_soi: u.Quantity = InterplanetaryTrajectories.sphere_of_influence(body=arrival_planet,
                                                                           main_attractor=bodies.Attractor.SUN)
        
        theta_hyp: float = np.arccos((p / r_soi.to_value(u.km) - 1) / e_hyp)
        
        tof: u.Quantity = op.OrbitalPosition.hyperbolic_orbit_time(true_anomaly=theta_hyp * u.rad,
                                                                   specific_angular_momentum=h_hyp * u.km**2 / u.s,
                                                                   eccentricity=e_hyp * u.one,
                                                                   attractor=arrival_planet)
        
        hyperbola_params: HyperbolaParameters = HyperbolaParameters(specific_angular_momentum=h_hyp * u.km**2 / u.s,
                                                                    eccentricity=e_hyp * u.one,
                                                                    periapsis_radius=r_p * u.km,
                                                                    asymptote_angle=asymptote_angle * u.rad,
                                                                    turning_angle=turn_angle * u.rad,
                                                                    aiming_radius=aiming_radius * u.km,
                                                                    specific_energy=(v_inf * u.km / u.s)**2 / 2,
                                                                    hyperbolic_excess_speed=v_inf * u.km / u.s,
                                                                    characteristic_energy=(v_inf * u.km / u.s)**2,
                                                                    time_of_flight=tof)
        
        # >>> 4. Maneuver
        
        v_p: float = np.sqrt(v_inf**2 + 2 * mu_2 / r_p)
        
        dv: float = v_p - np.sqrt(mu_2 / r_p)
        
        return dv * u.km / u.s, hyperbola_params, oe_capture
    
    @staticmethod
    def rendezvous_with_entry_interface(departure_planet: bodies.Attractor,
                                        arrival_planet: bodies.Attractor,
                                        radius: u.Quantity,
                                        flight_path_angle: u.Quantity)\
                                        -> typing.Tuple[u.Quantity, HyperbolaParameters, OrbitalElements]:
        """
        Planetary arrival hyperbola design with given entry interface (EI) conditions

        Args:
            departure_planet (bodies.Attractor): Departure planet
            arrival_planet (bodies.Attractor): Arrival planet
            radius (u.Quantity): Entry interface radius
            flight_path_angle (u.Quantity): Entry interface flight path angle

        Returns:
            typing.Tuple[u.Quantity, HyperbolaParameters, OrbitalElements]: [dv, params, Orbital Elements]
        """
        
        common.check_attractor(attractor=departure_planet)
        
        common.check_attractor(attractor=arrival_planet)
        
        common.check_angle(angle=flight_path_angle)
        
        mu_sun: float = bodies.BODIES[bodies.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        mu_2: float = bodies.BODIES[arrival_planet].mu.to_value(u.km**3 / u.s**2)
        
        R_1: float = bodies.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bodies.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        r_ei: float = radius.to_value(u.km) # ? Entry Interface
        
        fpa_ei: float = flight_path_angle.to_value(u.rad) # ? Entry Interface
        
        # >>> 1. Hyperbolic excess speed of the arrival hyperbola (ΔV_ARR = V_PLANET_ARR - V_SC_ARR)
        
        v_inf: float = np.sqrt(mu_sun / R_2) * (1 - np.sqrt(2 * R_1 / (R_1 + R_2)))
        
        # >>> 2. Entry interface
        
        v_ei: float = np.sqrt(v_inf**2 + 2 * mu_2 / r_ei) # ? Entry Interface
        
        # >>> 3. Hyperbolic trajectory
        
        h_hyp: float = r_ei * v_ei * np.cos(fpa_ei) # ? Specific angular momentum
        
        aiming_radius: float = (r_ei * np.cos(fpa_ei)) / v_inf * np.sqrt(v_inf**2 + 2 * mu_2 / r_ei)
        
        hyperbola_params: HyperbolaParameters = HyperbolaParameters(specific_angular_momentum=h_hyp * u.km**2 / u.s,
                                                                    eccentricity=0 * u.one,
                                                                    periapsis_radius=0 * u.km,
                                                                    asymptote_angle=0 * u.rad,
                                                                    turning_angle=0 * u.rad,
                                                                    aiming_radius=aiming_radius * u.km,
                                                                    specific_energy=(v_inf * u.km / u.s)**2 / 2,
                                                                    hyperbolic_excess_speed=v_inf * u.km / u.s,
                                                                    characteristic_energy=(v_inf * u.km / u.s)**2,
                                                                    time_of_flight=0 * u.s)
        
        # >>> 4. Maneuver
        
        return 0 * u.km / u.s, hyperbola_params, OrbitalElements()
    
    @staticmethod
    def flyby(departure_planet: bodies.Attractor,
              arrival_planet: bodies.Attractor,
              periapsis_radius: u.Quantity,
              true_anomaly_incoming: u.Quantity,
              side: FlybySide = FlybySide.DARK_SIDE)\
                  -> typing.Tuple[OrbitalElements, HyperbolaParameters, OrbitalElements]:
        """
        Planetary flyby hyperbola design
        
        Planet orbits are assumed to be circular and coplanar to simplify the calculations

        Args:
            departure_planet (bodies.Attractor): Departure planet
            arrival_planet (bodies.Attractor): Arrival planet
            periapse_radius (u.Quantity): Hyperbola periapsis radius
            true_anomaly_incoming (u.Quantity): True anomaly of the incoming trajectory
            side (FlybySide, optional): Side w.r.t. Sun. Defaults to FlybySide.DARK_SIDE.

        Returns:
            typing.Tuple[OrbitalElements, HyperbolaParameters, OrbitalElements]:
                [Pre-flyby Orbital Elements, Hyperbola Parameters, Post-flyby Orbital Elements]
        """
        
        common.check_attractor(attractor=departure_planet)
        
        common.check_attractor(attractor=arrival_planet)
        
        common.check_angle(angle=true_anomaly_incoming)
        
        mu_sun: float = bodies.BODIES[bodies.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        mu_2: float = bodies.BODIES[arrival_planet].mu.to_value(u.km**3 / u.s**2)
        
        R_1: float = bodies.BODIES[departure_planet].semi_major_axis.to_value(u.km)
        
        R_2: float = bodies.BODIES[arrival_planet].semi_major_axis.to_value(u.km)
        
        r_p: float = periapsis_radius.to_value(u.km)
        
        ta_1: float = true_anomaly_incoming.to_value(u.rad)
        
        # >>> 1. Preflyby ellipse (orbit 1) - Heliocentric frame
        
        e_1: float = (R_1 - R_2) / (R_1 + R_2 * np.cos(ta_1)) # ? Eccentricity
        
        h_1: float = np.sqrt(mu_sun * R_1 * (1 - e_1)) # ? Specific angular momentum
        
        V_t_1: float = mu_sun / h_1 * (1 + e_1 * np.cos(ta_1)) # ? Transverse velocity
        
        V_r_1: float = mu_sun / h_1 * e_1 * np.sin(ta_1) # ? Radial velocity
        
        oe_1: OrbitalElements = OrbitalElements(specific_angular_momentum=h_1 * u.km**2 / u.s,
                                                eccentricity=e_1 * u.one,
                                                true_anomaly=ta_1 * u.rad)
        
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
        
        p: float = h_hyp**2 / mu_2
        
        r_soi: u.Quantity = InterplanetaryTrajectories.sphere_of_influence(body=arrival_planet,
                                                                           main_attractor=bodies.Attractor.SUN)
        
        theta: float = np.arccos((p / r_soi.to_value(u.km) - 1) / e_hyp)
        
        tof: u.Quantity = op.OrbitalPosition.hyperbolic_orbit_time(true_anomaly=theta * u.rad,
                                                                   specific_angular_momentum=h_hyp * u.km**2 / u.s,
                                                                   eccentricity=e_hyp * u.one,
                                                                   attractor=arrival_planet)
        
        hyperbola_params: HyperbolaParameters = HyperbolaParameters(specific_angular_momentum=h_hyp * u.km**2 / u.s,
                                                                    eccentricity=e_hyp * u.one,
                                                                    periapsis_radius=r_p * u.km,
                                                                    asymptote_angle=asymptote_angle * u.rad,
                                                                    turning_angle=turn_angle * u.rad,
                                                                    aiming_radius=aiming_radius * u.km,
                                                                    specific_energy=(v_inf_1_norm * u.km / u.s)**2 / 2,
                                                                    hyperbolic_excess_speed=v_inf_1_norm * u.km / u.s,
                                                                    characteristic_energy=(v_inf_1_norm * u.km / u.s)**2,
                                                                    time_of_flight=tof)
        
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
        
        ta_2: float = np.arctan2(e_sin, e_cos)
        
        e_2: float = e_sin / np.sin(ta_2)
        
        oe_2: OrbitalElements = OrbitalElements(specific_angular_momentum=h_2 * u.km**2 / u.s,
                                                eccentricity=e_2 * u.one,
                                                true_anomaly=ta_2 * u.rad)
        
        # >>> 5. Maneuver
        
        return oe_1, hyperbola_params, oe_2
    
    @staticmethod
    def flyby_scheme(planet: bodies.Attractor,
                     planet_position_vector: u.Quantity,
                     planet_velocity_vector: u.Quantity,
                     spacecraft_position_vector: u.Quantity,
                     spacecraft_velocity_vector: u.Quantity) -> u.Quantity:
        """
        Planetary flyby scheme with generalized calculations for output velocity to a flyby that does not take place in
        the planet's orbital plane.

        Args:
            planet (bodies.Attractor): Planet
            planet_position_vector (u.Quantity): Position vector of the planet in the heliocentric frame
            planet_velocity_vector (u.Quantity): Velocity vector of the planet in the heliocentric frame
            spacecraft_position_vector (u.Quantity): Position vector of the spacecraft in the heliocentric frame
            spacecraft_velocity_vector (u.Quantity): Velocity vector of the spacecraft in the heliocentric frame

        Returns:
            u.Quantity: Outgoing velocity vector of the spacecraft after the flyby maneuver in the heliocentric frame
        """
        
        common.check_attractor(planet)
        common.check_position_vector(planet_position_vector.to_value(u.km))
        common.check_position_vector(spacecraft_position_vector.to_value(u.km))
        common.check_velocity_vector(planet_velocity_vector.to_value(u.km / u.s))
        common.check_velocity_vector(spacecraft_velocity_vector.to_value(u.km / u.s))
        
        mu_p: float = bodies.BODIES[planet].mu.to_value(u.km**3 / u.s**2)
        
        r_p: np.ndarray = planet_position_vector.to_value(u.km)
        v_p: np.ndarray = planet_velocity_vector.to_value(u.km)
        
        r_sc: np.ndarray = spacecraft_position_vector.to_value(u.km / u.s)
        v_in: np.ndarray = spacecraft_velocity_vector.to_value(u.km / u.s)
        
        # >>> 1. Hyperbolic excess velocity
        
        r_inf_minus: np.ndarray = r_sc - r_p
        v_inf_minus: np.ndarray = v_in - v_p
        
        v_inf_norm: float = np.linalg.vector_norm(v_inf_minus)
        
        v_inf_minus_hat: np.ndarray = v_inf_minus / v_inf_norm
        
        # >>> 2. Impact parameter
        
        delta: np.ndarray = r_inf_minus - v_inf_minus_hat * np.dot(v_inf_minus_hat, r_inf_minus)
        
        delta_norm: float = np.linalg.vector_norm(delta)
        
        delta_hat: np.ndarray = delta / delta_norm
        
        # ? Normal vector to the flyby plane
        n: np.ndarray = np.cross(v_inf_minus_hat, delta_hat) / np.linalg.vector_norm(np.cross(v_inf_minus_hat, delta_hat))
        
        delta_p: float = np.sign(np.dot(np.cross(r_inf_minus, delta), n)) * v_p**2 / mu_p * np.sqrt(np.dot(delta, delta))
        
        # >>> 3. Rotation matrix
        
        csi: float = delta_p * v_inf_norm**2 / np.linalg.vector_norm(v_p)**2
        
        R_delta: np.ndarray = 1 / (1 + csi**2) *\
            np.array([
                [ csi**2 - 1, - 2 * csi , 0          ],
                [ 2 * csi   , csi**2 - 1, 0          ],
                [ 0         , 0         , 1 + csi**2 ]
            ])
        
        # >>> 4. Transformation matrix (planetocentric system -> flyby plane)

        T_P_F = np.vstack((v_inf_minus_hat, delta_hat, n))
        
        # >>> 5. Outgoing velocity
        
        v_out: np.ndarray = T_P_F.T @ (R_delta @ (T_P_F @ (v_in - v_p))) + v_p
        
        return v_out * u.km / u.s
    
    @staticmethod
    def ephemeris(planet: bodies.Attractor, timestamp: time.Time) -> typing.List[u.Quantity]:
        """
        Evaluate the ephemeris for a given planet and timestamp
        
        Determine the state vector of a planet at a given date and time. All angular calculations must be adjusted so
        that they lie in the range 0° - 360° (except for inclination, which must be in the range -90° - 90°).

        Args:
            planet (bodies.Attractor): Planet
            timestamp (time.Time): Timestamp

        Returns:
            typing.List[u.Quantity]: [r_HEF, v_HEF] state vector in the Heliocentric Ecliptic Frame (HEF)
        """
        
        mu_sun: float = bodies.BODIES[bodies.Attractor.SUN].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 1. Julian day number
        
        JD: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp=timestamp)
        
        # >>> 2. Number of Julian centuries between J2000 and the given timestamp
        
        T_0: u.Quantity = (JD - od.OrbitDetermination.J2000) / 36_525 * bodies.julian_century
        
        # >>> 3. Orbital elements
        
        poe, dpoe_dt = bodies.get_ephemeris(planet)
        
        semi_major_axis: u.Quantity = (poe.semi_major_axis + dpoe_dt.semi_major_axis * T_0)
        
        eccentricity: u.Quantity = poe.eccentricity + dpoe_dt.eccentricity * T_0
        
        inclination: u.Quantity = common.wrap_angle(poe.inclination + dpoe_dt.inclination * T_0, low=-90, high=90)
        
        right_ascension_of_ascending_node: u.Quantity = common.wrap_angle(poe.right_ascension_of_ascending_node + dpoe_dt.right_ascension_of_ascending_node * T_0)
        
        longitude_of_perihelion: u.Quantity = common.wrap_angle(poe.longitude_of_perihelion + dpoe_dt.longitude_of_perihelion * T_0)
        
        mean_longitude: u.Quantity = common.wrap_angle(poe.mean_longitude + dpoe_dt.mean_longitude * T_0)
        
        # >>> 4. Specific angular momentum
        
        h: u.Quantity = np.sqrt(mu_sun * semi_major_axis.to_value(u.km) * (1 - eccentricity.to_value(u.one)**2)) * u.km**2 / u.s
        
        # >>> 5. Argument of Perihelion and Mean Anomaly
        
        argument_of_perihelion: u.Quantity = longitude_of_perihelion - right_ascension_of_ascending_node
        
        mean_anomaly: u.Quantity = mean_longitude - longitude_of_perihelion
        
        if mean_anomaly < 0 * u.rad:
            
            mean_anomaly += 2 * np.pi * u.rad
        
        # >>> 6. True anomaly
        
        period: u.Quantity = 2 * np.pi * np.sqrt(semi_major_axis.to_value(u.km)**3 / mu_sun) * u.s
        
        t: u.Quantity = mean_anomaly.to(u.rad) * period / (2 * np.pi * u.rad)
        
        ta: u.Quantity = op.OrbitalPosition.elliptical_orbit_true_anomaly(time_of_flight=t,
                                                                          period=period,
                                                                          eccentricity=eccentricity)
        
        # >>> 7. State vector
        
        oe: OrbitalElements = OrbitalElements(specific_angular_momentum=h,
                                              semimajor_axis=semi_major_axis,
                                              eccentricity=eccentricity,
                                              inclination=inclination,
                                              right_ascension_of_ascending_node=right_ascension_of_ascending_node,
                                              argument_of_periapsis=argument_of_perihelion,
                                              true_anomaly=ta)
        
        r_hef, v_hef = o3d.Orbit3D.keplerian_to_cartesian(attractor=bodies.Attractor.SUN, orbital_elements=oe) # ? HEF
        
        return r_hef, v_hef
    
    @staticmethod
    def optimal_transfer(departure_planet: bodies.Attractor,
                         arrival_planet: bodies.Attractor,
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
            departure_planet (bodies.Attractor): Departure planet
            arrival_planet (bodies.Attractor): Arrival planet
            departure_timestamp (time.Time): Departure timestamp
            arrival_timestamp (time.Time): Arrival timestamp
            departure_parking_orbit_radius (u.Quantity): Departure parking orbit radius
            arrival_orbit_period (u.Quantity): Arrival orbit period
            arrival_periapse_radius (u.Quantity): Arrival periapse radius

        Returns:
            typing.List[u.Quantity]: [dv_departure, dv_arrival]
        """
        
        common.check_attractor(attractor=departure_planet)
        
        common.check_attractor(attractor=arrival_planet)
        
        time_of_flight: time.TimeDelta = (arrival_timestamp - departure_timestamp)
        
        r_p_departure: float = departure_parking_orbit_radius.to_value(u.km)
        
        period_arrival: float = arrival_orbit_period.to_value(u.s)
        
        r_p_arrival: float = arrival_periapse_radius.to_value(u.km)
        
        mu_departure: float = bodies.BODIES[departure_planet].mu.to_value(u.km**3 / u.s**2)
        
        mu_arrival: float = bodies.BODIES[arrival_planet].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 1. Planetary ephemeris
        
        R_1, V_1 = InterplanetaryTrajectories.ephemeris(planet=departure_planet, timestamp=departure_timestamp)
        R_2, V_2 = InterplanetaryTrajectories.ephemeris(planet=arrival_planet, timestamp=arrival_timestamp)
        
        # >>> 2. Lambert problem
        
        V_D_v, V_A_v, _, _ = od.OrbitDetermination.lambert(attractor=bodies.Attractor.SUN,
                                                           departure_position=R_1,
                                                           arrival_position=R_2,
                                                           delta_time=time_of_flight)
        
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
        
        e_A: float = 1 - r_p_arrival / a_A
        
        v_p_A: float = np.sqrt(mu_arrival * (1 + e_A) / r_p_arrival)
        
        # >>> b. Hyperbola trajectory
        
        v_p_hyp: float = np.sqrt(np.linalg.norm(v_inf_A)**2 + 2 * mu_arrival / r_p_arrival)
        
        # >>> c. Maneuver
        
        dv_arrival: float = np.abs(v_p_hyp - v_p_A)
        
        return dv_departure * u.km / u.s, dv_arrival * u.km / u.s
