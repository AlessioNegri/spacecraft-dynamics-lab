"""
Orbit Determination

Algorithms for orbit determination.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 5: Preliminary Orbit Determination
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as time
import astropy.units as u
import enum
import erfa
import numpy as np
import scipy.optimize as opt
import typing
import warnings

import astro.bodies as bd
import astro.common as cm
import astro.orbit_3d as o3d
import astro.lagrange_coefficients as lc

class OrbitDirection(enum.IntEnum):
    """Orbit direction type"""
    
    PROGRADE    = 0
    RETROGRADE  = 1

class OrbitDetermination():
    """Orbit Determination
    """
    
    def __init__(self):
        """Constructor
        """
        
        pass
    
    # --- STATIC ---
    
    @staticmethod
    def gibbs_method(attractor: bd.Attractor, r_1 : u.Quantity, r_2 : u.Quantity, r_3 : u.Quantity) -> o3d.OrbitalElements:
        """Gibbs method of orbit determination from tree position vectors

        Args:
            attractor (bd.Attractor): Main attractor
            r1 (u.Quantity): Position vector 1
            r2 (u.Quantity): Position vector 2
            r3 (u.Quantity): Position vector 3

        Returns:
            o3d.OrbitalElements: Orbital elements
        """
        
        r_1: np.ndarray = r_1.to_value(u.km)
        r_2: np.ndarray = r_2.to_value(u.km)
        r_3: np.ndarray = r_3.to_value(u.km)
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        cm.check_attractor(attractor)
        cm.check_position_vector(r_1)
        cm.check_position_vector(r_2)
        cm.check_position_vector(r_3)
        
        # >>> 1. Norm
        
        r_1_m: float = np.linalg.norm(r_1)
        r_2_m: float = np.linalg.norm(r_2)
        r_3_m: float = np.linalg.norm(r_3)
        
        # >>> 2. Cross products
        
        C_12: float = np.cross(r_1, r_2)
        C_23: float = np.cross(r_2, r_3)
        C_31: float = np.cross(r_3, r_1)
        
        # >>> 3. Verify
        
        u_r_1: np.ndarray = r_1 / r_1_m
        
        if np.dot(u_r_1, C_23) > 1e-5: return o3d.OrbitalElements()
        
        # >>> 4. Calculate N, D, and S vectors
        
        N: np.ndarray = r_1_m * C_23 + r_2_m * C_31 + r_3_m * C_12
        
        N_m: float = np.linalg.norm(N)
        
        D: np.ndarray = C_12 + C_23 + C_31
        
        D_m: float = np.linalg.norm(D)
        
        S: np.ndarray = r_1 * (r_2_m - r_3_m) + r_2 * (r_3_m - r_1_m) + r_3 * (r_1_m - r_2_m)
        
        # >>> 5. Calculate velocity at 2
        
        v_2: np.ndarray = np.sqrt(mu / (N_m * D_m)) * (np.cross(D, r_2) / r_2_m + S)
        
        # >>> 6. Compute the orbital elements
        
        oe: o3d.OrbitalElements = o3d.Orbit3D.orbital_elements(attractor=attractor, r=r_2 * u.km, v=v_2 * u.km / u.s)
        
        return oe
    
    @staticmethod
    def lambert(attractor: bd.Attractor, r_1 : u.Quantity, r_2 : u.Quantity, dt : time.TimeDelta,
                direction : OrbitDirection = OrbitDirection.PROGRADE)\
                    -> typing.Tuple[u.Quantity, u.Quantity, o3d.OrbitalElements, u.Quantity]:
        """Lambert's problem

        Args:
            attractor (bd.Attractor): Main attractor
            r_1 (u.Quantity): Position vector 1
            r_2 (u.Quantity): Position vector 2
            dt (time.TimeDelta): Delta time
            direction (OrbitDirection, optional): Type of orbit direction. Defaults to OrbitDirection.PROGRADE.

        Returns:
            list: [v_1, v_2, orbital elements, nu_2]
        """
        
        r_1: np.ndarray = r_1.to_value(u.km)
        r_2: np.ndarray = r_2.to_value(u.km)
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        cm.check_attractor(attractor)
        cm.check_position_vector(r_1)
        cm.check_position_vector(r_2)
        cm.check_time_delta(dt)
        
        dt: float = dt.to_value(u.s)
        
        # >>> 1. Norm
        
        r_1_m : float = np.linalg.norm(r_1)
        r_2_m: float = np.linalg.norm(r_2)
        
        # >>> 2. Delta theta
        
        delta_theta: float = 0.0
        
        temp: float = np.arccos((np.dot(r_1, r_2)) / (r_1_m * r_2_m))
        
        condition: float = np.cross(r_1, r_2)[2] # ? Z component
        
        if direction == OrbitDirection.PROGRADE:
            
            delta_theta = temp if condition >= 0 else (2 * np.pi - temp)
            
        elif direction == OrbitDirection.RETROGRADE:
            
            delta_theta = temp if condition < 0 else (2 * np.pi - temp)
            
        # >>> 3. Parameter A
        
        A: float = np.sin(delta_theta) * np.sqrt((r_1_m * r_2_m) / (1 - np.cos(delta_theta)))
        
        # >>> 4. Orbit type
        
        z_0: float = -4.0
        
        while OrbitDetermination._lambert_equation(z_0, mu, r_1_m, r_2_m, A, dt) < 0:
            
            z_0 = z_0 + 0.1
        
        z: float = 0.0
        
        # with warnings.catch_warnings():
            
            # warnings.filterwarnings("error", category=RuntimeWarning)
            # warnings.simplefilter("ignore", category=RuntimeWarning)
            # warnings.simplefilter("ignore", category=erfa.ErfaWarning)
            
        failed_result: np.ndarray = [np.ones(r_1.shape) * 100.0 * u.km / u.s,
                                     np.ones(r_2.shape) * 100.0 * u.km / u.s,
                                     o3d.OrbitalElements(),
                                     0.0 * u.deg]

        try:
            
            z = opt.newton(func=OrbitDetermination._lambert_equation,
                            x0=z_0,
                            fprime=OrbitDetermination._lambert_equation_first_derivative,
                            args=(mu, r_1_m, r_2_m, A, dt))
        
        # except Warning:
            
        #     return failed_result
        
        except Exception:
            
            return failed_result
        
        # >>> 5. Parameter y
        
        S_z: float = lc.LagrangeCoefficients.S(z)
        C_z: float = lc.LagrangeCoefficients.C(z)
        
        y: float = r_1_m + r_2_m + A * (z * S_z - 1) / np.sqrt(C_z)
        
        # >>> 6. Lagrange functions
        
        f: float = 1 - y / r_1_m
        
        g: float = A * np.sqrt(y / mu)
        
        dg_dt: float = 1 - y / r_2_m
        
        # >>> 7. Velocities
        
        v_1: np.ndarray = 1 / g * (r_2 - f * r_1)
        
        v_2: np.ndarray = 1 / g * (dg_dt * r_2 - r_1)
        
        # >>> 8. Orbital elements
        
        oe_1: o3d.OrbitalElements = o3d.Orbit3D.orbital_elements(attractor=attractor, r=r_1 * u.km, v=v_1 * u.km / u.s)
        
        oe_2: o3d.OrbitalElements = o3d.Orbit3D.orbital_elements(attractor=attractor, r=r_2 * u.km, v=v_2 * u.km / u.s)
        
        return [v_1 * u.km / u.s, v_2 * u.km / u.s, oe_1, oe_2.nu]
    
    @staticmethod
    def timestamp_2_julian_day(timestamp: time.Time) -> float:
        """Convert the given timestamp in Julian day

        Args:
            timestamp (time.Time): Timestamp

        Returns:
            float: Julian day number [numer of days]
        """
        
        cm.check_time(time_=timestamp)
        
        year: int = timestamp.ymdhms.year
        month: int = timestamp.ymdhms.month
        day: int = timestamp.ymdhms.day
        hour: int = timestamp.ymdhms.hour
        minute: int = timestamp.ymdhms.minute
        second: int = timestamp.ymdhms.second
        
        # >>> 1. Checks
        
        if year < 1901 or year > 2099: raise ValueError("'year' must be in range 1901 - 2099")
        
        # >>> 2. Julian day at 0 h UT
        
        J0: float = 367 * year - int(7/4 * (year + int((month + 9) / 12))) + int(275/9 * month) + day + 1_721_013.5
        
        # >>> 3. Univeral Time
        
        UT: float = hour + minute / 60 + second / 3600
        
        # >>> 4. Julian day number
        
        return J0 + UT / 24
    
    @staticmethod
    def frac_day_2_hms(frac_day : float) -> typing.List[int]:
        """Splits the fractional day in hour - minute - second

        Args:
            frac_day (float): Fraction of day

        Returns:
            list: [hour, minute, second]
        """
        
        temp: float = frac_day * 24.0
        
        hour: int = int(np.fix(temp))
        
        minute: int = int(np.fix((temp - hour) * 60))
        
        second: int = int((temp - hour - minute / 60) * 3600)
        
        return [hour, minute, second]
    
    @staticmethod
    def julian_day_2_timestamp(julian_day : float) -> time.Time:
        """Convert the Julian day in timestamp (Fliegel–Van Flandern algorithm)

        Args:
            julian_day (float): Julian Day

        Returns:
            time.Time: Timestamp
        """
        
        # >>> 1. Shift the Julian Day and extract the integer part
        
        # ? 0.5 shifts the start of the day from noon (JD convention) to midnight
        # ? 32044 converts from Julian calendar to the proleptic Gregorian calendar epoch
        
        j: int = np.floor(julian_day + 0.5) + 32_044
        
        # >>> 2. Break the integer day into Gregorian cycles
        
        # ? Decompose the integer day into cycles of:
        # ? - 400‑year Gregorian cycles (except every 400 years → leap again)
        # ? - 100‑year subcycles (except every 100 years → not leap)
        # ? - 4‑year subcycles (every 4 years → leap year)
        # ? - 1‑year subcycles
        
        g: int = np.floor(j / 146_097) # ? Number of 400-year cycles
        
        dg: int = np.mod(j, 146_097)
        
        c: int = np.floor((np.floor(dg / 36_524) + 1) * 3/4)
        
        dc: int = dg - c * 36_524
        
        b: int = np.floor(dc / 1_461) # ? Number of 4-year cycles
        
        db: int = np.mod(dc, 1_461)
        
        a: int = np.floor((np.floor(db / 365) + 1) * 3/4)
        
        da: int = db - a * 365
        
        # >>> 3. Convert the year offset, month index, and day index in year, mont and day (Gregorian date)
        
        y: int = g * 400 + c * 100 + b * 4 + a
        
        m: int = np.floor((da * 5 + 308) / 153) - 2
        
        d: int = da - np.floor((m + 4) * 153/5) + 122
        
        year: int = int(y - 4800 + np.floor((m + 2) / 12))
        
        month: int = int(np.mod((m + 2), 12) + 1)
        
        day: int = int(np.floor(d + 1))
        
        # >>> 4. Extract the fractional day → hour, minute, second
        
        hour, minute, second = OrbitDetermination.frac_day_2_hms(np.mod(julian_day + 0.5, np.floor(julian_day + 0.5)))
        
        # >>> 5. Create the timestamp
        
        timestamp: time.Time = time.Time(
            {
                'year': year,
                'month': month,
                'day': day,
                'hour': hour,
                'minute': minute,
                'second': second
            })
        
        return timestamp
    
    @staticmethod
    def local_sidereal_time(timestamp: time.Time, longitude : u.Quantity) -> u.Quantity:
        """Calculate the local sidereal time from given timestamp and longitude

        Args:
            timestamp (time.Time): Timestamp
            longitude (u.Quantity): East longitude

        Returns:
            u.Quantity: Local sidereal time [deg]
        """
        
        cm.check_time(time_=timestamp)
        cm.check_angle(longitude.to_value(u.deg))
        
        year: int = timestamp.ymdhms.year
        month: int = timestamp.ymdhms.month
        day: int = timestamp.ymdhms.day
        hour: int = timestamp.ymdhms.hour
        minute: int = timestamp.ymdhms.minute
        second: int = timestamp.ymdhms.second
        
        # >>> 0. Checks
        
        if year < 1901 or year > 2099: raise ValueError("'year' must be in range 1901 - 2099")
        
        UT: float = hour + minute / 60 + second / 3600 # ? Univeral Time
        
        J_2000: int = 2_451_545
        
        # >>> 1. Julian day at 0 h UT
        
        J0: float = 367 * year - int(7/4 * (year + int((month + 9) / 12 ))) + int(275/9 * month) + day + 1_721_013.5
        
        # >>> 2. Time between J0 and J2000
        
        T0: float = (J0 - J_2000) / 36_525
        
        # >>> 3. Greenwich sideral time at 0 h UT [deg]
        
        theta_G0: float = 100.4606184 + 36000.77004 * T0 + 0.000387933 * T0**2 - 2.583e-8 * T0**3
        
        theta_G0 = cm.wrap_angle(theta_G0)
        
        # >>> 4. Greenwich sideral time [deg]
        
        theta_G: float = theta_G0 + 360.98564724 * UT / 24
        
        # >>> 5. Local sidereal time
        
        theta: float = theta_G + longitude.to_value(u.deg)
        
        theta = cm.wrap_angle(theta)
        
        return theta * u.deg
    
    @staticmethod
    def geocentric_equatorial_position_vector(attractor: bd.Attractor,
                                              theta : u.Quantity,
                                              phi : u.Quantity,
                                              H : u.Quantity = 0 * u.km) -> u.Quantity:
        """Geocentric Equatorial Frame position vector of the observer

        Args:
            attractor (bd.Attractor): Main attractor
            theta (u.Quantity): Local sidereal time
            phi (u.Quantity): Latitude
            H (u.Quantity, optional): Elevation above sea level. Defaults to 0 km.

        Returns:
            u.Quantity: Position vector
        """
        
        R_E: float = bd.BODIES[attractor].R_E.to_value(u.km)
        
        f: float = bd.BODIES[attractor].f if bd.BODIES[attractor].f != None else 0
        
        theta: float = theta.to_value(u.rad)
        
        phi: float = phi.to_value(u.rad)
        
        H: float = H.to_value(u.km)
        
        cm.check_attractor(attractor)
        cm.check_angle(theta)
        cm.check_angle(phi)
        
        if H < 0: raise ValueError("'H' must be > 0")
        
        A = (R_E / np.sqrt(1 - (2 * f - f**2) * np.sin(phi)**2) + H) * np.cos(phi)
        
        B = (R_E * (1 - f)**2 / np.sqrt(1 - (2 * f - f**2) * np.sin(phi)**2) + H) * np.sin(phi)
        
        R: u.Quantity = np.array([A * np.cos(theta), A * np.sin(theta), B]) * u.km
        
        return R
    
    @staticmethod
    def topocentric_equatorial_position_vector(attractor: bd.Attractor,
                                               r : u.Quantity,
                                               theta : u.Quantity,
                                               phi : u.Quantity,
                                               H : u.Quantity = 0 * u.km) -> u.Quantity:
        """Geocentric Equatorial Frame --> Topocentric Equatorial Frame

        Args:
            attractor (bd.Attractor): Main attractor
            r (u.Quantity): Geocentric equatorial position vector of the target
            theta (u.Quantity): Local sidereal time
            phi (u.Quantity): Latitude
            H (u.Quantity, optional): Elevation above sea level. Defaults to 0.

        Returns:
            u.Quantity: Position vector
        """
        
        cm.check_position_vector(r.to_value(u.km))
        
        # >>> 1. Geocentric position vector of the site
        
        R: u.Quantity = OrbitDetermination.geocentric_equatorial_position_vector(attractor=attractor,
                                                                                 theta=theta,
                                                                                 phi=phi,
                                                                                 H=H)
        
        # >>> 2. Topocentric equatorial position vector
        
        rho: u.Quantity = r - R
        
        return rho
    
    @staticmethod
    def topocentric_horizon_position_vector(attractor: bd.Attractor,
                                            r : u.Quantity,
                                            theta : u.Quantity,
                                            phi : u.Quantity,
                                            H : u.Quantity = 0 * u.km) -> typing.List[u.Quantity]:
        """Geocentric Equatorial Frame --> Topocentric Horizon Frame

        Args:
            attractor (bd.Attractor): Main attractor
            r (u.Quantity): Geocentric equatorial position vector of the target
            theta (u.Quantity): Local sidereal time
            phi (u.Quantity): Latitude
            H (u.Quantity, optional): Elevation above sea level. Defaults to 0.

        Returns:
            typing.List[u.Quantity]: [Position vector rho, Azimuth A, Elevation a]
        """
        
        # >>> 1. Topocentric equatorial position vector
        
        rho: u.Quantity = OrbitDetermination.topocentric_equatorial_position_vector(attractor=attractor,
                                                                                    r=r,
                                                                                    theta=theta,
                                                                                    phi=phi,
                                                                                    H=H)
        
        # >>> 2. Topocentric horizon position vector
        
        theta: float = theta.to_value(u.rad)
        
        phi: float = phi.to_value(u.rad)
        
        Q_Xx: np.ndarray = np.array(
            [
                [ -np.sin(theta)               , np.cos(theta)                , 0           ],
                [ -np.sin(phi) * np.cos(theta) , -np.sin(phi) * np.sin(theta) , np.cos(phi) ],
                [ np.cos(phi) * np.cos(theta)  , np.cos(phi) * np.sin(theta)  , np.sin(phi) ]
            ])
        
        rho: np.ndarray = np.matmul(Q_Xx, rho.to_value(u.km))
        
        # >>> 3. Azimuth and Elevation
        
        rho_h: np.ndarray = rho / np.linalg.norm(rho)
        
        a: float = np.arcsin(rho_h[2]) # ? Elevation
        
        A: float = np.arctan2(rho_h[0] / np.cos(a), rho_h[1] / np.cos(a)) # ? Azimuth
        
        return [rho * u.km, (A * u.rad).to(u.deg), (a * u.rad).to(u.deg)]
    
    @staticmethod
    def topocentric_equatorial_right_ascension_declination(attractor: bd.Attractor,
                                                           theta : u.Quantity,
                                                           phi : u.Quantity,
                                                           A : u.Quantity,
                                                           a : u.Quantity) -> typing.List[u.Quantity]:
        """Topocentric Horizone Frame --> Topocentric Equatorial Frame

        Args:
            attractor (bd.Attractor): Main attractor
            theta (u.Quantity): Local sidereal time
            phi (u.Quantity): Latitude
            A (u.Quantity): Azimuth
            a (u.Quantity): elevation

        Returns:
            typing.List[u.Quantity]: [Position vector rho, Right ascension alpha, Declination delta]
        """
        
        theta: float = theta.to_value(u.rad)
        
        phi: float = phi.to_value(u.rad)
        
        A: float = A.to_value(u.rad)
        
        a: float = a.to_value(u.rad)
        
        cm.check_attractor(attractor)
        cm.check_angle(theta)
        cm.check_angle(phi)
        cm.check_angle(A)
        cm.check_angle(a)
        
        # >>> 1. Topocentric horizon position vector
        
        Q_xX: np.ndarray = np.array(
            [
                [ -np.sin(theta) , -np.sin(phi) * np.cos(theta) , np.cos(phi) * np.cos(theta) ],
                [ np.cos(theta)  , -np.sin(phi) * np.sin(theta) , np.cos(phi) * np.sin(theta) ],
                [ 0              , np.cos(phi)                  , np.sin(phi)                 ]
            ])
        
        rho_h: np.ndarray = np.array([np.cos(a) * np.sin(A), np.cos(a) * np.cos(A), np.sin(a)])
        
        # >>> 2. Topocentric equatorial position vector
        
        rho: np.ndarray = np.matmul(Q_xX, rho_h)
        
        # >>> 3. Right Ascension and Declination
        
        alpha, delta = o3d.Orbit3D.right_ascension_declination(r=rho * u.km)
        
        return [rho * u.dimensionless_unscaled, alpha, delta]
    
    @staticmethod
    def predict_from_angle_range(attractor: bd.Attractor,
                                 rho : u.Quantity,
                                 A : u.Quantity,
                                 a : u.Quantity,
                                 drho_dt : u.Quantity,
                                 dA_dt : u.Quantity,
                                 da_dt : u.Quantity,
                                 theta : u.Quantity,
                                 phi : u.Quantity,
                                 H : u.Quantity = 0 * u.km) -> typing.List[u.Quantity]:
        """Predicts the geocentric position and velocity vectors from angle and range measurements

        Args:
            attractor (bd.Attractor): Main attractor
            rho (u.Quantity): Slant range
            A (u.Quantity): Azimuth
            a (u.Quantity): Elevation
            drho_dt (u.Quantity): Range rate
            dA_dt (u.Quantity): Azimuth rate
            da_dt (u.Quantity): Elevation rate
            theta (u.Quantity): Local sidereal time
            phi (u.Quantity): Latitude
            H (u.Quantity, optional): Elevation above sea level. Defaults to 0.

        Returns:
            typing.List[u.Quantity]: [r, v]
        """
        
        # >>> 1. Geocentric position vector of the site
        
        R: u.Quantity = OrbitDetermination.geocentric_equatorial_position_vector(attractor=attractor, theta=theta, phi=phi, H=H)
        
        rho: float = rho.to_value(u.km)
        
        A: float = A.to_value(u.rad)
        
        a: float = a.to_value(u.rad)
        
        drho_dt: float = drho_dt.to_value(u.km / u.s)
        
        dA_dt: float = dA_dt.to_value(u.rad / u.s)
        
        da_dt: float = da_dt.to_value(u.rad / u.s)
        
        omega: float = bd.BODIES[attractor].omega.to_value(u.rad / u.s)
        
        theta: float = theta.to_value(u.rad)
        
        phi: float = phi.to_value(u.rad)
        
        H: float = H.to_value(u.km)
        
        cm.check_angle(theta)
        cm.check_angle(phi)
        cm.check_angle(A)
        cm.check_angle(a)
        
        # >>> 2. Topocentric declination
        
        delta: float = np.arcsin(np.cos(phi) * np.cos(A) * np.cos(a) + np.sin(phi) * np.sin(a))
        
        # >>> 3. Topocentric right ascension
        
        h: float = 0.0 # ? Hour Angle
        
        if A > 0 and A < np.pi:
            
            h = 2* np.pi - np.arccos((np.cos(phi) * np.sin(a) - np.sin(phi) * np.cos(A) * np.cos(a)) / np.cos(delta))
            
        else:
            
            h = np.arccos((np.cos(phi) * np.sin(a) - np.sin(phi) * np.cos(A) * np.cos(a)) / np.cos(delta))
        
        alpha: float = theta - h
        
        # >>> 4. Direction cosine unit vector
        
        rho_h: np.ndarray = np.array([np.cos(delta) * np.cos(alpha), np.cos(delta) * np.sin(alpha), np.sin(delta)])
        
        # >>> 5. Geocentric position vector
        
        r: np.ndarray = R.to_value(u.km) + rho * rho_h
        
        # >>> 6. Inertial velocity of the site
        
        dR_dt: np.ndarray = np.cross(np.array([0, 0, omega]), R.to_value(u.km))
        
        # >>> 7. Declination rate
        
        ddelta_dt: float = 1 / np.cos(delta) * (-dA_dt * np.cos(phi) * np.sin(A) * np.cos(a) + \
            da_dt * (np.sin(phi) * np.cos(a) - np.cos(phi) * np.cos(A) * np.sin(a)))
        
        # >>> 8. Right ascension rate
        
        dalpha_dt: float = omega + (dA_dt * np.cos(A) * np.cos(a) - da_dt * np.sin(A) * np.sin(a) + \
            ddelta_dt * np.sin(A) * np.cos(a) * np.tan(delta)) / \
                (np.cos(phi) * np.sin(a) - np.sin(phi) * np.cos(A) * np.cos(a))
        
        # >>> 9. Direction cosine rate unit vector
        
        drho_h_dt: np.ndarray = np.array([
            -dalpha_dt * np.sin(alpha) * np.cos(delta) - ddelta_dt * np.cos(alpha) * np.sin(delta),
            dalpha_dt * np.cos(alpha) * np.cos(delta) - ddelta_dt * np.sin(alpha) * np.sin(delta),
            ddelta_dt * np.cos(delta)])
        
        # >>> 10 Geocentric velocity vector
        
        v = dR_dt + drho_dt * rho_h + rho * drho_h_dt
        
        return [r * u.km, v * u.km / u.s]
    
    @staticmethod
    def predict_from_gauss_method(attractor: bd.Attractor,
                                  phi : u.Quantity,
                                  theta : u.Quantity,
                                  alpha : u.Quantity,
                                  delta : u.Quantity,
                                  t : u.Quantity,
                                  H : u.Quantity = 0 * u.km) -> typing.List[u.Quantity]:
        """Predict position and velocity with the Gauss method

        Args:
            attractor (bd.Attractor): Main attractor
            phi (u.Quantity): Latitude
            theta (u.Quantity): List of 3 local sidereal times
            alpha (u.Quantity): List of 3 right ascensions
            delta (u.Quantity): List of 3 declinations
            t (u.Quantity): List of 3 observation times
            H (u.Quantity, optional): Elevation above sea level. Defaults to 0.

        Returns:
            typing.List[u.Quantity]: Parameters
        """
        
        if theta.shape != (3,): raise ValueError("'theta' must have shape = (3,)")
        
        if alpha.shape != (3,): raise ValueError("'alpha' must have shape = (3,)")
        
        if delta.shape != (3,): raise ValueError("'delta' must have shape = (3,)")
        
        if t.shape != (3,): raise ValueError("'t' must have shape = (3,)")
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        cm.check_attractor(attractor)
        
        alpha: np.ndarray = alpha.to_value(u.rad)
        
        delta: np.ndarray = delta.to_value(u.rad)
        
        t: np.ndarray = t.to_value(u.s)
        
        # >>> 0. Geocentric position vector of the site - Topocentric Horizon position vector
        
        R_1: np.ndarray = OrbitDetermination.geocentric_equatorial_position_vector(attractor, theta[0], phi, H).to_value(u.km)
        R_2: np.ndarray = OrbitDetermination.geocentric_equatorial_position_vector(attractor, theta[1], phi, H).to_value(u.km)
        R_3: np.ndarray = OrbitDetermination.geocentric_equatorial_position_vector(attractor, theta[2], phi, H).to_value(u.km)
        
        rho_h_1: np.ndarray = np.array([ np.cos(delta[0]) * np.cos(alpha[0]), np.cos(delta[0]) * np.sin(alpha[0]), np.sin(delta[0]) ])
        rho_h_2: np.ndarray = np.array([ np.cos(delta[1]) * np.cos(alpha[1]), np.cos(delta[1]) * np.sin(alpha[1]), np.sin(delta[1]) ])
        rho_h_3: np.ndarray = np.array([ np.cos(delta[2]) * np.cos(alpha[2]), np.cos(delta[2]) * np.sin(alpha[2]), np.sin(delta[2]) ])
        
        # >>> 1. Time intervals
        
        tau_1: float = t[0] - t[1]
        tau_3: float = t[2] - t[1]
        tau: float = tau_3 - tau_1
        
        # >>> 2. Cross products
        
        p_1: np.ndarray = np.cross(rho_h_2, rho_h_3)
        p_2: np.ndarray = np.cross(rho_h_1, rho_h_3)
        p_3: np.ndarray = np.cross(rho_h_1, rho_h_2)
        
        # >>> 3. D_0
        
        D_0: float = np.dot(rho_h_1, p_1)
        
        # >>> 4. D matrix
        
        D: np.ndarray = np.array(
            [
                [ np.dot(R_1, p_1), np.dot(R_1, p_2), np.dot(R_1, p_3) ],
                [ np.dot(R_2, p_1), np.dot(R_2, p_2), np.dot(R_2, p_3) ],
                [ np.dot(R_3, p_1), np.dot(R_3, p_2), np.dot(R_3, p_3) ]
            ]
        )
        
        # >>> 5. Calculate parameters A and B
        
        A: float = 1 / D_0 * (-D[0,1] * tau_3 / tau + D[1,1] + D[2,1] * tau_1 / tau)
        
        B: float = 1 / (6 * D_0) * (D[0,1] * (tau_3**2 - tau**2) * tau_3 / tau + D[2,1] * (tau**2 - tau_1**2) * tau_1 / tau)
        
        # >>> 6. Calculate E
        
        E: float = np.dot(R_2, rho_h_2)
        
        # >>> 7. Calculate a, b, and c
        
        a: float = - (A**2 + 2 * A * E + np.linalg.norm(R_2)**2)
        
        b: float = - 2 * mu * B * (A + E)
        
        c: float = - mu**2 * B**2
        
        # >>> 8. Find r_2
        
        f: callable = lambda x: x**8 + a * x**6 + b * x**3 + c
        
        dfdt: callable = lambda x: 8 * x**7 + 6 * a * x**5 + 3 * b * x**2
        
        r_2_m: float = opt.newton(f, x0=10000, fprime=dfdt, maxiter=100, tol=1e-8)
        
        # >>> 9. Slant ranges
        
        rho_1: float = 1 / D_0 * \
            ((6 * (D[2,0] * tau_1 / tau_3 + D[1,0] * tau / tau_3) * r_2_m**3 + \
                mu * D[2,0] * (tau**2 - tau_1**2) * tau_1 / tau_3 ) /
             (6 * r_2_m**3 + mu * (tau**2 - tau_3**2)) - D[0,0])
        
        rho_2: float = A + mu * B / r_2_m**3
        
        rho_3: float = 1 / D_0 * \
            ((6 * (D[0,2] * tau_3 / tau_1 - D[1,2] * tau / tau_1) * r_2_m**3 + \
                mu * D[0,2] * (tau**2 - tau_3**2) * tau_3 / tau_1 ) /
             (6 * r_2_m**3 + mu * (tau**2 - tau_1**2)) - D[2,2])
        
        # >>> 10. Geocentric position vector of the target
        
        r_1: np.ndarray = R_1 + rho_1 * rho_h_1
        r_2: np.ndarray = R_2 + rho_2 * rho_h_2
        r_3: np.ndarray = R_3 + rho_3 * rho_h_3
        
        # >>> 11. Lagrange coefficients
        
        f_1: float = 1 - 1/2 * mu / r_2_m**3 * tau_1**2
        f_3: float = 1 - 1/2 * mu / r_2_m**3 * tau_3**2
        g_1: float = tau_1 - 1/6 * mu / r_2_m**3 * tau_1**3
        g_3: float = tau_3 - 1/6 * mu / r_2_m**3 * tau_3**3
        
        # >>> 12. Position and velocity vectors
        
        v_2: np.ndarray = 1 / (f_1 * g_3 - f_3 * g_1) * (-f_3 * r_1 + f_1 * r_3)
        
        return [r_2 * u.km, v_2 * u.km / u.s]
    
    @staticmethod
    def predict_from_gauss_method_extended(attractor: bd.Attractor,
                                           phi : u.Quantity,
                                           theta : u.Quantity,
                                           alpha : u.Quantity,
                                           delta : u.Quantity,
                                           t : u.Quantity,
                                           H : u.Quantity = 0 * u.km) -> typing.List[u.Quantity]:
        """Predict position and velocity with the extended Gauss method

        Args:
            attractor (bd.Attractor): Main attractor
            phi (u.Quantity): Latitude
            theta (u.Quantity): List of 3 local sidereal times
            alpha (u.Quantity): List of 3 right ascensions
            delta (u.Quantity): List of 3 declinations
            t (u.Quantity): List of 3 observation times
            H (u.Quantity, optional): Elevation above sea level. Defaults to 0.

        Returns:
            typing.List[u.Quantity]: [Position, Velocity]
        """
        
        # >>> 0. Gauss method
        
        r_2, v_2 = OrbitDetermination.predict_from_gauss_method(attractor, phi, theta, alpha, delta, t, H)
        
        r_2: np.ndarray = r_2.to_value(u.km)
        v_2: np.ndarray = v_2.to_value(u.km / u.s)
        
        R_1: np.ndarray = OrbitDetermination.geocentric_equatorial_position_vector(attractor, theta[0], phi, H).to_value(u.km)
        R_2: np.ndarray = OrbitDetermination.geocentric_equatorial_position_vector(attractor, theta[1], phi, H).to_value(u.km)
        R_3: np.ndarray = OrbitDetermination.geocentric_equatorial_position_vector(attractor, theta[2], phi, H).to_value(u.km)
        
        alpha: np.ndarray = alpha.to_value(u.rad)
        delta: np.ndarray = delta.to_value(u.rad)
        
        rho_h_1: np.ndarray = np.array([ np.cos(delta[0]) * np.cos(alpha[0]), np.cos(delta[0]) * np.sin(alpha[0]), np.sin(delta[0]) ])
        rho_h_2: np.ndarray = np.array([ np.cos(delta[1]) * np.cos(alpha[1]), np.cos(delta[1]) * np.sin(alpha[1]), np.sin(delta[1]) ])
        rho_h_3: np.ndarray = np.array([ np.cos(delta[2]) * np.cos(alpha[2]), np.cos(delta[2]) * np.sin(alpha[2]), np.sin(delta[2]) ])
        
        p_1: np.ndarray = np.cross(rho_h_2, rho_h_3)
        p_2: np.ndarray = np.cross(rho_h_1, rho_h_3)
        p_3: np.ndarray = np.cross(rho_h_1, rho_h_2)
        
        D_0: float = np.dot(rho_h_1, p_1)
        
        D: np.ndarray = np.array(
            [
                [ np.dot(R_1, p_1), np.dot(R_1, p_2), np.dot(R_1, p_3) ],
                [ np.dot(R_2, p_1), np.dot(R_2, p_2), np.dot(R_2, p_3) ],
                [ np.dot(R_3, p_1), np.dot(R_3, p_2), np.dot(R_3, p_3) ]
            ]
        )
        
        mu: float = bd.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        f_1_prev: float = 0
        f_3_prev: float = 0
        g_1_prev: float = 0
        g_3_prev: float = 0
        
        rho_1_prev: float = np.inf
        rho_2_prev: float = np.inf
        rho_3_prev: float = np.inf
        
        tol: float = 1e-6
        
        iteration: int = 1
        
        max_iteration: int = 100
        
        while True:
            
            # >>> 1. Magnitudes
            
            r_2_m: float = np.linalg.norm(r_2)
            v_2_m: float = np.linalg.norm(v_2)
            
            # >>> 2. Alpha
            
            Alpha: float = 2 / r_2_m - v_2_m**2 / mu
            
            # >>> 3. Radial velocity
            
            v_r_2: float = np.dot(v_2, r_2) / r_2_m
            
            # >>> 4. Universal variables
            
            chi_1: u.Quantity = lc.LagrangeCoefficients.universal_kepler_solution(attractor=attractor,
                                                                                  r_0=r_2_m * u.km,
                                                                                  v_r_0=v_r_2 * u.km / u.s,
                                                                                  alpha=Alpha,
                                                                                  dt=time.TimeDelta(t[0] - t[1], format='sec'))
            
            chi_3: u.Quantity = lc.LagrangeCoefficients.universal_kepler_solution(attractor=attractor,
                                                                                  r_0=r_2_m * u.km,
                                                                                  v_r_0=v_r_2 * u.km / u.s,
                                                                                  alpha=Alpha,
                                                                                  dt=time.TimeDelta(t[2] - t[1], format='sec'))
            
            # >>> 5. Lagrange coefficients
            
            f_1, g_1 = lc.LagrangeCoefficients.lagrange_coefficients(attractor=attractor,
                                                                     r_0=r_2_m * u.km,
                                                                     alpha=Alpha,
                                                                     dt=time.TimeDelta(t[0] - t[1], format='sec'),
                                                                     chi=chi_1.to_value(u.km**0.5))
            
            f_1 = float(f_1.to_value(u.dimensionless_unscaled))
            g_1 = float(g_1.to_value(u.s))
            
            f_3, g_3 = lc.LagrangeCoefficients.lagrange_coefficients(attractor=attractor,
                                                                     r_0=r_2_m * u.km,
                                                                     alpha=Alpha,
                                                                     dt=time.TimeDelta(t[2] - t[1], format='sec'),
                                                                     chi=chi_3.to_value(u.km**0.5))
            
            f_3 = float(f_3.to_value(u.dimensionless_unscaled))
            g_3 = float(g_3.to_value(u.s))
            
            # >>> 6. Calculate parameters
            
            f_1 = (f_1 + f_1_prev) / 2 if f_1_prev != 0 else f_1
            f_3 = (f_3 + f_3_prev) / 2 if f_3_prev != 0 else f_3
            g_1 = (g_1 + g_1_prev) / 2 if g_1_prev != 0 else g_1
            g_3 = (g_3 + g_3_prev) / 2 if g_3_prev != 0 else g_3
            
            c_1: float = g_3 / (f_1 * g_3 - f_3 * g_1)
            c_3: float = -g_1 / (f_1 * g_3 - f_3 * g_1)
            
            f_1_prev = f_1
            f_3_prev = f_3
            g_1_prev = g_1
            g_3_prev = g_3
            
            # >>> 7. Updated slant ranges
            
            rho_1 = 1 / D_0 * (-D[0,0] + D[1,0] / c_1 - D[2,0] * c_3 / c_1)
            rho_2 = 1 / D_0 * (-c_1 * D[0,1] + D[1,1] - c_3 * D[2,1])
            rho_3 = 1 / D_0 * (-D[0,2] * c_1 / c_3 + D[1,2] / c_3 - D[2,2])
            
            # >>> 8. Geocentric position vector of the target
        
            r_1 = R_1 + rho_1 * rho_h_1
            r_2 = R_2 + rho_2 * rho_h_2
            r_3 = R_3 + rho_3 * rho_h_3
            
            # >>> 9. Velocity vector
            
            v_2 = 1 / (f_1 * g_3 - f_3 * g_1) * (-f_3 * r_1 + f_1 * r_3)
            
            if iteration > max_iteration:
                
                break
            
            if np.abs(rho_1 - rho_1_prev) <= tol and np.abs(rho_2 - rho_2_prev) <= tol and np.abs(rho_3 - rho_3_prev) <= tol:
                
                break
            
            rho_1_prev = rho_1
            rho_2_prev = rho_2
            rho_3_prev = rho_3
            
            iteration += 1
        
        # >>> 10. Position and velocity vectors
        
        return [r_2 * u.km, v_2 * u.km / u.s]
    
    # --- PRIVATE ---
    
    @staticmethod
    def _lambert_equation(z : float, mu: float, r_1 : float, r_2 : float, A : float, dt : float) -> float:
        """Lambert equation

        Args:
            z (float): Variable
            mu (float): Gravitational constant [km^3 / s^2]
            r_1 (float): Position 1
            r_2 (float): Position 2
            A (float): Parameter A
            dt (float): Delta time

        Returns:
            float: Result
        """
        
        S_z: float = lc.LagrangeCoefficients.S(z)
        C_z: float = lc.LagrangeCoefficients.C(z)
        
        y: float = max(r_1 + r_2 + A * (z * S_z - 1) / np.sqrt(C_z), 0)
        
        return (y / C_z)**(3/2) * S_z + A * np.sqrt(y) - np.sqrt(mu) * dt
    
    @staticmethod
    def _lambert_equation_first_derivative(z : float, mu: float, r_1 : float, r_2 : float, A : float, dt : float) -> float:
        """Lambert equation first derivative

        Args:
            z (float): Variable
            mu (float): Gravitational constant [km^3 / s^2]
            r_1 (float): Position 1
            r_2 (float): Position 2
            A (float): Parameter A
            dt (float): Delta time

        Returns:
            float: Result
        """
        
        S_0: float = lc.LagrangeCoefficients.S(0)
        C_0: float = lc.LagrangeCoefficients.C(0)
        S_z: float = lc.LagrangeCoefficients.S(z)
        C_z: float = lc.LagrangeCoefficients.C(z)
        
        y_0: float = r_1 + r_2 + A * (0 * S_0 - 1) / np.sqrt(C_0)
        
        y: float = r_1 + r_2 + A * (z * S_z - 1) / np.sqrt(C_z)
        
        if z == 0:
            
            return np.sqrt(2) / 40 * y_0**(3/2) + A / 8 * (np.sqrt(y_0) + A * 1 / np.sqrt(2 * y_0))
        
        else:
            
            return (y / C_z)**(3/2) * (1 / (2 * z) * (C_z - 3/2 * S_z / C_z) + 3/4 * S_z**2 / C_z) +\
                A / 8 * (3 * S_z / C_z * np.sqrt(y) + A * np.sqrt(C_z / y))