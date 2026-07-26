import astropy.units as u
import dataclasses as dc
import numpy as np

@dc.dataclass
class RocketMotor:
    """Rocket Motor"""
    
    specific_impulse: u.Quantity = dc.field(default_factory=lambda: 0 * u.s)
    thrust          : u.Quantity = dc.field(default_factory=lambda: 0 * u.N)
    spacecraft_mass : u.Quantity = dc.field(default_factory=lambda: 0 * u.kg) # ? Mass of the Spacecraft + propellant
    propellant_mass : u.Quantity = dc.field(default_factory=lambda: 0 * u.kg)
    
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
