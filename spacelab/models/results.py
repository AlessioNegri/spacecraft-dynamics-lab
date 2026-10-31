import astropy.units as u
import dataclasses as dc
import typing as ty

from spacelab.models.orbital_elements import OrbitalElements

@dc.dataclass
class Result:
    """
    Result of integration for Two-Body Problem.
    
    <hr>
    
    🧮 Attributes

    **success : bool** Integration status flag

    **time : u.Quantity** Propagation time

    **position_x : u.Quantity** Cartesian X-coordinate :math:`x`

    **position_y : u.Quantity** Cartesian Y-coordinate :math:`y`

    **position_z : u.Quantity** Cartesian Z-coordinate :math:`z`

    **velocity_x : u.Quantity** Cartesian X-velocity :math:`v_x`

    **velocity_y : u.Quantity** Cartesian Y-velocity :math:`v_y`

    **velocity_z : u.Quantity** Cartesian Z-velocity :math:`v_z`

    **mass_spacecraft : u.Quantity** Spacecraft mass
    """
    
    success         : bool = False
    time            : u.Quantity = 0 * u.s
    position_x      : u.Quantity = 0 * u.km
    position_y      : u.Quantity = 0 * u.km
    position_z      : u.Quantity = 0 * u.km
    velocity_x      : u.Quantity = 0 * u.km / u.s
    velocity_y      : u.Quantity = 0 * u.km / u.s
    velocity_z      : u.Quantity = 0 * u.km / u.s
    mass_spacecraft : u.Quantity = 0 * u.kg

@dc.dataclass
class ResultCR3BP:
    """
    Result of integration for Circular Restricted 3-Body Problem.
    
    <hr>
    
    🧮 Attributes

    **success : bool** Integration status flag

    **time : u.Quantity** Propagation time

    **position_x : u.Quantity** Cartesian X-coordinate in the rotating frame :math:`x`

    **position_y : u.Quantity** Cartesian Y-coordinate in the rotating frame :math:`y`

    **position_z : u.Quantity** Cartesian Z-coordinate in the rotating frame :math:`z`

    **velocity_x : u.Quantity** Cartesian X-velocity in the rotating frame :math:`\\dot{x}`

    **velocity_y : u.Quantity** Cartesian Y-velocity in the rotating frame :math:`\\dot{y}`

    **velocity_z : u.Quantity** Cartesian Z-velocity in the rotating frame :math:`\\dot{z}`
    """
    
    success         : bool = False
    time            : u.Quantity = 0 * u.s
    position_x      : u.Quantity = 0 * u.km
    position_y      : u.Quantity = 0 * u.km
    position_z      : u.Quantity = 0 * u.km
    velocity_x      : u.Quantity = 0 * u.km / u.s
    velocity_y      : u.Quantity = 0 * u.km / u.s
    velocity_z      : u.Quantity = 0 * u.km / u.s

@dc.dataclass
class ResultRM:
    """
    Result of integration for Relative Motion.
    
    <hr>
    
    🧮 Attributes

    **success : bool** Integration status flag

    **time : u.Quantity** Propagation time

    **relative_position_x : u.Quantity** Relative X-coordinate :math:`\\delta x`

    **relative_position_y : u.Quantity** Relative Y-coordinate :math:`\\delta y`

    **relative_position_z : u.Quantity** Relative Z-coordinate :math:`\\delta z`

    **relative_velocity_x : u.Quantity** Relative X-velocity :math:`\\delta v_x`

    **relative_velocity_y : u.Quantity** Relative Y-velocity :math:`\\delta v_y`

    **relative_velocity_z : u.Quantity** Relative Z-velocity :math:`\\delta v_z`

    **position_x : u.Quantity** Reference orbit X-coordinate :math:`x`

    **position_y : u.Quantity** Reference orbit Y-coordinate :math:`y`

    **position_z : u.Quantity** Reference orbit Z-coordinate :math:`z`

    **velocity_x : u.Quantity** Reference orbit X-velocity :math:`v_x`

    **velocity_y : u.Quantity** Reference orbit Y-velocity :math:`v_y`

    **velocity_z : u.Quantity** Reference orbit Z-velocity :math:`v_z`
    """
    
    success             : bool = False
    time                : u.Quantity = 0 * u.s
    relative_position_x : u.Quantity = 0 * u.km
    relative_position_y : u.Quantity = 0 * u.km
    relative_position_z : u.Quantity = 0 * u.km
    relative_velocity_x : u.Quantity = 0 * u.km / u.s
    relative_velocity_y : u.Quantity = 0 * u.km / u.s
    relative_velocity_z : u.Quantity = 0 * u.km / u.s
    position_x          : u.Quantity = 0 * u.km
    position_y          : u.Quantity = 0 * u.km
    position_z          : u.Quantity = 0 * u.km
    velocity_x          : u.Quantity = 0 * u.km / u.s
    velocity_y          : u.Quantity = 0 * u.km / u.s
    velocity_z          : u.Quantity = 0 * u.km / u.s

@dc.dataclass
class ResultOP:
    """
    Result of integration for Orbital Perturbations
    
    <hr>
    
    🧮 Attributes

    **success : bool** Integration status flag

    **time : u.Quantity** Propagation time

    **position_x : u.Quantity** Cartesian X-coordinate :math:`x`

    **position_y : u.Quantity** Cartesian Y-coordinate :math:`y`

    **position_z : u.Quantity** Cartesian Z-coordinate :math:`z`

    **velocity_x : u.Quantity** Cartesian X-velocity :math:`v_x`

    **velocity_y : u.Quantity** Cartesian Y-velocity :math:`v_y`

    **velocity_z : u.Quantity** Cartesian Z-velocity :math:`v_z`

    **orbital_elements : List[OrbitalElements]** Osculating orbital elements
    """
    
    success             : bool = False
    time                : u.Quantity = 0 * u.s
    position_x          : u.Quantity = 0 * u.km
    position_y          : u.Quantity = 0 * u.km
    position_z          : u.Quantity = 0 * u.km
    velocity_x          : u.Quantity = 0 * u.km / u.s
    velocity_y          : u.Quantity = 0 * u.km / u.s
    velocity_z          : u.Quantity = 0 * u.km / u.s
    orbital_elements    : ty.List[OrbitalElements] = dc.field(default_factory=lambda: [OrbitalElements()])

@dc.dataclass
class ManeuverResult:
    """
    Result of maneuver execution.
    
    <hr>
    
    🧮 Attributes

    **delta_velocity_list : List[u.Quantity]** Required velocity increments :math:`\\Delta v`

    **flight_time_list : List[u.Quantity]** Flight times between maneuver points

    **delta_mass_list : List[u.Quantity]** Propellant mass consumed at each maneuver

    **burn_time_list : List[u.Quantity]** Engine burn durations

    **orbital_elements_list : List[OrbitalElements]** Orbital elements after each maneuver point

    **true_anomaly_list : List[u.Quantity]** True anomalies at each maneuver point

    **rocket_elevation_angle_list : List[u.Quantity]** Rocket elevation angles at each maneuver point
    """
    
    delta_velocity_list         : ty.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.km / u.s])
    flight_time_list            : ty.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.s])
    delta_mass_list             : ty.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.kg])
    burn_time_list              : ty.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.s])
    orbital_elements_list       : ty.List[OrbitalElements] = dc.field(default_factory=lambda: [OrbitalElements()])
    true_anomaly_list           : ty.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.deg])
    rocket_elevation_angle_list : ty.List[u.Quantity] = dc.field(default_factory=lambda: [0 * u.deg])

@dc.dataclass
class NonImpulsiveManeuverResult:
    """
    Result of non-impulsive maneuver integration.
    
    <hr>
    
    🧮 Attributes

    **burn_time : u.Quantity** Total engine burn duration

    **position_x : u.Quantity** Final X-coordinate :math:`x`

    **position_y : u.Quantity** Final Y-coordinate :math:`y`

    **position_z : u.Quantity** Final Z-coordinate :math:`z`

    **velocity_x : u.Quantity** Final X-velocity :math:`v_x`

    **velocity_y : u.Quantity** Final Y-velocity :math:`v_y`

    **velocity_z : u.Quantity** Final Z-velocity :math:`v_z`

    **spacecraft_mass : u.Quantity** Final spacecraft mass
    """
    
    burn_time       : u.Quantity = 0 * u.s
    position_x      : u.Quantity = 0 * u.km
    position_y      : u.Quantity = 0 * u.km
    position_z      : u.Quantity = 0 * u.km
    velocity_x      : u.Quantity = 0 * u.km / u.s
    velocity_y      : u.Quantity = 0 * u.km / u.s
    velocity_z      : u.Quantity = 0 * u.km / u.s
    spacecraft_mass : u.Quantity = 0 * u.kg
