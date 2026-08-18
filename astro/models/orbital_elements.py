import astropy.units as u
import dataclasses as dc
import numpy as np

import astro.bodies as bodies
import astro.common as common

@dc.dataclass
class OrbitalElements:
    """
    Classical Orbital Elements
        - semimajor axis (a)
        - eccentricity (e)
        - inclination (i)
        - right ascension of ascending node (Ω)
        - argument of periapsis (ω)
        - time after periapsis passage (t - t_p) or mean anomaly (M = n * (t - t_p))
    
    Keplerian Elements
        - semimajor axis (a)
        - eccentricity (e)
        - inclination (i)
        - right ascension of ascending node (Ω)
        - argument of periapsis (ω)
        - true anomaly (θ) or eccentric anomaly (E) or hyperbolic anomaly (F) or universal anomaly (G)
    """
    
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
        
        if self.eccentricity < 1:
            
            r_p: u.Quantity = self.calc_perigee_radius()
            r_a: u.Quantity = self.calc_apogee_radius()
            
            mu: u.Quantity = bodies.BODIES[attractor].mu
            
            self.specific_angular_momentum = np.sqrt(2 * mu) * np.sqrt(r_a * r_p / (r_a + r_p))
            
        else:
            
            self.specific_angular_momentum = 0 * u.km**2 / u.s
        
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
        
        p: u.Quantity = (a * (1 - e**2)) if h == 0 else (h**2 / mu)
        
        return p
    
    def update_from_perigee_apogee(self, periapsis_radius: u.Quantity, apoapsis_radius: u.Quantity) -> None:
        
        r_p: u.Quantity = periapsis_radius.to(u.km)
        r_a: u.Quantity = apoapsis_radius.to(u.km)
        
        self.semimajor_axis = 0.5 * (r_p + r_a)
        self.eccentricity = (r_a - r_p) / (r_a + r_p)
    
    def calc_velocity(self, attractor: bodies.Attractor) -> u.Quantity:
        
        common.check_attractor(attractor)
        
        mu: float = bodies.BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        e: float = self.eccentricity.to_value(u.one)
        
        h: float = self.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        theta: float = self.true_anomaly.to_value(u.rad)
        
        r: float = h**2 / mu * 1 / (1 + e * np.cos(theta))
        
        v_t: float = h / r
        
        v_r: float = mu / h * e * np.sin(theta)
        
        v: float = np.sqrt(v_r**2 + v_t**2)
        
        return v * u.km / u.s

@dc.dataclass
class EquinoctialOrbitalElements:
    """
    (Standard) Equinoctial Orbital Elements
        - semimajor axis (a)
        - eccentricity vector components (h, k)
        - rescaled ascending node vector components (p, q)
        - location of periapsis in time (l)
    """

    semimajor_axis          : u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    eccentricity_vector_h   : u.Quantity = dc.field(default_factory=lambda: 0 * u.one)
    eccentricity_vector_k   : u.Quantity = dc.field(default_factory=lambda: 0 * u.one)
    ascending_node_vector_p : u.Quantity = dc.field(default_factory=lambda: 0 * u.one)
    ascending_node_vector_q : u.Quantity = dc.field(default_factory=lambda: 0 * u.one)
    periapsis_locaton       : u.Quantity = dc.field(default_factory=lambda: 0 * u.deg)
