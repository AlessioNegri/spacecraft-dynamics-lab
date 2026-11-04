import astropy.units as u
import dataclasses as dc
import numpy as np

@dc.dataclass
class OrbitParameters:
    """
    Two-Body orbit parameters.
    
    🧮 Attributes

    conic_type : str
        Type of conic section (*Linear*, *Circular*, *Elliptical*, *Parabolic*, *Hyperbolic*)
    
    specific_angular_momentum : u.Quantity
        Specific angular momentum :math:`h`
    
    transverse_velocity : u.Quantity
        Transverse component of the orbital velocity :math:`v_t`

    specific_energy : u.Quantity
        Specific mechanical energy :math:`\\varepsilon`

    semilatus_rectum : u.Quantity
        Semilatus rectum (a.k.a. orbital parameter) :math:`p`

    semimajor_axis : u.Quantity
        Semimajor axis :math:`a`

    eccentricity : u.Quantity
        Orbital eccentricity :math:`e`

    periapsis_radius : u.Quantity
        Radius at periapsis :math:`r_p`

    apoapsis_radius : u.Quantity
        Radius at apoapsis :math:`r_a`

    periapsis_velocity : u.Quantity
        Velocity at periapsis :math:`v_p`

    apoapsis_velocity : u.Quantity
        Velocity at apoapsis :math:`v_a`

    semiminor_axis : u.Quantity
        Semiminor axis :math:`b`

    period : u.Quantity
        Orbital period :math:`T`
        
    mean_motion : u.Quantity
        Mean motion :math:`n`

    first_cosmic_velocity : u.Quantity
        Circular velocity at the reference radius :math:`v_{\\triangleright}`

    second_cosmic_velocity : u.Quantity
        Escape velocity at the reference radius :math:`v_{\\triangleright\\triangleright}`

    escape_velocity : u.Quantity
        Local escape velocity :math:`v_{esc}`

    hyperbolic_excess_speed : u.Quantity
        Hyperbolic excess speed :math:`v_{\\infty}`

    oberth_maneuver_velocity : u.Quantity
        Velocity at the maneuver point used for Oberth-effect calculations

    turning_angle : u.Quantity
        Hyperbolic turning angle :math:`\\delta`

    asymptotic_true_anomaly : u.Quantity
        Asymptotic (infinite) true anomaly :math:`\\theta_{\\infty}`

    asymptote_angle : u.Quantity
        Angle between the hyperbolic asymptote and the periapsis direction :math:`\\beta`

    aiming_radius : u.Quantity
        Aiming radius (impact parameter) :math:`\\Delta`

    characteristic_energy : u.Quantity
        Characteristic energy :math:`C_3 = v_{\\infty}^2`
    """
    
    conic_type                  : str = ""
    specific_angular_momentum   : u.Quantity = 0.0 * u.km**2 / u.s
    transverse_velocity         : u.Quantity = 0.0 * u.km / u.s
    specific_energy             : u.Quantity = 0.0 * u.km**2 / u.s**2 
    semilatus_rectum            : u.Quantity = 0.0 * u.km
    semimajor_axis              : u.Quantity = 0.0 * u.km
    eccentricity                : u.Quantity = 0.0 * u.one
    periapsis_radius            : u.Quantity = 0.0 * u.km
    apoapsis_radius             : u.Quantity = 0.0 * u.km
    periapsis_velocity          : u.Quantity = 0.0 * u.km / u.s
    apoapsis_velocity           : u.Quantity = 0.0 * u.km / u.s
    semiminor_axis              : u.Quantity = 0.0 * u.km
    period                      : u.Quantity = 0.0 * u.s
    mean_motion                 : u.Quantity = 0.0 * u.rad / u.s
    first_cosmic_velocity       : u.Quantity = 0.0 * u.km / u.s
    second_cosmic_velocity      : u.Quantity = 0.0 * u.km / u.s
    escape_velocity             : u.Quantity = 0.0 * u.km / u.s
    hyperbolic_excess_speed     : u.Quantity = 0.0 * u.km / u.s
    oberth_maneuver_velocity    : u.Quantity = 0.0 * u.km / u.s
    turning_angle               : u.Quantity = 0.0 * u.deg
    asymptotic_true_anomaly     : u.Quantity = 0.0 * u.deg
    asymptote_angle             : u.Quantity = 0.0 * u.deg
    aiming_radius               : u.Quantity = 0.0 * u.km
    characteristic_energy       : u.Quantity = 0.0 * u.km**2 / u.s**2

@dc.dataclass
class OrbitParametersCR3BP:
    """
    Circular Restricted 3-Body orbit parameters.
    
    🧮 Attributes

    libration_point_1 : u.Quantity
        Collinear equilibrium point (Eulerian point) :math:`L_1`

    libration_point_2 : u.Quantity
        Collinear equilibrium point (Eulerian point) :math:`L_2`

    libration_point_3 : u.Quantity
        Collinear equilibrium point (Eulerian point) :math:`L_3`

    libration_point_4 : u.Quantity
        Equilateral equilibrium point (Lagrangian point) :math:`L_4`

    libration_point_5 : u.Quantity
        Equilateral equilibrium point (Lagrangian point) :math:`L_5`

    inertial_angular_velocity : u.Quantity
        Angular velocity of the rotating reference frame :math:`\\omega`

    dimensionless_mass_ratio_1 : u.Quantity
        Dimensionless mass ratio of the primary body :math:`\\pi_1`

    dimensionless_mass_ratio_2 : u.Quantity
        Dimensionless mass ratio of the secondary body :math:`\\pi_2`

    gravitational_parameter_1 : u.Quantity
        Standard gravitational parameter of the primary body :math:`\\mu_1`

    gravitational_parameter_2 : u.Quantity
        Standard gravitational parameter of the secondary body :math:`\\mu_2`

    body_position_1 : u.Quantity
        Position of the primary body in the rotating frame :math:`x_1`

    body_position_2 : u.Quantity
        Position of the secondary body in the rotating frame :math:`x_2`

    body_distance : u.Quantity
        Distance between the two primaries :math:`r_{12}`
    
    📌 **Notes**
        
    The *collinear equilibrium points* are also known as **Eulerian points** L1, L2, L3, and the *equilateral
    equilibrium points* are also known as **Lagrangian points** L4 and L5. All five points together are the so-called
    **libration points**, but quite frequently and confusingly they are also called Lagrangian points.
    """
    
    libration_point_1           : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    libration_point_2           : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    libration_point_3           : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    libration_point_4           : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    libration_point_5           : u.Quantity = np.array([0.0, 0.0, 0.0]) * u.km
    inertial_angular_velocity   : u.Quantity = 0.0 * u.rad / u.s
    dimensionless_mass_ratio_1  : u.Quantity = 0.0 * u.one
    dimensionless_mass_ratio_2  : u.Quantity = 0.0 * u.one
    gravitational_parameter_1   : u.Quantity = 0.0 * u.km**3 / u.s**2
    gravitational_parameter_2   : u.Quantity = 0.0 * u.km**3 / u.s**2
    body_position_1             : u.Quantity = 0.0 * u.km
    body_position_2             : u.Quantity = 0.0 * u.km
    body_distance               : u.Quantity = 0.0 * u.km

@dc.dataclass
class HyperbolaParameters():
    """
    Hyperbola Parameters.
    
    🧮 Attributes

    specific_angular_momentum : u.Quantity
        Specific angular momentum :math:`h`

    eccentricity : u.Quantity
        Hyperbolic eccentricity :math:`e`

    periapsis_radius : u.Quantity
        Radius at periapsis :math:`r_p`

    asymptote_angle : u.Quantity
        Hyperbola asymptote angle :math:`\\beta`

    turning_angle : u.Quantity
        Hyperbolic turning angle :math:`\\delta`

    aiming_radius : u.Quantity
        Aiming radius (impact parameter) :math:`\\Delta`

    specific_energy : u.Quantity
        Specific mechanical energy :math:`\\varepsilon`

    hyperbolic_excess_speed : u.Quantity
        Hyperbolic excess speed :math:`v_{\\infty}`

    characteristic_energy : u.Quantity
        Characteristic energy :math:`C_3 = v_{\\infty}^2`

    time_of_flight : u.Quantity
        Time of flight between two points on the hyperbolic trajectory :math:`tof`
    """
    
    specific_angular_momentum   : u.Quantity = 0.0 * u.km**2 / u.s
    eccentricity                : u.Quantity = 0.0 * u.one
    periapsis_radius            : u.Quantity = 0.0 * u.km
    asymptote_angle             : u.Quantity = 0.0 * u.rad
    turning_angle               : u.Quantity = 0.0 * u.rad
    aiming_radius               : u.Quantity = 0.0 * u.km
    specific_energy             : u.Quantity = 0.0 * u.km**2 / u.s**2
    hyperbolic_excess_speed     : u.Quantity = 0.0 * u.km / u.s
    characteristic_energy       : u.Quantity = 0.0 * u.km**2 / u.s**2
    time_of_flight              : u.Quantity = 0.0 * u.s
