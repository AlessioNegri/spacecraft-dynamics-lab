"""
Circular Restricted Three-Body Problem

Two major assumptions are required for the CR3BP:
1) the two gravitational bodies move in circular orbits about their center of mass;
2) the mass of the third body is negligible and does not influence the motion of the two primary bodies.

References:
- Howard D. Curtis, "Orbital Mechanics for Engineering Students"
    - Chapter 2: The Two-Body Problem

- Craig A. Kluever, "Space Flight Dynamics"
    - Chapter 5: Non-Keplerian Motion
"""

__author__      = "Alessio Negri"
__license__     = "LGPL v3"
__maintainer__  = "Alessio Negri"

import astropy.time as time
import astropy.units as u
import dataclasses
import numpy as np
import scipy.integrate as ode
import scipy.optimize as optimize
import typing

import astro.bodies as bd
import astro.common as cm
import astro.physical_constants as pc

@dataclasses.dataclass
class OrbitParameters:
    """Orbit parameters"""
    
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

class Result:
    """Result of integration"""
    
    success         : bool
    time            : u.Quantity
    position_x      : u.Quantity
    position_y      : u.Quantity
    position_z      : u.Quantity
    velocity_x      : u.Quantity
    velocity_y      : u.Quantity
    velocity_z      : u.Quantity

class Orbit:
    """Generic orbit in circular restricted three-body problem"""
    
    def __init__(self):
        """Constructor"""
        
        self.ready: bool = False
        
        self.body_1: bd.Body = bd.get_body(bd.Attractor.EARTH)
        
        self.body_2: bd.Body = bd.get_body(bd.Attractor.MOON)
        
        self.position: np.ndarray = np.zeros(3)
        
        self.velocity: np.ndarray = np.zeros(3)
    
    # --- STATIC ---
    
    @staticmethod
    def orbit_parameters(body_1: bd.Attractor, body_2: bd.Attractor) -> OrbitParameters:
        """Calculate the orbit parameters

        Args:
            body_1 (bodies.Attractor): First body
            body_2 (bodies.Attractor): Second body
        
        Returns:
            OrbitParameters: Orbit parameters
        """
        
        cm.check_attractor(body_1)
        cm.check_attractor(body_2)
        
        parameters: OrbitParameters = OrbitParameters()
        
        # * Global gravitational parameter
        
        mass_1: u.Quantity = bd.BODIES[body_1].M
        
        mass_2: u.Quantity = bd.BODIES[body_2].M
        
        mu: u.Quantity = pc.universal_gravitational_constant * (mass_1 + mass_2)
        
        # * Inertial angular velocity
        
        body_distance: u.Quantity = bd.BODIES[body_2].semi_major_axis.to(u.km)
        
        parameters.inertial_angular_velocity = np.sqrt(mu / body_distance**3) * u.rad
        
        # * Dimensionless mass ratio
        
        parameters.dimensionless_mass_ratio_1 = mass_1 / (mass_1 + mass_2)
        
        parameters.dimensionless_mass_ratio_2 = mass_2 / (mass_1 + mass_2)
        
        # * Gravitational parameter
        
        parameters.gravitational_parameter_1 = mu * parameters.dimensionless_mass_ratio_1
        
        parameters.gravitational_parameter_2 = mu * parameters.dimensionless_mass_ratio_2
        
        # * Bodies position
        
        parameters.body_position_1 = - parameters.dimensionless_mass_ratio_2 * body_distance
        
        parameters.body_position_2 = + parameters.dimensionless_mass_ratio_1 * body_distance
        
        # * Lagrange points
        
        pi_2: float = parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        f: callable = lambda csi: (1 - pi_2) / np.abs(csi + pi_2)**3 * (csi + pi_2) +\
            pi_2 / np.abs(csi + pi_2 - 1)**3 * (csi + pi_2 - 1) - csi
        
        # >>> Analytic approximations
        
        eps: float = (pi_2 / 3)**(1/3)

        x0_L1: float = 1 - eps
        x0_L2: float = 1 + eps
        x0_L3: float = - 1 - 5 * pi_2 / 12
        
        # >>> Bracketed roots (guaranteed)
        
        csi_1: float = optimize.brentq(f, a=0 + 1e-6, b=1 - pi_2 - 1e-6, maxiter=100, xtol=1e-8, rtol=1e-8)
        csi_2: float = optimize.brentq(f, a=1 - pi_2 + 1e-6, b=10, maxiter=100, xtol=1e-8, rtol=1e-8)
        csi_3: float = optimize.brentq(f, a=-10, b=- pi_2 - 1e-6, maxiter=100, xtol=1e-8, rtol=1e-8)
        
        # >>> Optional Newton refinement
        
        try:
            csi_1 = optimize.newton(f, x0=x0_L1, maxiter=100, tol=1e-8)
        except any:
            pass

        try:
            csi_2 = optimize.newton(f, x0=x0_L2, maxiter=100, tol=1e-8)
        except any:
            pass

        try:
            csi_3 = optimize.newton(f, x0=x0_L3, maxiter=100, tol=1e-8)
        except any:
            pass
        
        r_12: float = body_distance.to_value(u.km)
        
        x_1: float = parameters.body_position_1.to_value(u.km)
        
        parameters.lagrangian_equilibrium_point_1 = np.array([csi_1 * r_12, 0, 0]) * u.km
        parameters.lagrangian_equilibrium_point_2 = np.array([csi_2 * r_12, 0, 0]) * u.km
        parameters.lagrangian_equilibrium_point_3 = np.array([csi_3 * r_12, 0, 0]) * u.km
        parameters.lagrangian_equilibrium_point_4 = np.array([0.5 * r_12 + x_1, + np.sqrt(3) / 2 * r_12, 0]) * u.km
        parameters.lagrangian_equilibrium_point_5 = np.array([0.5 * r_12 + x_1, - np.sqrt(3) / 2 * r_12, 0]) * u.km
        
        return parameters
    
    @staticmethod
    def zero_velocity_curves(body_1: bd.Attractor, body_2: bd.Attractor, jacobi_constant: u.Quantity) -> np.ndarray:
        """Calculate the Zero Velocity Curves (ZVC) given the Jacobi constant

        Args:
            body_1 (bodies.Attractor): First body
            body_2 (bodies.Attractor): Second body
            jacobi_constant (u.Quantity): Jacobi constant
        
        Returns:
            np.ndarray: Zero Velocity Curves
        """
        
        op: OrbitParameters = Orbit.orbit_parameters(body_1=body_1, body_2=body_2)
        
        C: float = jacobi_constant.to_value(u.km**2 / u.s**2)
        
        OMEGA: float = op.inertial_angular_velocity.to_value(u.rad / u.s)
        
        pi_1: float = op.dimensionless_mass_ratio_1.to_value(u.one)
        
        pi_2: float = op.dimensionless_mass_ratio_2.to_value(u.one)
        
        mu_1: float = op.gravitational_parameter_1.to_value(u.km**3 / u.s**2)
        
        mu_2: float = op.gravitational_parameter_2.to_value(u.km**3 / u.s**2)
        
        r_12: float = bd.BODIES[body_2].semi_major_axis.to_value(u.km)
        
        size: int = 1000
        
        # * Create a grid using the Lagrange points as reference
        
        x_arr: np.ndarray = np.linspace(start=op.lagrangian_equilibrium_point_3[0].to_value(u.km) * 1.5,
                                        stop=op.lagrangian_equilibrium_point_2[0].to_value(u.km) * 1.5,
                                        num=size)
        
        y_arr: np.ndarray = np.linspace(start=op.lagrangian_equilibrium_point_5[1].to_value(u.km) * 2,
                                        stop=op.lagrangian_equilibrium_point_4[1].to_value(u.km) * 2,
                                        num=size)
        
        regions: np.ndarray = np.zeros(shape=(size, size))
        
        # * Iterate and apply the Jacobi equation
        
        for x_idx, x in enumerate(x_arr):
            
            for y_idx, y in enumerate(y_arr):
            
                r_1: float = np.sqrt((x + pi_2 * r_12)**2 + y**2)
                r_2: float = np.sqrt((x - pi_1 * r_12)**2 + y**2)
                
                v_squared: float = OMEGA**2 * (x**2 + y**2) + 2 * mu_1 / r_1 + 2 * mu_2 / r_2 + 2 * C
                
                regions[x_idx][y_idx] = +1 if v_squared >= 0.0 else 0.0
        
        return regions
    
    # --- PUBLIC ---
    
    def init(self, body_1: bd.Attractor, body_2: bd.Attractor, position: u.Quantity, velocity: u.Quantity) -> None:
        """
        Initialize the orbit based on cartesian position and velocity vectors

        Args:
            body_1 (bodies.Attractor): First body
            body_2 (bodies.Attractor): Second body
            position (u.Quantity): Position vector
            velocity (u.Quantity): Velocity vector
        """
        
        cm.check_attractor(body_1)
        cm.check_attractor(body_2)
        cm.check_position_vector(position.to_value(u.km))
        cm.check_velocity_vector(velocity.to_value(u.km / u.s))
        
        self.ready = True
        
        self.body_1 = body_1
        
        self.body_2 = body_2
        
        self.position = typing.cast(np.ndarray, position.to(u.km).to_value())
        
        self.velocity = typing.cast(np.ndarray, velocity.to(u.km / u.s).to_value())
    
    def propagate_for(self, delta: time.TimeDelta) -> Result:
        """
        Propagate the orbit for the given delta time

        Args:
            delta (float): Delta time for propagation

        Returns:
            Result: Integration result
        """
        
        cm.check_time_delta(delta)
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        result: Result = Result()
        
        parameters: OrbitParameters = Orbit.orbit_parameters(body_1=self.body_1, body_2=self.body_2)
        
        solution: dict = ode.solve_ivp(fun=self._equations_relative_motion,
                                       t_span=[0, delta.to_value(u.s)],
                                       y0=np.concat([self.position, self.velocity]),
                                       method='RK45',
                                       args=(parameters, ),
                                       rtol=1e-12,
                                       atol=1e-12)
        
        result.success = solution['success']
        result.time = solution['t'] * u.s
        result.position_x = solution['y'][0, :] * u.km
        result.position_y = solution['y'][1, :] * u.km
        result.position_z = solution['y'][2, :] * u.km
        result.velocity_x = solution['y'][3, :] * u.km / u.s
        result.velocity_y = solution['y'][4, :] * u.km / u.s
        result.velocity_z = solution['y'][5, :] * u.km / u.s
        
        return result
    
    # --- PRIVATE ---
    
    def _equations_relative_motion(self, t : float, X : np.ndarray, orbit_parameters : OrbitParameters) -> np.ndarray:
        """        
        Equations of motion for the Circular Restricted Three-Body Problem (CR3BP) in the rotating synodic frame.

        The state vector is:
            X = [x, y, z, v_x, v_y, v_z]

        Let the two primaries have gravitational parameters μ₁ and μ₂, and let their positions along the x-axis in the
        rotating frame be x₁ and x₂. The distances from the third body to each primary are:

            r₁ = sqrt((x - x₁)² + y² + z²)
            r₂ = sqrt((x - x₂)² + y² + z²)

        The rotating frame has angular velocity Ω, so the Coriolis and centrifugal terms appear explicitly.

        The equations of motion are:

            dx/dt   = v_x
            dy/dt   = v_y
            dz/dt   = v_z

            dv_x/dt = + 2 Ω v_y + Ω² x - μ₁ (x - x₁) / r₁³ - μ₂ (x - x₂) / r₂³
            dv_y/dt = - 2 Ω v_x + Ω² y - μ₁ y / r₁³ - μ₂ y / r₂³
            dv_z/dt = - μ₁ z / r₁³ - μ₂ z / r₂³

        These are the standard dimensional CR3BP equations in the uniformly rotating synodic frame.

        Args:
            t (float): Time (included for ODE solver compatibility)
            X (np.ndarray): State vector [x, y, z, v_x, v_y, v_z]
            orbit_parameters (OrbitParameters): Precomputed CR3BP parameters including μ₁, μ₂, Ω, x₁, x₂.

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        x, y, z, v_x, v_y, v_z = X
        
        OMEGA: float = orbit_parameters.inertial_angular_velocity.to_value(u.rad / u.s)
        
        mu_1: float = orbit_parameters.gravitational_parameter_1.to_value(u.km**3 / u.s**2)
        
        mu_2: float = orbit_parameters.gravitational_parameter_2.to_value(u.km**3 / u.s**2)
        
        x_1: float = orbit_parameters.body_position_1.to_value(u.km)
        
        x_2: float = orbit_parameters.body_position_2.to_value(u.km)
        
        r_1: float = np.sqrt((x - x_1)**2 + y**2 + z**2)
        
        r_2: float = np.sqrt((x - x_2)**2 + y**2 + z**2)
        
        dx_dt = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = + 2 * OMEGA * v_y + OMEGA**2 * x - mu_1 / r_1**3 * (x - x_1) - mu_2 / r_2**3 * (x - x_2)
        dx_dt[4] = - 2 * OMEGA * v_x + OMEGA**2 * y - mu_1 / r_1**3 * y - mu_2 / r_2**3 * y
        dx_dt[5] = - mu_1 / r_1**3 * z - mu_2 / r_2**3 * z
        
        return dx_dt
