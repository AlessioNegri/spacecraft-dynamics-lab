import astropy.units as u
import dataclasses as dc
import numpy as np

@dc.dataclass
class OrbitParameters:
    """Orbit parameters based on orbit geometry (linear - circular - elliptical - parabolic - hyperbolic)"""
    
    conic_type                  : str = "" # ? Type of conic section
    specific_angular_momentum   : u.Quantity = 0.0 * u.km**2 / u.s
    transverse_velocity         : u.Quantity = 0.0 * u.km / u.s
    specific_energy             : u.Quantity = 0.0 * u.km**2 / u.s**2 # ? Specific Mechanical Energy
    semilatus_rectum            : u.Quantity = 0.0 * u.km # ? Semilatus Rectum (Parameter)
    semimajor_axis              : u.Quantity = 0.0 * u.km
    eccentricity                : u.Quantity = 0.0 * u.one
    periapsis_radius            : u.Quantity = 0.0 * u.km
    apoapsis_radius             : u.Quantity = 0.0 * u.km
    semiminor_axis              : u.Quantity = 0.0 * u.km
    period                      : u.Quantity = 0.0 * u.s # ? Orbital Period
    escape_velocity             : u.Quantity = 0.0 * u.km / u.s
    hyperbolic_excess_speed     : u.Quantity = 0.0 * u.km / u.s
    turning_angle               : u.Quantity = 0.0 * u.deg
    asymptotic_true_anomaly     : u.Quantity = 0.0 * u.deg # ? Infinite True Anomaly
    asymptote_angle             : u.Quantity = 0.0 * u.deg # ? Hyperbola Asymptote Angle
    aiming_radius               : u.Quantity = 0.0 * u.km
    characteristic_energy       : u.Quantity = 0.0 * u.km**2 / u.s**2

@dc.dataclass
class OrbitParametersCR3BP:
    """Orbit parameters for Circular Restricted 3-Body Problem"""
    
    lagrangian_equilibrium_point_1  : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    lagrangian_equilibrium_point_2  : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    lagrangian_equilibrium_point_3  : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    lagrangian_equilibrium_point_4  : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    lagrangian_equilibrium_point_5  : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    inertial_angular_velocity       : u.Quantity = 0.0 * u.rad / u.s
    dimensionless_mass_ratio_1      : u.Quantity = 0.0 * u.one
    dimensionless_mass_ratio_2      : u.Quantity = 0.0 * u.one
    gravitational_parameter_1       : u.Quantity = 0.0 * u.km**3 / u.s**2
    gravitational_parameter_2       : u.Quantity = 0.0 * u.km**3 / u.s**2
    body_position_1                 : u.Quantity = 0.0 * u.km
    body_position_2                 : u.Quantity = 0.0 * u.km

@dc.dataclass
class HyperbolaParameters():
    """Hyperbola Parameters
    """
    
    specific_angular_momentum   : u.Quantity = 0.0 * u.km**2 / u.s
    eccentricity                : u.Quantity = 0.0 * u.one
    periapsis_radius            : u.Quantity = 0.0 * u.km
    asymptote_angle             : u.Quantity = 0.0 * u.rad # ? beta
    turning_angle               : u.Quantity = 0.0 * u.rad # ? delta
    aiming_radius               : u.Quantity = 0.0 * u.km # ? Delta
    specific_energy             : u.Quantity = 0.0 * u.km**2 / u.s**2
    hyperbolic_excess_speed     : u.Quantity = 0.0 * u.km / u.s
    characteristic_energy       : u.Quantity = 0.0 * u.km**2 / u.s**2
    time_of_flight              : u.Quantity = 0.0 * u.s
