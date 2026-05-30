"""
Orbit in Three Dimensions

Transformations among reference frames.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 4: Orbit in Three Dimensions

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 3: Orbit Determination
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.units as u
import astropy.time as time
import dataclasses as dc
import typing as t
import numpy as np

import astro.bodies as bodies
import astro.common as common
import astro.orbital_position as orbital_position
import astro.two_body_problem as two_body_problem

@dc.dataclass
class OrbitalElements:
    """Classical Orbital Elements"""
    
    specific_angular_momentum           : u.Quantity = dc.field(default_factory=lambda: 0 * u.km**2 / u.s)
    semimajor_axis                      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    eccentricity                        : u.Quantity = dc.field(default_factory=lambda: 0 * u.one)
    inclination                         : u.Quantity = dc.field(default_factory=lambda: 0 * u.deg)
    right_ascension_of_ascending_node   : u.Quantity = dc.field(default_factory=lambda: 0 * u.deg)
    argument_of_periapsis               : u.Quantity = dc.field(default_factory=lambda: 0 * u.deg)
    true_anomaly                        : u.Quantity = dc.field(default_factory=lambda: 0 * u.deg)
    
    def calc_semimajor_axis(self, attractor: bodies.Attractor) -> u.Quantity:
        
        common.check_attractor(attractor)
        
        h: u.Quantity = self.specific_angular_momentum
        e: u.Quantity = self.eccentricity
        
        self.semimajor_axis = h**2 / (bodies.BODIES[attractor].mu * (1 - e**2))
        
        return self.semimajor_axis
    
    def calc_perigee_radius(self) -> u.Quantity:
        
        a: u.Quantity = self.semimajor_axis
        e: u.Quantity = self.eccentricity
        
        return a * (1 - e)
    
    def calc_apogee_radius(self) -> u.Quantity:
        
        a: u.Quantity = self.semimajor_axis
        e: u.Quantity = self.eccentricity
        
        return a * (1 + e)
    
    def calc_specific_angular_momentum(self, attractor: bodies.Attractor) -> u.Quantity:
        
        common.check_attractor(attractor)
        
        r_p: u.Quantity = self.calc_perigee_radius()
        r_a: u.Quantity = self.calc_apogee_radius()
        
        mu: u.Quantity = bodies.BODIES[attractor].mu
        
        self.specific_angular_momentum = np.sqrt(2 * mu) * np.sqrt(r_a * r_p / (r_a + r_p))
        
        return self.specific_angular_momentum
    
    def calc_orbital_period(self, attractor: bodies.Attractor) -> u.Quantity:
        
        common.check_attractor(attractor)
        
        h: u.Quantity = self.calc_specific_angular_momentum(attractor=attractor)
        a: u.Quantity = self.semimajor_axis
        e: u.Quantity = self.eccentricity
        
        mu: u.Quantity = bodies.BODIES[attractor].mu
        
        if a != 0 * u.km:
            
            return 2 * np.pi / np.sqrt(mu) * a**(3/2)
        
        elif h != 0 * u.km**2 / u.s:
        
            return 2 * np.pi / mu**2 * (h / np.sqrt(1 - e**2))**3
        
        else:
            
            return 0 * u.s
    
    def calc_semilatus_rectum(self, attractor: bodies.Attractor) -> u.Quantity:
        
        common.check_attractor(attractor)
        
        h: u.Quantity = self.specific_angular_momentum
        a: u.Quantity = self.semimajor_axis
        e: u.Quantity = self.eccentricity
        
        mu: u.Quantity = bodies.BODIES[attractor].mu
        
        return (a * (1 - e**2)) if h == 0 else (h**2 / mu)
    
    def update_from_perigee_apogee(self, periapsis_radius: u.Quantity, apoapsis_radius: u.Quantity) -> None:
        
        r_p: u.Quantity = periapsis_radius.to(u.km)
        r_a: u.Quantity = apoapsis_radius.to(u.km)
        
        self.semimajor_axis = 0.5 * (r_p + r_a)
        self.eccentricity = (r_a - r_p) / (r_a + r_p)

class Orbit3D():
    """Orbit in Three Dimensions
    """
    
    # --- STATIC ---
    
    @staticmethod
    def right_ascension_declination(position : u.Quantity) -> t.List[u.Quantity, u.Quantity]:
        """Calculate the Right Ascension and Declination of the position vector

        Args:
            position (u.Quantity): Position vector

        Returns:
            t.List[u.Quantity, u.Quantity]: [alpha (-180; +180), delta (0; 360)]
        """
        
        r: np.ndarray = position.to_value(u.km)
        
        common.check_position_vector(r)
        
        # >>> 1. Magnitude
        
        r_m: float = np.linalg.norm(r)
        
        # >>> 2. Direction cosines
        
        l: float = r[0] / r_m
        m: float = r[1] / r_m
        n: float = r[2] / r_m
        
        # >>> 3. Declination
        
        delta: float = np.arcsin(n)
        
        # >>> 4. Right Ascension
        
        alpha: float = np.arccos(l / np.cos(delta)) if m > 0 else (2 * np.pi - np.arccos(l / np.cos(delta)))
        
        return [np.rad2deg(alpha) * u.deg, np.rad2deg(delta) * u.deg]
    
    @staticmethod
    def cartesian_to_keplerian(attractor: bodies.Attractor,
                               position : u.Quantity,
                               velocity : u.Quantity) -> OrbitalElements:
        """
        Calculates the Orbital Elements from position and velocity vectors in Geocentric Equatorial Frame (GEF)
        
        Earth-centered inertial (ECI) frame

        Args:
            attractor (bodies.Attractor): Main attractor
            position (u.Quantity): Position vector
            velocity (u.Quantity): Velocity vector

        Returns:
            OrbitalElements: Orbital Elements
        """
        
        r: np.ndarray = position.to_value(u.km)
        v: np.ndarray = velocity.to_value(u.km / u.s)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        common.check_attractor(attractor)
        common.check_position_vector(r)
        common.check_velocity_vector(v)
        
        oe: OrbitalElements = OrbitalElements()
        
        # >>> 1. Distance
        
        r_m: float = np.linalg.norm(r)
        
        # >>> 2. Speed
        
        v_m: float = np.linalg.norm(v)
        
        # >>> 3. Radial velocity
        
        v_r: float = np.dot(r, v) / r_m
        
        # >>> 4. Specific angular momentum
        
        h: np.ndarray = np.cross(r, v)
        
        h_m: float = np.linalg.norm(h)
        
        oe.specific_angular_momentum = h_m * u.km**2 / u.s
        
        # >>> 5. Semi-major axis
        
        epsilon: float = v_m**2 / 2 - mu / r_m # ? Specific Mechanical Energy
        
        oe.semimajor_axis = - 0.5 * mu / epsilon * u.km
        
        # >>> 6. Inclination
        
        inc: float = np.arccos(h[2] / h_m)
        
        oe.inclination = u.Quantity(inc, u.rad).to(u.deg)
        
        # >>> 7. Line of nodes
        
        N: np.ndarray
        
        tol: float = 1e-6 # ? Tolerance to consider the orbit as equatorial or polar
        
        inc_min: float = np.deg2rad(1) # ? Minimum inclination to consider the orbit as non-equatorial
        
        if inc <= 0.5 * np.pi:
        
            if inc > inc_min or (inc < inc_min and inc > tol):
                
                N = np.cross(np.array([0, 0, 1]), h) # ? K x h
                
            else:
            
                N = np.array([1, 0, 0]) # ? I
                
        else:
            
            if inc < (np.pi - inc_min) or (inc > (np.pi - inc_min) and (np.pi - inc) > tol):
                
                N = np.cross(np.array([0, 0, 1]), h) # ? K x h
                
            else:
            
                N = np.array([1, 0, 0]) # ? I
        
        # >>> 8. Magnitude of the line of nodes
        
        N_m: float = np.linalg.norm(N)
        
        # >>> 9. Right ascension of the ascending node (RAAN): N / N_m = cos(raan) * I + sin(raan) * J
        
        raan: float = np.arccos(N[0] / N_m)
        
        oe.right_ascension_of_ascending_node = u.Quantity(raan if N[1] >= 0 else (2 * np.pi - raan), u.rad).to(u.deg)
        
        # >>> 10. Eccentricity vector
        
        ecc: np.ndarray = 1 / mu * ((v_m**2 - mu / r_m) * r - r_m * v_r * v)
        
        # >>> 11. Eccentricity
        
        ecc_m: float = np.linalg.norm(ecc)
        
        oe.eccentricity = ecc_m * u.one
        
        # >>> 12. Argument of periapsis
        
        argp: float = np.arccos(np.dot(N, ecc) / (N_m * ecc_m))
        
        oe.argument_of_periapsis = u.Quantity(argp if ecc[2] >= 0 else (2 * np.pi - argp), u.rad).to(u.deg)
        
        # >>> 13. True anomaly
        
        theta: float = np.arccos(np.dot(ecc, r) / (ecc_m * r_m))
        
        oe.true_anomaly = u.Quantity(theta if v_r >= 0 else (2 * np.pi - theta), u.rad).to(u.deg)
        
        return oe
    
    @staticmethod
    def rotation_matrix_ijk_to_pqw(orbital_elements : OrbitalElements) -> np.ndarray:
        """Rotation matrix from Geocentric Equatorial Frame (IJK) to Perifocal Frame (PQW)
        
        3-1-3 Euler angles IJK --> PQW

        Args:
            orbital_elements (OrbitalElements): Orbital Elements
            
        Returns:
            np.ndarray: Rotation matrix
        """
        
        common.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                          orbital_elements.eccentricity.to_value(),
                                          orbital_elements.inclination.to_value(u.deg),
                                          orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                          orbital_elements.argument_of_periapsis.to_value(u.deg),
                                          orbital_elements.true_anomaly.to_value(u.deg))
        
        inc: float = orbital_elements.inclination.to_value(u.rad)
        raan: float = orbital_elements.right_ascension_of_ascending_node.to_value(u.rad)
        argp: float = orbital_elements.argument_of_periapsis.to_value(u.rad)
        
        R_3_raan: np.ndarray = np.array( # ? Rotation about K through angle RAAN
            [
                [ + np.cos(raan) , + np.sin(raan) , 0 ],
                [ - np.sin(raan) , + np.cos(raan) , 0 ],
                [ 0              , 0              , 1 ]
            ])
        
        R_1_inc: np.ndarray = np.array( # ? Rotation about X' through angle inc
            [
                [ 1 , 0             , 0             ],
                [ 0 , + np.cos(inc) , + np.sin(inc) ],
                [ 0 , - np.sin(inc) , + np.cos(inc) ]
            ])
        
        R_3_argp: np.ndarray = np.array( # ? Rotation about Z'' through angle argument of periapsis
            [
                [ + np.cos(argp) , + np.sin(argp) , 0 ],
                [ - np.sin(argp) , + np.cos(argp) , 0 ],
                [ 0              , 0              , 1 ]
            ])
        
        R: np.ndarray = np.matmul(R_3_argp, np.matmul(R_1_inc, R_3_raan))
        
        return R
    
    @staticmethod
    def geocentric_equatorial_to_perifocal(attractor: bodies.Attractor,
                                           position : u.Quantity,
                                           velocity : u.Quantity) -> t.List[u.Quantity, u.Quantity]:
        """Geocentric Equatiorial Frame (IJK) --> Perifocal Frame (PQW)

        Args:
            attractor (bodies.Attractor): Main attractor
            position (u.Quantity): Position vector GEF
            velocity (u.Quantity): Velocity vector GEF

        Returns:
            t.List[u.Quantity, u.Quantity]: [r_PF, v_PF]
        """
        
        r_GEF: np.ndarray = position.to_value(u.km)
        v_GEF: np.ndarray = velocity.to_value(u.km / u.s)
        
        common.check_attractor(attractor)
        common.check_position_vector(position)
        common.check_velocity_vector(velocity)
        
        # >>> 1. Calculate orbital elements
        
        oe: OrbitalElements = Orbit3D.cartesian_to_keplerian(attractor=attractor, position=position, velocity=velocity)
        
        # >>> 2. Overall rotation matrix (3-1-3 Euler angles IJK --> PQW)
        
        R: np.ndarray = Orbit3D.rotation_matrix_ijk_to_pqw(orbital_elements=oe)
        
        # >>> 3. Calculate position and velocity in perifocal frame
        
        r_PF: u.Quantity = np.matmul(R, r_GEF) * u.km
        v_PF: u.Quantity = np.matmul(R, v_GEF) * u.km / u.s
        
        return [r_PF, v_PF]
    
    @staticmethod
    def keplerian_to_cartesian(attractor: bodies.Attractor,
                               orbital_elements : OrbitalElements) -> t.List[u.Quantity, u.Quantity]:
        """Perifocal Frame --> Geocentric Equatiorial Frame

        Args:
            attractor (bodies.Attractor): Main attractor
            orbital_elements (OrbitalElements): Orbital Elements

        Returns:
            t.List[u.Quantity, u.Quantity]: [r_GEF, v_GEF]
        """
        
        common.check_attractor(attractor)
        
        common.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                          orbital_elements.eccentricity.to_value(),
                                          orbital_elements.inclination.to_value(u.deg),
                                          orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                          orbital_elements.argument_of_periapsis.to_value(u.deg),
                                          orbital_elements.true_anomaly.to_value(u.deg))
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        ecc: float = orbital_elements.eccentricity.to_value()
        ta: float = orbital_elements.true_anomaly.to_value(u.rad)
        
        p: float = orbital_elements.calc_semilatus_rectum(attractor=attractor).to_value(u.km)
        
        # >>> 1. Calculate position in perifocal frame
        
        r_PF: np.ndarray = p / (1 + ecc * np.cos(ta)) * np.array([np.cos(ta), np.sin(ta), 0])
        
        # >>> 2. Calculate velocity in perifocal frame
        
        v_PF: np.ndarray = np.sqrt(mu / p) * np.array([-np.sin(ta), ecc + np.cos(ta), 0])
        
        # >>> 2. Overall rotation matrix (3-1-3 Euler angles PQW --> IJK)
        
        R: np.ndarray = Orbit3D.rotation_matrix_ijk_to_pqw(orbital_elements=orbital_elements).T # ? Transpose
        
        # >>> 4. Calculate position and velocity in geocentric equatorial frame
        
        r_GEF: u.Quantity = np.matmul(R, r_PF) * u.km
        v_GEF: u.Quantity = np.matmul(R, v_PF) * u.km / u.s
        
        return [r_GEF, v_GEF]
    
    @staticmethod
    def perifocal_to_geocentric_equatorial_position_vector(orbital_elements : OrbitalElements,
                                                           perifocal_position: u.Quantity) -> u.Quantity:
        """Perifocal Frame --> Geocentric Equatiorial Frame for a given position vector

        Args:
            orbital_elements (OrbitalElements): Orbital Elements
            perifocal_position (u.Quantity): Position vector in Perifocal Frame

        Returns:
            u.Quantity: r_GEF
        """
        
        common.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                          orbital_elements.eccentricity.to_value(),
                                          orbital_elements.inclination.to_value(u.deg),
                                          orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                          orbital_elements.argument_of_periapsis.to_value(u.deg),
                                          orbital_elements.true_anomaly.to_value(u.deg))
        
        common.check_position_vector(perifocal_position)
        
        R: np.ndarray = Orbit3D.rotation_matrix_ijk_to_pqw(orbital_elements=orbital_elements).T # ? Transpose
        
        r_GEF: u.Quantity = np.matmul(R, perifocal_position.to_value(u.km)) * u.km
        
        return r_GEF
    
    @staticmethod
    def planet_oblateness_effect(attractor: bodies.Attractor, orbital_elements : OrbitalElements) -> t.List[u.Quantity, u.Quantity]:
        """Calculates the planet oblateness effect
        
        Args:
            attractor (bodies.Attractor): Main attractor
            orbital_elements (OrbitalElements): Orbital Elements

        Returns:
            t.List[u.Quantity, u.Quantity]: [dOmega_dt, domega_dt]
        """
        
        common.check_attractor(attractor)
        
        common.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                          orbital_elements.eccentricity.to_value(),
                                          orbital_elements.inclination.to_value(u.deg),
                                          orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                          orbital_elements.argument_of_periapsis.to_value(u.deg),
                                          orbital_elements.true_anomaly.to_value(u.deg))
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        R_E: float = bodies.BODIES[attractor].R_E.to_value(u.km)
        J_2: float = bodies.BODIES[attractor].J2.to_value(u.one) if bodies.BODIES[attractor].J2 is not None else 0
        
        a: float = orbital_elements.semimajor_axis.to_value(u.km)
        ecc: float = orbital_elements.eccentricity.to_value()
        inc: float = orbital_elements.inclination.to_value(u.rad)
        
        # >>> Right ascension of the ascending node variation
        
        d_raan_dt: float = - 3/2 * (np.sqrt(mu) * J_2 * R_E**2) / ((1 - ecc**2)**2 * a**(7/2)) * np.cos(inc)
        
        # >>> Argument of the periapsis variation
        
        d_argp_dt: float = - 3/2 * (np.sqrt(mu) * J_2 * R_E**2) / ((1 - ecc**2)**2 * a**(7/2)) * (5/2 * np.sin(inc)**2 - 2)
        
        return [u.Quantity(d_raan_dt, u.rad / u.s).to(u.deg / u.s), u.Quantity(d_argp_dt, u.rad / u.s).to(u.deg / u.s)]
    
    @staticmethod
    def ground_track_propagation(attractor: bodies.Attractor,
                                 orbital_elements : OrbitalElements,
                                 time_step : time.TimeDelta) -> t.List[u.Quantity, u.Quantity]:
        """Calculates the Ground Track for the given time step

        Args:
            attractor (bodies.Attractor): Main attractor
            orbital_elements (OrbitalElements): Orbital Elements
            time_step (time.TimeDelta): Time step
            
        Returns:
            t.List[u.Quantity, u.Quantity]: [right ascension (-180; +180), declination (0; 360)]
        """
        
        common.check_attractor(attractor)
        
        common.check_keplerian_parameters(orbital_elements.semimajor_axis.to_value(u.km),
                                          orbital_elements.eccentricity.to_value(),
                                          orbital_elements.inclination.to_value(u.deg),
                                          orbital_elements.right_ascension_of_ascending_node.to_value(u.deg),
                                          orbital_elements.argument_of_periapsis.to_value(u.deg),
                                          orbital_elements.true_anomaly.to_value(u.deg))
        
        body: bodies.Body = bodies.BODIES[attractor]
        
        ecc: float = orbital_elements.eccentricity.to_value()
        
        if ecc >= 1.0: return [u.Quantity(0, u.deg), u.Quantity(0, u.deg)]
        
        # >>> 1. Oblateness
        
        d_raan_dt, d_argp_dt = Orbit3D.planet_oblateness_effect(attractor=attractor, orbital_elements=orbital_elements)
        
        # >>> 2. Initial condition
        
        r_GEF, v_GEF = Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=orbital_elements)
        
        op: two_body_problem.OrbitParameters = two_body_problem.Orbit.cartesian_to_orbit_parameters(attractor=attractor,
                                                                                                    position=r_GEF,
                                                                                                    velocity=v_GEF)
        
        t_0: u.Quantity = 0.0 * u.s
        
        if ecc == 0:
            
            t_0 = orbital_position.OrbitalPosition.circular_orbit_time(nu=orbital_elements.true_anomaly, T=op.period)
            
        elif ecc < 1.0:
            
            t_0 = orbital_position.OrbitalPosition.elliptical_orbit_time(nu=orbital_elements.true_anomaly,
                                                                         T=op.period,
                                                                         e=orbital_elements.eccentricity.to_value())
        
        # >>> 3. Propagation
        
        t: u.Quantity = t_0.to(u.s) + time_step.to(u.s)
            
        # >>> a) True anomaly
        
        ta: u.Quantity = 0.0 * u.rad
        
        if ecc == 0:
            
            ta = orbital_position.OrbitalPosition.circular_orbit_true_anomaly(t=t, T=op.period)
            
        elif ecc < 1.0:
            
            ta = orbital_position.OrbitalPosition.elliptical_orbit_true_anomaly(t=t,
                                                                                T=op.period,
                                                                                e=orbital_elements.eccentricity.to_value())
        
        # >>> b) New Orbital Elements
        
        orbital_elements.right_ascension_of_ascending_node += d_raan_dt * time_step.to(u.s)
        orbital_elements.argument_of_periapsis += d_argp_dt * time_step.to(u.s)
        
        orbital_elements.true_anomaly = ta
        
        orbital_elements.right_ascension_of_ascending_node = common.wrap_angle(orbital_elements.right_ascension_of_ascending_node)
        orbital_elements.argument_of_periapsis = common.wrap_angle(orbital_elements.argument_of_periapsis)
        
        # >>> c) New state
        
        r_GEF, v_GEF = Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=orbital_elements)
        
        # >>> d) New position
        
        ta: float = common.wrap_angle(body.omega.to_value(u.deg / u.s) * (t.to_value(u.s) - t_0.to_value(u.s)), low=0, high=360)
        
        ta = np.deg2rad(ta)
        
        # * Rotation matrix from inertial frame (XYZ) to rotating frame (Earth-fixed, x'y'z')
        
        R_3_t = np.array(
            [
                [+ np.cos(ta) , + np.sin(ta), 0],
                [- np.sin(ta) , + np.cos(ta), 0],
                [0            , 0           , 1]
            ])
        
        # >>> e) Right Ascension and Declination
        
        alpha, delta = Orbit3D.right_ascension_declination(position=np.matmul(R_3_t, r_GEF.to_value(u.km)) * u.km)
        
        return [alpha - 180 * u.deg, delta]