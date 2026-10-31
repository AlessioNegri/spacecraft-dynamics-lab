import astropy.units as u
import dataclasses as dc
import numpy as np

from spacelab.bodies import Attractor, BODIES
from spacelab.utils.logger import logger
from spacelab.utils.validator import validate_quantity, validate_attractor

@dc.dataclass
class OrbitalElements:
    """
    An orbital element is any quantity that specifies an orbit under consideration. Constant orbital elements are also
    called *integrals of motion* (a.k.a. *invariants of motion*) and, evidently, they are of particular interest to
    characterize an orbit.
    
    <hr>
        
    📖 **References**
    
    - :cite:`(1) Orbital Mechanics for Engineering Students`
        - :cite:`Chapter 2 "The Two-Body Problem"`
        
    - :cite:`(2) Space Flight Dynamics`
        - :cite:`Chapter 2 "Two-Body Orbital Mechanics"`
        
    - :cite:`(3) Manned Spacecraft - Design Principles`
        - :cite:`Chapter 5 "ORBITAL MECHANICS"`
    
    - :cite:`(4) Astronautics - The Physics of Space Flight`
        - :cite:`Chapter 7 "Orbits"`
    
    <hr>
    
    📌 **Notes**
    
    In **Classical Orbital Elements**, the first two elements describe the dimension of the orbit (*metric elements*),
    the next three describe the orientation of the orbital plane + orientation in the orbital plane (*angular elements*),
    and the sixth parameter determines the location on the orbit (*orbital state sequencer*):
    
        - Semi-major axis (a) / Specific angular momentum (h)
        - Eccentricity (e)
        - Inclination (i)
        - Tight ascension of ascending node (Ω)
        - Argument of periapsis (ω)
        - time after periapsis passage (t - t_p) or mean anomaly (M = n * (t - t_p))
    
    In **Keplerian Elements**, the sequencer is replaced by one of the followings:
    
        - semimajor axis (a) / specific angular momentum (h)
        - eccentricity (e)
        - inclination (i)
        - right ascension of ascending node (Ω)
        - argument of periapsis (ω)
        - true anomaly (θ) or eccentric anomaly (E) or hyperbolic anomaly (F) or universal anomaly (G)
    
    <hr>
    
    🧮 Attributes

    **specific_angular_momentum : u.Quantity** Specific angular momentum :math:`h`

    **semimajor_axis : u.Quantity** Semi-major axis :math:`a`

    **eccentricity : u.Quantity** Eccentricity :math:`e`

    **inclination : u.Quantity** Inclination :math:`i`
    
    **right_ascension_of_ascending_node : u.Quantity** Right ascension of ascending node :math:`\\Omega`
    
    **argument_of_periapsis : u.Quantity** Argument of periapsis :math:`\\omega`
    
    **true_anomaly : u.Quantity** True anomaly :math:`\\theta`
    """
    
    specific_angular_momentum           : u.Quantity = 0 * u.km**2 / u.s
    semimajor_axis                      : u.Quantity = 0 * u.km
    eccentricity                        : u.Quantity = 0 * u.one
    inclination                         : u.Quantity = 0 * u.deg
    right_ascension_of_ascending_node   : u.Quantity = 0 * u.deg
    argument_of_periapsis               : u.Quantity = 0 * u.deg
    true_anomaly                        : u.Quantity = 0 * u.deg
    
    def calc_semimajor_axis(self, attractor: Attractor = Attractor.EARTH) -> u.Quantity:
        """
        Calculates the **semi-major axis** of the orbit.
        
        <hr>
        
        📖 **References**
        
        - :cite:`(1) Section 2.7 "Elliptical orbits (0 < e < 1)"`
        - :cite:`(4) Section 7.3.1 "Orbit Equation"`
        
        <hr>

        :param attractor: Main attractor, defaults to Attractor.EARTH
        :type attractor: Attractor
        :return: Semi-major axis
        :rtype: u.Quantity
        """
        
        # >>> Validation
        
        # * attractor
        
        error_msg = validate_attractor(attractor)
        
        if error_msg: logger.warning(error_msg); return 0 * u.km
        
        # >>> Algorithm
        
        self.semimajor_axis = self.specific_angular_momentum**2 / (BODIES[attractor].mu * (1 - self.eccentricity**2))
        
        return self.semimajor_axis
    
    def calc_periapsis_radius(self) -> u.Quantity:
        """
        Calculates the **periapsis** of the orbit (i.e. minimum distance to the central body at the focal point).
        
        <hr>
        
        📖 **References**
        
        - :cite:`(1) Section 2.7 "Elliptical orbits (0 < e < 1)"`
        - :cite:`(2) Section 2.4.1 "Trajectory Equation"`
        - :cite:`(4) Section 7.4.2 "Elliptic Orbit"`
        
        <hr>
        
        📌 **Notes**
        
        The general term periapsis is also called pericenter. Depending on the central body, the specific terms are
        perigee (Earth), perihelion (Sun), periselene (Moon), etc.

        <hr>

        :return: Periapsis radius
        :rtype: u.Quantity
        """
        
        return self.semimajor_axis * (1 - self.eccentricity)
    
    def calc_apoapsis_radius(self) -> u.Quantity:
        """
        Calculates the **apoapsis** of the orbut (i.e. maximum distance to the central body at the focal point).
        
        <hr>
        
        📖 **References**
        
        - :cite:`(1) Section 2.7 "Elliptical orbits (0 < e < 1)"`
        - :cite:`(2) Section 2.4.1 "Trajectory Equation"`
        - :cite:`(4) Section 7.4.2 "Elliptic Orbit"`
        
        <hr>
        
        📌 **Notes**
        
        The general term apoapsis is also called apocenter. Depending on the central body, the specific terms are
        apogee (Earth), apohelion (Sun), aposelene (Moon), etc.
        
        <hr>

        :return: Apoapsis radius
        :rtype: u.Quantity
        """
        
        return self.semimajor_axis * (1 + self.eccentricity)
    
    def calc_specific_angular_momentum(self, attractor: Attractor = Attractor.EARTH) -> u.Quantity:
        """
        Calculates the **specific angular momentum** of the orbit.
        
        <hr>

        :param attractor: Main attractor, defaults to Attractor.EARTH
        :type attractor: Attractor
        :return: Specific angular momentum
        :rtype: u.Quantity
        """
        
        # >>> Validation
        
        # * attractor
        
        error_msg = validate_attractor(attractor)
        
        if error_msg: logger.warning(error_msg); return 0 * u.km**2 / u.s
        
        # >>> Algorithm
        
        if self.eccentricity < 1 and self.semimajor_axis != 0 * u.km:
            
            r_p: u.Quantity = self.calc_periapsis_radius()
            r_a: u.Quantity = self.calc_apoapsis_radius()
            
            mu: u.Quantity = BODIES[attractor].mu
            
            self.specific_angular_momentum = np.sqrt(2 * mu) * np.sqrt(r_a * r_p / (r_a + r_p))
            
        else:
            
            self.specific_angular_momentum = 0 * u.km**2 / u.s
        
        return self.specific_angular_momentum
    
    def calc_orbital_period(self, attractor: Attractor = Attractor.EARTH) -> u.Quantity:
        """
        Calculates the **orbital period** of the orbit.
        
        <hr>
        
        📖 **References**
        
        - :cite:`(1) Section 2.7 "Elliptical orbits (0 < e < 1)"`
        - :cite:`(2) Section 2.5.3 "Period of an Elliptical Orbit"`
        - :cite:`(3) Section 5.1.2 "CLOSED ORBITS IN A CENTRAL FORCE FIELD"`
        - :cite:`(4) Section 7.4.1 "Circular Orbit"`
        
        <hr>

        :param attractor: Main attractor, defaults to Attractor.EARTH
        :type attractor: Attractor
        :return: Orbital period
        :rtype: u.Quantity
        """
        
        # >>> Validation
        
        # * attractor
        
        error_msg = validate_attractor(attractor)
        
        if error_msg: logger.warning(error_msg); return 0 * u.s
        
        # >>> Algorithm
        
        self.calc_specific_angular_momentum(attractor=attractor)
        
        a: u.Quantity = self.semimajor_axis
        e: u.Quantity = self.eccentricity
        
        mu: u.Quantity = BODIES[attractor].mu
        
        if a != 0 * u.km:

            return 2 * np.pi / np.sqrt(mu) * a**(3/2)
        
        elif self.specific_angular_momentum != 0 * u.km**2 / u.s:
        
            return 2 * np.pi / mu**2 * (self.specific_angular_momentum / np.sqrt(1 - e**2))**3
        
        else:
            
            return 0 * u.s
    
    def calc_semilatus_rectum(self, attractor: Attractor = Attractor.EARTH) -> u.Quantity:
        """
        Calculates the **semi-latus rectum** of the orbit.
        
        <hr>
        
        📖 **References**
        
        - :cite:`(1) Section 2.4 "Angular momentum and the orbit formulas"`
        - :cite:`(2) Section 2.4.1 "Trajectory Equation"`
        - :cite:`(3) Section 5.2.2 "CONSERVATION OF ANGULAR MOMENTUM"`
        - :cite:`(4) Section 7.3.1 "Orbit Equation"`
        
        <hr>

        :param attractor: _description_
        :type attractor: Attractor
        :return: _description_
        :rtype: u.Quantity
        """
        
        # >>> Validation
        
        # * attractor
        
        error_msg = validate_attractor(attractor)
        
        if error_msg: logger.warning(error_msg); return 0 * u.km
        
        # >>> Algorithm
        
        h: u.Quantity = self.specific_angular_momentum
        a: u.Quantity = self.semimajor_axis
        e: u.Quantity = self.eccentricity
        
        mu: u.Quantity = BODIES[attractor].mu
        
        p: u.Quantity = (a * (1 - e**2)) if h == 0 else (h**2 / mu)
        
        return p
    
    def update_from_periapsis_apoapsis(self, periapsis_radius: u.Quantity, apoapsis_radius: u.Quantity) -> None:
        """
        Updates the *semi-major axis* and *eccentricity* from the given apsis radii.
        
        <hr>
        
        📖 **References**
        
        - :cite:`(1) Section 2.7 "Elliptical orbits (0 < e < 1)"`
        - :cite:`(2) Section 2.5.1 "Ellipse Geometry"`
        - :cite:`(3) Section 5.1.2 "CLOSED ORBITS IN A CENTRAL FORCE FIELD"`
        
        <hr>

        :param periapsis_radius: Periapsis radius
        :type periapsis_radius: u.Quantity
        :param apoapsis_radius: Apoapsis radius
        :type apoapsis_radius: u.Quantity
        """
        
        # >>> Validation
        
        # * periapsis_radius
        
        err_msg: str | None = validate_quantity("periapsis_radius", periapsis_radius, u.m)
        
        if err_msg: logger.warning(err_msg); return
        
        r_p: u.Quantity = periapsis_radius.to(u.km)
        
        # * apoapsis_radius
        
        err_msg: str | None = validate_quantity("apoapsis_radius", apoapsis_radius, u.m)
        
        if err_msg: logger.warning(err_msg); return
        
        r_a: u.Quantity = apoapsis_radius.to(u.km)
        
        # >>> Algorithm
        
        self.semimajor_axis = 0.5 * (r_p + r_a)
        self.eccentricity = (r_a - r_p) / (r_a + r_p)
    
    def calc_velocity(self, attractor: Attractor = Attractor.EARTH) -> u.Quantity:
        """
        _summary_
        
        📖 **References**
        
        - :cite:`(1) Section 2.4 "Angular momentum and the orbit formulas"`
        - :cite:`(2) Section 2.5.2 "Flight-Path Angle and Velocity Components"`
        - :cite:`(4) Section 7.3.3 "Orbital Velocity"`

        :param attractor: _description_
        :type attractor: Attractor
        :return: _description_
        :rtype: u.Quantity
        """
        
        # >>> Validation
                
        # * attractor
        
        error_msg = validate_attractor(attractor)
        
        if error_msg: logger.warning(error_msg); return 0 * u.km / u.s
        
        mu: float = BODIES[attractor].mu.to_value(u.km**3 / u.s**2)
        
        # >>> Algorithm
        
        e: float = self.eccentricity.to_value(u.one)
        
        h: float = self.calc_specific_angular_momentum(attractor=attractor).to_value(u.km**2 / u.s)
        
        if h == 0: logger.warning("Specific angular momentum is zero"); return 0 * u.km / u.s
        
        theta: float = self.true_anomaly.to_value(u.rad)
        
        r: float = h**2 / mu * 1 / (1 + e * np.cos(theta))
        
        v_t: float = h / r
        
        v_r: float = mu / h * e * np.sin(theta)
        
        v: float = np.sqrt(v_r**2 + v_t**2)
        
        return v * u.km / u.s

@dc.dataclass
class EquinoctialOrbitalElements:
    """
    One problem of standard orbital elements *orbit degeneracy* with angular elements arises because *Right Ascension of
    Ascending Node* and *argument of periapsis* are measured relative to the ascending line of nodes, which vanishes for
    *inclination* = 0. The other orbit degeneracy problem is that *Argument of periapsis* and *true anomaly* (or M)
    will become undefined for *eccentricity* = 0. These problems are solved by adopting the **standard equinoctial
    orbital elements**.
    
    <hr>
        
    📖 **References**
    
    - :cite:`(4) Astronautics - The Physics of Space Flight`
        - :cite:`Chapter 7 "Orbits"`
    
    <hr>
    
    📌 **Notes**
    
    In **Classical Orbital Elements**, the first two elements describe the dimension of the orbit (*metric elements*),
    the next three describe the orientation of the orbital plane + orientation in the orbital plane (*angular elements*),
    and the sixth parameter determines the location on the orbit (*orbital state sequencer*):
    
        - Semi-major axis (a) / Specific angular momentum (h)
        - Eccentricity (e)
        - Inclination (i)
        - Tight ascension of ascending node (Ω)
        - Argument of periapsis (ω)
        - time after periapsis passage (t - t_p) or mean anomaly (M = n * (t - t_p))
    
    In **Keplerian Elements**, the sequencer is replaced by one of the followings:
    
        - semimajor axis (a) / specific angular momentum (h)
        - eccentricity (e)
        - inclination (i)
        - right ascension of ascending node (Ω)
        - argument of periapsis (ω)
        - true anomaly (θ) or eccentric anomaly (E) or hyperbolic anomaly (F) or universal anomaly (G)
    
    <hr>
    
    🧮 Attributes

    **semimajor_axis : u.Quantity** Semi-major axis :math:`a`

    **eccentricity_vector_h : u.Quantity** Eccentricity vector component :math:`h`

    **eccentricity_vector_k : u.Quantity** Eccentricity vector component :math:`k`

    **ascending_node_vector_p : u.Quantity** Rescaled ascending node vector component :math:`p`
    
    **ascending_node_vector_q : u.Quantity** Rescaled ascending node vector component :math:`q`
    
    **periapsis_locaton : u.Quantity** Periapsis location in time :math:`l`
    """

    semimajor_axis          : u.Quantity = 0 * u.km
    eccentricity_vector_h   : u.Quantity = 0 * u.one
    eccentricity_vector_k   : u.Quantity = 0 * u.one
    ascending_node_vector_p : u.Quantity = 0 * u.one
    ascending_node_vector_q : u.Quantity = 0 * u.one
    periapsis_locaton       : u.Quantity = 0 * u.deg
