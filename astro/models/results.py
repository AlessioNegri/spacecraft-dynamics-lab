import astropy.units as u
import dataclasses as dc
import typing

from astro.models.orbital_elements import OrbitalElements

class Result:
    """Result of integration for 2-Body Problem"""
    
    success         : bool
    time            : u.Quantity
    position_x      : u.Quantity
    position_y      : u.Quantity
    position_z      : u.Quantity
    velocity_x      : u.Quantity
    velocity_y      : u.Quantity
    velocity_z      : u.Quantity
    mass_spacecraft : u.Quantity

class ResultCR3BP:
    """Result of integration for Circular Restricted 3-Body Problem"""
    
    success         : bool
    time            : u.Quantity
    position_x      : u.Quantity
    position_y      : u.Quantity
    position_z      : u.Quantity
    velocity_x      : u.Quantity
    velocity_y      : u.Quantity
    velocity_z      : u.Quantity

class ResultRM:
    """Result of integration for Relative Motion"""
    
    success             : bool
    time                : u.Quantity
    relative_position_x : u.Quantity
    relative_position_y : u.Quantity
    relative_position_z : u.Quantity
    relative_velocity_x : u.Quantity
    relative_velocity_y : u.Quantity
    relative_velocity_z : u.Quantity
    position_x          : u.Quantity
    position_y          : u.Quantity
    position_z          : u.Quantity
    velocity_x          : u.Quantity
    velocity_y          : u.Quantity
    velocity_z          : u.Quantity

class ResultOP:
    """Result of integration for Orbital Perturbations"""
    
    success             : bool
    time                : u.Quantity
    position_x          : u.Quantity
    position_y          : u.Quantity
    position_z          : u.Quantity
    velocity_x          : u.Quantity
    velocity_y          : u.Quantity
    velocity_z          : u.Quantity
    orbital_elements    : typing.List[OrbitalElements]

@dc.dataclass
class ManeuverResult:
    """Maneuver parameters
    
    **orbital_elements_list**: List of orbital elements after each maneuver point
    
    **true_anomaly_list**: List of true anomalies at each maneuver point
    
    **rocket_elevation_angle_list**: List of rocket elevation angles at each maneuver point
    """
    
    delta_velocity_list         : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.km / u.s])
    flight_time_list            : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.s])
    delta_mass_list             : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.kg])
    burn_time_list              : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.s])
    orbital_elements_list       : typing.List[OrbitalElements] = dc.field(default_factory=lambda: [OrbitalElements()])
    true_anomaly_list           : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.deg])
    rocket_elevation_angle_list : typing.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.deg])

@dc.dataclass
class NonImpulsiveManeuverResult:
    """Result of non-impulsive maneuver integration"""
    
    burn_time       : u.Quantity = dc.field(default_factory=lambda: 0 * u.s)
    position_x      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    position_y      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    position_z      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km)
    velocity_x      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km / u.s)
    velocity_y      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km / u.s)
    velocity_z      : u.Quantity = dc.field(default_factory=lambda: 0 * u.km / u.s)
    spacecraft_mass : u.Quantity = dc.field(default_factory=lambda: 0 * u.kg)
