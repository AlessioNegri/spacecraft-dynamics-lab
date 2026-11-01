import astropy.units as u
import dataclasses as dc
import numpy as np

from spacelab.bodies import Attractor, BODIES
from spacelab.utils.logger import logger
from spacelab.utils.validator import validate_quantity, validate_attractor

@dc.dataclass
class RocketMotor:
    """
    This class implements a **Rocket Motor** model, which is used in orbital maneuvers calculations.
    
    <hr>
    
    📖 **References**
    
    - cite`(1) Orbital Mechanics for Engineering Students`
        - cite`Chapter 6 "Orbital Maneuvers"`
        - cite`Chapter 11 "Rocket Vehicle Dynamics"`
        
    - cite`(2) Space Flight Dynamics`
        - cite`Chapter 6 "Rocket Performance"`
        
    - cite`(3) Manned Spacecraft - Design Principles`
        - cite`Chapter 7 "LAUNCH MECHANICS"`
    
    - cite`(4) Astronautics - The Physics of Space Flight`
        - cite`Chapter 1 "Rocket Fundamentals"`
        - cite`Chapter 2 "Rocket Flight"`
    
    <hr>
    
    🧮 Attributes

    **specific_impulse : u.Quantity** Engine specific impulse :math:`I_{sp}`

    **thrust : u.Quantity** Engine thrust :math:`T`

    **spacecraft_mass : u.Quantity** Total spacecraft mass, including propellant :math:`m_0`

    **propellant_mass : u.Quantity** Propellant mass required to accomplish the maneuver :math:`m_p`
    """
    
    specific_impulse: u.Quantity
    thrust          : u.Quantity
    spacecraft_mass : u.Quantity
    propellant_mass : u.Quantity = 0 * u.kg
    
    def calc_propellant_mass(self, delta_velocity: u.Quantity, attractor: Attractor = Attractor.EARTH) -> u.Quantity:
        """
        Calculates the propellant mass required for a given delta velocity using the **ideal rocket equation**.
        
        <hr>
        
        📖 **References**
        
        - cite`(1) Section 6.2 "Impulsive maneuvers"`
        - cite`(2) Section 6.3 "The Rocket Equation"`
        - cite`(4) Section 2.2 "Rocket in Free Space"`
        
        <hr>
        
        📌 **Notes**
        
        The ideal rocket equation is also known as the **Tsiolkovsky rocket equation**.
        
        <hr>

        :param delta_velocity: Delta velocity
        :type delta_velocity: u.Quantity
        :param attractor: Main attractor, defaults to Attractor.EARTH
        :type attractor: Attractor, optional
        :return: Propellant mass
        :rtype: u.Quantity
        """
        
        # >>> Validation
        
        # * delta_velocity
        
        error_msg: str | None = validate_quantity('delta_velocity', delta_velocity, u.km / u.s)
        
        if error_msg: logger.warning(error_msg); return 0 * u.kg
        
        dv: float = delta_velocity.to_value(u.km / u.s)
        
        # * attractor
        
        error_msg = validate_attractor(attractor)
        
        if error_msg: logger.warning(error_msg); return 0 * u.kg
        
        g_0: float = BODIES[attractor].g_0.to_value(u.km / u.s**2)
        
        # * specific_impulse
        
        i_sp: float = self.specific_impulse.to_value(u.s)
        
        if i_sp <= 0:
        
            error_msg = f"Specific impulse shall be greater than zero ({i_sp} s <= 0 s)"
            
            logger.warning(error_msg)
            
            return 0 * u.kg
        
        # >>> Algorithm
        
        m_sc: float = self.spacecraft_mass.to_value(u.kg)
        
        self.propellant_mass = m_sc * (1 - np.exp(-dv / (i_sp * g_0))) * u.kg
        
        return self.propellant_mass
    
    def calc_burn_time(self, propellant_mass: u.Quantity, attractor: Attractor = Attractor.EARTH) -> u.Quantity:
        """
        Calculates the burn time.
        
        <hr>
        
        📖 **References**
        
        - cite`(1) Section 11.4 "Rocket performance"`
        - cite`(2) Section 6.3 "The Rocket Equation"`
        - cite`(3) Section 7.2.1 "ROCKET ENGINE THRUST"`

        :param propellant_mass: Propellant mass
        :type propellant_mass: u.Quantity
        :param attractor: Main attractor, defaults to Attractor.EARTH
        :type attractor: Attractor, optional
        :return: Burn time
        :rtype: u.Quantity
        """
        
        # >>> Validation
        
        # * propellant_mass
        
        error_msg: str | None = validate_quantity('propellant_mass', propellant_mass, u.kg)
        
        if error_msg: logger.warning(error_msg); return 0 * u.s
        
        m_prop: float = propellant_mass.to_value(u.kg)
        
        # * attractor
        
        error_msg = validate_attractor(attractor)
        
        if error_msg: logger.warning(error_msg); return 0 * u.s
        
        g_0: float = BODIES[attractor].g_0.to_value(u.m / u.s**2)
        
        # * specific_impulse
        
        i_sp: float = self.specific_impulse.to_value(u.s)
        
        if i_sp <= 0:
        
            error_msg = f"Specific impulse shall be greater than zero ({i_sp} s <= 0 s)"
            
            logger.warning(error_msg)
            
            return 0 * u.s
        
        # * thrust
        
        T: float = self.thrust.to_value(u.N)
        
        if T <= 0:
                
            error_msg = f"Thrust shall be greater than zero ({T} N <= 0 N)"
            
            logger.warning(error_msg)
            
            return 0 * u.s
        
        # >>> Algorithm
        
        # ? Engine mass-flow rate
        m_dot: float = T / (i_sp * g_0)
        
        burn_time: u.Quantity = m_prop / m_dot * u.s
        
        return burn_time
    
    def calc_effective_exhaust_velocity(self, attractor: Attractor = Attractor.EARTH) -> u.Quantity:
        """
        Calculates the effective exhaust velocity.
        
        <hr>
        
        📖 **References**
        
        - cite`(1) Section 11.3 "The thrust equation"`
        - cite`(2) Section 6.2 "Rocket Propulsion Fundamentals"`
        - cite`(3) Section 7.2.1 "ROCKET ENGINE THRUST"`
        - cite`(4) Section 1.1.2 "Total Trust"`
        
        <hr>

        :param attractor: Main attractor, defaults to Attractor.EARTH
        :type attractor: Attractor
        :return: Effective exhaust velocity
        :rtype: u.Quantity
        """
        
        # >>> Validation
        
        error_msg: str | None = validate_attractor(attractor)
        
        if error_msg: logger.warning(error_msg); return 0 * u.m / u.s
        
        g_0: u.Quantity = BODIES[attractor].g_0.to(u.m / u.s**2)
        
        # >>> Algorithm
        
        i_sp: u.Quantity = self.specific_impulse.to(u.s)
        
        c: u.Quantity = i_sp * g_0
        
        return c
    
    def calc_propellant_mass_flow_rate(self, attractor: Attractor = Attractor.EARTH) -> u.Quantity:
        """
        Calculates the propellant mass flow-rate.
        
        <hr>
        
        📖 **References**
        
        - cite`(1) Section 11.3 "The thrust equation"`
        - cite`(2) Section 6.2 "Rocket Propulsion Fundamentals"`
        - cite`(3) Section 7.2.1 "ROCKET ENGINE THRUST"`
        - cite`(4) Section 1.1.2 "Total Trust"`
        
        <hr>

        :param attractor: Main attractor, defaults to Attractor.EARTH
        :type attractor: Attractor
        :return: Propellant mass flow-rate
        :rtype: u.Quantity
        """
        
        # >>> Validation
                
        error_msg: str | None = validate_attractor(attractor)
        
        if error_msg: logger.warning(error_msg); return 0 * u.kg / u.s
        
        # >>> Algorithm
        
        T: float = self.thrust.to(u.N)
        
        c: u.Quantity = self.calc_effective_exhaust_velocity(attractor=attractor)
        
        if c <= 0 * u.m / u.s:
            
            error_msg = f"Effective exhaust velocity shall be greater than zero ({c} m/s <= 0 m/s)"
            
            logger.warning(error_msg)
            
            return 0 * u.kg / u.s
        
        m_dot: u.Quantity = T / c
        
        return m_dot
