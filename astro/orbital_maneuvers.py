"""
Orbital Maneuvers

Implementation of orbital maneuver algorithms.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 6: Orbital Maneuvers

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 3: Orbit Determination
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
import astro.orbit_3d as o3d
import astro.orbital_position as op
import astro.orbit_determination as od
import astro.two_body_problem as tbp
import astro.lagrange_coefficients as lc

@dc.dataclass
class ManeuverResult:
    """Maneuver parameters"""
    
    dv: typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.km / u.s])                    # ? Delta Velocity
    dt: typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.s])                           # ? Delta Time
    dm: typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.kg])                          # ? Delta Mass
    oe: typing.List[o3d.OrbitalElements] = dc.field(default_factory=lambda: [o3d.OrbitalElements()])    # ? Orbital Elements of the transfer orbits
    nu: typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.deg])                         # ? True anomaly at maneuver points
    fpa: typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.deg])                        # ? Flight Path Angle at maneuver point

@dc.dataclass
class RocketMotor:
    """
    Rocket Motor
    
    Args:
        I_sp (float): Specific impulse
        T (float): Thrust
        m_sc (float): Spacecraft mass
        m_prop (float): Propellant mass
    """
    
    I_sp : u.Quantity = dc.field(default_factory=lambda: 0 * u.s)       # ? Specific Impulse
    T : u.Quantity = dc.field(default_factory=lambda: 0 * u.N)          # ? Thrust
    m_sc : u.Quantity = dc.field(default_factory=lambda: 0 * u.kg)      # ? Mass of the Spacecraft (propellant included)
    m_prop : u.Quantity = dc.field(default_factory=lambda: 0 * u.kg)    # ? Mass of the Propellant
    
    def consumed_propellant_mass(self, dv : u.Quantity, g_0 : u.Quantity) -> u.Quantity:
        """Ideal rocket equation mass calculation

        Args:
            dv (float): Delta velocity
            g_0 (float): Standard gravity

        Returns:
            float: Propellant mass
        """
        
        self.m_prop = self.m_sc.to_value(u.kg) *\
                      (1 - np.exp(-dv.to_value(u.km / u.s) / (self.I_sp.to_value(u.s) * g_0.to_value(u.km / u.s**2))))
        
        return self.m_prop * u.kg

class HohmannDirection(enum.IntEnum):
    """List of Hohmann transfer directions"""
    
    PERICENTER_APOCENTER = 0
    APOCENTER_PERICENTER = 1

@dc.dataclass
class NonImpulsiveManeuverResult:
    """Result of non-impulsive maneuver integration
    """
    
    t_burn: u.Quantity = dc.field(default_factory=lambda: 0 * u.s)
    r_x: u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    r_y: u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    r_z: u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    v_x: u.Quantity = dc.field(default_factory=lambda: 0 * u.km / u.s)
    v_y: u.Quantity = dc.field(default_factory=lambda: 0 * u.km / u.s)
    v_z: u.Quantity = dc.field(default_factory=lambda: 0 * u.km / u.s)
    m_sc: u.Quantity = dc.field(default_factory=lambda: 0 * u.kg)

class OrbitalManeuvers():
    """Orbital Maneuvers
    """
    
    def __init__(self):
        """Constructor
        """
        
        pass
    
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
                         oe_1 : o3d.OrbitalElements,
                         oe_2 : o3d.OrbitalElements,
                         direction : HohmannDirection) -> ManeuverResult:
        """
        Hohmann transfer maneuver
        
        The Hohmann transfer is a two‑impulse orbital maneuver used to transfer a spacecraft between two coplanar,
        elliptical or circular orbits around the same central body. It is the minimum‑energy transfer between two 
        circular orbits and a widely used approximation for transfers between low‑eccentricity orbits.
        
        This implementation generalizes the classical Hohmann transfer to allow transfers between arbitrary coplanar 
        elliptical orbits, using one of two possible geometric configurations
        - pericenter → apocenter
        - apocenter → pericenter


        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            oe_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            oe_2 (o3d.OrbitalElements): Orbital elements of the target orbit
            direction (HohmannDirection): Direction of the transfer

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(oe_1.semimajor_axis.to_value(u.km),
                                      oe_1.eccentricity.to_value(),
                                      oe_1.inclination.to_value(u.deg),
                                      oe_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe_1.argument_of_periapsis.to_value(u.deg),
                                      oe_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(oe_2.semimajor_axis.to_value(u.km),
                                      oe_2.eccentricity.to_value(),
                                      oe_2.inclination.to_value(u.deg),
                                      oe_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe_2.argument_of_periapsis.to_value(u.deg),
                                      oe_2.true_anomaly.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 0. Pericenter/Apocenter radii
        
        r_p_1: float = oe_1.calc_perigee_radius().to_value(u.km)
        r_a_1: float = oe_1.calc_apogee_radius().to_value(u.km)
        
        r_p_2: float = oe_2.calc_perigee_radius().to_value(u.km)
        r_a_2: float = oe_2.calc_apogee_radius().to_value(u.km)
        
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
        
        T_t = 2 * np.pi / float(np.sqrt(mu)) * a_t**(3/2) # ? Orbital Period
        
        # >>> 4. Delta-V Calculations
        
        dv_1: float = 0.0
        dv_2: float = 0.0
        nu_1: float = 0.0
        nu_t: float = 0.0
        
        if direction == HohmannDirection.PERICENTER_APOCENTER:
            
            dv_1 = abs(v_p_t - (v_p_1 if not swap else v_a_2))
            
            dv_2 = abs((v_a_2 if not swap else v_p_1) - v_a_t)
            
            nu_1 = 0.0
            
            nu_t = 0.0 if not swap else 180.0
        
        elif direction == HohmannDirection.APOCENTER_PERICENTER:
            
            dv_1 = abs(v_a_t - (v_a_1 if not swap else v_p_2))
            
            dv_2 = abs((v_p_2 if not swap else v_a_1) - v_p_t)
            
            nu_1 = 180.0
            
            nu_t = 180.0 if not swap else 0.0
        
        argp_t: float = oe_1.argument_of_periapsis.to_value(u.deg)
        
        if swap:
            
            argp_t = cm.wrap_angle(argp_t + 180.0, -180.0, +180.0)
        
        # >>> 5. Result
        
        dm_1: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv_1 * u.km / u.s, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm_1
        
        dm_2: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv_2 * u.km / u.s, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm_2
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.dv=[dv_1 * u.km / u.s, dv_2 * u.km / u.s]
        maneuver.dt=[0.5 * T_t * u.s]
        maneuver.dm=[dm_1, dm_2]
        maneuver.oe=[o3d.OrbitalElements(specific_angular_momentum=h_t * u.km**2 / u.s,
                                         semimajor_axis=a_t * u.km,
                                         eccentricity=e_t * u.dimensionless_unscaled,
                                         inclination=oe_1.inclination,
                                         right_ascension_of_ascending_node=oe_1.right_ascension_of_ascending_node,
                                         argument_of_periapsis=argp_t * u.deg,
                                         true_anomaly=nu_t * u.deg)]
        maneuver.nu=[nu_1 * u.deg]
        
        return maneuver
    
    @staticmethod
    def bi_elliptic_hohmann_transfer(attractor: bd.Attractor,
                                     rocket_motor: RocketMotor,
                                     oe_1 : o3d.OrbitalElements,
                                     oe_2 : o3d.OrbitalElements,
                                     r_3 : u.Quantity) -> ManeuverResult:
        """
        Bi-Elliptic Hohmann transfer maneuver
        
        The bi‑elliptic Hohmann transfer is a three‑impulse orbital maneuver used to transfer a spacecraft between two 
        coplanar orbits when the ratio between the final and initial orbital radii is sufficiently large.
        Unlike the classical Hohmann transfer, which uses a single transfer ellipse, the bi‑elliptic transfer introduces
        an intermediate apocenter r_3, allowing the spacecraft to perform part of the maneuver at a very low velocity.
        This can reduce the total Δv when the target orbit is much larger than the initial one.
        
        This implementation generalizes the bi‑elliptic transfer to elliptical orbits by computing the maneuver at the
        appropriate pericenter or apocenter radii of the initial and final orbits.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            oe_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            oe_2 (o3d.OrbitalElements): Orbital elements of the target orbit
            r_3 (u.Quantity): Apocenter of intermediate orbit

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        oe_t_1: o3d.OrbitalElements = copy.deepcopy(oe_1)
        
        oe_t_1.update_from_perigee_apogee(periapsis_radius=oe_1.calc_perigee_radius(), apoapsis_radius=r_3)
        
        maneuver_1: ManeuverResult = OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                       rocket_motor=rocket_motor,
                                                                       oe_1=oe_1,
                                                                       oe_2=oe_t_1,
                                                                       direction=HohmannDirection.PERICENTER_APOCENTER)
        
        oe_t_2: o3d.OrbitalElements = copy.deepcopy(oe_2)
        
        oe_t_2.update_from_perigee_apogee(periapsis_radius=oe_2.calc_perigee_radius(), apoapsis_radius=r_3)
        
        maneuver_2: ManeuverResult = OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                      rocket_motor=rocket_motor,
                                                                      oe_1=oe_t_1,
                                                                      oe_2=oe_t_2,
                                                                      direction=HohmannDirection.APOCENTER_PERICENTER)
        
        maneuver_3: ManeuverResult = OrbitalManeuvers.hohmann_transfer(attractor=attractor,
                                                                      rocket_motor=rocket_motor,
                                                                      oe_1=oe_t_2,
                                                                      oe_2=oe_2,
                                                                      direction=HohmannDirection.APOCENTER_PERICENTER)
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.dv=[maneuver_1.dv[0], maneuver_2.dv[0], maneuver_3.dv[1]]
        maneuver.dt=[maneuver_1.dt[0], maneuver_2.dt[0]]
        maneuver.dm=[maneuver_1.dm[0], maneuver_2.dm[0], maneuver_3.dm[1]]
        maneuver.oe=[maneuver_1.oe[0], maneuver_2.oe[0]]
        maneuver.nu=[maneuver_1.nu[0], maneuver_2.nu[0], maneuver_3.nu[0]]
        
        return maneuver
    
    @staticmethod
    def phasing_maneuver(attractor: bd.Attractor,
                         rocket_motor: RocketMotor,
                         oe : o3d.OrbitalElements,
                         nu_target : u.Quantity,
                         num_revolutions : int = 1) -> ManeuverResult:
        """
        Phasing maneuver from chaser A to target B
        
        A phasing maneuver is a two‑impulse orbital strategy used to synchronize the position of a chaser spacecraft (A)
        with a target spacecraft (B) located on the same orbital plane. The goal is to adjust the orbital period of the
        chaser so that, after completing a specified number of revolutions on a temporary “phasing orbit,” it arrives at
        the same true anomaly as the target.
        
        This maneuver is commonly used for rendezvous, formation flying, and constellation maintenance.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            oe (o3d.OrbitalElements): Orbital elements of chaser A
            nu_target (u.Quantity): True anomaly of target B
            num_revolutions (int, optional): Number of revolutions on phasing orbit. Defaults to 1.

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(oe.semimajor_axis.to_value(u.km),
                                      oe.eccentricity.to_value(),
                                      oe.inclination.to_value(u.deg),
                                      oe.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe.argument_of_periapsis.to_value(u.deg),
                                      oe.true_anomaly.to_value(u.deg))
        
        cm.check_angle(nu_target.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 1. Chaser Orbit period and velocity at pericenter
        
        oe.calc_specific_angular_momentum(attractor)
        
        T_1: float = oe.calc_orbital_period(attractor=attractor).to_value(u.s)
        
        v_p_1: float = oe.specific_angular_momentum.to_value(u.km**2 / u.s) / oe.calc_perigee_radius().to_value(u.km)
        
        # >>> 2. Time from A (pericenter - chaser) to B (target) placed at nu_target w.r.t. A
        
        t_AB: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(nu=nu_target, T=T_1 * u.s, e=oe.eccentricity.to_value())
        
        # >>> 3. Orbit 2 (Phasing Orbit with kick at pericenter)
        
        T_2: float = T_1 - t_AB.to_value(u.s) / num_revolutions
        
        a_2: float = (float(np.sqrt(mu)) * T_2 / (2 * np.pi))**(2/3)
        
        r_A: float = oe.calc_perigee_radius().to_value(u.km) # ? Maneuver point is the pericenter of the chaser orbit
        
        r_D: float = 2 * a_2 - r_A # ? Opposite point of the phasing orbit
        
        h_2: float = np.sqrt(2 * mu) * np.sqrt(r_A * r_D / (r_A + r_D))
        
        v_p_A: float = h_2 / r_A
        
        # >>> 4. Delta-V Calculations
        
        dv_1: float = np.abs(v_p_A - v_p_1)
        
        dv_2: float = np.abs(v_p_1 - v_p_A)
        
        # >>> 5. Result
        
        dm_1: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv_1 * u.km / u.s, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm_1
        
        dm_2: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv_2 * u.km / u.s, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm_2
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.dv=[dv_1 * u.km / u.s, dv_2 * u.km / u.s]
        maneuver.dt=[num_revolutions * T_2 * u.s]
        maneuver.dm=[dm_1, dm_2]
        maneuver.oe=[o3d.OrbitalElements(specific_angular_momentum=h_2 * u.km**2 / u.s,
                                         semimajor_axis=a_2 * u.km,
                                         eccentricity=(r_D - r_A) / (r_D + r_A) * u.dimensionless_unscaled,
                                         inclination=oe.inclination,
                                         right_ascension_of_ascending_node=oe.right_ascension_of_ascending_node,
                                         argument_of_periapsis=oe.argument_of_periapsis,
                                         true_anomaly=0 * u.deg)]
        
        return maneuver
    
    @staticmethod
    def non_hohmann_transfer(attractor: bd.Attractor,
                             rocket_motor: RocketMotor,
                             oe_1 : o3d.OrbitalElements,
                             r_2 : u.Quantity,
                             nu_2: u.Quantity) -> ManeuverResult:
        """
        Non-Hohmann transfer between coaxial elliptical orbits
        
        A non‑Hohmann transfer is a general two‑impulse maneuver used to move a spacecraft from an initial elliptical
        orbit to a target point located at a specified radius and true anomaly on a second coaxial (same‑focus) orbit.
        Unlike the classical Hohmann transfer, which is constrained to pericenter‑to‑apocenter geometry, the non‑Hohmann
        transfer allows the spacecraft to intercept the target at an arbitrary true anomaly. This makes it suitable for
        rendezvous, phasing, and transfers between elliptical orbits where the target point is not aligned with the apsides.
        This maneuver computes a single transfer ellipse that connects:
        - the spacecraft’s current position on the initial orbit
        - the desired target position defined by radius r_2 and true anomaly nu _2
        
        The transfer is completed with two tangential burns: one to enter the transfer ellipse and one to match the target orbit at the interception point.


        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            oe_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            r_2 (u.Quantity): Target radius
            nu_2 (u.Quantity): Target true anomaly

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(oe_1.semimajor_axis.to_value(u.km),
                                      oe_1.eccentricity.to_value(),
                                      oe_1.inclination.to_value(u.deg),
                                      oe_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe_1.argument_of_periapsis.to_value(u.deg),
                                      oe_1.true_anomaly.to_value(u.deg))
        
        cm.check_angle(nu_2.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        r_2: float = r_2.to_value(u.km)
        nu_2: float = nu_2.to_value(u.rad)
        
        # >>> 1. Orbit 1 (Starting Orbit)
        
        r_p_1: float = oe_1.calc_perigee_radius().to_value(u.km)
        r_a_1: float = oe_1.calc_apogee_radius().to_value(u.km)
        
        h_1: float = np.sqrt(2 * mu) * np.sqrt(r_a_1 * r_p_1 / (r_a_1 + r_p_1))
        
        r_1: float = h_1**2 / mu * 1 / (1 + oe_1.eccentricity.to_value() * np.cos(oe_1.true_anomaly.to_value(u.rad))) # ? Radius at maneuver point
        
        v_t_1: float = h_1 / r_1 # ? Transversal velocity at maneuver point
        
        v_r_1: float = mu / h_1 * oe_1.eccentricity.to_value() * np.sin(oe_1.true_anomaly.to_value(u.rad)) # ? Radial velocity at maneuver point
        
        v_1: float = np.sqrt(v_r_1**2 + v_t_1**2) # ? Velocity at maneuver point
        
        fpa_1: float = np.arctan(v_r_1 / v_t_1) # ? Flight path angle at maneuver point
        
        # >>> 2. Transfer Orbit
        
        e_T: float = - (r_2 - r_1) / (r_2 * np.cos(nu_2) - r_1 * np.cos(oe_1.true_anomaly.to_value(u.rad)))
        
        h_T: float = np.sqrt(mu * r_1 * r_2) * np.sqrt((np.cos(nu_2) - np.cos(oe_1.true_anomaly.to_value(u.rad))) /\
            (r_2 * np.cos(nu_2) - r_1 * np.cos(oe_1.true_anomaly.to_value(u.rad))))
        
        v_t_T: float = h_T / r_1
        
        v_r_T: float = mu / h_T * e_T * np.sin(oe_1.true_anomaly.to_value(u.rad))
        
        v_T: float = np.sqrt(v_r_T**2 + v_t_T**2)
        
        fpa_T: float = np.arctan(v_r_T / v_t_T)
        
        r_p_T: float = h_T**2 / mu * 1 / (1 + e_T)
        
        r_a_T: float = h_T**2 / mu * 1 / (1 - e_T)
        
        a_T: float = 0.5 * (r_p_T + r_a_T)
        
        T_T: float = 2 * np.pi / float(np.sqrt(mu)) * a_T**(3/2)
        
        # >>> 4. Result
        
        dfpa: float = fpa_T - fpa_1
        
        dv: float = np.sqrt(v_1**2 + v_T**2 - 2 * v_1 * v_T * np.cos(dfpa))
        
        phi: float = np.arctan((v_r_T - v_r_1) / (v_t_T - v_t_1))
        
        if (phi < 0):
            
            phi += np.pi
        
        t_1: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(nu=oe_1.true_anomaly, T=T_T * u.s, e=e_T)
        
        dm: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv * u.km / u.s, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.dv = [dv * u.km / u.s]
        maneuver.dt = [T_T * u.s - t_1]
        maneuver.dm = [dm]
        maneuver.oe = [o3d.OrbitalElements(specific_angular_momentum=h_T * u.km**2 / u.s,
                                           semimajor_axis=a_T * u.km,
                                           eccentricity=e_T * u.dimensionless_unscaled,
                                           inclination=oe_1.inclination,
                                           right_ascension_of_ascending_node=oe_1.right_ascension_of_ascending_node,
                                           argument_of_periapsis=oe_1.argument_of_periapsis,
                                           true_anomaly=oe_1.true_anomaly)]
        maneuver.fpa = [phi * u.rad]
        
        return maneuver
    
    @staticmethod
    def apse_line_rotation_from_eta(attractor: bd.Attractor,
                                    rocket_motor: RocketMotor,
                                    oe_1: o3d.OrbitalElements,
                                    oe_2: o3d.OrbitalElements,
                                    eta : u.Quantity,
                                    second_intersection_point : bool = False) -> ManeuverResult:
        """
        Apse line rotation from angle variation eta
        
        An apse‑line rotation maneuver is a two‑impulse orbital maneuver used to rotate the line of apsides (the line
        connecting pericenter and apocenter) of an elliptical orbit by a specified angle eta , without changing the
        orbital energy or inclination. This maneuver is required when the spacecraft must realign its argument of
        perigee to match a target orbit or to achieve a specific geometric configuration for rendezvous, phasing, or
        mission design.
        
        The maneuver exploits the fact that two coaxial elliptical orbits with different arguments of perigee intersect
        at two points. By performing impulsive burns at one of these intersection points, the spacecraft can transition
        from the initial orbit to the target orbit while rotating the apse line by the desired angle.


        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            oe_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            oe_2 (o3d.OrbitalElements): Orbital elements of the target orbit
            eta (u.Quantity): Apse line angle rotation
            second_intersection_point (bool, optional): True for using the second intersection point. Defaults to False.

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(oe_1.semimajor_axis.to_value(u.km),
                                      oe_1.eccentricity.to_value(),
                                      oe_1.inclination.to_value(u.deg),
                                      oe_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe_1.argument_of_periapsis.to_value(u.deg),
                                      oe_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(oe_2.semimajor_axis.to_value(u.km),
                                      oe_2.eccentricity.to_value(),
                                      oe_2.inclination.to_value(u.deg),
                                      oe_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe_2.argument_of_periapsis.to_value(u.deg),
                                      oe_2.true_anomaly.to_value(u.deg))
        
        cm.check_angle(eta.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        eta: float = eta.to_value(u.rad)
        
        # >>> 1. Orbit parameters
        
        e_1: float = oe_1.eccentricity.to_value()
        
        h_1: float = oe_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        e_2: float = oe_2.eccentricity.to_value()
        
        h_2: float = oe_2.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        # >>> 2. Coefficients a, b, c of the quadratic equation for the true anomaly at the intersection point
        
        a: float = e_1 * h_2**2 - e_2 * h_1**2 * np.cos(eta)
        
        b: float = - e_2 * h_1**2 * np.sin(eta)
        
        c: float = h_1**2 - h_2**2
        
        phi: float = np.arctan(b / a)
        
        sign: int = 1 if not second_intersection_point else -1
        
        nu_1: float = phi + sign * np.arccos(c / a * np.cos(phi))
        
        if nu_1 < 0: nu_1 = 2 * np.pi + nu_1
        
        r: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(nu_1))
        
        # >>> 3. Orbit 1
        
        v_t_1: float = h_1 / r
        
        v_r_1: float = mu / h_1 * e_1 * np.sin(nu_1)
        
        v_1: float = np.sqrt(v_r_1**2 + v_t_1**2)
        
        fpa_1: float = np.arctan(v_r_1 / v_t_1)
        
        # >>> 4. Orbit 2
        
        v_t_2: float = h_2 / r
        
        v_r_2: float = mu / h_2 * e_2 * np.sin(nu_1 - eta)
        
        v_2: float = np.sqrt(v_r_2**2 + v_t_2**2)
        
        fpa_2: float = np.arctan(v_r_2 / v_t_2)
        
        # >>> 5. Result
        
        dfpa: float = fpa_2 - fpa_1
        
        dv: float = np.sqrt(v_1**2 + v_2**2 - 2 * v_1 * v_2 * np.cos(dfpa))
        
        phi: float = 0.0
        
        if np.abs(v_t_2 - v_t_1) < 1e-6:
            
            phi = np.pi if v_r_2 - v_r_1 > 0 else -np.pi
            
        else:
            
            phi = np.arctan((v_r_2 - v_r_1) / (v_t_2 - v_t_1))
            
        if (phi < 0):
            
            phi += np.pi
        
        dm: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv * u.km / u.s, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.dv = [dv * u.km / u.s]
        maneuver.dt = [0 * u.s]
        maneuver.dm = [dm]
        maneuver.oe = [o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                           semimajor_axis=0 * u.km,
                                           eccentricity=0 * u.dimensionless_unscaled,
                                           inclination=0 * u.deg,
                                           right_ascension_of_ascending_node=0 * u.deg,
                                           argument_of_periapsis=0 * u.deg,
                                           true_anomaly=nu_1 * u.rad)]
        maneuver.fpa = [phi * u.rad]
        
        return maneuver
    
    @staticmethod
    def apse_line_rotation_from_true_anomaly(attractor: bd.Attractor,
                                             rocket_motor: RocketMotor,
                                             oe: o3d.OrbitalElements,
                                             dv : u.Quantity,
                                             fpa : u.Quantity) -> ManeuverResult:
        """
        Apse line rotation from true anomaly
        
        This maneuver computes the rotation of the line of apsides (argument of perigee change) produced by a single,
        finite‑magnitude impulse applied at a given true anomaly on an elliptical orbit. Unlike apse‑line rotation
        maneuvers defined by a desired angle between two orbits, this formulation starts from a prescribed Δv vector
        (magnitude and flight‑path angle) and determines the resulting change in the orbit’s geometry.
        
        The algorithm assumes:
        - coplanar motion around a central body
        - an impulsive burn applied at the current position of the spacecraft
        - the burn direction defined in the local orbital frame by a flight path angle relative to the local velocity
        direction


        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            oe (o3d.OrbitalElements): Orbital elements of the initial orbit
            dv (u.Quantity): Delta v
            fpa (u.Quantity): Flight path angle of delta v

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(oe.semimajor_axis.to_value(u.km),
                                      oe.eccentricity.to_value(),
                                      oe.inclination.to_value(u.deg),
                                      oe.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe.argument_of_periapsis.to_value(u.deg),
                                      oe.true_anomaly.to_value(u.deg))
        
        cm.check_angle(fpa.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 1. Orbit 1
        
        e_1: float = oe.eccentricity.to_value()
        
        h_1: float = oe.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        nu_1: float = oe.true_anomaly.to_value(u.rad)
        
        r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(nu_1))
        
        v_t_1: float = h_1 / r_1
        
        v_r_1: float = mu / h_1 * e_1 * np.sin(nu_1)
        
        # >>> 2. Delta v
        
        dv_t: float = dv.to_value(u.km / u.s) * np.cos(fpa.to_value(u.rad))
        
        dv_r: float = dv.to_value(u.km / u.s) * np.sin(fpa.to_value(u.rad))
        
        # >>> 3. Orbit 2
        
        h_2: float = h_1 + r_1 * dv_t
        
        numerator: float = (v_t_1 + dv_t) * (v_r_1 + dv_r) * v_t_1**2 * 1 / (mu / r_1)
        
        denominator: float = (v_t_1 + dv_t)**2 * e_1 * np.cos(nu_1) + (2 * v_t_1 + dv_t) * dv_t
        
        nu_2: float = np.arctan(numerator / denominator)
        
        eta: float = nu_1 - nu_2
        
        e_2: float = ((h_1 + r_1 * dv_t)**2 * e_1 * np.cos(nu_1) + (2 * h_1 + r_1 * dv_t) * r_1 * dv_t) /\
            (h_1**2 * np.cos(nu_2))
        
        r_p_2: float = h_2**2 / mu * 1 / (1 + e_2)
        
        r_a_2: float = h_2**2 / mu * 1 / (1 - e_2)
        
        # >>> 4. Result
        
        dm: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.dv = [dv]
        maneuver.dt = [0 * u.s]
        maneuver.dm = [dm]
        maneuver.oe = [o3d.OrbitalElements(specific_angular_momentum=h_2 * u.km**2 / u.s,
                                           semimajor_axis=0.5 * (r_p_2 + r_a_2) * u.km,
                                           eccentricity=e_2 * u.dimensionless_unscaled,
                                           inclination=oe.inclination,
                                           right_ascension_of_ascending_node=oe.right_ascension_of_ascending_node,
                                           argument_of_periapsis=(oe.argument_of_periapsis.to_value(u.rad) + eta) * u.rad,
                                           true_anomaly=nu_2 * u.rad)]
        maneuver.fpa = [fpa]
        
        return maneuver
    
    @staticmethod
    def chase_maneuver(attractor: bd.Attractor,
                       rocket_motor: RocketMotor,
                       oe: o3d.OrbitalElements,
                       nu_T : u.Quantity,
                       dt : time.TimeDelta) -> ManeuverResult:
        """
        Chase maneuver from Chaser C to Target T
        
        A chase maneuver is a two‑impulse orbital maneuver used to intercept a target spacecraft located at a known true
        anomaly after a specified time interval. Unlike a phasing maneuver, which adjusts the orbital period to achieve
        alignment after several revolutions, the chase maneuver computes a single transfer ellipse that brings the
        chaser to the target’s position exactly after a prescribed time of flight Delta t.
        
        This maneuver is essential for time‑critical rendezvous operations, interception trajectories, and short‑arc
        pursuit strategies.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            oe (o3d.OrbitalElements): Orbital elements of the initial orbit
            nu_T (u.Quantity): True anomaly of Target
            dt (time.TimeDelta): Delta time for the interception

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(oe.semimajor_axis.to_value(u.km),
                                      oe.eccentricity.to_value(),
                                      oe.inclination.to_value(u.deg),
                                      oe.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe.argument_of_periapsis.to_value(u.deg),
                                      oe.true_anomaly.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # >>> 1. Parameters of the chaser and target orbits
        
        h: float = oe.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        T: float = oe.calc_orbital_period(attractor=attractor).to_value(u.s)
        
        # >>> 2. Perifocal Frame state vector for Chaser C
        
        e: float = oe.eccentricity.to_value()
        
        nu_C: float = oe.true_anomaly.to_value(u.rad)
        
        r_C: float = h**2 / mu * 1 / (1 + e * np.cos(nu_C)) * np.array([np.cos(nu_C), np.sin(nu_C), 0])
        
        v_C: float = mu / h * np.array([-np.sin(nu_C), (e + np.cos(nu_C)), 0])
        
        # >>> 3. New Perifocal Frame state vector for Target T after dt
        
        t_T: float = op.OrbitalPosition.elliptical_orbit_time(nu=nu_T, T=T * u.s, e=e).to_value(u.s)
        
        t_T_new: float = t_T + dt.to_value(u.s)
        
        nu_T_new: float = op.OrbitalPosition.elliptical_orbit_true_anomaly(t=t_T_new * u.s,
                                                                           T=T * u.s,
                                                                           e=e).to_value(u.rad)
        
        r_T: float = h**2 / mu * 1 / (1 + e * np.cos(nu_T_new)) * np.array([np.cos(nu_T_new), np.sin(nu_T_new), 0])
        
        v_T: float = mu / h * np.array([-np.sin(nu_T_new), (e + np.cos(nu_T_new)), 0])
        
        # >>> 4. Lambert problem solution for the transfer from C to T in time dt
        
        r_C: u.Quantity = o3d.Orbit3D.perifocal_to_geocentric_equatorial_position_vector(orbital_elements=oe, perifocal_position=r_C * u.km)
        r_T: u.Quantity = o3d.Orbit3D.perifocal_to_geocentric_equatorial_position_vector(orbital_elements=oe, perifocal_position=r_T * u.km)
        
        if oe.inclination <= 90.0 * u.deg:
            
            direction : od.OrbitDirection = od.OrbitDirection.PROGRADE
            
        else:
            
            direction = od.OrbitDirection.RETROGRADE
        
        v_t_C, v_t_T, oe_t, nu_t_2 = od.OrbitDetermination.lambert(attractor=attractor,
                                                                   r_1=r_C,
                                                                   r_2=r_T,
                                                                   dt=dt,
                                                                   direction=direction)
        
        oe_t_2: o3d.OrbitalElements = copy.deepcopy(oe_t)
        
        oe_t_2.nu = nu_t_2
        
        # >>> 5. Result
        
        dv_1: u.Quantity = np.linalg.norm(v_t_C.to_value(u.km / u.s) - v_C) * u.km / u.s
        
        dv_2: u.Quantity = np.linalg.norm(v_T - v_t_T.to_value(u.km / u.s)) * u.km / u.s
        
        dm_1: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv_1, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm_1
        
        dm_2: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv_2, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm_2
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.dv = [dv_1, dv_2]
        maneuver.dt = [dt.to_value(u.s) * u.s]
        maneuver.dm = [dm_1, dm_2]
        maneuver.oe = [oe_t, oe_t_2]
        
        return maneuver
    
    @staticmethod
    def plane_change_maneuver_from_dihedral_angle(attractor: bd.Attractor,
                                                  rocket_motor: RocketMotor,
                                                  oe_1: o3d.OrbitalElements,
                                                  oe_2: o3d.OrbitalElements,
                                                  dihedral_angle: u.Quantity) -> ManeuverResult:
        """
        Plane change maneuver from dihedral angle between orbital planes
        
        A plane change maneuver is a single‑impulse orbital maneuver used to change the inclination and/or the right
        ascension of the ascending node (RAAN) of a spacecraft’s orbit. When two orbits have different orientations, 
        the angle between their orbital planes is called the dihedral angle.
        
        This maneuver computes the Δv required to rotate the spacecraft’s velocity vector by the dihedral angle at a
        specific point in the orbit, typically at the intersection of the two planes, to achieve the desired plane
        change. The algorithm calculates the velocity components in the initial and target orbits at the maneuver point
        and determines the required Δv to transition between the two planes while minimizing fuel consumption.
        
        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            oe_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            oe_2 (o3d.OrbitalElements): Orbital elements of the target orbit
            dihedral_angle (u.Quantity): Dihedral angle between the two orbital planes in degrees

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(oe_1.semimajor_axis.to_value(u.km),
                                      oe_1.eccentricity.to_value(),
                                      oe_1.inclination.to_value(u.deg),
                                      oe_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe_1.argument_of_periapsis.to_value(u.deg),
                                      oe_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(oe_2.semimajor_axis.to_value(u.km),
                                      oe_2.eccentricity.to_value(),
                                      oe_2.inclination.to_value(u.deg),
                                      oe_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe_2.argument_of_periapsis.to_value(u.deg),
                                      oe_2.true_anomaly.to_value(u.deg))
        
        cm.check_angle(dihedral_angle.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        dihedral_angle: float = dihedral_angle.to_value(u.rad)
        
        # >>> 1. Orbit 1
        
        e_1: float = oe_1.eccentricity.to_value()
        
        nu_1: float = oe_1.true_anomaly.to_value(u.rad)
        
        h_1: float = oe_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(nu_1))
        
        v_t_1: float = h_1 / r_1
        
        v_r_1: float = mu / h_1 * e_1 * np.sin(nu_1)
        
        # >>> 2. Orbit 2
        
        e_2: float = oe_2.eccentricity.to_value()
        
        nu_2: float = oe_2.true_anomaly.to_value(u.rad)
        
        h_2: float = oe_2.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        r_2: float = h_2**2 / mu * 1 / (1 + e_2 * np.cos(nu_2))
        
        v_t_2: float = h_2 / r_2
        
        v_r_2: float = mu / h_2 * e_2 * np.sin(nu_2)
        
        # >>> 3. Result
        
        dv: float = np.sqrt((v_r_2 - v_r_1)**2 + v_t_1**2 + v_t_2**2 - 2 * v_t_1 * v_t_2 * np.cos(dihedral_angle))
        
        dm: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv * u.km / u.s, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.dv = [dv * u.km / u.s]
        maneuver.dt = [0 * u.s]
        maneuver.dm = [dm]
        maneuver.oe = []
        
        return maneuver
    
    @staticmethod
    def plane_change_maneuver_from_raan_and_inclination(attractor: bd.Attractor,
                                                        rocket_motor: RocketMotor,
                                                        oe_1: o3d.OrbitalElements,
                                                        oe_2: o3d.OrbitalElements) -> ManeuverResult:
        """
        Plane change maneuver from RAAN and inclination differences
        
        This maneuver computes the plane change required to transition between two orbits with different orientations
        by analyzing the differences in their right ascension of the ascending node (RAAN) and inclination.
        By determining the dihedral angle between the orbital planes from these angular differences, the maneuver
        calculates the necessary Δv to achieve the desired plane change while minimizing fuel consumption.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            oe_1 (o3d.OrbitalElements): Orbital elements of the initial orbit
            oe_2 (o3d.OrbitalElements): Orbital elements of the target orbit

        Returns:
            ManeuverResult: Maneuver result [dv, dt, dm, orbital elements]
        """
        
        cm.check_attractor(attractor)
        
        cm.check_keplerian_parameters(oe_1.semimajor_axis.to_value(u.km),
                                      oe_1.eccentricity.to_value(),
                                      oe_1.inclination.to_value(u.deg),
                                      oe_1.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe_1.argument_of_periapsis.to_value(u.deg),
                                      oe_1.true_anomaly.to_value(u.deg))
        
        cm.check_keplerian_parameters(oe_2.semimajor_axis.to_value(u.km),
                                      oe_2.eccentricity.to_value(),
                                      oe_2.inclination.to_value(u.deg),
                                      oe_2.right_ascension_of_ascending_node.to_value(u.deg),
                                      oe_2.argument_of_periapsis.to_value(u.deg),
                                      oe_2.true_anomaly.to_value(u.deg))
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        inc_1: float = oe_1.inclination.to_value(u.rad)
        inc_2: float = oe_2.inclination.to_value(u.rad)
        
        raan_1: float = oe_1.right_ascension_of_ascending_node.to_value(u.rad)
        raan_2: float = oe_2.right_ascension_of_ascending_node.to_value(u.rad)
        
        argp_1: float = oe_1.argument_of_periapsis.to_value(u.rad)
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
            
            nu_1: float = u_1 - argp_1
            
            argp_2: float = nu_1 + u_2
        
        else:
            
            delta: float = np.arccos(np.cos(inc_1) * np.cos(inc_2) + np.sin(inc_1) * np.sin(inc_2) * np.cos(delta_raan))
            
            cos_u_1: float = (+np.cos(inc_2) - np.cos(delta) * np.cos(inc_1)) / (np.sin(delta) * np.sin(inc_1))
            cos_u_2: float = (-np.cos(inc_1) + np.cos(delta) * np.cos(inc_2)) / (np.sin(delta) * np.sin(inc_2))
            sin_u_1: float = np.sin(delta_raan) * np.sin(inc_2) / np.sin(delta)
            sin_u_2: float = np.sin(delta_raan) * np.sin(inc_1) / np.sin(delta)
            
            u_1: float = np.arctan2(sin_u_1, cos_u_1)
            u_2: float = np.arctan2(sin_u_2, cos_u_2)
            
            nu_1: float = 2 * np.pi - u_1 - argp_1
            
            argp_2: float = 2 * np.pi - u_2 - nu_1
        
        # >>> 3. Orbit 1 at the maneuver point
        
        e_1: float = oe_1.eccentricity.to_value()
        
        h_1: float = oe_1.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        r_1: float = h_1**2 / mu * 1 / (1 + e_1 * np.cos(nu_1))
        
        v_t_1: float = h_1 / r_1
        
        # >>> 4. Result
        
        dv: float = 2 * v_t_1 * np.sin(delta / 2)
        
        dm: u.Quantity = rocket_motor.consumed_propellant_mass(dv=dv * u.km / u.s, g_0=bd.BODIES[attractor].g_0)
        
        rocket_motor.m_sc -= dm
        
        maneuver: ManeuverResult = ManeuverResult()
        
        maneuver.dv = [dv * u.km / u.s]
        maneuver.dt = [0 * u.s]
        maneuver.dm = [dm]
        maneuver.oe = [o3d.OrbitalElements(specific_angular_momentum=oe_1.specific_angular_momentum,
                                           semimajor_axis=oe_1.semimajor_axis,
                                           eccentricity=oe_1.eccentricity,
                                           inclination=inc_2 * u.rad,
                                           right_ascension_of_ascending_node=raan_2 * u.rad,
                                           argument_of_periapsis=argp_2 * u.rad,
                                           true_anomaly=nu_1 * u.rad)]
        
        return maneuver
    
    @staticmethod
    def constant_tangential_thrust_transfer_from_time(attractor: bd.Attractor,
                                                      rocket_motor: RocketMotor,
                                                      r_0 : u.Quantity,
                                                      tof : u.Quantity) -> typing.List[u.Quantity]:
        """
        Constant tangential thrust transfer from burning time
        
        This maneuver computes the final radius and propellant mass consumed for a constant tangential thrust transfer
        given the initial radius and the time of flight. The algorithm assumes a constant tangential thrust applied over
        the specified time interval, resulting in a continuous acceleration that modifies the spacecraft’s orbit.
        
        By integrating the equations of motion under constant tangential thrust, the maneuver calculates the final
        orbital radius after the burn and the total propellant mass consumed based on the rocket motor’s parameters and
        specific impulse. 

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            r_0 (u.Quantity): Initial radius
            tof (u.Quantity): Time of flight

        Returns:
            typing.List[u.Quantity]: [final radius, propellant mass]
        """
        
        cm.check_attractor(attractor)
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        g_0: float = bd.BODIES[attractor].g_0.to_value(u.km / u.s**2)
        
        T: float = rocket_motor.T.to_value(u.N) * 1e-3 # ? Convert meters to kilometers
        I_sp: float = rocket_motor.I_sp.to_value(u.s)
        m_0: float = rocket_motor.m_sc.to_value(u.kg)
        
        r_0: float = r_0.to_value(u.km)
        tof: float = tof.to_value(u.s)
        
        # >>> 1. Target radius
        
        r: float = mu / (np.sqrt(mu / r_0) + I_sp * g_0 * np.log(1 - T * tof / (m_0 * g_0 * I_sp)))**2
        
        # >>> 2. Propellant mass
        
        m_p: float = T / (I_sp * g_0) * tof
        
        return [r * u.km, m_p * u.kg]
    
    @staticmethod
    def constant_tangential_thrust_transfer_from_radius(attractor: bd.Attractor,
                                                        rocket_motor: RocketMotor,
                                                        r_0 : u.Quantity,
                                                        r_f : u.Quantity) -> typing.List[u.Quantity]:
        """
        Constant tangential thrust transfer from final radius
        
        This maneuver computes the time of flight and propellant mass consumed for a constant tangential thrust transfer
        given the initial and final radii. The algorithm assumes a constant tangential thrust applied over the transfer,
        resulting in a continuous acceleration that modifies the spacecraft’s orbit.
        
        By integrating the equations of motion under constant tangential thrust, the maneuver calculates the time of
        flight required to reach the final radius and the total propellant mass consumed based on the rocket motor’s
        parameters and specific impulse.

        Args:
            attractor (bd.Attractor): Main attractor
            rocket_motor (RocketMotor): Rocket motor parameters
            r_0 (u.Quantity): Initial radius
            r_f (u.Quantity): Final radius

        Returns:
            list: [time of flight, propellant mass]
        """
        
        cm.check_attractor(attractor)
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        g_0: float = bd.BODIES[attractor].g_0.to_value(u.km / u.s**2)
        
        T: float = rocket_motor.T.to_value(u.N) * 1e-3 # ? Convert meters to kilometers
        I_sp: float = rocket_motor.I_sp.to_value(u.s)
        m_0: float = rocket_motor.m_sc.to_value(u.kg)
        
        r_0: float = r_0.to_value(u.km)
        r_f: float = r_f.to_value(u.km)
        
        # >>> 1. Flight time
        
        tof: float = m_0 * g_0 * I_sp / T * (1 - np.exp(1 / (I_sp * g_0) * (np.sqrt(mu / r_f) - np.sqrt(mu / r_0))))
        
        # >>> 2. Propellant mass
        
        m_p: float = T / (I_sp * g_0) * tof
        
        return [tof * u.s, m_p * u.kg]
    
    @staticmethod
    def non_impulsive_maneuver(attractor: bd.Attractor,
                               rocket_motor: RocketMotor,
                               r_0: u.Quantity,
                               v_0: u.Quantity,
                               t_0: u.Quantity,
                               dt: u.Quantity,
                               r_f: u.Quantity,
                               semi_major_axis_target: bool = False,
                               tol: float = 1e-8) -> NonImpulsiveManeuverResult:
        """
        Non impulsive maneuver
        
        

        Args:
            t_0 (float): Initial burning time guess
            dt (float): Time step for burning time calculation
            r_0 (np.ndarray): Initial position vector
            v_0 (np.ndarray): Initial velocity vector
            r_f (np.ndarray): Final position vector
            m_0 (float): Initial mass
            T (float): Thrust
            I_sp (float): Specific impulse
            semiMajorAxis (bool, optional): True for semi-major axis target - False for position vector norm target. Defaults to False.
            tol (float, optional): Tolerance. Defaults to 1e-8.

        Returns:
            list: [burning time, final state vector]
        """
        
        if t_0.to_value(u.s) <= 0: raise ValueError('Initial burning time guess must be greater than zero.')
        
        t_burn: time.TimeDelta = time.TimeDelta(t_0.to_value(u.s) * u.s)
        
        prev_epsilon: float = 0.0
        
        maneuver: NonImpulsiveManeuverResult = NonImpulsiveManeuverResult()
        
        while True:
            
            # >>> 1. Integrate
            
            orbit: tbp.Orbit = tbp.Orbit()
            
            orbit.from_cartesian(attractor=attractor, position=r_0, velocity=v_0,
                                 epoch=time.Time('2026-01-01T00:00:00', format='isot', scale='utc'))
            
            result: tbp.Result = orbit.propagate_for(delta=t_burn, rocket_motor=rocket_motor)
            
            if not result.success: raise RuntimeError('Integration failed.')
            
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
                
                epsilon: float = oe.semimajor_axis.to_value(u.km) - np.linalg.norm(r_f.to_value(u.km))
                
                maneuver.r_x = r[0]
                maneuver.r_y = r[1]
                maneuver.r_z = r[2]
                maneuver.v_x = v[0]
                maneuver.v_y = v[1]
                maneuver.v_z = v[2]
                maneuver.m_sc = m_sc
                
            else:
            
                delta_theta: u.Quantity = u.Quantity(180.0, u.deg) - oe.true_anomaly
            
                l_r_f, l_v_f = lc.LagrangeCoefficients.propagate_of_angle(attractor=attractor,
                                                                          r_0=r,
                                                                          v_0=v,
                                                                          delta=delta_theta)
            
                epsilon: float = np.linalg.norm(l_r_f.to_value(u.km)) - np.linalg.norm(r_f.to_value(u.km))
                
                maneuver.r_x = l_r_f[0]
                maneuver.r_y = l_r_f[1]
                maneuver.r_z = l_r_f[2]
                maneuver.v_x = l_v_f[0]
                maneuver.v_y = l_v_f[1]
                maneuver.v_z = l_v_f[2]
                maneuver.m_sc = m_sc
            
            # >>> 4. Check error
            
            if np.abs(epsilon) < tol: break
            
            # >>> 5. Update time interval
            
            if not np.isclose(prev_epsilon, 0.0, rtol=1e-09, atol=1e-09) and prev_epsilon * epsilon < 0:
                
                dt = dt / 2.0
            
            if epsilon < 0:
                
                t_burn += time.TimeDelta(dt.to_value(u.s) * u.s)
                
            else:
                
                t_burn -= time.TimeDelta(dt.to_value(u.s) * u.s)
            
            maneuver.t_burn = t_burn.to(u.s)
                
            # >>> 6. Update error
            
            prev_epsilon = epsilon
        
        return maneuver