"""
Orbital Maneuvers

Implementation of orbital maneuver algorithms.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 6: Orbital Maneuvers

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 3: Orbit Determination
    - Chapter 7: Impulsive Orbital Maneuvers
    - Chapter 9: Low-Thrust Transfers
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as time
import astropy.units as u
import copy
import dataclasses as dc
import enum
import numpy as np
import typing

import astro.bodies as bd
import astro.common as cm
import astro.enums as ae
import astro.orbit_3d as o3d
import astro.orbital_position as op
import astro.orbit_determination as od
import astro.two_body_problem as tbp
import astro.lagrange_coefficients as lc

@dc.dataclass
class ManeuverResult:
    """Maneuver parameters
    
    **orbital_elements_list**: List of orbital elements after each maneuver point
    
    **true_anomaly_list**: List of true anomalies at each maneuver point
    
    **rocket_elevation_angle_list**: List of rocket elevation angles at each maneuver point
    """
    
    delta_velocity_list         : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.km / u.s])
    flight_time_list            : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.s])
    delta_mass_list             : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.kg])
    burn_time_list              : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.s])
    orbital_elements_list       : typing.List[o3d.OrbitalElements] = dc.field(default_factory=lambda: [o3d.OrbitalElements()])
    true_anomaly_list           : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.deg])
    rocket_elevation_angle_list : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.deg])

@dc.dataclass
class RocketMotor:
    """Rocket Motor"""
    
    specific_impulse: u.Quantity = dc.field(default_factory=lambda: 0 * u.s)    # ? Specific Impulse
    thrust          : u.Quantity = dc.field(default_factory=lambda: 0 * u.N)    # ? Thrust
    spacecraft_mass : u.Quantity = dc.field(default_factory=lambda: 0 * u.kg)   # ? Mass of the Spacecraft + propellant
    propellant_mass : u.Quantity = dc.field(default_factory=lambda: 0 * u.kg)   # ? Mass of the propellant
    
    def calc_propellant_mass(self, delta_velocity: u.Quantity, sea_level_gravity: u.Quantity) -> u.Quantity:
        """
        Ideal rocket equation mass calculation

        Args:
            delta_velocity (u.Quantity): Delta velocity
            sea_level_gravity (u.Quantity): Standard gravitational acceleration near sea level

        Returns:
            u.Quantity: Propellant mass
        """
        
        dv: float = delta_velocity.to_value(u.km / u.s)
        g_0: float = sea_level_gravity.to_value(u.km / u.s**2)
        i_sp: float = self.specific_impulse.to_value(u.s)
        m_sc: float = self.spacecraft_mass.to_value(u.kg)
        
        self.propellant_mass = m_sc * (1 - np.exp(-dv / (i_sp * g_0))) * u.kg
        
        return self.propellant_mass
    
    def calc_burn_time(self, propellant_mass: u.Quantity, sea_level_gravity: u.Quantity) -> u.Quantity:
        """
        Burn time calculation

        Args:
            propellant_mass (u.Quantity): Propellant mass
            sea_level_gravity (u.Quantity): Standard gravitational acceleration near sea level

        Returns:
            u.Quantity: Burn time
        """
        
        m_prop: float = propellant_mass.to_value(u.kg)
        g_0: float = sea_level_gravity.to_value(u.m / u.s**2)
        i_sp: float = self.specific_impulse.to_value(u.s)
        T: float = self.thrust.to_value(u.N)
        
        m_dot: float = T / (i_sp * g_0) # ? Engine mass-flow rate
        
        burn_time: u.Quantity = m_prop / m_dot * u.s
        
        return burn_time
    
    def calc_effective_exhaust_velocity(self, sea_level_gravity: u.Quantity) -> u.Quantity:
        """
        Effective exhaust velocity calculation

        Args:
            sea_level_gravity (u.Quantity): Standard gravitational acceleration near sea level

        Returns:
            u.Quantity: Effective exhaust velocity
        """
        
        g_0: u.Quantity = sea_level_gravity.to(u.m / u.s**2)
        
        i_sp: u.Quantity = self.specific_impulse.to(u.s)
        
        c: u.Quantity = i_sp * g_0
        
        return c
    
    def calc_propellant_mass_flow_rate(self, sea_level_gravity: u.Quantity) -> u.Quantity:
        """
        Propellant mass flow-rate calculation

        Args:
            sea_level_gravity (u.Quantity): Standard gravitational acceleration near sea level

        Returns:
            u.Quantity: Propellant mass flow-rate
        """
        
        T: float = self.thrust.to(u.N)
        
        c: u.Quantity = self.calc_effective_exhaust_velocity(sea_level_gravity=sea_level_gravity)
        
        m_dot: u.Quantity = T / c
        
        return m_dot

class HohmannDirection(enum.IntEnum):
    """List of Hohmann transfer directions"""
    
    PERICENTER_APOCENTER = 0
    APOCENTER_PERICENTER = 1

class SpiralDirection(enum.IntEnum):
    """List of Spiral transfer directions"""
    
    OUTWARD = 0
    INWARD = 1

@dc.dataclass
class NonImpulsiveManeuverResult:
    """Result of non-impulsive maneuver integration"""
    
    burn_time       : u.Quantity = dc.field(default_factory=lambda: 0 * u.s)
    position_x      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    position_y      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    position_z      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    velocity_x      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km / u.s)
    velocity_y      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km / u.s)
    velocity_z      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km / u.s)
    spacecraft_mass : u.Quantity = dc.field(default_factory=lambda: 0 * u.kg)

class OrbitalManeuvers():
    """Orbital Maneuvers
    """
    
    # --- STATIC ---
    
    @staticmethod
    def launch_azimuth(launch_site_latitude: u.Quantity,
                       target_inclination: u.Quantity) -> u.Quantity:
        """
        Launch azimuth calculation for a given target inclination and launch site latitude

        Args:
            launch_site_latitude (u.Quantity): Launch site latitude
            target_inclination (u.Quantity): Target inclination

        Returns:
            u.Quantity: Launch azimuth
        """
        
        cm.check_angle(launch_site_latitude.to_value(u.deg))
        
        cm.check_angle(target_inclination.to_value(u.deg))
        
        phi: float = launch_site_latitude.to_value(u.rad)
        
        inc: float = target_inclination.to_value(u.rad)
        
        if (inc < abs(phi)):
            
            raise ValueError("Target inclination must be greater than or equal to the absolute value of the launch site latitude")
        
        if (inc > np.pi - abs(phi)):
            
            raise ValueError("Target inclination must be less than or equal to 180° - absolute value of the launch site latitude")
        
        azimuth: float = np.arcsin(np.cos(inc) / np.cos(phi))
        
        azimuth = azimuth % (2 * np.pi)
        
        return azimuth * u.rad
    
    @staticmethod
    def hohmann_transfer(attractor: bd.Attractor,
                         rocket_motor: RocketMotor,
                         orbital_elements_1 : o3d.OrbitalElements,
                         orbital_elements_2 : o3d.OrbitalElements,
                         direction : HohmannDirection) -> ManeuverResult:
        """
        Hohmann transfer maneuver
        
        The Hohmann transfer is a two-impulse orbital maneuver used to transfer a spacecraft between two coplanar,
        elliptical or circular orbits around the same central body. It is the minimum-energy transfer between two 
        circular orbits and a widely used approximation for transfers between low-eccentricity orbits.
        
        This implementation generalizes the classical Hohmann transfer to allow transfers between arbitrary coplanar 
        elliptical orbits, using one of two possible geometric configurations
        - pericenter → apocenter
        - apocenter → pericenter


        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            orbital_elements_2 (o3d.OrbitalElements): Orbital elements of the target orbit
            direction (HohmannDirection): Direction of the transfer

        Returns:
            ManeuverResult: Maneuver result
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(orbital_elements_1.semimajor_axis.to_value(u.km),
                                      orbital_elements_1.eccentricity.to_value(),
                                      orbital_elements_1.inclination.to_value(u.deg),
                                      orbital_elements_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_1.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(orbital_elements_2.semimajor_axis.to_value(u.km),
                                      orbital_elements_2.eccentricity.to_value(),
                                      orbital_elements_2.inclination.to_value(u.deg),
                                      orbital_elements_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_2.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_2.true_anomaly.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = bd.BODIES[attractor].g_0
        
        # >>> 0. Pericenter/Apocenter radii
        
        r_p_1: float = orbital_elements_1.calc_perigee_radius().to_value(u.km)
        r_a_1: float = orbital_elements_1.calc_apogee_radius().to_value(u.km)
        
        r_p_2: float = orbital_elements_2.calc_perigee_radius().to_value(u.km)
        r_a_2: float = orbital_elements_2.calc_apogee_radius().to_value(u.km)
        
        # >>> 1. Orbit 1 (Specific Angular Momentum, Velocity at Pericenter and Apocenter)
        
        h_1: float = np.sqrt(2 * mu) * np.sqrt(r_a_1 * r_p_1 / (r_a_1 + r_p_1))
        
        v_p_1: float = h_1 / r_p_1
        
        v_a_1: float = h_1 / r_a_1
        
        # >>> 2. Orbit 2 (Specific Angular Momentum, Velocity at Pericenter and Apocenter)
        
        h_2: float = np.sqrt(2 * mu) * np.sqrt(r_a_2 * r_p_2 / (r_a_2 + r_p_2))
        
        v_p_2: float = h_2 / r_p_2
        
        v_a_2: float = h_2 / r_a_2
        
        # >>> 3. Transfer Orbit
        
        r_p_t: float = 0.0
        r_a_t: float = 0.0
        
        swap: bool = False
        
        if direction == HohmannDirection.PERICENTER_APOCENTER:
            
            r_p_t: float = min(r_p_1, r_a_2)
            r_a_t: float = max(r_p_1, r_a_2)
            
            swap = r_p_1 > r_a_2
            
        elif direction == HohmannDirection.APOCENTER_PERICENTER:
            
            r_p_t: float = min(r_p_2, r_a_1)
            r_a_t: float = max(r_p_2, r_a_1)
            
            swap = r_p_2 > r_a_1
            
        a_t: float = 0.5 * (r_p_t + r_a_t)
        
        e_t: float = (r_a_t - r_p_t) / (r_a_t + r_p_t)

        h_t: float = np.sqrt(2 * mu) * np.sqrt(r_a_t * r_p_t / (r_a_t + r_p_t))
        
        v_p_t: float = h_t / r_p_t
        
        v_a_t: float = h_t / r_a_t
        
        t_t = 2 * np.pi / float(np.sqrt(mu)) * a_t**(3/2) # ? Orbital Period
        
        # >>> 4. Delta-V Calculations
        
        dv_1: float = 0.0
        dv_2: float = 0.0
        ta_1: float = 0.0 # ? True anomaly at first maneuver point
        ta_t: float = 0.0 # ? True anomaly at second maneuver point
        
        if direction == HohmannDirection.PERICENTER_APOCENTER:
            
            dv_1 = abs(v_p_t - (v_p_1 if not swap else v_a_2))
            
            dv_2 = abs((v_a_2 if not swap else v_p_1) - v_a_t)
            
            ta_1 = 0.0
            
            ta_t = 0.0 if not swap else 180.0
        
        elif direction == HohmannDirection.APOCENTER_PERICENTER:
            
            dv_1 = abs(v_a_t - (v_a_1 if not swap else v_p_2))
            
            dv_2 = abs((v_p_2 if not swap else v_a_1) - v_p_t)
            
            ta_1 = 180.0
            
            ta_t = 180.0 if not swap else 0.0
        
        argp_t: float = orbital_elements_1.argument_of_periapsis.to_value(u.deg)
        
        if swap:
            
            argp_t = cm.wrap_angle(argp_t + 180.0, -180.0, +180.0)
        
        # >>> 5. Result
        
        dm_1: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_1 * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn_1: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_1, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm_1
        
        dm_2: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_2 * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn_2: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_2, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm_2
        
        oe_t: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=h_t * u.km**2 / u.s,
                                                        semimajor_axis=a_t * u.km,
                                                        eccentricity=e_t * u.one,
                                                        inclination=orbital_elements_1.inclination,
                                                        right_ascension_of_ascending_node=orbital_elements_1.right_ascension_of_ascending_node,
                                                        argument_of_periapsis=argp_t * u.deg,
                                                        true_anomaly=ta_t * u.deg)
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list=[dv_1 * u.km / u.s, dv_2 * u.km / u.s]
        maneuver.flight_time_list=[0.5 * t_t * u.s]
        maneuver.delta_mass_list=[dm_1, dm_2]
        maneuver.burn_time_list=[t_burn_1, t_burn_2]
        maneuver.orbital_elements_list=[oe_t]
        maneuver.true_anomaly_list=[ta_1 * u.deg]
        maneuver.rocket_elevation_angle_list=[0 * u.deg, 0 * u.deg]
        
        return maneuver
    
    @staticmethod
    def bi_elliptic_hohmann_transfer(attractor: bd.Attractor,
                                     rocket_motor: RocketMotor,
                                     orbital_elements_1 : o3d.OrbitalElements,
                                     orbital_elements_2 : o3d.OrbitalElements,
                                     apoapsis_radius : u.Quantity) -> ManeuverResult:
        """
        Bi-Elliptic Hohmann transfer maneuver
        
        The bi-elliptic Hohmann transfer is a three-impulse orbital maneuver used to transfer a spacecraft between two 
        coplanar orbits when the ratio between the final and initial orbital radii is sufficiently large.
        Unlike the classical Hohmann transfer, which uses a single transfer ellipse, the bi-elliptic transfer introduces
        an intermediate apoapsis r_3, allowing the spacecraft to perform part of the maneuver at a very low velocity.
        This can reduce the total Δv when the target orbit is much larger than the initial one.
        
        This implementation generalizes the bi-elliptic transfer to elliptical orbits by computing the maneuver at the
        appropriate pericenter or apoapsis radii of the initial and final orbits.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            orbital_elements_2 (o3d.OrbitalElements): Orbital elements of the target orbit
            apoapsis_radius (u.Quantity): Apoapsis of intermediate orbit

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        oe_t_1: o3d.OrbitalElements = copy.deepcopy(orbital_elements_1)
        
        oe_t_1.update_from_perigee_apogee(periapsis_radius=orbital_elements_1.calc_perigee_radius(),
                                          apoapsis_radius=apoapsis_radius)
        
        maneuver_1: ManeuverResult = OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements_1=orbital_elements_1,
                                                                       orbital_elements_2=oe_t_1,
                                                                       direction=HohmannDirection.PERICENTER_APOCENTER)
        
        oe_t_2: o3d.OrbitalElements = copy.deepcopy(orbital_elements_2)
        
        oe_t_2.update_from_perigee_apogee(periapsis_radius=orbital_elements_2.calc_perigee_radius(),
                                          apoapsis_radius=apoapsis_radius)
        
        maneuver_2: ManeuverResult = OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements_1=oe_t_1,
                                                                       orbital_elements_2=oe_t_2,
                                                                       direction=HohmannDirection.APOCENTER_PERICENTER)
        
        maneuver_3: ManeuverResult = OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       orbital_elements_1=oe_t_2,
                                                                       orbital_elements_2=orbital_elements_2,
                                                                       direction=HohmannDirection.APOCENTER_PERICENTER)
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list=[maneuver_1.delta_velocity_list[0],
                                      maneuver_2.delta_velocity_list[0],
                                      maneuver_3.delta_velocity_list[1]]
        
        maneuver.flight_time_list=[maneuver_1.flight_time_list[0],
                                   maneuver_2.flight_time_list[0]]
        
        maneuver.delta_mass_list=[maneuver_1.delta_mass_list[0],
                                  maneuver_2.delta_mass_list[0],
                                  maneuver_3.delta_mass_list[1]]
        
        maneuver.burn_time_list=[maneuver_1.burn_time_list[0],
                                 maneuver_2.burn_time_list[0],
                                 maneuver_3.burn_time_list[1]]
        
        maneuver.orbital_elements_list=[maneuver_1.orbital_elements_list[0],
                                        maneuver_2.orbital_elements_list[0]]
        
        maneuver.true_anomaly_list=[maneuver_1.true_anomaly_list[0],
                                    maneuver_2.true_anomaly_list[0],
                                    maneuver_3.true_anomaly_list[0]]
        
        maneuver.rocket_elevation_angle_list=[maneuver_1.rocket_elevation_angle_list[0],
                                              maneuver_2.rocket_elevation_angle_list[0],
                                              maneuver_3.rocket_elevation_angle_list[1]]
        
        return maneuver
    
    @staticmethod
    def phasing_maneuver(attractor: bd.Attractor,
                         rocket_motor: RocketMotor,
                         orbital_elements: o3d.OrbitalElements,
                         true_anomaly_target: u.Quantity,
                         num_revolutions: int = 1) -> ManeuverResult:
        """
        Phasing maneuver from chaser A to target B
        
        A phasing maneuver is a two-impulse orbital strategy used to synchronize the position of a chaser spacecraft (A)
        with a target spacecraft (B) located on the same orbital plane. The goal is to adjust the orbital period of the
        chaser so that, after completing a specified number of revolutions on a temporary “phasing orbit,” it arrives at
        the same true anomaly as the target.
        
        This maneuver is commonly used for rendezvous, formation flying, and constellation maintenance.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements (o3d.OrbitalElements): Orbital elements of chaser A
            true_anomaly_target (u.Quantity): True anomaly of target B
            num_revolutions (int, optional): Number of revolutions on phasing orbit. Defaults to 1.

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                      orbital_elements.eccentricity.to_value(),
                                      orbital_elements.inclination.to_value(u.deg),
                                      orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements.true_anomaly.to_value(u.deg))
        
        cm.check_angle(true_anomaly_target.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = bd.BODIES[attractor].g_0
        
        # >>> 1. Chaser Orbit period and velocity at pericenter
        
        orbital_elements.calc_specific_angular_momentum(attractor)
        
        T_1: float = orbital_elements.calc_orbital_period(attractor=attractor).to_value(u.s)
        
        v_p_1: float = orbital_elements.specific_angular_momentum.to_value(u.km**2 / u.s) / orbital_elements.calc_perigee_radius().to_value(u.km)
        
        # >>> 2. Time from A (pericenter - chaser) to B (target) placed at true_anomaly_target w.r.t. A
        
        t_ab: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=true_anomaly_target,
                                                                    period=T_1 * u.s,
                                                                    eccentricity=orbital_elements.eccentricity)
        
        # >>> 3. Orbit 2 (Phasing Orbit with kick at pericenter)
        
        T_2: float = T_1 - t_ab.to_value(u.s) / num_revolutions
        
        a_2: float = (np.sqrt(mu) * T_2 / (2 * np.pi))**(2/3)
        
        r_a: float = orbital_elements.calc_perigee_radius().to_value(u.km) # ? Maneuver point is the pericenter of the chaser orbit
        
        r_d: float = 2 * a_2 - r_a # ? Opposite point of the phasing orbit
        
        h_2: float = np.sqrt(2 * mu) * np.sqrt(r_a * r_d / (r_a + r_d))
        
        v_p_a: float = h_2 / r_a
        
        # >>> 4. Delta-V Calculations
        
        dv_1: float = np.abs(v_p_a - v_p_1)
        
        dv_2: float = np.abs(v_p_1 - v_p_a)
        
        # >>> 5. Result
        
        dm_1: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_1 * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn_1: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_1, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm_1
        
        dm_2: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_2 * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn_2: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_2, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm_2
        
        oe_t: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=h_2 * u.km**2 / u.s,
                                                        semimajor_axis=a_2 * u.km,
                                                        eccentricity=(r_d - r_a) / (r_d + r_a) * u.one,
                                                        inclination=orbital_elements.inclination,
                                                        right_ascension_of_ascending_node=orbital_elements.right_ascension_of_ascending_node,
                                                        argument_of_periapsis=orbital_elements.argument_of_periapsis,
                                                        true_anomaly=0 * u.deg)
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list=[dv_1 * u.km / u.s, dv_2 * u.km / u.s]
        maneuver.flight_time_list=[num_revolutions * T_2 * u.s]
        maneuver.delta_mass_list=[dm_1, dm_2]
        maneuver.burn_time_list=[t_burn_1, t_burn_2]
        maneuver.orbital_elements_list=[oe_t]
        maneuver.rocket_elevation_angle_list=[0 * u.deg, 0 * u.deg]
        
        return maneuver
    
    @staticmethod
    def non_hohmann_transfer(attractor: bd.Attractor,
                             rocket_motor: RocketMotor,
                             orbital_elements_1: o3d.OrbitalElements,
                             orbital_elements_2: o3d.OrbitalElements) -> ManeuverResult:
        """
        Non-Hohmann transfer between coaxial elliptical orbits
        
        A non-Hohmann transfer is a general two-impulse maneuver used to move a spacecraft from an initial elliptical
        orbit to a target point located at a specified radius and true anomaly on a second coaxial (same-focus) orbit.
        Unlike the classical Hohmann transfer, which is constrained to pericenter-to-apocenter geometry, the non-Hohmann
        transfer allows the spacecraft to intercept the target at an arbitrary true anomaly. This makes it suitable for
        rendezvous, phasing, and transfers between elliptical orbits where the target point is not aligned with the
        apsides.
        This maneuver computes a single transfer ellipse that connects:
        - the spacecraft’s current position on the initial orbit
        - the desired target position on the final orbit, defined by the specified radius and true anomaly.
        
        The transfer is completed with two tangential burns: one to enter the transfer ellipse and one to match the
        target orbit at the interception point.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            orbital_elements_2 (o3d.OrbitalElements): Orbital elements of the target orbit

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(orbital_elements_1.semimajor_axis.to_value(u.km),
                                      orbital_elements_1.eccentricity.to_value(),
                                      orbital_elements_1.inclination.to_value(u.deg),
                                      orbital_elements_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_1.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(orbital_elements_2.semimajor_axis.to_value(u.km),
                                      orbital_elements_2.eccentricity.to_value(),
                                      orbital_elements_2.inclination.to_value(u.deg),
                                      orbital_elements_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_2.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_2.true_anomaly.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = bd.BODIES[attractor].g_0
        
        # >>> 1. Orbit 1 (Starting Orbit)
        
        ecc_1: float = orbital_elements_1.eccentricity.to_value()
        ta_1: float = orbital_elements_1.true_anomaly.to_value(u.rad)
        
        h_1: float = orbital_elements_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        r_1: float = h_1**2 / mu * 1 / (1 + ecc_1 * np.cos(ta_1)) # ? Radius at maneuver point
        
        v_t_1: float = h_1 / r_1 # ? Transversal velocity at maneuver point
        
        v_r_1: float = mu / h_1 * ecc_1 * np.sin(ta_1) # ? Radial velocity at maneuver point
        
        v_1: float = np.sqrt(v_r_1**2 + v_t_1**2) # ? Velocity at maneuver point
        
        fpa_1: float = np.arctan(v_r_1 / v_t_1) # ? Flight path angle at maneuver point
        
        # >>> 2. Orbit 2 (Target Orbit)
        
        ecc_2: float = orbital_elements_2.eccentricity.to_value()
        ta_2: float = orbital_elements_2.true_anomaly.to_value(u.rad)
        
        h_2: float = orbital_elements_2.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        r_2: float = h_2**2 / mu * 1 / (1 + ecc_2 * np.cos(ta_2)) # ? Radius at target point
        
        v_t_2: float = h_2 / r_2 # ? Transversal velocity at target point
        
        v_r_2: float = mu / h_2 * ecc_2 * np.sin(ta_2) # ? Radial velocity at target point
        
        v_2: float = np.sqrt(v_r_2**2 + v_t_2**2) # ? Velocity at target point
        
        fpa_2: float = np.arctan(v_r_2 / v_t_2) # ? Flight path angle at target point
        
        # >>> 3. Transfer Orbit
        
        # ? ta_1 and ta_2 are the true anomalies of the transfer orbit at the maneuver point and at the target point,
        # ? respectively. Since the transfer orbit is coaxial with the initial orbit, ta_1 is equal to the true anomaly
        # ? of the initial orbit at the maneuver point, same for ta_2 on target orbit.
        
        e_t: float = - (r_2 - r_1) / (r_2 * np.cos(ta_2) - r_1 * np.cos(ta_1))
        
        h_t: float = np.sqrt(mu * r_1 * r_2) * np.sqrt((np.cos(ta_2) - np.cos(ta_1)) /\
            (r_2 * np.cos(ta_2) - r_1 * np.cos(ta_1)))
        
        r_p_t: float = h_t**2 / mu * 1 / (1 + e_t)
        
        r_a_t: float = h_t**2 / mu * 1 / (1 - e_t)
        
        a_t: float = 0.5 * (r_p_t + r_a_t) if e_t < 1 else 0
        
        period_t: float = 2 * np.pi / float(np.sqrt(mu)) * a_t**(3/2) if e_t < 1 else 0
        
        # >>> 3. Starting point of the transfer orbit (maneuver point)
        
        v_t_t_1: float = h_t / r_1
        
        v_r_t_1: float = mu / h_t * e_t * np.sin(ta_1)
        
        v_t_1: float = np.sqrt(v_r_t_1**2 + v_t_t_1**2)
        
        fpa_t_1: float = np.arctan(v_r_t_1 / v_t_t_1)
        
        # >>> 4. Target point of the transfer orbit (interception point)
        
        v_t_t_2: float = h_t / r_2
        
        v_r_t_2: float = mu / h_t * e_t * np.sin(ta_2)
        
        v_t_2: float = np.sqrt(v_r_t_2**2 + v_t_t_2**2)
        
        fpa_t_2: float = np.arctan(v_r_t_2 / v_t_t_2)
        
        # >>> 4. Result
        
        delta_fpa_1: float = (fpa_t_1 - fpa_1)
        delta_fpa_2: float = (fpa_t_2 - fpa_2)
        
        dv_1: float = np.sqrt(v_1**2 + v_t_1**2 - 2 * v_1 * v_t_1 * np.cos(delta_fpa_1))
        dv_2: float = np.sqrt(v_2**2 + v_t_2**2 - 2 * v_2 * v_t_2 * np.cos(delta_fpa_2))
        
        #phi_1: float = np.arctan2((v_r_t_1 - v_r_1), (v_t_t_1 - v_t_1))
        #phi_2: float = np.arctan2((v_r_2 - v_r_t_2), (v_t_2 - v_t_t_2))
        
        phi_1: float = np.pi - np.arcsin(v_t_1 / dv_1 * np.sin(delta_fpa_1)) + fpa_1
        phi_2: float = np.pi - np.arcsin(v_t_2 / dv_2 * np.sin(delta_fpa_2)) + fpa_2
        
        if (phi_1 < 0):
            
            phi_1 += np.pi
            
        if (phi_2 < 0):
            
            phi_2 += np.pi
        
        if e_t < 1:
            
            t_1: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=orbital_elements_1.true_anomaly,
                                                                    period=period_t * u.s,
                                                                    eccentricity=e_t * u.one)
        
        else:
            
            t_1: u.Quantity = op.OrbitalPosition.hyperbolic_orbit_time(true_anomaly=orbital_elements_1.true_anomaly,
                                                                       specific_angular_momentum=h_t * u.km**2 / u.s,
                                                                       eccentricity=e_t * u.one,
                                                                       attractor=attractor)
        
        dm_1: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_1 * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn_1: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_1, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm_1
        
        if e_t < 1:
            
            t_2: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=orbital_elements_2.true_anomaly,
                                                                    period=period_t * u.s,
                                                                    eccentricity=e_t * u.one)
            
        else:
            
            t_2: u.Quantity = op.OrbitalPosition.hyperbolic_orbit_time(true_anomaly=orbital_elements_2.true_anomaly,
                                                                       specific_angular_momentum=h_t * u.km**2 / u.s,
                                                                       eccentricity=e_t * u.one,
                                                                       attractor=attractor)
        
        dm_2: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_2 * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn_2: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_2, sea_level_gravity=g_0)
        
        oe_t: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=h_t * u.km**2 / u.s,
                                                        semimajor_axis=a_t * u.km,
                                                        eccentricity=e_t * u.dimensionless_unscaled,
                                                        inclination=orbital_elements_1.inclination,
                                                        right_ascension_of_ascending_node=orbital_elements_1.right_ascension_of_ascending_node,
                                                        argument_of_periapsis=orbital_elements_1.argument_of_periapsis,
                                                        true_anomaly=orbital_elements_1.true_anomaly)
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list = [dv_1 * u.km / u.s, dv_2 * u.km / u.s]
        maneuver.flight_time_list = [t_2 - t_1]
        maneuver.delta_mass_list = [dm_1, dm_2]
        maneuver.burn_time_list=[t_burn_1, t_burn_2]
        maneuver.orbital_elements_list = [oe_t]
        maneuver.true_anomaly_list=[orbital_elements_1.true_anomaly, orbital_elements_2.true_anomaly]
        maneuver.rocket_elevation_angle_list=[phi_1 * u.rad, phi_2 * u.rad]
        
        return maneuver
    
    @staticmethod
    def apse_line_rotation_from_eta(attractor: bd.Attractor,
                                    rocket_motor: RocketMotor,
                                    orbital_elements_1: o3d.OrbitalElements,
                                    orbital_elements_2: o3d.OrbitalElements,
                                    eta: u.Quantity,
                                    second_intersection_point: bool = False) -> ManeuverResult:
        """
        Apse line rotation from angle variation eta
        
        An apse-line rotation maneuver is a two-impulse orbital maneuver used to rotate the line of apsides (the line
        connecting pericenter and apocenter) of an elliptical orbit by a specified angle eta, without changing the
        orbital energy or inclination. This maneuver is required when the spacecraft must realign its argument of
        perigee to match a target orbit or to achieve a specific geometric configuration for rendezvous, phasing, or
        mission design.
        
        The maneuver exploits the fact that two coaxial elliptical orbits with different arguments of perigee intersect
        at two points. By performing impulsive burns at one of these intersection points, the spacecraft can transition
        from the initial orbit to the target orbit while rotating the apse line by the desired angle.


        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            orbital_elements_2 (o3d.OrbitalElements): Orbital elements of the target orbit
            eta (u.Quantity): Apse line angle rotation
            second_intersection_point (bool, optional): True for using the second intersection point. Defaults to False.

        Returns:
            ManeuverResult: Maneuver result
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(orbital_elements_1.semimajor_axis.to_value(u.km),
                                      orbital_elements_1.eccentricity.to_value(),
                                      orbital_elements_1.inclination.to_value(u.deg),
                                      orbital_elements_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_1.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(orbital_elements_2.semimajor_axis.to_value(u.km),
                                      orbital_elements_2.eccentricity.to_value(),
                                      orbital_elements_2.inclination.to_value(u.deg),
                                      orbital_elements_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_2.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_2.true_anomaly.to_value(u.deg))
        
        cm.check_angle(eta.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = bd.BODIES[attractor].g_0
        
        eta: float = eta.to_value(u.rad)
        
        # >>> 1. Orbit parameters
        
        e_1: float = orbital_elements_1.eccentricity.to_value()
        
        h_1: float = orbital_elements_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        e_2: float = orbital_elements_2.eccentricity.to_value()
        
        h_2: float = orbital_elements_2.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        # >>> 2. Coefficients a, b, c of the quadratic equation for the true anomaly at the intersection point
        
        a: float = e_1 * h_2**2 - e_2 * h_1**2 * np.cos(eta)
        
        b: float = - e_2 * h_1**2 * np.sin(eta)
        
        c: float = h_1**2 - h_2**2
        
        phi: float = np.arctan(b / a)
        
        sign: int = 1 if not second_intersection_point else -1
        
        ta_1: float = phi + sign * np.arccos(c / a * np.cos(phi))
        
        if ta_1 < 0: ta_1 = 2 * np.pi + ta_1
        
        r: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(ta_1))
        
        # >>> 3. Orbit 1
        
        v_t_1: float = h_1 / r
        
        v_r_1: float = mu / h_1 * e_1 * np.sin(ta_1)
        
        v_1: float = np.sqrt(v_r_1**2 + v_t_1**2)
        
        fpa_1: float = np.arctan(v_r_1 / v_t_1)
        
        # >>> 4. Orbit 2
        
        v_t_2: float = h_2 / r
        
        v_r_2: float = mu / h_2 * e_2 * np.sin(ta_1 - eta)
        
        v_2: float = np.sqrt(v_r_2**2 + v_t_2**2)
        
        fpa_2: float = np.arctan(v_r_2 / v_t_2)
        
        # >>> 5. Result
        
        delta_fpa: float = fpa_2 - fpa_1
        
        dv: float = np.sqrt(v_1**2 + v_2**2 - 2 * v_1 * v_2 * np.cos(delta_fpa))
        
        phi: float = 0.0
        #phi: float = np.pi - np.arcsin(v_2 / dv * np.sin(delta_fpa)) + fpa_1
        
        if np.abs(v_t_2 - v_t_1) < 1e-6:
            
            phi = np.pi if v_r_2 - v_r_1 > 0 else -np.pi
            
        else:
            
            phi = np.arctan((v_r_2 - v_r_1) / (v_t_2 - v_t_1))
            
        if (phi < 0):
            
            phi += np.pi
        
        dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm
        
        oe_t: o3d.OrbitalElements = o3d.OrbitalElements(true_anomaly=((ta_1 - eta) * u.rad).to(u.deg))
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list = [dv * u.km / u.s]
        maneuver.flight_time_list = [0 * u.s]
        maneuver.delta_mass_list = [dm]
        maneuver.burn_time_list=[t_burn]
        maneuver.orbital_elements_list = [oe_t]
        maneuver.true_anomaly_list=[(ta_1 * u.rad).to(u.deg)]
        maneuver.rocket_elevation_angle_list = [(phi * u.rad).to(u.deg)]
        
        return maneuver
    
    @staticmethod
    def apse_line_rotation_from_true_anomaly(attractor: bd.Attractor,
                                             rocket_motor: RocketMotor,
                                             orbital_elements: o3d.OrbitalElements,
                                             delta_velocity: u.Quantity,
                                             flight_path_angle: u.Quantity) -> ManeuverResult:
        """
        Apse line rotation from true anomaly
        
        This maneuver computes the rotation of the line of apsides (argument of perigee change) produced by a single,
        finite-magnitude impulse applied at a given true anomaly on an elliptical orbit. Unlike apse-line rotation
        maneuvers defined by a desired angle between two orbits, this formulation starts from a prescribed Δv vector
        (magnitude and flight-path angle) and determines the resulting change in the orbit’s geometry.
        
        The algorithm assumes:
        - coplanar motion around a central body
        - an impulsive burn applied at the current position of the spacecraft
        - the burn direction defined in the local orbital frame by a flight path angle relative to the local velocity
        direction


        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements (o3d.OrbitalElements): Orbital elements of the initial orbit
            delta_velocity (u.Quantity): Delta v
            flight_path_angle (u.Quantity): Flight path angle of delta v

        Returns:
            ManeuverResult: Maneuver result
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                      orbital_elements.eccentricity.to_value(),
                                      orbital_elements.inclination.to_value(u.deg),
                                      orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements.true_anomaly.to_value(u.deg))
        
        cm.check_angle(flight_path_angle.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = bd.BODIES[attractor].g_0
        
        # >>> 1. Orbit 1
        
        e_1: float = orbital_elements.eccentricity.to_value()
        
        h_1: float = orbital_elements.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        ta_1: float = orbital_elements.true_anomaly.to_value(u.rad)
        
        r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(ta_1))
        
        v_t_1: float = h_1 / r_1
        
        v_r_1: float = mu / h_1 * e_1 * np.sin(ta_1)
        
        # >>> 2. Delta v
        
        dv_t: float = delta_velocity.to_value(u.km / u.s) * np.cos(flight_path_angle.to_value(u.rad))
        
        dv_r: float = delta_velocity.to_value(u.km / u.s) * np.sin(flight_path_angle.to_value(u.rad))
        
        # >>> 3. Orbit 2
        
        h_2: float = h_1 + r_1 * dv_t
        
        numerator: float = (v_t_1 + dv_t) * (v_r_1 + dv_r) * v_t_1**2 * 1 / (mu / r_1)
        
        denominator: float = (v_t_1 + dv_t)**2 * e_1 * np.cos(ta_1) + (2 * v_t_1 + dv_t) * dv_t
        
        ta_2: float = np.arctan(numerator / denominator)
        
        eta: float = ta_1 - ta_2
        
        e_2: float = ((h_1 + r_1 * dv_t)**2 * e_1 * np.cos(ta_1) + (2 * h_1 + r_1 * dv_t) * r_1 * dv_t) /\
            (h_1**2 * np.cos(ta_2))
        
        r_p_2: float = h_2**2 / mu * 1 / (1 + e_2)
        
        r_a_2: float = h_2**2 / mu * 1 / (1 - e_2)
        
        # >>> 4. Result
        
        dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=delta_velocity, sea_level_gravity=g_0)
        
        t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm
        
        oe_t: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=h_2 * u.km**2 / u.s,
                                                        semimajor_axis=0.5 * (r_p_2 + r_a_2) * u.km,
                                                        eccentricity=e_2 * u.one,
                                                        inclination=orbital_elements.inclination,
                                                        right_ascension_of_ascending_node=orbital_elements.right_ascension_of_ascending_node,
                                                        argument_of_periapsis=(orbital_elements.argument_of_periapsis.to_value(u.rad) + eta) * u.rad,
                                                        true_anomaly=ta_2 * u.rad)
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list = [delta_velocity]
        maneuver.flight_time_list = [0 * u.s]
        maneuver.delta_mass_list = [dm]
        maneuver.burn_time_list=[t_burn]
        maneuver.orbital_elements_list = [oe_t]
        maneuver.true_anomaly_list=[(ta_1 * u.rad).to(u.deg)]
        maneuver.rocket_elevation_angle_list = [flight_path_angle]
        
        return maneuver
    
    @staticmethod
    def chase_maneuver(attractor: bd.Attractor,
                       rocket_motor: RocketMotor,
                       orbital_elements: o3d.OrbitalElements,
                       true_anomaly_target: u.Quantity,
                       delta_time: time.TimeDelta) -> ManeuverResult:
        """
        Chase maneuver from Chaser C to Target T
        
        A chase maneuver is a two-impulse orbital maneuver used to intercept a target spacecraft located at a known true
        anomaly after a specified time interval. Unlike a phasing maneuver, which adjusts the orbital period to achieve
        alignment after several revolutions, the chase maneuver computes a single transfer ellipse that brings the
        chaser to the target’s position exactly after a prescribed time of flight Delta t.
        
        This maneuver is essential for time-critical rendezvous operations, interception trajectories, and short-arc
        pursuit strategies.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements (o3d.OrbitalElements): Orbital elements of the initial orbit
            true_anomaly_target (u.Quantity): True anomaly of Target
            delta_time (time.TimeDelta): Delta time for the interception

        Returns:
            ManeuverResult: Maneuver result
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                      orbital_elements.eccentricity.to_value(),
                                      orbital_elements.inclination.to_value(u.deg),
                                      orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements.true_anomaly.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = bd.BODIES[attractor].g_0
        
        # >>> 1. Parameters of the chaser and target orbits
        
        h: float = orbital_elements.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        T: float = orbital_elements.calc_orbital_period(attractor=attractor).to_value(u.s)
        
        # >>> 2. Perifocal Frame state vector for Chaser C
        
        e: float = orbital_elements.eccentricity.to_value()
        
        ta_c: float = orbital_elements.true_anomaly.to_value(u.rad)
        
        r_c: float = h**2 / mu * 1 / (1 + e * np.cos(ta_c)) * np.array([np.cos(ta_c), np.sin(ta_c), 0])
        
        v_c: float = mu / h * np.array([-np.sin(ta_c), (e + np.cos(ta_c)), 0])
        
        # >>> 3. New Perifocal Frame state vector for Target T after dt
        
        t_t: float = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=true_anomaly_target,
                                                              period=T * u.s,
                                                              eccentricity=e * u.one).to_value(u.s)
        
        t_t_new: float = t_t + delta_time.to_value(u.s)
        
        ta_t_new: float = op.OrbitalPosition.elliptical_orbit_true_anomaly(time_of_flight=t_t_new * u.s,
                                                                           period=T * u.s,
                                                                           eccentricity=e * u.one).to_value(u.rad)
        
        r_t: float = h**2 / mu * 1 / (1 + e * np.cos(ta_t_new)) * np.array([np.cos(ta_t_new), np.sin(ta_t_new), 0])
        
        v_t: float = mu / h * np.array([-np.sin(ta_t_new), (e + np.cos(ta_t_new)), 0])
        
        # >>> 4. Lambert problem solution for the transfer from C to T in time dt
        
        r_c: u.Quantity = o3d.Orbit3D.perifocal_to_geocentric_equatorial_position_vector(orbital_elements=orbital_elements,
                                                                                         perifocal_position=r_c * u.km)
        
        r_t: u.Quantity = o3d.Orbit3D.perifocal_to_geocentric_equatorial_position_vector(orbital_elements=orbital_elements,
                                                                                         perifocal_position=r_t * u.km)
        
        if orbital_elements.inclination <= 90.0 * u.deg:
            
            direction : od.OrbitDirection = od.OrbitDirection.PROGRADE
            
        else:
            
            direction = od.OrbitDirection.RETROGRADE
        
        v_t_c, v_t_t, oe_t, ta_t_2 = od.OrbitDetermination.lambert(attractor=attractor,
                                                                   departure_position=r_c,
                                                                   arrival_position=r_t,
                                                                   delta_time=delta_time,
                                                                   direction=direction)
        
        oe_t_2: o3d.OrbitalElements = copy.deepcopy(oe_t)
        
        oe_t_2.true_anomaly = ta_t_2
        
        # >>> 5. Result
        
        dv_1: u.Quantity = np.linalg.norm(v_t_c.to_value(u.km / u.s) - v_c) * u.km / u.s
        
        dv_2: u.Quantity = np.linalg.norm(v_t - v_t_t.to_value(u.km / u.s)) * u.km / u.s
        
        dm_1: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_1, sea_level_gravity=g_0)
        
        t_burn_1: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_1, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm_1
        
        dm_2: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv_2, sea_level_gravity=g_0)
        
        t_burn_2: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm_2, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm_2
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list = [dv_1, dv_2]
        maneuver.flight_time_list = [delta_time.to_value(u.s) * u.s]
        maneuver.delta_mass_list = [dm_1, dm_2]
        maneuver.burn_time_list=[t_burn_1, t_burn_2]
        maneuver.orbital_elements_list = [oe_t, oe_t_2]
        
        return maneuver
    
    @staticmethod
    def inclination_change_maneuver(attractor: bd.Attractor,
                                    rocket_motor: RocketMotor,
                                    orbital_elements_1: o3d.OrbitalElements,
                                    orbital_elements_2: o3d.OrbitalElements) -> ManeuverResult:
        """Inclination change maneuver on line on nodes

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            orbital_elements_2 (o3d.OrbitalElements): Orbital elements of the target orbit

        Returns:
            ManeuverResult: Maneuver result
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(orbital_elements_1.semimajor_axis.to_value(u.km),
                                      orbital_elements_1.eccentricity.to_value(),
                                      orbital_elements_1.inclination.to_value(u.deg),
                                      orbital_elements_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_1.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(orbital_elements_2.semimajor_axis.to_value(u.km),
                                      orbital_elements_2.eccentricity.to_value(),
                                      orbital_elements_2.inclination.to_value(u.deg),
                                      orbital_elements_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_2.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_2.true_anomaly.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = bd.BODIES[attractor].g_0
        
        delta_inc: float = (orbital_elements_2.inclination.to_value(u.rad) - orbital_elements_1.inclination.to_value(u.rad))
        
        # >>> 1. Orbit 1
        
        e_1: float = orbital_elements_1.eccentricity.to_value()
        
        h_1: float = orbital_elements_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        omega: float = orbital_elements_1.argument_of_periapsis.to_value(u.rad)
        
        ta_current: float = cm.wrap_angle(orbital_elements_1.true_anomaly.to_value(u.rad), low=0, high=2 * np.pi)

        ta_an: float = cm.wrap_angle(-omega, low=0, high=2 * np.pi) # ? True anomaly of Ascending Node
        
        ta_dn: float = cm.wrap_angle(np.pi - omega, low=0, high=2 * np.pi) # ? True anomaly of Descending Node
        
        ta_1: float = ta_dn if (ta_an < ta_current < ta_dn) else ta_an
        
        r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(ta_1))
        
        v_t_1: float = h_1 / r_1
        
        v_r_1: float = mu / h_1 * e_1 * np.sin(ta_1)
        
        v_1: float = np.sqrt(v_r_1**2 + v_t_1**2)
        
        fpa_1: float = np.arctan(v_r_1 / v_t_1)
        
        # >>> 2. Result
        
        dv: float = np.abs(2 * v_1 * np.cos(fpa_1) * np.sin(delta_inc / 2))
        
        dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list=[dv * u.km / u.s]
        maneuver.flight_time_list=[0 * u.s]
        maneuver.delta_mass_list=[dm]
        maneuver.burn_time_list=[t_burn]
        maneuver.true_anomaly_list=[(ta_1 * u.rad).to(u.deg)]
        
        return maneuver
    
    @staticmethod
    def plane_change_maneuver_from_dihedral_angle(attractor: bd.Attractor,
                                                  rocket_motor: RocketMotor,
                                                  orbital_elements_1: o3d.OrbitalElements,
                                                  orbital_elements_2: o3d.OrbitalElements,
                                                  dihedral_angle: u.Quantity) -> ManeuverResult:
        """
        Plane change maneuver from dihedral angle between orbital planes
        
        A plane change maneuver is a single-impulse orbital maneuver used to change the inclination and/or the right
        ascension of the ascending node (RAAN) of a spacecraft’s orbit. When two orbits have different orientations, 
        the angle between their orbital planes is called the dihedral angle.
        
        This maneuver computes the Δv required to rotate the spacecraft’s velocity vector by the dihedral angle at a
        specific point in the orbit, typically at the intersection of the two planes, to achieve the desired plane
        change. The algorithm calculates the velocity components in the initial and target orbits at the maneuver point
        and determines the required Δv to transition between the two planes while minimizing fuel consumption.
        
        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            orbital_elements_2 (o3d.OrbitalElements): Orbital elements of the target orbit
            dihedral_angle (u.Quantity): Dihedral angle between the two orbital planes in degrees

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(orbital_elements_1.semimajor_axis.to_value(u.km),
                                      orbital_elements_1.eccentricity.to_value(),
                                      orbital_elements_1.inclination.to_value(u.deg),
                                      orbital_elements_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_1.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(orbital_elements_2.semimajor_axis.to_value(u.km),
                                      orbital_elements_2.eccentricity.to_value(),
                                      orbital_elements_2.inclination.to_value(u.deg),
                                      orbital_elements_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_2.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_2.true_anomaly.to_value(u.deg))
        
        cm.check_angle(dihedral_angle.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = bd.BODIES[attractor].g_0
        
        dihedral_angle: float = dihedral_angle.to_value(u.rad)
        
        # >>> 1. Orbit 1
        
        e_1: float = orbital_elements_1.eccentricity.to_value()
        
        ta1: float = orbital_elements_1.true_anomaly.to_value(u.rad)
        
        h_1: float = orbital_elements_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(ta1))
        
        v_t_1: float = h_1 / r_1
        
        v_r_1: float = mu / h_1 * e_1 * np.sin(ta1)
        
        # >>> 2. Orbit 2
        
        e_2: float = orbital_elements_2.eccentricity.to_value()
        
        ta_2: float = orbital_elements_2.true_anomaly.to_value(u.rad)
        
        h_2: float = orbital_elements_2.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        r_2: float = h_2**2 / mu * 1 / (1 + e_2 * np.cos(ta_2))
        
        v_t_2: float = h_2 / r_2
        
        v_r_2: float = mu / h_2 * e_2 * np.sin(ta_2)
        
        # >>> 3. Result
        
        dv: float = np.sqrt((v_r_2 - v_r_1)**2 + v_t_1**2 + v_t_2**2 - 2 * v_t_1 * v_t_2 * np.cos(dihedral_angle))
        
        dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list = [dv * u.km / u.s]
        maneuver.flight_time_list = [0 * u.s]
        maneuver.delta_mass_list = [dm]
        maneuver.burn_time_list=[t_burn]
        maneuver.orbital_elements_list = []
        
        return maneuver
    
    @staticmethod
    def plane_change_maneuver_from_raan_and_inclination(attractor: bd.Attractor,
                                                        rocket_motor: RocketMotor,
                                                        orbital_elements_1: o3d.OrbitalElements,
                                                        orbital_elements_2: o3d.OrbitalElements) -> ManeuverResult:
        """
        Plane change maneuver from RAAN and inclination differences
        
        This maneuver computes the plane change required to transition between two orbits with different orientations
        by analyzing the differences in their right ascension of the ascending node (RAAN) and inclination.
        By determining the dihedral angle between the orbital planes from these angular differences, the maneuver
        calculates the necessary Δv to achieve the desired plane change while minimizing fuel consumption.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            orbital_elements_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            orbital_elements_2 (o3d.OrbitalElements): Orbital elements of the target orbit

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(orbital_elements_1.semimajor_axis.to_value(u.km),
                                      orbital_elements_1.eccentricity.to_value(),
                                      orbital_elements_1.inclination.to_value(u.deg),
                                      orbital_elements_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_1.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(orbital_elements_2.semimajor_axis.to_value(u.km),
                                      orbital_elements_2.eccentricity.to_value(),
                                      orbital_elements_2.inclination.to_value(u.deg),
                                      orbital_elements_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      orbital_elements_2.argument_of_periapsis.to_value(u.deg),
                                      orbital_elements_2.true_anomaly.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: float = bd.BODIES[attractor].g_0
        
        inc_1: float = orbital_elements_1.inclination.to_value(u.rad)
        inc_2: float = orbital_elements_2.inclination.to_value(u.rad)
        
        raan_1: float = orbital_elements_1.right_ascension_of_ascending_node.to_value(u.rad)
        raan_2: float = orbital_elements_2.right_ascension_of_ascending_node.to_value(u.rad)
        
        argp_1: float = orbital_elements_1.argument_of_periapsis.to_value(u.rad)
        argp_2: float = 0.0
        
        # >>> 1. Differences
        
        delta_raan: float = raan_2 - raan_1
        
        delta_inc: float = inc_2 - inc_1
        
        # >>> 2. Plane Change
        
        if delta_raan * delta_inc > 0:
            
            delta: float = np.arccos(np.cos(inc_1) * np.cos(inc_2) + np.sin(inc_1) * np.sin(inc_2) * np.cos(delta_raan))
            
            cos_u_1: float = (-np.cos(inc_2) + np.cos(delta) * np.cos(inc_1)) / (np.sin(delta) * np.sin(inc_1))
            cos_u_2: float = (+np.cos(inc_1) - np.cos(delta) * np.cos(inc_2)) / (np.sin(delta) * np.sin(inc_2))
            sin_u_1: float = np.sin(delta_raan) * np.sin(inc_2) / np.sin(delta)
            sin_u_2: float = np.sin(delta_raan) * np.sin(inc_1) / np.sin(delta)
            
            u_1: float = np.arctan2(sin_u_1, cos_u_1)
            u_2: float = np.arctan2(sin_u_2, cos_u_2)
            
            ta_1: float = u_1 - argp_1
            
            argp_2: float = ta_1 + u_2
        
        else:
            
            delta: float = np.arccos(np.cos(inc_1) * np.cos(inc_2) + np.sin(inc_1) * np.sin(inc_2) * np.cos(delta_raan))
            
            cos_u_1: float = (+np.cos(inc_2) - np.cos(delta) * np.cos(inc_1)) / (np.sin(delta) * np.sin(inc_1))
            cos_u_2: float = (-np.cos(inc_1) + np.cos(delta) * np.cos(inc_2)) / (np.sin(delta) * np.sin(inc_2))
            sin_u_1: float = np.sin(delta_raan) * np.sin(inc_2) / np.sin(delta)
            sin_u_2: float = np.sin(delta_raan) * np.sin(inc_1) / np.sin(delta)
            
            u_1: float = np.arctan2(sin_u_1, cos_u_1)
            u_2: float = np.arctan2(sin_u_2, cos_u_2)
            
            ta_1: float = 2 * np.pi - u_1 - argp_1
            
            argp_2: float = 2 * np.pi - u_2 - ta_1
        
        # >>> 3. Orbit 1 at the maneuver point
        
        e_1: float = orbital_elements_1.eccentricity.to_value()
        
        h_1: float = orbital_elements_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(ta_1))
        
        v_t_1: float = h_1 / r_1
        
        # >>> 4. Result
        
        dv: float = 2 * v_t_1 * np.sin(delta / 2)
        
        dm: u.Quantity = rocket_motor.calc_propellant_mass(delta_velocity=dv * u.km / u.s, sea_level_gravity=g_0)
        
        t_burn: u.Quantity = rocket_motor.calc_burn_time(propellant_mass=dm, sea_level_gravity=g_0)
        
        rocket_motor.spacecraft_mass -= dm
        
        oe_t: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=orbital_elements_1.specific_angular_momentum,
                                                        semimajor_axis=orbital_elements_1.semimajor_axis,
                                                        eccentricity=orbital_elements_1.eccentricity,
                                                        inclination=inc_2 * u.rad,
                                                        right_ascension_of_ascending_node=raan_2 * u.rad,
                                                        argument_of_periapsis=argp_2 * u.rad,
                                                        true_anomaly=ta_1 * u.rad)
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.delta_velocity_list = [dv * u.km / u.s]
        maneuver.flight_time_list = [0 * u.s]
        maneuver.delta_mass_list = [dm]
        maneuver.burn_time_list=[t_burn]
        maneuver.orbital_elements_list = [oe_t]
        
        return maneuver
    
    @staticmethod
    def constant_tangential_thrust_transfer_from_time(attractor: bd.Attractor,
                                                      rocket_motor: RocketMotor,
                                                      initial_radius: u.Quantity,
                                                      time_of_flight: u.Quantity,
                                                      direction: SpiralDirection) -> typing.List[u.Quantity]:
        """
        Constant tangential thrust transfer from burning time
        
        This maneuver computes the final radius and propellant mass consumed for a constant tangential thrust transfer
        given the initial radius and the time of flight. The algorithm assumes a constant tangential thrust applied over
        the specified time interval, resulting in a continuous acceleration that modifies the spacecraf's orbit.
        
        By integrating the equations of motion under constant tangential thrust, the maneuver calculates the final
        orbital radius after the burn and the total propellant mass consumed based on the rocket motor's parameters and
        specific impulse. 

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            initial_radius (u.Quantity): Initial circular orbit radius
            time_of_flight (u.Quantity): Time of flight
            direction (SpiralDirection): Direction of the spiral

        Returns:
            typing.List[u.Quantity]: [final radius, propellant mass]
        """
        
        cm.check_attractor(attractor)
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: u.Quantity = bd.BODIES[attractor].g_0.to(u.m / u.s**2)
        
        m_0: float = rocket_motor.spacecraft_mass.to_value(u.kg)
        
        r_0: float = initial_radius.to_value(u.km)
        
        tof: float = time_of_flight.to_value(u.s)
        
        # >>> 1. Target radius
        
        v_0: float = np.sqrt(mu / r_0) # ? Initial circular orbit velocity
        
        c: float = rocket_motor.calc_effective_exhaust_velocity(sea_level_gravity=g_0).to_value(u.km / u.s)
        
        m_dot: float = rocket_motor.calc_propellant_mass_flow_rate(sea_level_gravity=g_0).to_value(u.kg / u.s)
        
        sign: float = +1 if direction == SpiralDirection.OUTWARD else -1
        
        r: float = mu / (v_0 + sign * c * np.log(1 - m_dot / m_0 * tof))**2
        
        # >>> 2. Propellant mass
        
        m_p: float = m_dot * tof
        
        return [r * u.km, m_p * u.kg]
    
    @staticmethod
    def constant_tangential_thrust_transfer_from_radius(attractor: bd.Attractor,
                                                        rocket_motor: RocketMotor,
                                                        initial_radius: u.Quantity,
                                                        final_radius: u.Quantity,
                                                        earth_shadow: bool = False) -> typing.List[u.Quantity]:
        """
        Constant tangential thrust transfer from final radius
        
        This maneuver computes the time of flight and propellant mass consumed for a constant tangential thrust transfer
        given the initial and final radii. The algorithm assumes a constant tangential thrust applied over the transfer,
        resulting in a continuous acceleration that modifies the spacecraft's orbit.
        
        By integrating the equations of motion under constant tangential thrust, the maneuver calculates the time of
        flight required to reach the final radius and the total propellant mass consumed based on the rocket motor's
        parameters and specific impulse.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            initial_radius (u.Quantity): Initial circular orbit radius
            final_radius (u.Quantity): Final circular orbit radius
            earth_shadow (bool): Enable/disable the earth shadow effect. Defaults to False.

        Returns:
            list: [time of flight, propellant mass, delta velocity]
        """
        
        cm.check_attractor(attractor)
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        R_E: float = bd.BODIES[attractor].R_E.to_value(u.km)
        
        g_0: u.Quantity = bd.BODIES[attractor].g_0.to(u.m / u.s**2)
        
        m_0: float = rocket_motor.spacecraft_mass.to_value(u.kg)
        
        r_0: float = initial_radius.to_value(u.km)
        
        r_f: float = final_radius.to_value(u.km)
        
        # >>> 1. Flight time
        
        v_0: float = np.sqrt(mu / r_0) # ? Initial circular orbit velocity
        
        v_f: float = np.sqrt(mu / r_f) # ? Final circular orbit velocity
        
        dv: float = - np.abs(v_f - v_0)
        
        c: float = rocket_motor.calc_effective_exhaust_velocity(sea_level_gravity=g_0).to_value(u.km / u.s)
        
        c_tilde: float = dv
        
        if earth_shadow:
            
            coeff: float = np.pi / R_E
            
            c_tilde = np.sqrt(coeff * mu) * (np.arctanh(np.sqrt(coeff * r_f) + 0j) - np.arctanh(np.sqrt(coeff * r_0) + 0j))
        
        m_dot: float = rocket_motor.calc_propellant_mass_flow_rate(sea_level_gravity=g_0).to_value(u.kg / u.s)
        
        tof: float = m_0 / m_dot * (1 - np.exp(c_tilde.real / c))
        
        # >>> 2. Propellant mass
        
        m_p: float = m_dot * tof
        
        return [tof * u.s, m_p * u.kg, dv * u.km / u.s]
    
    @staticmethod
    def earth_shadow(attractor: bd.Attractor, radius: u.Quantity) -> u.Quantity:
        """
        Compute the percentage of time the spacecraft spends in sunlight over one orbital revolution

        Args:
            attractor (bd.Attractor): Main attractor
            radius (u.Quantity): Circular orbit radius

        Returns:
            u.Quantity: Percentage of sunlight
        """
        
        R_E: float = bd.BODIES[attractor].R_E.to_value(u.km)
        
        r: float = radius.to_value(u.km)
        
        # >>> 1. Earth-shadow angle
        
        phi: float = 2 * np.arcsin(R_E / r)
        
        # >>> 2. Sunlight weighting function
        
        w: float = 1 - phi / (2 * np.pi)
        
        return w * u.one
    
    @staticmethod
    def non_impulsive_inclination_change_maneuver(attractor: bd.Attractor,
                                                  rocket_motor: RocketMotor,
                                                  radius: u.Quantity,
                                                  initial_inclination: u.Quantity,
                                                  final_inclination: u.Quantity) -> typing.List[u.Quantity]:
        """
        Non-impulsive inclination change maneuver

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor object
            radius (u.Quantity): Circular orbit radius
            initial_inclination (u.Quantity): Initial orbital inclination
            final_inclination (u.Quantity): Final orbital inclination

        Returns:
            list: [time of flight, propellant mass, delta velocity]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_angle(initial_inclination.to_value(u.deg))
        cm.check_angle(final_inclination.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: u.Quantity = bd.BODIES[attractor].g_0.to(u.m / u.s**2)
        
        m_0: float = rocket_motor.spacecraft_mass.to_value(u.kg)
        
        r: float = radius.to_value(u.km)
        
        i_0: float = initial_inclination.to_value(u.rad)
        
        i_f: float = final_inclination.to_value(u.rad)
        
        # >>> 1. Flight time
        
        v: float = np.sqrt(mu / r) # ? Circular orbit velocity
        
        d_i: float = np.abs(i_f - i_0)
        
        dv: float = d_i * np.pi * v / 2
        
        c: float = rocket_motor.calc_effective_exhaust_velocity(sea_level_gravity=g_0).to_value(u.km / u.s)
        
        m_dot: float = rocket_motor.calc_propellant_mass_flow_rate(sea_level_gravity=g_0).to_value(u.kg / u.s)
        
        tof: float = m_0 / m_dot * (1 - np.exp(- dv / c))
        
        # >>> 2. Propellant mass
        
        m_p: float = m_dot * tof
        
        return [tof * u.s, m_p * u.kg, dv * u.km / u.s]
    
    @staticmethod
    def non_impulsive_inclined_circular_orbits_transfer(attractor: bd.Attractor,
                                                        rocket_motor: RocketMotor,
                                                        initial_radius: u.Quantity,
                                                        final_radius: u.Quantity,
                                                        initial_inclination: u.Quantity,
                                                        final_inclination: u.Quantity) -> typing.List[u.Quantity]:
        """
        Non-impulsive transfer between two inclined circular orbits

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor object
            initial_radius (u.Quantity): Initial circular orbit radius
            final_radius (u.Quantity): Final circular orbit radius
            initial_inclination (u.Quantity): Initial orbital inclination
            final_inclination (u.Quantity): Final orbital inclination

        Returns:
            list: [time of flight, propellant mass, delta velocity]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_angle(initial_inclination.to_value(u.deg))
        cm.check_angle(final_inclination.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        g_0: u.Quantity = bd.BODIES[attractor].g_0.to(u.m / u.s**2)
        
        m_0: float = rocket_motor.spacecraft_mass.to_value(u.kg)
        
        r_0: float = initial_radius.to_value(u.km)
        
        r_f: float = final_radius.to_value(u.km)
        
        i_0: float = initial_inclination.to_value(u.rad)
        
        i_f: float = final_inclination.to_value(u.rad)
        
        # >>> 1. Flight time
        
        v_0: float = np.sqrt(mu / r_0) # ? Initial circular orbit velocity
        
        v_f: float = np.sqrt(mu / r_f) # ? Final circular orbit velocity
        
        d_i: float = i_f - i_0
        
        # * T. N. Edelbaum equation
        
        dv: float = np.sqrt(v_0**2 + v_f**2 - 2 * v_0 * v_f * np.cos(d_i * np.pi / 2))
        
        c: float = rocket_motor.calc_effective_exhaust_velocity(sea_level_gravity=g_0).to_value(u.km / u.s)
        
        m_dot: float = rocket_motor.calc_propellant_mass_flow_rate(sea_level_gravity=g_0).to_value(u.kg / u.s)
        
        tof: float = m_0 / m_dot * (1 - np.exp(- dv / c))
        
        # >>> 2. Propellant mass
        
        m_p: float = m_dot * tof
        
        return [tof * u.s, m_p * u.kg, dv * u.km / u.s]
    
    @staticmethod
    def non_impulsive_maneuver(attractor: bd.Attractor,
                               rocket_motor: RocketMotor,
                               initial_position: u.Quantity,
                               initial_velocity: u.Quantity,
                               burning_time_guess: u.Quantity,
                               time_step: u.Quantity,
                               final_position: u.Quantity,
                               semi_major_axis_target: bool = False,
                               inclination_target: bool = False,
                               initial_radius: u.Quantity = 0 * u.km,
                               final_radius: u.Quantity = 0 * u.km,
                               initial_inclination: u.Quantity = 0 * u.deg,
                               final_inclination: u.Quantity = 0 * u.deg,
                               thrust_direction: ae.ThrustDirection = ae.ThrustDirection.ALONG_VELOCITY,
                               tolerance: float = 1e-0) -> typing.Tuple[NonImpulsiveManeuverResult, tbp.Result]:
        """
        Non impulsive maneuver that, starting from an initial position and velocity, computes the final position and
        velocity after a given burning time guess. That guess is adjusted iteratively until the final position is close
        enough to the target position or the semi-major axis.
        
        If the 'semi_major_axis_target' is set to True, the algorithm will try to match the semi-major axis of the final
        orbit to the norm of the final position vector. Otherwise, it will try to match the final position vector norm
        to the target final position vector norm.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor object
            initial_position (u.Quantity): Initial position vector
            initial_velocity (u.Quantity): Initial velocity vector
            burning_time_guess (u.Quantity): Initial burning time guess
            time_step (u.Quantity): Time step for burning time calculation
            final_position (u.Quantity): Final position vector
            semi_major_axis_target (bool, optional): Semi-major axis target. Defaults to False.
            inclination_target (bool, optional): Inclination target. Defaults to False.
            initial_radius (u.Quantity, optional): Initial radius. Defaults to 0 * u.km.
            final_radius (u.Quantity, optional): Final radius. Defaults to 0 * u.km.
            initial_inclination (u.Quantity, optional): Initial inclination. Defaults to 0 * u.deg.
            final_inclination (u.Quantity, optional): Final inclination. Defaults to 0 * u.deg.
            thrust_direction (ae.ThrustDirection, optional): Thrust direction. Defaults to ae.ThrustDirection.ALONG_VELOCITY.
            tolerance (float, optional): Tolerance. Defaults to 1e-0.

        Returns:
            typing.Tuple[NonImpulsiveManeuverResult, tbp.Result]: Maneuver result & integration result
        """
        
        if burning_time_guess.to_value(u.s) <= 0:
            
            raise ValueError('Initial burning time guess must be greater than zero.')
        
        t_burn: time.TimeDelta = time.TimeDelta(burning_time_guess.to_value(u.s) * u.s)
        
        prev_epsilon: float = 0.0
        
        maneuver: NonImpulsiveManeuverResult = NonImpulsiveManeuverResult()
        
        result: tbp.Result = tbp.Result()
        
        maneuver.burn_time = t_burn.to(u.s)
        
        max_iterations: int = 100
        
        iteration: int = 0
        
        while True:
            
            if iteration > max_iterations:
                
                print('Reached max iterations.')
                
                break
            
            # >>> 1. Integrate
            
            orbit: tbp.Orbit = tbp.Orbit()
            
            orbit.from_cartesian(attractor=attractor,
                                 position=initial_position,
                                 velocity=initial_velocity,
                                 epoch=time.Time('2026-01-01T00:00:00', format='isot', scale='utc'))
            
            result = orbit.propagate_for(delta=t_burn,
                                         rocket_motor=rocket_motor,
                                         thrust_direction=thrust_direction,
                                         initial_radius=initial_radius.to_value(u.km),
                                         target_radius=final_radius.to_value(u.km),
                                         initial_inclination=initial_inclination.to_value(u.rad),
                                         target_inclination=final_inclination.to_value(u.rad))
            
            if not result.success:
                
                print('Integration failed.')
                
                break
            
            r: u.Quantity = np.array([result.position_x[-1].to_value(u.km),
                                      result.position_y[-1].to_value(u.km),
                                      result.position_z[-1].to_value(u.km)]) * u.km
            
            v: u.Quantity = np.array([result.velocity_x[-1].to_value(u.km / u.s),
                                      result.velocity_y[-1].to_value(u.km / u.s),
                                      result.velocity_z[-1].to_value(u.km / u.s)]) * u.km / u.s
            
            m_sc: u.Quantity = result.mass_spacecraft[-1]
            
            # >>> 2. Calculate orbital elements
            
            oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r, velocity=v)
            
            # >>> 3. Update state vector
            
            if semi_major_axis_target:
                
                epsilon: float = oe.semimajor_axis.to_value(u.km) - np.linalg.norm(final_position.to_value(u.km))
                
                maneuver.position_x = r[0]
                maneuver.position_y = r[1]
                maneuver.position_z = r[2]
                maneuver.velocity_x = v[0]
                maneuver.velocity_y = v[1]
                maneuver.velocity_z = v[2]
                maneuver.spacecraft_mass = m_sc
            
            elif inclination_target:
                
                epsilon: float = oe.inclination.to_value(u.deg) - final_inclination.to_value(u.deg)
                
                maneuver.position_x = r[0]
                maneuver.position_y = r[1]
                maneuver.position_z = r[2]
                maneuver.velocity_x = v[0]
                maneuver.velocity_y = v[1]
                maneuver.velocity_z = v[2]
                maneuver.spacecraft_mass = m_sc
                
            else:
            
                delta_theta: u.Quantity = u.Quantity(180.0, u.deg) - oe.true_anomaly
            
                l_r_f, l_v_f = lc.LagrangeCoefficients.propagate_of_angle(attractor=attractor,
                                                                          initial_position=r,
                                                                          initial_velocity=v,
                                                                          delta_true_anomaly=delta_theta)
            
                epsilon: float = np.linalg.norm(l_r_f.to_value(u.km)) - np.linalg.norm(final_position.to_value(u.km))
                
                maneuver.position_x = l_r_f[0]
                maneuver.position_y = l_r_f[1]
                maneuver.position_z = l_r_f[2]
                maneuver.velocity_x = l_v_f[0]
                maneuver.velocity_y = l_v_f[1]
                maneuver.velocity_z = l_v_f[2]
                maneuver.spacecraft_mass = m_sc
            
            # >>> 4. Check error
            
            if np.abs(epsilon) < tolerance: break
            
            # >>> 5. Update time interval
            
            if not np.isclose(prev_epsilon, 0.0, rtol=1e-09, atol=1e-09) and prev_epsilon * epsilon < 0:
                
                time_step = time_step / 2.0
            
            if epsilon < 0:
                
                t_burn += time.TimeDelta(time_step.to_value(u.s) * u.s)
                
            else:
                
                t_burn -= time.TimeDelta(time_step.to_value(u.s) * u.s)
            
            maneuver.burn_time = t_burn.to(u.s)
            
            # >>> 6. Update error
            
            prev_epsilon = epsilon
            
            iteration += 1
        
        return maneuver, result
