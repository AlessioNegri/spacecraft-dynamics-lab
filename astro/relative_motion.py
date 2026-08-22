"""
Relative Motion

Implementation of relative motion algorithms.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 7: Relative Motion and Rendezvous

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 8: Relative Motion and Orbital Rendezvous

- Ulrich Walter, "Astronautics - The Physics of Space Flight"
    - Chapter 8: Orbital Maneuvering
"""

import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.integrate as ode
import typing

import astro.bodies as bodies
import astro.common as common
import astro.orbit_3d as o3d
import astro.orbital_position as op
import astro.lagrange_coefficients as lc
import astro.orbit_determination as od

from astro.enums import ClosingApproachStrategy, ClosingApproachTrajectory
from astro.models.results import ResultRM
from astro.models.orbital_elements import OrbitalElements

class RelativeMotion():
    """Relative Motion"""
    
    def __init__(self):
        """Constructor"""
        
        self.ready: bool = False
        
        self.attractor: bodies.Body = bodies.get_body(bodies.Attractor.EARTH)
        
        self.position: np.ndarray = np.zeros(3)
        
        self.velocity: np.ndarray = np.zeros(3)
        
        self.relative_position: np.ndarray = np.zeros(3)
        
        self.relative_velocity: np.ndarray = np.zeros(3)
    
    # --- STATIC ---
    
    @staticmethod
    def lvlh_kinematics(attractor: bodies.Attractor,
                        orbital_elements_target: OrbitalElements,
                        orbital_elements_chaser: OrbitalElements) -> typing.List[u.Quantity]:
        """        
        Given the state vectors (`r_target`, `v_target`) of the **target spacecraft** and (`r_chaser`, `v_chaser`) of
        the **chaser spacecraft**, find the position, velocity, and acceleration of Chaser relative to Target along the
        **Local Vertical Local Horizontal** (*LVLH*) axes attached to the Target.

        Args:
            attractor (bodies.Attractor): Main attractor
            orbital_elements_target (OrbitalElements): Target orbital elements
            orbital_elements_chaser (OrbitalElements): Chaser orbital elements
            
        Returns:
            typing.List[u.Quantity]: [r_rel_lvlh, v_rel_lvlh, a_rel_lvlh, omega_lvlh]
        """
        
        r_target, v_target = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor,
                                                                orbital_elements=orbital_elements_target)
        
        r_chaser, v_chaser = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor,
                                                                orbital_elements=orbital_elements_chaser)
        
        common.check_attractor(attractor)
        
        common.check_position_vector(r_target)
        common.check_position_vector(r_chaser)
        
        common.check_velocity_vector(v_target)
        common.check_velocity_vector(v_chaser)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        r_target: np.ndarray = r_target.to_value(u.km)
        r_chaser: np.ndarray = r_chaser.to_value(u.km)
        
        v_target: np.ndarray = v_target.to_value(u.km / u.s)
        v_chaser: np.ndarray = v_chaser.to_value(u.km / u.s)
        
        # >>> 1. Angular momentum of the Target
        
        h_target: np.ndarray = np.cross(r_target, v_target)
        
        # >>> 2. Unit vectors of the comoving frame of the target (x)
        
        i: np.ndarray = r_target / np.linalg.norm(r_target)
        k: np.ndarray = h_target / np.linalg.norm(h_target)
        j: np.ndarray = np.cross(k, i)
        
        # >>> 3. Orthogonal trasformation matrix Q_Xx (direction cosines matrix)
        
        dcm: np.ndarray = np.vstack((i, j, k))
        
        # >>> 4. Angular velocity Ω and acceleration dΩ / dt of the comoving frame of the target
        
        omega: np.ndarray = h_target / np.linalg.norm(r_target)**2
        
        d_omega_dt: np.ndarray = - 2 * np.dot(v_target, r_target) / np.linalg.norm(r_target)**2 * omega
        
        # >>> 5. Absolute accelerations of Target and Chase
        
        a_target: np.ndarray = - mu / np.linalg.norm(r_target)**3 * r_target
        a_chaser: np.ndarray = - mu / np.linalg.norm(r_chaser)**3 * r_chaser
        
        # >>> 6. Relative position in Geocentric Equatioral Frame (X)
        
        r_rel: np.ndarray = r_chaser - r_target
        
        # >>> 7. Relative velocity in Geocentric Equatioral Frame (X)
        
        v_rel: np.ndarray = v_chaser - v_target - np.cross(omega, r_rel)
        
        # >>> 8. Relative acceleration in Geocentric Equatioral Frame (X)
        
        a_rel: np.ndarray = a_chaser - a_target - np.cross(d_omega_dt, r_rel) - \
            np.cross(omega, np.cross(omega, r_rel)) - 2 * np.cross(omega, v_rel)
        
        # >>> 9. LVLH kinematics (x)
        
        r_rel_lvlh: np.ndarray = np.matmul(dcm, r_rel)
        v_rel_lvlh: np.ndarray = np.matmul(dcm, v_rel)
        a_rel_lvlh: np.ndarray = np.matmul(dcm, a_rel)
        omega_lvlh: np.ndarray = np.matmul(dcm, omega)
        
        return [r_rel_lvlh * u.km, v_rel_lvlh * u.km / u.s, a_rel_lvlh * u.km / u.s**2, omega_lvlh * u.rad / u.s]
    
    @staticmethod
    def geocentric_equatorial_kinematics(position_target: u.Quantity,
                                         velocity_target: u.Quantity,
                                         position_rel_lvlh: u.Quantity,
                                         velocity_rel_lvlh: u.Quantity) -> typing.List[u.Quantity]:
        """
        Given the state vectors (`position_target`, `velocity_target`) of the **target spacecraft** and
        (`position_rel_lvlh`, `velocity_rel_lvlh`) of the **chaser spacecraft** relative to Target along the
        **Local Vertical Local Horizontal** (*LVLH*) axes attached to the Target, find the position and velocity of
        Chaser in the Geocentric Equatorial frame.

        Args:
            position_target (np.ndarray): Target position vector
            velocity_target (np.ndarray): Target velocity vector
            position_rel_lvlh (u.Quantity): Relative position vector
            velocity_rel_lvlh (u.Quantity): Relative velocity vector
            
        Returns:
            typing.List[u.Quantity]: [r_chaser, v_chaser]
        """
        
        common.check_position_vector(position_target)
        common.check_position_vector(position_rel_lvlh)
        
        common.check_velocity_vector(velocity_target)
        common.check_velocity_vector(velocity_rel_lvlh)
        
        r_target: np.ndarray = position_target.to_value(u.km)
        r_rel_lvlh: np.ndarray = position_rel_lvlh.to_value(u.km)
        
        v_target: np.ndarray = velocity_target.to_value(u.km / u.s)
        v_rel_lvlh: np.ndarray = velocity_rel_lvlh.to_value(u.km / u.s)
        
        # >>> 1. Angular momentum of the Target
        
        h_target: np.ndarray = np.cross(r_target, v_target)
        
        # >>> 2. Unit vectors of the comoving frame of the target (x)
        
        i: np.ndarray = r_target / np.linalg.norm(r_target)
        k: np.ndarray = h_target / np.linalg.norm(h_target)
        j: np.ndarray = np.cross(k, i)
        
        # >>> 3. Orthogonal trasformation matrix Q_Xx (direction cosines matrix)
        
        dcm: np.ndarray = np.vstack((i, j, k))
        
        # >>> 4. Relative position-velocity in Geocentric Equatioral Frame (X)
        
        r_rel: np.ndarray = np.matmul(np.linalg.inv(dcm), r_rel_lvlh)
        v_rel: np.ndarray = np.matmul(np.linalg.inv(dcm), v_rel_lvlh)
        
        # >>> 5. Angular velocity Ω of the comoving frame of the target
        
        omega: np.ndarray = h_target / np.linalg.norm(r_target)**2
        
        # >>> 6. Chaser position in Geocentric Equatioral Frame (X)
        
        r_chaser: np.ndarray  = r_target + r_rel
        
        # >>> 7. Chaser velocity in Geocentric Equatioral Frame (X)
        
        v_chaser: np.ndarray = v_target + v_rel + np.cross(omega, r_rel)
        
        return [r_chaser * u.km, v_chaser * u.km / u.s]
    
    @staticmethod
    def simulate_lvlh_kinematics(attractor: bodies.Attractor,
                                 orbital_elements_target: OrbitalElements,
                                 orbital_elements_chaser: OrbitalElements,
                                 target_period_multiplier: int = 60,
                                 points_number: int = 1000) -> list:
        """
        Simulate the motion of the Target w.r.t. the Chaser in the LVLH frame

        Args:
            attractor (bodies.Attractor): Main attractor
            orbital_elements_target (OrbitalElements): Target orbital elements
            orbital_elements_chaser (OrbitalElements): Chaser orbital elements
            target_period_multiplier (int, optional): Multiple of the Target period. Defaults to 60.
            points_number (int, optional): Number of points to simulate. Defaults to 1000.
        """
        
        if not isinstance(target_period_multiplier, int): raise TypeError("'target_period_multiplier' must be of type 'int'")
        
        if not isinstance(points_number, int): raise TypeError("'points_number' must be of type 'int'")
        
        if target_period_multiplier < 0: raise ValueError("'target_period_multiplier' must be positive")
        
        if points_number < 0: raise ValueError("'points_number' must be positive")
        
        # >>> 1. Calculate state vectors from orbital elements
        
        orbital_elements_target.calc_semimajor_axis(attractor=attractor)
        
        orbital_elements_chaser.calc_semimajor_axis(attractor=attractor)
        
        r_target, v_target = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor,
                                                                orbital_elements=orbital_elements_target)
        
        r_chaser, v_chaser = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor,
                                                                orbital_elements=orbital_elements_chaser)
        
        common.check_attractor(attractor)
        
        common.check_position_vector(r_target)
        common.check_position_vector(r_chaser)
        
        common.check_velocity_vector(v_target)
        common.check_velocity_vector(v_chaser)
        
        # >>> 2. Target period
        
        t_target: u.Quantity = orbital_elements_target.calc_orbital_period(attractor=attractor)
        
        # >>> 3. Target initial time
        
        t_0: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=orbital_elements_target.true_anomaly,
                                                                   period=t_target,
                                                                   eccentricity=orbital_elements_target.eccentricity)
        
        # >>> 4. Final time
        
        t_f: u.Quantity = t_0 + target_period_multiplier * t_target
        
        # >>> 5. Time step
        
        dt: float = (t_f.to_value(u.s) - t_0.to_value(u.s)) / float(points_number)
        
        # >>> 6. Cycle
        
        times: np.ndarray = np.linspace(t_0, t_f, points_number)
        
        x: list = []
        y: list = []
        z: list = []
        
        for _ in times:
            
            # >>> a. LVLH quantities
        
            r_rel_lvlh, _, _, _ = RelativeMotion.lvlh_kinematics(attractor=attractor,
                                                                 orbital_elements_target=orbital_elements_target,
                                                                 orbital_elements_chaser=orbital_elements_chaser)
            
            x.append(r_rel_lvlh[0].to_value(u.km))
            y.append(r_rel_lvlh[1].to_value(u.km))
            z.append(r_rel_lvlh[2].to_value(u.km))
            
            # >>> b. Update Target-Chaser vectors
            
            r_target, v_target = lc.LagrangeCoefficients.propagate_position_velocity(attractor=attractor,
                                                                                     initial_position=r_target,
                                                                                     initial_velocity=v_target,
                                                                                     delta_time=time.TimeDelta(dt * u.s))
            
            r_chaser, v_chaser = lc.LagrangeCoefficients.propagate_position_velocity(attractor=attractor,
                                                                                     initial_position=r_chaser,
                                                                                     initial_velocity=v_chaser,
                                                                                     delta_time=time.TimeDelta(dt * u.s))
            
            # >>> c. Update Target-Chaser orbital elements
            
            orbital_elements_target = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor,
                                                                         position=r_target,
                                                                         velocity=v_target)
            
            orbital_elements_chaser = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor,
                                                                         position=r_chaser,
                                                                         velocity=v_chaser)
        
        # >>> 6. Result
        
        return [x, y, z]
    
    @staticmethod
    def clohessy_wiltshire_matrices(mean_motion: u.Quantity, final_time: u.Quantity) -> list:
        """
        Clohessy-Wiltshire matrices
        
        δr(t) = Φ_rr * δr_0 + Φ_rv * δv_0
        
        δv(t) = Φ_vr * δr_0 + Φ_vv * δv_0

        Args:
            mean_motion (u.Quantity): Target orbit mean motion
            final_time (u.Quantity): Final time

        Returns:
            list: [phi_rr, phi_rv, phi_vr, phi_vv]
        """
        
        n: float = mean_motion.to_value(u.rad / u.s)
        t: float = final_time.to_value(u.s)
        
        phi_rr: np.ndarray = np.array(
            [
                [ 4 - 3 * np.cos(n * t)       , 0 , 0             ],
                [ 6 * (np.sin(n * t) - n * t) , 1 , 0             ],
                [ 0                           , 0 , np.cos(n * t) ]
            ])
        
        phi_rv: np.ndarray = np.array(
            [
                [ 1 / n * np.sin(n * t)       , 2 / n * (1 - np.cos(n * t))             , 0                     ],
                [ 2 / n * (np.cos(n * t) - 1) , 1 / n * (4 * np.sin(n * t) - 3 * n * t) , 0                     ],
                [ 0                           , 0                                       , 1 / n * np.sin(n * t) ]
            ])
        
        phi_vr: np.ndarray = np.array(
            [
                [ 3 * n * np.sin(n * t)       , 0 , 0                   ],
                [ 6 * n * (np.cos(n * t) - 1) , 0 , 0                   ],
                [ 0                           , 0 , - n * np.sin(n * t) ]
            ])
        
        phi_vv: np.ndarray = np.array(
            [
                [ np.cos(n * t)       , 2 * np.sin(n * t)     , 0             ],
                [ - 2 * np.sin(n * t) , 4 * np.cos(n * t) - 3 , 0             ],
                [ 0                   , 0                     , np.cos(n * t) ]
            ])
        
        return [phi_rr, phi_rv, phi_vr, phi_vv]
    
    @staticmethod
    def clohessy_wiltshire_equations(relative_position_0: u.Quantity,
                                     relative_velocity_0: u.Quantity,
                                     mean_motion: u.Quantity,
                                     final_time: u.Quantity) -> typing.List[u.Quantity]:
        """
        Clohessy-Wiltshire equations
        
        δr(t) = Φ_rr * δr_0 + Φ_rv * δv_0
        
        δv(t) = Φ_vr * δr_0 + Φ_vv * δv_0

        Args:
            relative_position_0 (u.Quantity): Initial relative position vector
            dv_0 (u.Quantity): Initial relative velocity vector
            mean_motion (u.Quantity): Target orbit mean motion
            final_time (u.Quantity): Final time

        Returns:
            typing.List[u.Quantity]: [dr, dv]
        """
        
        common.check_position_vector(position=relative_position_0)
        
        common.check_velocity_vector(velocity=relative_velocity_0)
        
        dr_0: np.ndarray = relative_position_0.to_value(u.km)
        
        dv_0: np.ndarray = relative_velocity_0.to_value(u.km / u.s)
        
        phi_rr, phi_rv, phi_vr, phi_vv = RelativeMotion.clohessy_wiltshire_matrices(mean_motion=mean_motion,
                                                                                    final_time=final_time)
        
        dr: np.ndarray = np.matmul(phi_rr, dr_0) + np.matmul(phi_rv, dv_0)
        dv: np.ndarray = np.matmul(phi_vr, dr_0) + np.matmul(phi_vv, dv_0)
        
        return [dr * u.km, dv * u.km / u.s]
    
    @staticmethod
    def two_impulsive_rendezvous_maneuver(attractor: bodies.Attractor,
                                          orbital_elements_target: OrbitalElements,
                                          orbital_elements_chaser: OrbitalElements,
                                          maneuver_time: u.Quantity) -> typing.List[u.Quantity]:
        """
        Two-Impulse Rendezvous maneuver
        
        The first impulse is done at initial position to move closer to the target. The second impulse is done once the
        target is reached to nullify the relative velocity.

        Args:
            attractor (bodies.Attractor): Main attractor
            orbital_elements_target (OrbitalElements): Target orbital elements
            oe_chaser (OrbitalElements): Chaser orbital elements
            maneuver_time (u.Quantity): Maneuver time

        Returns:
            typing.List[u.Quantity]: [dv_tot, dx, dy, dz]
        """
        
        if orbital_elements_target.eccentricity != 0:
            
            print("Target orbit must be a circle")
        
            return [0 * u.km / u.s, np.zeros(1000) * u.km, np.zeros(1000) * u.km, np.zeros(1000) * u.km]
        
        # >>> 1. LVLH kinematics at the beginning of the rendezvous
        
        dr_0, dv_0_minus, _, omega = RelativeMotion.lvlh_kinematics(attractor=attractor,
                                                                    orbital_elements_target=orbital_elements_target,
                                                                    orbital_elements_chaser=orbital_elements_chaser)
        
        n: u.Quantity = np.linalg.norm(omega.to_value(u.rad / u.s)) * u.rad / u.s # ? Mean motion
        
        # >>> 2. Clohessy-Wiltshire solution for the maneuver (when reached the target => dr = 0, dv = 0)
        
        phi_rr, phi_rv, _, _ = RelativeMotion.clohessy_wiltshire_matrices(mean_motion=n, final_time=maneuver_time)
        
        dv_0_plus: np.ndarray = - np.matmul(np.matmul(np.linalg.inv(phi_rv), phi_rr), dr_0.to_value(u.km))
        
        _, dv_f_minus = RelativeMotion.clohessy_wiltshire_equations(relative_position_0=dr_0,
                                                                    relative_velocity_0=dv_0_plus * u.km / u.s,
                                                                    mean_motion=n,
                                                                    final_time=maneuver_time)
        
        dv_f_plus: np.ndarray = np.zeros(shape=(3))
        
        # >>> 3. Maneuver result
        
        dv_tot: float = np.linalg.norm(dv_0_plus - dv_0_minus.to_value(u.km / u.s)) + \
                        np.linalg.norm(dv_f_plus - dv_f_minus.to_value(u.km / u.s))
        
        dx: list = []
        dy: list = []
        dz: list = []
        
        # * Iterate on the maneuver time to obtain the rendezvous trajectory
        
        for t in np.linspace(0, maneuver_time.to_value(u.s), 1000):
            
            dr, _ = RelativeMotion.clohessy_wiltshire_equations(relative_position_0=dr_0,
                                                                relative_velocity_0=dv_0_plus * u.km / u.s,
                                                                mean_motion=n,
                                                                final_time=t * u.s)
            
            dx.append(dr[0].to_value(u.km))
            dy.append(dr[1].to_value(u.km))
            dz.append(dr[2].to_value(u.km))
        
        return [dv_tot * u.km / u.s, np.array(dx) * u.km, np.array(dy) * u.km, np.array(dz) * u.km]
    
    @staticmethod
    def circular_orbit_rendezvous(relative_position_0: u.Quantity,
                                  mean_motion: u.Quantity,
                                  final_time: u.Quantity) -> typing.List[u.Quantity]:
        """
        Circular orbit rendezvous maneuver
        
        If at time t0 = 0 a S/C is at an initial point r0 = (dx0 dy0 dz0) find the initial velocity v0 (dx0_dt dy0_dt
        dz0_dt) to meet after time t a given target point r (dx dy dz) = (0 0 0).
        
        The solution is valid for (n * t)**2 << 1 => t < 0.02 * T_orbit.

        Args:
            relative_position_0 (u.Quantity): Initial relative position vector
            mean_motion (u.Quantity): Mean motion of the target orbit
            final_time (u.Quantity): Final time of the rendezvous maneuver

        Returns:
            typing.List[u.Quantity]: [dx0_dt, dy0_dt, dz0_dt]
        """
        
        common.check_position_vector(position=relative_position_0)
        
        dx0: float = relative_position_0[0].to_value(u.km)
        dy0: float = relative_position_0[1].to_value(u.km)
        dz0: float = relative_position_0[2].to_value(u.km)
        
        n: float = mean_motion.to_value(u.rad / u.s)
        t: float = final_time.to_value(u.s)

        dx0_dt: float = - dx0 / t + n * dy0
        dy0_dt: float = - dy0 / t - n * dx0
        dz0_dt: float = - dz0 / t
        
        return [dx0_dt * u.km / u.s, dy0_dt * u.km / u.s, dz0_dt * u.km / u.s]
    
    @staticmethod
    def launch_phase(timestamp: time.Time,
                     launch_site_latitude: u.Quantity,
                     launch_site_longitude: u.Quantity,
                     target_inclination: u.Quantity,
                     target_right_ascension_ascending_node: u.Quantity) -> typing.List[u.Quantity]:
        """
        Calculate the launch phase for a given timestamp and orbital parameters.
        
        The launch phase comprises the injection of the chaser (interceptor) into the orbital plane of the target, as
        well as achieving stable orbital conditions. To directly meet the plane of the target, the interceptor must be
        launched inside a narrow launch window.

        Args:
            timestamp (time.Time): Timestamp
            launch_site_latitude (u.Quantity): Latitude of the launch site
            launch_site_longitude (u.Quantity): Longitude of the launch site
            target_inclination (u.Quantity): Inclination of the target orbit
            target_right_ascension_ascending_node (u.Quantity): Right ascension of the ascending node of the target orbit

        Returns:
            typing.List[u.Quantity]: [T_UT_ascending_pass, T_UT_descending_pass]
        """
        
        common.check_time(timestamp)
        common.check_angle(launch_site_latitude)
        common.check_angle(launch_site_longitude)
        common.check_angle(target_inclination)
        common.check_angle(target_right_ascension_ascending_node)
        
        beta: float = launch_site_latitude.to_value(u.rad)
        lambda_: float = launch_site_longitude.to_value(u.rad)
        inc: float = target_inclination.to_value(u.rad)
        raan: float = target_right_ascension_ascending_node.to_value(u.rad)
        
        # >>> 1. Azimuth
        
        if (inc < abs(beta)):
            
            print("Error: target_inclination < ||launch_site_latitude||")
        
            return [0 * u.deg, 0 * u.deg]
        
        if (inc > np.pi - abs(beta)):
            
            print("Error: target_inclination > 180° - ||launch_site_latitude||")
            
            return [0 * u.deg, 0 * u.deg]
        
        azimuth_ascending_pass: u.Quantity = np.arcsin(np.cos(inc) / np.cos(beta)) * u.rad
        
        azimuth_descending_pass: u.Quantity = (np.pi - np.arcsin(np.cos(inc) / np.cos(beta))) * u.rad
        
        # >>> 2. Universal Time of launch / in-plane time / launch time
        
        omega: float = bodies.BODIES[bodies.Attractor.EARTH].omega.to_value(u.rad / u.s) # ? Earth’s sidereal rotation rate
        
        theta: float = od.OrbitDetermination.local_sidereal_time(timestamp=timestamp, longitude=lambda_ * u.rad).to_value(u.rad)
        
        # ! θ = θ_G_MST_0 + λ
        
        lambda_u: float = np.arccos(np.cos(azimuth_ascending_pass.to_value(u.rad)) / np.sin(inc))
        
        T_UT_ascending_pass = (raan + lambda_u - theta) / omega
        
        lambda_u = np.arccos(np.cos(azimuth_descending_pass.to_value(u.rad)) / np.sin(inc))
        
        T_UT_descending_pass = (raan + lambda_u - theta) / omega
        
        return [T_UT_ascending_pass * u.s, T_UT_descending_pass * u.s]
    
    @staticmethod
    def phasing(semimajor_axis_chaser: u.Quantity,
                semimajor_axis_target: u.Quantity) -> typing.List[u.Quantity]:
        """
        After successful completion of the launch phase, the interceptor spacecraft achieves a stable orbit within the
        same plane as the target. The two orbits are thus coplanar and typically near circular.
        
        However, the target might be anywhere on its orbit. Therefore, the first part of the target rendezvous, the
        so-called far range rendezvous, requires first a reduction in the distance to the target, until it can be
        acquired by the sensors of the interceptor, and then a transfer to a stable holding point on the trailing side
        of the target.
        
        This first part of far range rendezvous phase is called **phasing** because it is to reduce the so-called
        (orbital) phase angle θ, which is the difference in true anomaly as measured in the flight direction from the
        target to the interceptor.
        
        Notes:
        -
        - Assume small differences in the semi-major axes
        - a_chaser < a_target
        
        Args:
            semimajor_axis_chaser (u.Quantity): Semimajor axis of the chaser orbit
            semimajor_axis_target (u.Quantity): Semimajor axis of the target orbit

        Returns:
            typing.List[u.Quantity]: [dtheta, dx]
        """
        
        a_C: float = semimajor_axis_chaser.to_value(u.km)
        a_T: float = semimajor_axis_target.to_value(u.km)
        
        # >>> 1. Phase angle reduction per orbit revolution
        
        dtheta: float = 3 * np.pi * (a_C - a_T) / a_T
        
        # >>> 2. Closing distance
        
        dx: float = dtheta * a_T
        
        return [np.abs(dtheta) * u.rad, np.abs(dx) * u.km]

    @staticmethod
    def homing_phase(semimajor_axis_chaser: u.Quantity,
                     semimajor_axis_target: u.Quantity) -> typing.List[u.Quantity]:
        """
        The objective of the homing transfer, the second part of the far range rendezvous, is to transfer the
        interceptor to a stable holding and aiming point in the vicinity of the target. A prerequisite of the transfer
        is that the target must be acquired by the relative navigation sensors of the interceptor.
        
        The homing transfer is a classical Hohmann transfer, where the orbits have a radial distance of typically only
        about 10 km. Owing to this, the phase angle at the beginning of the Hohmann maneuver is practically zero while
        its complement to 180°, the so-called lead angle, is alpha_L = 180 - theta ≈ 180°.
        
        Let θ_i be the initial phase angle and let θ_f be the final phase angle behind the target.

        Args:
            semimajor_axis_chaser (u.Quantity): Semimajor axis of the chaser orbit
            semimajor_axis_target (u.Quantity): Semimajor axis of the target orbit

        Returns:
            typing.List[u.Quantity]: [theta_i, dv]
        """
        
        a_C: float = semimajor_axis_chaser.to_value(u.km)
        a_T: float = semimajor_axis_target.to_value(u.km)
        
        mu: float = bodies.BODIES[bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
        
        v_T: float = np.sqrt(mu / a_T) # ? Target orbit velocity
        
        r: float = (a_C - a_T) / a_T # ? Relative difference in semi-major axes
        
        theta_f: float = np.rad2deg(np.abs(r)) # ? Final phase angle behind the target
        
        theta_i: float = theta_f - 135 * r # ? Initial phase angle (rad)
        
        dv: float = v_T * (np.sqrt(1 - r) - 1) # ? Delta-v for the Hohmann transfer
        
        return [theta_i * u.deg, dv * u.km / u.s]
    
    @staticmethod
    def closing_phase(semimajor_axis_target: u.Quantity,
                      distance: u.Quantity,
                      strategy: ClosingApproachStrategy,
                      trajectory: ClosingApproachTrajectory = ClosingApproachTrajectory.ELLIPTIC,
                      cycloidal_revolutions: int = 1,
                      initial_velocity: u.Quantity = 0 * u.km / u.s) -> u.Quantity:
        """
        The target now is within range of the interceptor sensors and thus relative navigation can commence. This
        station-keeping point is essential to assess the situation and plan the upcoming closing maneuver.
        
        The closing maneuver depends on the type of final approach (R-bar or V-bar) and we ingress the Approach
        Ellipsoid.
        
        Args:
            semimajor_axis_target (u.Quantity): Semimajor axis of the target orbit
            distance (u.Quantity): Distance to the target
            strategy (ClosingApproachStrategy): Closing approach strategy
            trajectory (ClosingApproachTrajectory, optional): Closing approach trajectory. Defaults to ClosingApproachTrajectory.ELLIPTIC.
            cycloidal_revolutions (int, optional): Number of cycloidal revolutions. Defaults to 1.
            initial_velocity (u.Quantity, optional): Initial velocity. Defaults to 0 * u.km / u.s.

        Returns:
            u.Quantity: Delta-v for the closing maneuver
        """
        
        a: float = semimajor_axis_target.to_value(u.km)
        v0: float = initial_velocity.to_value(u.km / u.s)
        
        mu: float = bodies.BODIES[bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
        
        n: float = np.sqrt(mu / a**3) # ? Target orbit mean motion
        
        dv: float
        
        if strategy == ClosingApproachStrategy.V_BAR_POS or strategy == ClosingApproachStrategy.V_BAR_NEG:
            
            dx: float = distance.to_value(u.km)
            
            if trajectory == ClosingApproachTrajectory.ELLIPTIC: # ? Safer
                
                dv = 2 * dx / 4 * n
            
            elif trajectory == ClosingApproachTrajectory.CYCLOIDAL: # ? Efficient
                
                dv = 2 * dx / (6 * np.pi * cycloidal_revolutions) * n
        
        elif strategy == ClosingApproachStrategy.R_BAR_POS or strategy == ClosingApproachStrategy.R_BAR_NEG:
            
            dr: float = distance.to_value(u.km)
            
            dv_i: float = dr / 4 * n
            
            dv_f: float = - 5 * v0
            
            dv = np.abs(dv_i) + np.abs(dv_f)
        
        return (dv * u.km / u.s).to(u.m / u.s)
    
    @staticmethod
    def final_approach(semimajor_axis_target: u.Quantity,
                       distance: u.Quantity,
                       time: u.Quantity,
                       strategy: ClosingApproachStrategy) -> u.Quantity:
        """
        In the final approach (a.k.a. proximity operations or terminal phase), the trajectories now are more or less
        straight to directly intercept the target and therefore are on “collision course” with it. The interceptor is
        now on the waiting point just outside of the Keep-Out Sphere (a.k.a. KOS).
        
        The final approach ends at a distance of a few meters upfront.

        Args:
            semimajor_axis_target (u.Quantity): Semimajor axis of the target orbit
            distance (u.Quantity): Distance to the target
            time (u.Quantity): Time to reach the waiting point
            strategy (ClosingApproachStrategy): Closing approach strategy

        Returns:
            u.Quantity: Delta-v for the final approach maneuver
        """
        
        a: float = semimajor_axis_target.to_value(u.km)
        t: float = time.to_value(u.s)
        
        mu: float = bodies.BODIES[bodies.Attractor.EARTH].mu.to_value(u.km**3 / u.s**2)
        
        n: float = np.sqrt(mu / a**3) # ? Target orbit mean motion
        
        dv: float
        
        if strategy == ClosingApproachStrategy.V_BAR_POS or strategy == ClosingApproachStrategy.V_BAR_NEG:
            
            dx: float = distance.to_value(u.km)
            
            dv = 2 * (dx / t + n * dx)
        
        elif strategy == ClosingApproachStrategy.R_BAR_POS or strategy == ClosingApproachStrategy.R_BAR_NEG:
            
            dz: float = distance.to_value(u.km)
            
            dv = 2 * (dz / t + n * dz)
        
        return (dv * u.km / u.s).to(u.m / u.s)

    # --- PUBLIC ---
    
    def init(self,
             attractor: bodies.Attractor,
             position: u.Quantity,
             velocity: u.Quantity,
             relative_position: u.Quantity,
             relative_velocity: u.Quantity) -> None:
        """
        Initialize the parameters for the propagation

        Args:
            attractor (bodies.Attractor): Main attractor
            r (u.Quantity): Position vector
            v (u.Quantity): Velocity vector
            dr (u.Quantity): Relative position vector
            dv (u.Quantity): Relative velocity vector
        """
        
        common.check_attractor(attractor)
        
        common.check_position_vector(position.to_value(u.km))
        
        common.check_position_vector(relative_position.to_value(u.km))
        
        common.check_velocity_vector(velocity.to_value(u.km / u.s))
        
        common.check_velocity_vector(relative_velocity.to_value(u.km / u.s))
        
        self.ready              = True
        self.attractor          = bodies.BODIES[attractor]
        self.position           = position.to(u.km).to_value()
        self.velocity           = velocity.to(u.km / u.s).to_value()
        self.relative_position  = relative_position.to(u.km).to_value()
        self.relative_velocity  = relative_velocity.to(u.km / u.s).to_value()
    
    def propagate_for(self, delta: time.TimeDelta) -> ResultRM:
        """Propagate the linearized relative motion in the LVLH frame for delta time

        Args:
            delta (time.TimeDelta): Delta time for propagation
        
        Returns:
            ResultRM: Integration result
        """
        
        if not self.ready: raise ValueError("Relative Motion object is not ready")
        
        common.check_time_delta(delta)
        
        result: ResultRM = ResultRM()
        
        solution: dict = ode.solve_ivp(fun=self._linearized_equations_relative_motion,
                                       t_span=[0, delta.to_value(u.s)],
                                       y0=np.concat([self.relative_position,
                                                     self.relative_velocity,
                                                     self.position,
                                                     self.velocity]),
                                       method='RK45',
                                       args=(),
                                       rtol=1e-8,
                                       atol=1e-8)
        
        result.success = solution['success']
        result.time = solution['t'] * u.s
        result.relative_position_x = solution['y'][0, :] * u.km
        result.relative_position_y = solution['y'][1, :] * u.km
        result.relative_position_z = solution['y'][2, :] * u.km
        result.relative_velocity_x = solution['y'][3, :] * u.km / u.s
        result.relative_velocity_y = solution['y'][4, :] * u.km / u.s
        result.relative_velocity_z = solution['y'][5, :] * u.km / u.s
        result.position_x = solution['y'][6, :] * u.km
        result.position_y = solution['y'][7, :] * u.km
        result.position_z = solution['y'][8, :] * u.km
        result.velocity_x = solution['y'][9, :] * u.km / u.s
        result.velocity_y = solution['y'][10, :] * u.km / u.s
        result.velocity_z = solution['y'][11, :] * u.km / u.S
        
        return result
    
    def propagate_near_circular_orbit_for(self, delta: time.TimeDelta, eccentricity: u.Quantity) -> ResultRM:
        """
        Propagate the near-circular orbit motion in the LVLH frame for delta time.
        
        These equations are valid for eccentricities e << 1, and for e = 0 they are the Hill's equations.

        Args:
            delta (time.TimeDelta): Delta time for propagation
            eccentricity (u.Quantity): Eccentricity of the orbit
        
        Returns:
            ResultRM: Integration result
        """
        
        if not self.ready: raise ValueError("Relative Motion object is not ready")
        
        common.check_time_delta(delta)
        
        result: ResultRM = ResultRM()
        
        solution: dict = ode.solve_ivp(fun=self._near_circular_orbit_equations_relative_motion,
                                        t_span=[0, delta.to_value(u.s)],
                                        y0=np.concat([self.relative_position,
                                                      self.relative_velocity,
                                                      self.position,
                                                      self.velocity]),
                                        method='RK45',
                                        args=(eccentricity.to_value(u.one),),
                                        rtol=1e-8,
                                        atol=1e-8)
        
        result.success = solution['success']
        result.time = solution['t'] * u.s
        result.relative_position_x = solution['y'][0, :] * u.km
        result.relative_position_y = solution['y'][1, :] * u.km
        result.relative_position_z = solution['y'][2, :] * u.km
        result.relative_velocity_x = solution['y'][3, :] * u.km / u.s
        result.relative_velocity_y = solution['y'][4, :] * u.km / u.s
        result.relative_velocity_z = solution['y'][5, :] * u.km / u.s
        result.position_x = solution['y'][6, :] * u.km
        result.position_y = solution['y'][7, :] * u.km
        result.position_z = solution['y'][8, :] * u.km
        result.velocity_x = solution['y'][9, :] * u.km / u.s
        result.velocity_y = solution['y'][10, :] * u.km / u.s
        result.velocity_z = solution['y'][11, :] * u.km / u.S
        
        return result
    
    # --- PRIVATE ---
    
    def _linearized_equations_relative_motion(self, t: float, X: np.ndarray) -> np.ndarray:
        """
        Linearized equations of relative motion in the LVLH frame.
        
        This model propagates the first-order (linearized) relative motion between a chaser spacecraft and a target
        spacecraft following a Keplerian two-body orbit.
        The state vector contains both the *relative* position/velocity (dx, dy, dz, dv_x, dv_y, dv_z) and the *target*
        inertial position/velocity (x, y, z, v_x, v_y, v_z).
        The linearized dynamics are obtained by expanding the full nonlinear equations  around the target's
        instantaneous orbital state.

        The target's orbital quantities used in the linearization are:
            - R  : target radial distance
            - h  : target specific angular momentum magnitude
            - VR : target radial velocity
            - μ  : gravitational parameter of the attractor
            - Ω  : target angular velocity magnitude
            - dΩ/dt : target angular acceleration magnitude

        The resulting system corresponds to the classical first-order variational equations  for relative motion, valid
        for small separations and assuming a purely Keplerian (unperturbed) target trajectory.

        Notes
        -----
        - Valid for small relative distances compared to the orbital radius.
        - Assumes a Keplerian central-gravity field with no perturbations.
        - The linearized terms include coupling through the target's angular momentum,
        radial velocity, and instantaneous orbital geometry.
        - These equations are written in LVLH frame:
            - x-axis points along the radial direction from the attractor to the target
            - y-axis points along the target's velocity direction (tangential)
            - z-axis completes the right-handed frame (normal to the orbital plane)
        - In case we want to use the RSW frame:
            - x-axis points along the target's velocity direction (tangential)
            - y-axis completes the right-handed frame (normal to the orbital plane)
            - z-axis points along the radial direction from the attractor to the target
        
        The transformation from the LVLH frame to the RSW frame can be achieved as follows:
        - x-LVLH = z-RSW
        - y-LVLH = x-RSW
        - z-LVLH = y-RSW
        
        Args:
            t (float): Time (unused, included for ODE solver compatibility)
            X (np.ndarray): State vector [dx, dy, dz, dv_x, dv_y, dv_z, x, y, z, v_x, v_y, v_z]

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        dx, dy, dz, dv_x, dv_y, dv_z, x, y, z, v_x, v_y, v_z = X
        
        R: float = np.sqrt(x**2 + y**2 + z**2)
        
        h: float = np.linalg.norm(np.cross(np.array([x, y, z]), np.array([v_x, v_y, v_z])))
        
        VR: float = np.dot(np.array([x, y, z]), np.array([v_x, v_y, v_z]))
        
        mu: float = self.attractor.mu.to_value(u.km**3 / u.s**2)
        
        omega: float = h / R**2
        
        domega_dt: float = - 2 * VR * h / R**4
        
        dx_dt: np.ndarray = np.zeros(shape=(12))
        
        dx_dt[0]  = dv_x
        dx_dt[1]  = dv_y
        dx_dt[2]  = dv_z
        dx_dt[3]  = (2 * mu / R**3 + omega**2) * dx + domega_dt * dy + 2 * omega * dv_y
        dx_dt[4]  = (omega**2 - mu / R**3) * dy - domega_dt * dx - 2 * omega * dv_x
        dx_dt[5]  = - mu / R**3 * dz
        dx_dt[6]  = v_x
        dx_dt[7]  = v_y
        dx_dt[8]  = v_z
        dx_dt[9]  = - (mu / R**3) * x
        dx_dt[10] = - (mu / R**3) * y
        dx_dt[11] = - (mu / R**3) * z
        
        return dx_dt

    def _near_circular_orbit_equations_relative_motion(self, t: float, X: np.ndarray, e: float) -> np.ndarray:
        """
        Linearized equations of relative motion for a near-circular target orbit (HCW + first-order eccentricity terms).

        This model propagates the relative motion between a chaser spacecraft and a target spacecraft assuming the
        target follows a *near-circular* Keplerian orbit. The dynamics reduce to the classical Hill-Clohessy-Wiltshire
        (HCW) equations plus first-order corrections proportional to the target's eccentricity `e`.

        The state vector contains both the *relative* position/velocity (dx, dy, dz, dv_x, dv_y, dv_z) and the *target*
        inertial position/velocity (x, y, z, v_x, v_y, v_z). The linearization is performed around the instantaneous
        circular reference orbit, with the mean motion:

            n = h / R²

        where R is the target radial distance and h its specific angular momentum.

        The resulting system corresponds to the first-order variational equations for near-circular motion, valid for
        small separations and small eccentricities. The eccentricity-dependent terms introduce periodic forcing at the
        orbital frequency `n`, capturing the deviation from ideal circular HCW dynamics.

        Notes
        -----
        - Valid for small relative distances compared to the orbital radius.
        - Assumes a near-circular Keplerian orbit: eccentricity `e << 1`.
        - Reduces to the classical HCW equations when `e = 0`.
        - The linearized terms include coupling through the target's mean motion and first-order periodic corrections
          proportional to `e * cos(n t)` and `e * sin(n t)`.
        - These equations are written in the LVLH frame:
            - x-axis: radial direction (from attractor to target)
            - y-axis: along-track direction (target velocity)
            - z-axis: cross-track direction (normal to orbital plane)
        - For the RSW frame:
            - x-RSW = y-LVLH
            - y-RSW = z-LVLH
            - z-RSW = x-LVLH

        Args:
            t (float): Time (unused, included for ODE solver compatibility)
            X (np.ndarray): State vector [dx, dy, dz, dv_x, dv_y, dv_z, x, y, z, v_x, v_y, v_z]
            e (float): Target orbital eccentricity (assumed small)

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        dx, dy, dz, dv_x, dv_y, dv_z, x, y, z, v_x, v_y, v_z = X
        
        R: float = np.sqrt(x**2 + y**2 + z**2)
        
        h: float = np.linalg.norm(np.cross(np.array([x, y, z]), np.array([v_x, v_y, v_z])))
        
        mu: float = self.attractor.mu.to_value(u.km**3 / u.s**2)
        
        n: float = h / R**2
        
        dx_dt: np.ndarray = np.zeros(shape=(12))
        
        dx_dt[0]  = dv_x
        dx_dt[1]  = dv_y
        dx_dt[2]  = dv_z
        dx_dt[3]  = 2 * n * dv_y + 3 * n**2 * dx
        dx_dt[3]  += 2 * e * n * (- n * dy * np.sin(n * t) + 5 * n * dx * np.cos(n * t) + 2 * dv_y * np.cos(n * t))
        dx_dt[4]  = - 2 * n * dv_x
        dx_dt[4]  += e * n * (n * dy * np.cos(n * t) + 2 * n * dx * np.sin(n * t) - 4 * dv_x * np.cos(n * t))
        dx_dt[5]  = - n**2 * dz
        dx_dt[5]  += - 3 * e * n**2 * dz * np.cos(n * t)
        dx_dt[6]  = v_x
        dx_dt[7]  = v_y
        dx_dt[8]  = v_z
        dx_dt[9]  = - (mu / R**3) * x
        dx_dt[10] = - (mu / R**3) * y
        dx_dt[11] = - (mu / R**3) * z
        
        return dx_dt
