"""
Orbit in Three Dimensions

Transformations among reference frames.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 4: Orbit in Three Dimensions
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
    """
    Orbital Elements
    
    Args:
        h (float): Specific angular momentum
        a (float): Semi-major axis
        ecc (float): Eccentricity
        inc (float): Inclination
        raan (float): Right Ascension of the Ascending Node
        argp (float): Argument of Perigee
        nu (float): True Anomaly
    """
    
    h       : u.Quantity    = dc.field(default_factory=lambda: 0 * u.km**2 / u.s)
    a       : u.Quantity    = dc.field(default_factory=lambda: 0 * u.km)
    ecc     : u.Quantity    = dc.field(default_factory=lambda: 0 * u.dimensionless_unscaled)
    inc     : u.Quantity    = dc.field(default_factory=lambda: 0 * u.deg)
    raan    : u.Quantity    = dc.field(default_factory=lambda: 0 * u.deg)
    argp    : u.Quantity    = dc.field(default_factory=lambda: 0 * u.deg)
    nu      : u.Quantity    = dc.field(default_factory=lambda: 0 * u.deg)
    
    def semi_major_axis(self, attractor: bodies.Attractor) -> u.Quantity:
        """Calculate the semi-major axis

        Args:
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: Semi-major axis
        """
        
        common.check_attractor(attractor)
        
        return self.h**2 / (bodies.BODIES[attractor].mu * (1 - self.ecc**2))
    
    def perigee_radius(self) -> u.Quantity:
        """Calculate the perigee radius

        Returns:
            u.Quantity: Perigee radius
        """
        
        return self.a * (1 - self.ecc)
    
    def apogee_radius(self) -> u.Quantity:
        """Calculate the apogee radius

        Returns:
            u.Quantity: Apogee radius
        """
        
        return self.a * (1 + self.ecc)
    
    def specific_angular_momentum(self, attractor: bodies.Attractor) -> u.Quantity:
        """Calculate the specific angular momentum

        Args:
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: Specific angular momentum
        """
        
        common.check_attractor(attractor)
        
        r_p: float = self.perigee_radius().to_value(u.km)
        r_a: float = self.apogee_radius().to_value(u.km)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        return np.sqrt(2 * mu) * np.sqrt(r_a * r_p / (r_a + r_p)) * u.km**2 / u.s
    
    def orbital_period(self, attractor: bodies.Attractor) -> u.Quantity:
        """Calculate the orbital period

        Args:
            attractor (bodies.Attractor): Main attractor

        Returns:
            u.Quantity: Orbital period
        """
        
        common.check_attractor(attractor)
        
        h: float = self.specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        e: float = self.ecc.to_value()
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        return 2 * np.pi / mu**2 * (h / np.sqrt(1 - e**2))**3 * u.s
    
    def update_from_perigee_apogee(self, r_p : u.Quantity, r_a : u.Quantity) -> None:
        """Update the orbital elements from perigee and apogee radius

        Args:
            r_p (u.Quantity): Perigee radius
            r_a (u.Quantity): Apogee radius
        """
        
        r_p: float = r_p.to_value(u.km)
        r_a: float = r_a.to_value(u.km)
        
        self.a = 0.5 * (r_p + r_a) * u.km
        self.ecc = (r_a - r_p) / (r_a + r_p) * u.dimensionless_unscaled

class Orbit3D():
    """Orbit in Three Dimensions
    """
    
    def __init__(self):
        """Constructor
        """
        
        pass
    
    # --- STATIC ---
    
    @staticmethod
    def right_ascension_declination(r : u.Quantity) -> t.List[u.Quantity, u.Quantity]:
        """Calculate the Right Ascension and Declination of the position vector `r`

        Args:
            r (u.Quantity): Position vector

        Returns:
            t.List[u.Quantity, u.Quantity]: [alpha (-180; +180), delta (0; 360)]
        """
        
        r: np.ndarray = r.to_value(u.km)
        
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
        
        return [u.Quantity(np.rad2deg(alpha), u.deg), u.Quantity(np.rad2deg(delta), u.deg)]
    
    @staticmethod
    def orbital_elements(attractor: bodies.Attractor, r : u.Quantity, v : u.Quantity) -> OrbitalElements:
        """Calculates the Orbital Elements from position and velocity vectors in Geocentric Equatorial Frame (GEF)

        Args:
            attractor (bodies.Attractor): Main attractor
            r (u.Quantity): Position vector
            v (u.Quantity): Velocity vector

        Returns:
            OrbitalElements: Orbital Elements
        """
        
        r = r.to_value(u.km)
        v = v.to_value(u.km / u.s)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        common.check_attractor(attractor)
        common.check_position_vector(r)
        common.check_velocity_vector(v)
        
        oe = OrbitalElements()
        
        # >>> 1. Distance
        
        r_m: float = np.linalg.norm(r)
        
        # >>> 2. Speed
        
        v_m: float = np.linalg.norm(v)
        
        # >>> 3. Radial velocity
        
        v_r: float = np.dot(r, v) / r_m
        
        # >>> 4. Specific angular momentum
        
        h: np.ndarray = np.cross(r, v)
        
        h_m: float = np.linalg.norm(h)
        
        oe.h = u.Quantity(h_m, u.km**2 / u.s)
        
        # >>> 5. Semi-major axis
        
        oe.a = u.Quantity(- 0.5 * mu / (0.5 * v_m**2 - mu / r_m), u.km)
        
        # >>> 6. Inclination
        
        inc: float = np.arccos(h[2] / h_m)
        
        oe.inc = u.Quantity(inc, u.rad).to(u.deg)
        
        # >>> 7. Line of nodes
        
        N: np.ndarray
        
        tol: float = 1e-6
        
        inc_min: float = np.deg2rad(1)
        
        if (inc <= 0.5 * np.pi):
        
            if inc > inc_min or (inc < inc_min and inc > tol):
                
                N = np.cross(np.array([0, 0, 1]), h)
                
            else:
            
                N = np.array([1, 0, 0])
                
        else:
            
            if inc < (np.pi - inc_min) or (inc > (np.pi - inc_min) and (np.pi - inc) > tol):
                
                N = np.cross(np.array([0, 0, 1]), h)
                
            else:
            
                N = np.array([1, 0, 0])
        
        # >>> 8.
        
        N_m: float = np.linalg.norm(N)
        
        # >>> 9. Right Ascension of the ascending node
        
        raan: float = np.arccos(N[0] / N_m)
        
        oe.raan = u.Quantity(raan if N[1] >= 0 else (2 * np.pi - raan), u.rad).to(u.deg)
        
        # >>> 10. Eccentricity vector
        
        ecc = 1 / mu * ((v_m**2 - mu / r_m) * r - r_m * v_r * v)
        
        # >>> 11. Eccentricity
        
        ecc_m: float = np.linalg.norm(ecc)
        
        oe.ecc = u.Quantity(ecc_m, u.dimensionless_unscaled)
        
        # >>> 12. Anomaly of the perigee
        
        argp: float = np.arccos(np.dot(N, ecc) / (N_m * ecc_m))
        
        oe.argp = u.Quantity(argp if ecc[2] >= 0 else (2 * np.pi - argp), u.rad).to(u.deg)
        
        # >>> 13. True anomaly
        
        nu: float = np.arccos(np.dot(ecc, r) / (ecc_m * r_m))
        
        oe.nu = u.Quantity(nu if v_r >= 0 else (2 * np.pi - nu), u.rad).to(u.deg)
        
        return oe
    
    @staticmethod
    def geocentric_equatorial_to_perifocal(attractor: bodies.Attractor, r : u.Quantity, v : u.Quantity) -> t.List[u.Quantity, u.Quantity]:
        """Geocentric Equatiorial Frame --> Perifocal Frame

        Args:
            attractor (bodies.Attractor): Main attractor
            r (u.Quantity): Position vector GEF
            v (u.Quantity): Velocity vector GEF

        Returns:
            t.List[u.Quantity, u.Quantity]: [r_PF, v_PF]
        """
        
        r_GEF: np.ndarray = r.to_value(u.km)
        v_GEF: np.ndarray = v.to_value(u.km / u.s)
        
        common.check_attractor(attractor)
        common.check_position_vector(r)
        common.check_velocity_vector(v)
        
        # >>> 1. Calculate orbital elements
        
        oe: OrbitalElements = Orbit3D.orbital_elements(attractor, r, v)
        
        inc: float = oe.inc.to_value(u.rad)
        raan: float = oe.raan.to_value(u.rad)
        argp: float = oe.argp.to_value(u.rad)
        
        # >>> 2. Rotation matrices
        
        R_3_raan: np.ndarray = np.array(
            [
                [ + np.cos(raan) , + np.sin(raan) , 0 ],
                [ - np.sin(raan) , + np.cos(raan) , 0 ],
                [ 0              , 0              , 1 ]
            ])
        
        R_1_inc: np.ndarray = np.array(
            [
                [ 1 , 0             , 0             ],
                [ 0 , + np.cos(inc) , + np.sin(inc) ],
                [ 0 , - np.sin(inc) , + np.cos(inc) ]
            ])
        
        R_3_argp: np.ndarray = np.array(
            [
                [ + np.cos(argp) , + np.sin(argp) , 0 ],
                [ - np.sin(argp) , + np.cos(argp) , 0 ],
                [ 0              , 0              , 1 ]
            ])
        
        R: np.ndarray = np.matmul(R_3_argp, np.matmul(R_1_inc, R_3_raan))
        
        # >>> 3. Calculate position and velocity in perifocal frame
        
        r_PF: u.Quantity = u.Quantity(np.matmul(R, r_GEF), u.km)
        v_PF: u.Quantity = u.Quantity(np.matmul(R, v_GEF), u.km / u.s)
        
        return [r_PF, v_PF]
    
    @staticmethod
    def perifocal_to_geocentric_equatorial(attractor: bodies.Attractor, oe : OrbitalElements) -> t.List[u.Quantity, u.Quantity] :
        """Perifocal Frame --> Geocentric Equatiorial Frame

        Args:
            attractor (bodies.Attractor): Main attractor
            oe (OrbitalElements): Orbital Elements

        Returns:
            t.List[u.Quantity, u.Quantity]: [r_GEF, v_GEF]
        """
        
        common.check_attractor(attractor)
        common.check_keplerian_parameters(oe.a.to_value(u.km),
                                          oe.ecc.to_value(),
                                          oe.inc.to_value(u.deg),
                                          oe.raan.to_value(u.deg),
                                          oe.argp.to_value(u.deg),
                                          oe.nu.to_value(u.deg))
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        h: float = oe.h.to_value(u.km**2 / u.s)
        a: float = oe.a.to_value(u.km)
        ecc: float = oe.ecc.to_value()
        inc: float = oe.inc.to_value(u.rad)
        raan: float = oe.raan.to_value(u.rad)
        argp: float = oe.argp.to_value(u.rad)
        nu: float = oe.nu.to_value(u.rad)
        
        p: float = (a * (1 - ecc**2)) if h == 0 else (h**2 / mu) # ? Parameter of the conic section
        
        # >>> 1. Calculate position in perifocal frame
        
        r_PF: np.ndarray = p / (1 + ecc * np.cos(nu)) * np.array([np.cos(nu), np.sin(nu), 0])
        
        # >>> 2. Calculate velocity in perifocal frame
        
        v_PF: np.ndarray = np.sqrt(mu / p) * np.array([-np.sin(nu), ecc + np.cos(nu), 0])
        
        # >>> 3. Rotation matrices
        
        R_3_raan: np.ndarray = np.array(
            [
                [ + np.cos(raan) , + np.sin(raan) , 0 ],
                [ - np.sin(raan) , + np.cos(raan) , 0 ],
                [ 0              , 0              , 1 ]
            ])
        
        R_1_inc: np.ndarray = np.array(
            [
                [ 1 , 0              , 0              ],
                [ 0 , + np.cos(inc) , + np.sin(inc) ],
                [ 0 , - np.sin(inc) , + np.cos(inc) ]
            ])
        
        R_3_argp: np.ndarray = np.array(
            [
                [ + np.cos(argp) , + np.sin(argp) , 0 ],
                [ - np.sin(argp) , + np.cos(argp) , 0 ],
                [ 0              , 0              , 1 ]
            ])
        
        R: np.ndarray = np.matmul(R_3_argp, np.matmul(R_1_inc, R_3_raan))
        
        # >>> 4. Calculate position and velocity in geocentric equatorial frame
        
        r_GEF: u.Quantity = u.Quantity(np.matmul(R.T, r_PF), u.km)
        v_GEF: u.Quantity = u.Quantity(np.matmul(R.T, v_PF), u.km / u.s)
        
        return [r_GEF, v_GEF]
    
    @staticmethod
    def perifocal_to_geocentric_equatorial_position_vector(oe : OrbitalElements, r_PF: u.Quantity) -> u.Quantity:
        """Perifocal Frame --> Geocentric Equatiorial Frame for a given position vector

        Args:
            oe (OrbitalElements): Orbital Elements
            r_PF (u.Quantity): Position vector in Perifocal Frame

        Returns:
            u.Quantity: r_GEF
        """
        
        common.check_keplerian_parameters(oe.a.to_value(u.km),
                                          oe.ecc.to_value(),
                                          oe.inc.to_value(u.deg),
                                          oe.raan.to_value(u.deg),
                                          oe.argp.to_value(u.deg),
                                          oe.nu.to_value(u.deg))
        
        common.check_position_vector(r_PF)
        
        inc: float = oe.inc.to_value(u.rad)
        raan: float = oe.raan.to_value(u.rad)
        argp: float = oe.argp.to_value(u.rad)
        
        R_3_raan: np.ndarray = np.array(
            [
                [ + np.cos(raan) , + np.sin(raan) , 0 ],
                [ - np.sin(raan) , + np.cos(raan) , 0 ],
                [ 0              , 0              , 1 ]
            ])
        
        R_1_inc: np.ndarray = np.array(
            [
                [ 1 , 0              , 0              ],
                [ 0 , + np.cos(inc) , + np.sin(inc) ],
                [ 0 , - np.sin(inc) , + np.cos(inc) ]
            ])
        
        R_3_argp: np.ndarray = np.array(
            [
                [ + np.cos(argp) , + np.sin(argp) , 0 ],
                [ - np.sin(argp) , + np.cos(argp) , 0 ],
                [ 0              , 0              , 1 ]
            ])
        
        R: np.ndarray = np.matmul(R_3_argp, np.matmul(R_1_inc, R_3_raan))
        
        r_GEF: u.Quantity = u.Quantity(np.matmul(R.T, r_PF.to_value(u.km)), u.km)
        
        return r_GEF
    
    @staticmethod
    def planet_oblateness_effect(attractor: bodies.Attractor, oe : OrbitalElements) -> t.List[u.Quantity, u.Quantity]:
        """Calculates the planet oblateness effect
        
        Args:
            attractor (bodies.Attractor): Main attractor
            oe (OrbitalElements): Orbital Elements

        Returns:
            t.List[u.Quantity, u.Quantity]: [dOmega_dt, domega_dt]
        """
        
        common.check_attractor(attractor)
        common.check_keplerian_parameters(oe.a.to_value(u.km),
                                          oe.ecc.to_value(),
                                          oe.inc.to_value(u.deg),
                                          oe.raan.to_value(u.deg),
                                          oe.argp.to_value(u.deg),
                                          oe.nu.to_value(u.deg))
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        R_E: float = bodies.BODIES[attractor].R_E.to_value(u.km)
        J_2: float = bodies.BODIES[attractor].J2 if bodies.BODIES[attractor].J2 is not None else 0
        
        a: float = oe.a.to_value(u.km)
        ecc: float = oe.ecc.to_value()
        inc: float = oe.inc.to_value(u.rad)
        
        # >>> Right Ascension of the ascending node variation
        
        d_raan_dt: float = - 3/2 * (np.sqrt(mu) * J_2 * R_E**2) / ((1 - ecc**2)**2 * a**(7/2)) * np.cos(inc)
        
        # >>> Anomaly/Argument of the perigee variation
        
        d_argp_dt: float = - 3/2 * (np.sqrt(mu) * J_2 * R_E**2) / ((1 - ecc**2)**2 * a**(7/2)) * (5/2 * np.sin(inc)**2 - 2)
        
        return [u.Quantity(d_raan_dt, u.rad / u.s).to(u.deg / u.s), u.Quantity(d_argp_dt, u.rad / u.s).to(u.deg / u.s)]
    
    @staticmethod
    def ground_track_propagation(attractor: bodies.Attractor, oe : OrbitalElements, dt : time.TimeDelta) -> t.List[u.Quantity, u.Quantity]:
        """Calculates the Ground Track for the given time step

        Args:
            attractor (bodies.Attractor): Main attractor
            oe (OrbitalElements): Orbital Elements
            dt (time.TimeDelta): Time step
            
        Returns:
            t.List[u.Quantity, u.Quantity]: [right ascension (-180; +180), declination (0; 360)]
        """
        
        common.check_attractor(attractor)
        common.check_keplerian_parameters(oe.a.to_value(u.km),
                                          oe.ecc.to_value(),
                                          oe.inc.to_value(u.deg),
                                          oe.raan.to_value(u.deg),
                                          oe.argp.to_value(u.deg),
                                          oe.nu.to_value(u.deg))
        
        body: bodies.Body = bodies.BODIES[attractor]
        
        ecc: float = oe.ecc.to_value()
        
        if ecc >= 1.0: return [u.Quantity(0, u.deg), u.Quantity(0, u.deg)]
        
        # >>> 1. Oblateness
        
        d_raan_dt, d_argp_dt = Orbit3D.planet_oblateness_effect(attractor, oe)
        
        # >>> 2. Initial condition
        
        r_GEF, v_GEF = Orbit3D.perifocal_to_geocentric_equatorial(attractor, oe)
        
        op: two_body_problem.OrbitParameters = two_body_problem.Orbit.cartesian_to_orbit_parameters(attractor, r_GEF, v_GEF)
        
        t_0: u.Quantity = 0.0 * u.s
        
        if ecc == 0:
            
            t_0 = orbital_position.OrbitalPosition.circular_orbit_time(oe.nu, op.period)
            
        elif ecc < 1.0:
            
            t_0 = orbital_position.OrbitalPosition.elliptical_orbit_time(oe.nu, op.period, oe.ecc.to_value())
        
        # >>> 3. Propagation
        
        t: u.Quantity = t_0.to(u.s) + dt.to(u.s)
            
        # >>> a) True anomaly
        
        nu: u.Quantity = 0.0 * u.rad
        
        if ecc == 0:
            
            nu = orbital_position.OrbitalPosition.circular_orbit_true_anomaly(t, op.period)
            
        elif ecc < 1.0:
            
            nu = orbital_position.OrbitalPosition.elliptical_orbit_true_anomaly(t, op.period, oe.ecc.to_value())
        
        # >>> b) New Orbital Elements
        
        oe.raan = oe.raan + d_raan_dt * dt.to(u.s)
        oe.argp = oe.argp + d_argp_dt * dt.to(u.s)
        oe.nu = nu
        
        oe.raan = common.wrap_angle(oe.raan.to_value(u.deg)) * u.deg
        oe.argp = common.wrap_angle(oe.argp.to_value(u.deg)) * u.deg
        
        # >>> c) New state
        
        r_GEF, v_GEF = Orbit3D.perifocal_to_geocentric_equatorial(attractor, oe)
        
        # >>> d) New position
        
        nu: float = common.wrap_angle(body.omega.to_value(u.deg / u.s) * (t.to_value(u.s) - t_0.to_value(u.s)), low=0, high=360)
        
        nu = np.deg2rad(nu)
        
        R_3_t = np.array(
            [
                [+ np.cos(nu) , + np.sin(nu), 0],
                [- np.sin(nu) , + np.cos(nu), 0],
                [0            , 0           , 1]
            ])
        
        # >>> e) Right Ascension and Declination
        
        alpha, delta = Orbit3D.right_ascension_declination(np.matmul(R_3_t, r_GEF.to_value(u.km)) * u.km)
        
        return [alpha - 180 * u.deg, delta]