"""
Relative Motion

Implementation of relative motion algorithms.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 7: Relative Motion and Rendezvous
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.integrate as ode
import typing

import astro.bodies as bd
import astro.common as cm
import astro.orbit_3d as o3d
import astro.orbital_position as op
import astro.lagrange_coefficients as lc

class Result:
    """Result of integration
    """
    
    success: bool
    t: u.Quantity
    dr_x: u.Quantity
    dr_y: u.Quantity
    dr_z: u.Quantity
    dv_x: u.Quantity
    dv_y: u.Quantity
    dv_z: u.Quantity
    r_x: u.Quantity
    r_y: u.Quantity
    r_z: u.Quantity
    v_x: u.Quantity
    v_y: u.Quantity
    v_z: u.Quantity

class RelativeMotion():
    """Relative Motion
    """
    
    def __init__(self):
        """Constructor
        """
        
        self.ready: bool = False
        
        self.attractor: bd.Body = bd.get_body(bd.Attractor.EARTH)
        
        self.r: np.ndarray = np.zeros(3)
        
        self.v: np.ndarray = np.zeros(3)
    
    # --- STATIC ---
    
    @staticmethod
    def lvlh_kinematics(attractor: bd.Attractor,
                        oe_target: o3d.OrbitalElements,
                        oe_chaser: o3d.OrbitalElements) -> typing.List[u.Quantity]:
        """        
        Given the state vectors (`r_target`, `v_target`) of the **target spacecraft** and (`r_chaser`, `v_chaser`) of
        the **chaser spacecraft**, find the position, velocity, and acceleration of Chaser relative to Target along the
        **Local Vertical Local Horizontal** (*LVLH*) axes attached to the Target.

        Args:
            attractor (bd.Attractor): Main attractor
            oe_target (o3d.OrbitalElements): Target orbital elements
            oe_chaser (o3d.OrbitalElements): Chaser orbital elements
            
        Returns:
            typing.List[u.Quantity]: [r_rel_lvlh, v_rel_lvlh, a_rel_lvlh, omega_lvlh]
        """
        
        r_target, v_target = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_target)
        
        r_chaser, v_chaser = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_chaser)
        
        cm.check_attractor(attractor)
        
        cm.check_position_vector(r_target)
        cm.check_position_vector(r_chaser)
        
        cm.check_velocity_vector(v_target)
        cm.check_velocity_vector(v_chaser)
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        r_target: np.ndarray = r_target.to_value(u.km)
        r_chaser: np.ndarray = r_chaser.to_value(u.km)
        
        v_target: np.ndarray = v_target.to_value(u.km / u.s)
        v_chaser: np.ndarray = v_chaser.to_value(u.km / u.s)
        
        # >>> 1. Angular momentum of the Target
        
        h_target: np.ndarray = np.cross(r_target, v_target)
        
        # >>> 2. Unit vectors of the comoving frame
        
        i: np.ndarray = r_target / np.linalg.norm(r_target)
        k: np.ndarray = h_target / np.linalg.norm(h_target)
        j: np.ndarray = np.cross(k, i)
        
        # >>> 3. Orthogonal trasformation matrix (direction cosines matrix)
        
        dcm: np.ndarray = np.vstack((i, j, k)) # ? Q_Xx
        
        # >>> 4. Angular velocity
        
        omega: np.ndarray = h_target / np.linalg.norm(r_target)**2 # ? Ω
        
        d_omega_dt = - 2 * np.dot(v_target, r_target) / np.linalg.norm(r_target)**2 * omega # ? dΩ / dt
        
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
    def geocentric_equatorial_kinematics(r_target: u.Quantity,
                                         v_target: u.Quantity,
                                         r_rel_lvlh: u.Quantity,
                                         v_rel_lvlh: u.Quantity) -> typing.List[u.Quantity]:
        """
        Given the state vectors (`r_target`, `v_target`) of the **target spacecraft** and (`r_rel_lvlh`, `v_rel_lvlh`)
        of the **chaser spacecraft** relative to Target along the **Local Vertical Local Horizontal** (*LVLH*) axes
        attached to the Target, find the position and velocity of Chaser in the Geocentric Equatorial frame.

        Args:
            r_target (np.ndarray): Target position vector
            v_target (np.ndarray): Target velocity vector
            r_rel_lvlh (u.Quantity): Relative position vector
            v_rel_lvlh (u.Quantity): Relative velocity vector
            
        Returns:
            typing.List[u.Quantity]: [r_chaser, v_chaser]
        """
        
        cm.check_position_vector(r_target)
        cm.check_position_vector(r_rel_lvlh)
        
        cm.check_velocity_vector(v_target)
        cm.check_velocity_vector(v_rel_lvlh)
        
        r_target: np.ndarray = r_target.to_value(u.km)
        r_rel_lvlh: np.ndarray = r_rel_lvlh.to_value(u.km)
        
        v_target: np.ndarray = v_target.to_value(u.km / u.s)
        v_rel_lvlh: np.ndarray = v_rel_lvlh.to_value(u.km / u.s)
        
        # >>> 1. Angular momentum of the Target
        
        h_target: np.ndarray = np.cross(r_target, v_target)
        
        # >>> 2. Unit vectors of the comoving frame
        
        i: np.ndarray = r_target / np.linalg.norm(r_target)
        k: np.ndarray = h_target / np.linalg.norm(h_target)
        j: np.ndarray = np.cross(k, i)
        
        # >>> 3. Orthogonal trasformation matrix (direction cosines matrix)
        
        dcm: np.ndarray = np.vstack((i, j, k)) # ? Q_Xx
        
        # >>> 4. Relative position-velocity in Geocentric Equatioral Frame (X)
        
        r_rel: np.ndarray = np.matmul(np.linalg.inv(dcm), r_rel_lvlh)
        v_rel: np.ndarray = np.matmul(np.linalg.inv(dcm), v_rel_lvlh)
        
        # >>> 5. Angular velocity
        
        omega: np.ndarray = h_target / np.linalg.norm(r_target)**2 # ? Ω
        
        # >>> 6. Chaser position in Geocentric Equatioral Frame (X)
        
        r_chaser: np.ndarray  = r_target + r_rel
        
        # >>> 7. Chaser velocity in Geocentric Equatioral Frame (X)
        
        v_chaser: np.ndarray = v_target + v_rel + np.cross(omega, r_rel)
        
        return [r_chaser * u.km, v_chaser * u.km / u.s]
    
    @staticmethod
    def simulate_lvlh_kinematics(attractor: bd.Attractor,
                                 oe_target: o3d.OrbitalElements,
                                 oe_chaser: o3d.OrbitalElements,
                                 target_period_multiplier: int = 60,
                                 points_number: int = 1000) -> list:
        """
        Simulate the motion of the Target w.r.t. the Chaser in the LVLH frame

        Args:
            r_T (np.ndarray): Target position vector
            v_T (np.ndarray): Target velocity vector
            r_C (np.ndarray): Chaser position vector
            v_C (np.ndarray): Chaser velocity vector
            m (float, optional): Multiple of the Target period. Defaults to 60.
            n (float, optional): Number of points to plot. Defaults to 1000.
        """
        
        if not isinstance(target_period_multiplier, int): raise TypeError("'target_period_multiplier' must be of type 'int'")
        
        if not isinstance(points_number, int): raise TypeError("'points_number' must be of type 'int'")
        
        if target_period_multiplier < 0: raise ValueError("'target_period_multiplier' must be positive")
        
        if points_number < 0: raise ValueError("'points_number' must be positive")
        
        # >>> 1. Calculate state vectors from orbital elements
        
        oe_target.calc_semimajor_axis(attractor=attractor)
        
        oe_chaser.calc_semimajor_axis(attractor=attractor)
        
        r_target, v_target = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_target)
        
        r_chaser, v_chaser = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_chaser)
        
        cm.check_attractor(attractor)
        
        cm.check_position_vector(r_target)
        cm.check_position_vector(r_chaser)
        
        cm.check_velocity_vector(v_target)
        cm.check_velocity_vector(v_chaser)
        
        # >>> 2. Target period
        
        t_target: u.Quantity = oe_target.calc_orbital_period(attractor=attractor)
        
        # >>> 3. Target initial time
        
        t_0: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=oe_target.true_anomaly,
                                                                   period=t_target,
                                                                   eccentricity=oe_target.eccentricity.to_value())
        
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
                                                                 oe_target=oe_target,
                                                                 oe_chaser=oe_chaser)
            
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
            
            oe_target = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r_target, velocity=v_target)
            
            oe_chaser = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r_chaser, velocity=v_chaser)
        
        # >>> 6. Result
        
        return [x, y, z]
    
    @staticmethod
    def clohessy_wiltshire_matrices(n: u.Quantity, t: u.Quantity) -> list:
        """
        Clohessy-Wiltshire matrices
        
        δr(t) = Φ_rr * δr_0 + Φ_rv * δv_0
        
        δv(t) = Φ_vr * δr_0 + Φ_vv * δv_0

        Args:
            n (u.Quantity): Target orbit mean motion
            t (u.Quantity): Final time

        Returns:
            list: [phi_rr, phi_rv, phi_vr, phi_vv]
        """
        
        n: float = n.to_value(u.rad / u.s)
        t: float = t.to_value(u.s)
        
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
    def clohessy_wiltshire_equations(dr_0: u.Quantity,
                                     dv_0: u.Quantity,
                                     n: u.Quantity,
                                     t: float) -> typing.List[u.Quantity]:
        """
        Clohessy-Wiltshire equations
        
        δr(t) = Φ_rr * δr_0 + Φ_rv * δv_0
        
        δv(t) = Φ_vr * δr_0 + Φ_vv * δv_0

        Args:
            dr_0 (u.Quantity): Initial relative position vector
            dv_0 (u.Quantity): Initial relative velocity vector
            n (u.Quantity): Target orbit mean motion
            t (u.Quantity): Final time

        Returns:
            typing.List[u.Quantity]: [dr, dv]
        """
        
        cm.check_position_vector(r=dr_0)
        
        cm.check_velocity_vector(v=dv_0)
        
        dr_0: np.ndarray = dr_0.to_value(u.km)
        
        dv_0: np.ndarray = dv_0.to_value(u.km / u.s)
        
        phi_rr, phi_rv, phi_vr, phi_vv = RelativeMotion.clohessy_wiltshire_matrices(n=n, t=t)
        
        dr: np.ndarray = np.matmul(phi_rr, dr_0) + np.matmul(phi_rv, dv_0)
        dv: np.ndarray = np.matmul(phi_vr, dr_0) + np.matmul(phi_vv, dv_0)
        
        return [dr * u.km, dv * u.km / u.s]
    
    @staticmethod
    def two_impulsive_rendezvous_maneuver(attractor: bd.Attractor,
                                          oe_target: o3d.OrbitalElements,
                                          oe_chaser: o3d.OrbitalElements,
                                          t_maneuver: u.Quantity) -> typing.List[u.Quantity]:
        """
        Two-Impulse Rendezvous maneuver

        Args:
            attractor (bd.Attractor): Main attractor
            oe_target (o3d.OrbitalElements): Target orbital elements
            oe_chaser (o3d.OrbitalElements): Chaser orbital elements
            t_maneuver (u.Quantity): Maneuver time

        Returns:
            typing.List[u.Quantity]: [dv_tot, dx, dy, dz]
        """
        
        # >>> 1. LVLH kinematics at the beginning of the rendezvous
        
        dr_0, dv_0_minus, _, omega = RelativeMotion.lvlh_kinematics(attractor=attractor,
                                                                    oe_target=oe_target,
                                                                    oe_chaser=oe_chaser)
        
        n: u.Quantity = np.linalg.norm(omega.to_value(u.rad / u.s)) * u.rad / u.s
        
        # >>> 2. Clohessy-Wiltshire solution for the maneuver (when reached the target => dr = 0, dv = 0)
        
        phi_rr, phi_rv, _, _ = RelativeMotion.clohessy_wiltshire_matrices(n=n, t=t_maneuver)
        
        dv_0_plus: np.ndarray = - np.matmul(np.matmul(np.linalg.inv(phi_rv), phi_rr), dr_0.to_value(u.km))
        
        _, dv_f_minus = RelativeMotion.clohessy_wiltshire_equations(dr_0=dr_0,
                                                                    dv_0=dv_0_plus * u.km / u.s,
                                                                    n=n,
                                                                    t=t_maneuver)
        
        dv_f_plus: np.ndarray = np.zeros(shape=(3))
        
        # >>> 3. Maneuver result
        
        dv_tot: float = np.linalg.norm(dv_0_plus - dv_0_minus.to_value(u.km / u.s)) + \
                        np.linalg.norm(dv_f_plus - dv_f_minus.to_value(u.km / u.s))
        
        dx: list = []
        dy: list = []
        dz: list = []
        
        for t in np.linspace(0, t_maneuver.to_value(u.s), 1000):
            
            dr, _ = RelativeMotion.clohessy_wiltshire_equations(dr_0=dr_0, dv_0=dv_0_plus * u.km / u.s, n=n, t=t * u.s)
            
            dx.append(dr[0].to_value(u.km))
            dy.append(dr[1].to_value(u.km))
            dz.append(dr[2].to_value(u.km))
        
        return [dv_tot * u.km / u.s, np.array(dx) * u.km, np.array(dy) * u.km, np.array(dz) * u.km]
    
    # --- PUBLIC ---
    
    def init(self,
             attractor: bd.Attractor,
             r: u.Quantity,
             v: u.Quantity,
             dr: u.Quantity,
             dv: u.Quantity) -> None:
        """
        Initialize the parameters for the propagation

        Args:
            attractor (bd.Attractor): Main attractor
            r (u.Quantity): Position vector
            v (u.Quantity): Velocity vector
            dr (u.Quantity): Relative position vector
            dv (u.Quantity): Relative velocity vector
        """
        
        cm.check_attractor(attractor)
        
        cm.check_position_vector(r.to_value(u.km))
        
        cm.check_position_vector(dr.to_value(u.km))
        
        cm.check_velocity_vector(v.to_value(u.km / u.s))
        
        cm.check_velocity_vector(dv.to_value(u.km / u.s))
        
        self.ready      = True
        self.attractor  = bd.BODIES[attractor]
        self.r          = r.to(u.km).to_value()
        self.v          = v.to(u.km / u.s).to_value()
        self.dr         = dr.to(u.km).to_value()
        self.dv         = dv.to(u.km / u.s).to_value()
    
    def propagate_for(self, delta: time.TimeDelta) -> Result:
        """Propagate the linearized relative motion in the LVLH frame for delta time

        Args:
            delta (time.TimeDelta): Delta time for propagation
        
        Returns:
            Result: Integration result
        """
        
        if not self.ready: raise ValueError("Relative Motion object is not ready")
        
        cm.check_time_delta(delta)
        
        result: Result = Result()
        
        solution: dict = ode.solve_ivp(fun=self._linearized_equations_relative_motion,
                                       t_span=[0, delta.to(u.s).to_value()],
                                       y0=np.concat([self.dr, self.dv, self.r, self.v]),
                                       method='RK45',
                                       args=(),
                                       rtol=1e-8,
                                       atol=1e-8)
        
        result.success = solution['success']
        result.t = solution['t'] * u.s
        result.dr_x = solution['y'][0, :] * u.km
        result.dr_y = solution['y'][1, :] * u.km
        result.dr_z = solution['y'][2, :] * u.km
        result.dv_x = solution['y'][3, :] * u.km / u.s
        result.dv_y = solution['y'][4, :] * u.km / u.s
        result.dv_z = solution['y'][5, :] * u.km / u.s
        result.r_x = solution['y'][6, :] * u.km
        result.r_y = solution['y'][7, :] * u.km
        result.r_z = solution['y'][8, :] * u.km
        result.v_x = solution['y'][9, :] * u.km / u.s
        result.v_y = solution['y'][10, :] * u.km / u.s
        result.v_z = solution['y'][11, :] * u.km / u.S
        
        return result
        
    # --- PRIVATE ---
    
    def _linearized_equations_relative_motion(self, t: float, X: np.ndarray) -> np.ndarray:
        """Linearized equations of relative motion

        Args:
            t (float): Time
            X (np.ndarray): State [12, 1]

        Returns:
            np.ndarray: Derivative of state
        """
        
        dx, dy, dz, dv_x, dv_y, dv_z, x, y, z, v_x, v_y, v_z = X
        
        R: float = np.sqrt(x**2 + y**2 + z**2)
        
        h: np.ndarray = np.linalg.norm(np.cross(np.array([x, y, z]), np.array([v_x, v_y, v_z])))
        
        VR: float = np.dot(np.array([x, y, z]), np.array([v_x, v_y, v_z]))
        
        mu: float = self.attractor.mu.to_value(u.km**3 / u.s**2)
        
        dx_dt: np.ndarray = np.zeros(shape=(12))
        
        dx_dt[0]  = dv_x
        dx_dt[1]  = dv_y
        dx_dt[2]  = dv_z
        dx_dt[3]  = (2 * mu / R**3 + h**2 / R**4) * dx - 2 * VR * h / R**4 * dy + 2 * h / R**2 * dv_y
        dx_dt[4]  = (h**2 / R**4 - mu / R**3) * dy + 2 * VR * h / R**4 * dx - 2 * h / R**2 * dv_x
        dx_dt[5]  = - mu / R**3 * dz
        dx_dt[6]  = v_x
        dx_dt[7]  = v_y
        dx_dt[8]  = v_z
        dx_dt[9]  = - (mu / R**3) * x
        dx_dt[10] = - (mu / R**3) * y
        dx_dt[11] = - (mu / R**3) * z
        
        return dx_dt
