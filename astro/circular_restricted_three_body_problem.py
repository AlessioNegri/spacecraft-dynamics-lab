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

- Ulrich Walter, "Astronautics - The Physics of Space Flight"
    - Chapter 11: Three-Body Problem
"""

import astropy.time as time
import astropy.units as u
import numpy as np
import scipy.integrate as ode
import scipy.optimize as optimize
import typing

import astro.bodies as bodies
import astro.common as common
import astro.physical_constants as physical_constants

from astro.enums import LibrationPoint
from astro.models.orbit_parameters import OrbitParametersCR3BP
from astro.models.results import ResultCR3BP

class Orbit:
    """Generic orbit in circular restricted three-body problem"""
    
    def __init__(self):
        """Constructor"""
        
        self.ready: bool = False
        
        self.body_1: bodies.Body = bodies.get_body(bodies.Attractor.EARTH)
        
        self.body_2: bodies.Body = bodies.get_body(bodies.Attractor.MOON)
        
        self.position: np.ndarray = np.zeros(3)
        
        self.velocity: np.ndarray = np.zeros(3)
    
    # --- STATIC ---
    
    @staticmethod
    def orbit_parameters(body_1: bodies.Attractor, body_2: bodies.Attractor) -> OrbitParametersCR3BP:
        """
        Calculate the orbit parameters
        
        The *collinear equilibrium points* are also known as **Eulerian points** L1, L2, L3, and the *equilateral
        equilibrium points* are also known as **Lagrangian points** L4 and L5. All five points together are the so-called
        **libration points**, but quite frequently and confusingly they are also called Lagrangian points.

        Args:
            body_1 (bodies.Attractor): First body
            body_2 (bodies.Attractor): Second body
        
        Returns:
            OrbitParametersCR3BP: Orbit parameters
        """
        
        common.check_attractor(body_1)
        common.check_attractor(body_2)
        
        parameters: OrbitParametersCR3BP = OrbitParametersCR3BP()
        
        # * Global gravitational parameter
        
        mass_1: u.Quantity = bodies.BODIES[body_1].M
        
        mass_2: u.Quantity = bodies.BODIES[body_2].M
        
        mu: u.Quantity = physical_constants.universal_gravitational_constant * (mass_1 + mass_2)
        
        # * Inertial angular velocity
        
        body_distance: u.Quantity = bodies.BODIES[body_2].semi_major_axis.to(u.km)
        
        parameters.body_distance = body_distance
        
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
        
        # * Libration points
        
        pi_2: float = parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        f: callable = lambda csi: (1 - pi_2) / np.abs(csi + pi_2)**3 * (csi + pi_2) +\
            pi_2 / np.abs(csi + pi_2 - 1)**3 * (csi + pi_2 - 1) - csi
        
        # >>> Analytic approximations
        
        eps: float = (pi_2 / 3)**(1/3)

        x0_lagrange_1: float = 1 - eps
        x0_lagrange_2: float = 1 + eps
        x0_lagrange_3: float = - 1 - 5 * pi_2 / 12
        
        # >>> Bracketed roots (guaranteed)
        
        csi_1: float = optimize.brentq(f, a=0 + 1e-6, b=1 - pi_2 - 1e-6, maxiter=100, xtol=1e-8, rtol=1e-8)
        csi_2: float = optimize.brentq(f, a=1 - pi_2 + 1e-6, b=10, maxiter=100, xtol=1e-8, rtol=1e-8)
        csi_3: float = optimize.brentq(f, a=-10, b=- pi_2 - 1e-6, maxiter=100, xtol=1e-8, rtol=1e-8)
        
        # >>> Optional Newton refinement
        
        try:
            csi_1 = optimize.newton(f, x0=x0_lagrange_1, maxiter=100, tol=1e-8)
        except any:
            pass

        try:
            csi_2 = optimize.newton(f, x0=x0_lagrange_2, maxiter=100, tol=1e-8)
        except any:
            pass

        try:
            csi_3 = optimize.newton(f, x0=x0_lagrange_3, maxiter=100, tol=1e-8)
        except any:
            pass
        
        r_12: float = body_distance.to_value(u.km)
        
        x_1: float = parameters.body_position_1.to_value(u.km)
        
        # >>> Eulerian points
        
        parameters.lagrangian_equilibrium_point_1 = np.array([csi_1 * r_12, 0, 0]) * u.km
        parameters.lagrangian_equilibrium_point_2 = np.array([csi_2 * r_12, 0, 0]) * u.km
        parameters.lagrangian_equilibrium_point_3 = np.array([csi_3 * r_12, 0, 0]) * u.km
        
        # >>> Lagrangian points
        
        parameters.lagrangian_equilibrium_point_4 = np.array([0.5 * r_12 + x_1, + np.sqrt(3) / 2 * r_12, 0]) * u.km
        parameters.lagrangian_equilibrium_point_5 = np.array([0.5 * r_12 + x_1, - np.sqrt(3) / 2 * r_12, 0]) * u.km
        
        return parameters
    
    @staticmethod
    def zero_velocity_curves(body_1: bodies.Attractor,
                             body_2: bodies.Attractor,
                             jacobi_constant: u.Quantity) -> np.ndarray:
        """
        Calculate the Zero Velocity Curves (ZVC), a.k.a. Hill curve, given the Jacobi constant.

        Args:
            body_1 (bodies.Attractor): First body
            body_2 (bodies.Attractor): Second body
            jacobi_constant (u.Quantity): Jacobi constant
        
        Returns:
            np.ndarray: Zero Velocity Curves
        """
        
        op: OrbitParametersCR3BP = Orbit.orbit_parameters(body_1=body_1, body_2=body_2)
        
        C: float = jacobi_constant.to_value(u.km**2 / u.s**2)
        
        OMEGA: float = op.inertial_angular_velocity.to_value(u.rad / u.s)
        
        pi_1: float = op.dimensionless_mass_ratio_1.to_value(u.one)
        
        pi_2: float = op.dimensionless_mass_ratio_2.to_value(u.one)
        
        mu_1: float = op.gravitational_parameter_1.to_value(u.km**3 / u.s**2)
        
        mu_2: float = op.gravitational_parameter_2.to_value(u.km**3 / u.s**2)
        
        r_12: float = bodies.BODIES[body_2].semi_major_axis.to_value(u.km)
        
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
    
    def init(self,
             body_1: bodies.Attractor,
             body_2: bodies.Attractor,
             position: u.Quantity,
             velocity: u.Quantity) -> None:
        """
        Initialize the orbit based on cartesian position and velocity vectors

        Args:
            body_1 (bodies.Attractor): First body
            body_2 (bodies.Attractor): Second body
            position (u.Quantity): Position vector
            velocity (u.Quantity): Velocity vector
        """
        
        common.check_attractor(body_1)
        common.check_attractor(body_2)
        common.check_position_vector(position.to_value(u.km))
        common.check_velocity_vector(velocity.to_value(u.km / u.s))
        
        self.ready = True
        
        self.body_1 = body_1
        
        self.body_2 = body_2
        
        self.position = typing.cast(np.ndarray, position.to(u.km).to_value())
        
        self.velocity = typing.cast(np.ndarray, velocity.to(u.km / u.s).to_value())
    
    def propagate_for(self, delta: time.TimeDelta, dimensionless: bool = False) -> ResultCR3BP:
        """
        Propagate the orbit for the given delta time

        Args:
            delta (float): Delta time for propagation
            dimensionless (bool, optional): If True, use dimensionless equations of motion. Defaults to False.

        Returns:
            ResultCR3BP: Integration result
        """
        
        common.check_time_delta(delta)
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        result: ResultCR3BP = ResultCR3BP()
        
        parameters: OrbitParametersCR3BP = Orbit.orbit_parameters(body_1=self.body_1, body_2=self.body_2)
        
        if dimensionless:
            
            L: float = bodies.BODIES[self.body_2].semi_major_axis.to_value(u.km)
            n: float = parameters.inertial_angular_velocity.to_value(u.rad / u.s)
            
            solution: dict = ode.solve_ivp(fun=self._equations_relative_motion_dimensionless,
                                        t_span=[0, delta.to_value(u.s) * n],
                                        y0=np.concat([self.position / L, self.velocity / L / n]),
                                        method='RK45',
                                        args=(parameters, ),
                                        rtol=1e-12,
                                        atol=1e-12)
            
            result.success = solution['success']
            result.time = solution['t'] / n * u.s
            result.position_x = solution['y'][0, :] * L * u.km
            result.position_y = solution['y'][1, :] * L * u.km
            result.position_z = solution['y'][2, :] * L * u.km
            result.velocity_x = solution['y'][3, :] * n * L * u.km / u.s
            result.velocity_y = solution['y'][4, :] * n * L * u.km / u.s
            result.velocity_z = solution['y'][5, :] * n * L * u.km / u.s
        
        else:
            
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
    
    def propagate_libration_for(self, delta: time.TimeDelta, libration_point: LibrationPoint) -> ResultCR3BP:
        """
        Propagate the orbit for the given delta time
        
        Propagate the CR3BP dynamics in the rotating synodic frame, using the dimensionless libration-point-centered
        equations of motion.

        This routine integrates the motion of a massless particle relative to a chosen libration point (L1-L5).
        The state is internally converted to the standard CR3BP nondimensional units:

        - Distance unit: separation between the primaries (L)
        - Time unit: 1 / n, where n is the mean motion of the primaries
        - Velocity unit: n·L

        The initial dimensional state (km, km/s) is converted to nondimensional form, integrated using the
        libration-point equations, and converted back to physical units upon return.

        Args:
            delta (float): Delta time for propagation
            libration_point (LibrationPoint): Selected equilibrium point (L1-L5)

        Returns:
            ResultCR3BP: Integration result
        """
        
        common.check_time_delta(delta)
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        result: ResultCR3BP = ResultCR3BP()
        
        parameters: OrbitParametersCR3BP = Orbit.orbit_parameters(body_1=self.body_1, body_2=self.body_2)
            
        L: float = bodies.BODIES[self.body_2].semi_major_axis.to_value(u.km)
        
        n: float = parameters.inertial_angular_velocity.to_value(u.rad / u.s)
        
        solution: dict = ode.solve_ivp(fun=self._equations_relative_motion_libration_dimensionless,
                                       t_span=[0, delta.to_value(u.s) * n],
                                       y0=np.concat([self.position / L, self.velocity / L / n]),
                                       method='RK45',
                                       args=(parameters, libration_point),
                                       rtol=1e-12,
                                       atol=1e-12)
        
        result.success = solution['success']
        result.time = solution['t'] / n * u.s
        result.position_x = solution['y'][0, :] * L * u.km
        result.position_y = solution['y'][1, :] * L * u.km
        result.position_z = solution['y'][2, :] * L * u.km
        result.velocity_x = solution['y'][3, :] * n * L * u.km / u.s
        result.velocity_y = solution['y'][4, :] * n * L * u.km / u.s
        result.velocity_z = solution['y'][5, :] * n * L * u.km / u.s
        
        return result
    
    def propagate_eulerian_for(self, delta: time.TimeDelta, libration_point: LibrationPoint) -> ResultCR3BP:
        """
        Propagate the linearized (Eulerian) CR3BP dynamics about a selected collinear libration point (L1, L2, or L3) in
        the rotating synodic frame.

        This routine integrates the motion of a massless particle using the dimensionless Eulerian approximation, which
        is obtained by linearizing the CR3BP equations of motion around a collinear equilibrium point. The nonlinear
        gravitational terms are replaced by constant curvature coefficients (c₂) derived from the second derivatives of
        the effective potential at the chosen libration point.

        The initial dimensional state (km, km/s) is internally converted to the standard CR3BP nondimensional units:

            - Distance unit: separation between the primaries (L)
            - Time unit: 1 / n, where n is the mean motion of the primaries
            - Velocity unit: n·L

        The state is then propagated using the Eulerian linearized equations, and the resulting nondimensional trajectory
        is converted back to physical units upon return.

        Args:
            delta (TimeDelta): Dimensional propagation time
            libration_point (LibrationPoint): Selected collinear equilibrium point (L1, L2, or L3)

        Returns:
            ResultCR3BP: Object containing dimensional time, position, velocity, and integration success flag
        """
        
        common.check_time_delta(delta)
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        result: ResultCR3BP = ResultCR3BP()
        
        parameters: OrbitParametersCR3BP = Orbit.orbit_parameters(body_1=self.body_1, body_2=self.body_2)
            
        L: float = bodies.BODIES[self.body_2].semi_major_axis.to_value(u.km)
        
        n: float = parameters.inertial_angular_velocity.to_value(u.rad / u.s)
        
        solution: dict = ode.solve_ivp(fun=self._equations_relative_motion_eulerian_dimensionless,
                                        t_span=[0, delta.to_value(u.s) * n],
                                        y0=np.concat([self.position / L, self.velocity / L / n]),
                                        method='RK45',
                                        args=(parameters, libration_point),
                                        rtol=1e-12,
                                        atol=1e-12)
        
        result.success = solution['success']
        result.time = solution['t'] / n * u.s
        result.position_x = solution['y'][0, :] * L * u.km
        result.position_y = solution['y'][1, :] * L * u.km
        result.position_z = solution['y'][2, :] * L * u.km
        result.velocity_x = solution['y'][3, :] * n * L * u.km / u.s
        result.velocity_y = solution['y'][4, :] * n * L * u.km / u.s
        result.velocity_z = solution['y'][5, :] * n * L * u.km / u.s
        
        return result
    
    def propagate_lagrangian_for(self, delta: time.TimeDelta, libration_point: LibrationPoint) -> ResultCR3BP:
        """
        Propagate the linearized (Lagrangian) CR3BP dynamics about a selected equilateral libration point (L4 or L5) in
        the rotating synodic frame.

        This routine integrates the motion of a massless particle using the dimensionless Lagrangian approximation, which
        is obtained by linearizing the CR3BP equations of motion around an equilateral equilibrium point. The nonlinear
        gravitational terms are replaced by constant curvature coefficients (c) derived from the second derivatives of
        the effective potential at the chosen libration point.

        The initial dimensional state (km, km/s) is internally converted to the standard CR3BP nondimensional units:

            - Distance unit: separation between the primaries (L)
            - Time unit: 1 / n, where n is the mean motion of the primaries
            - Velocity unit: n·L

        The state is then propagated using the Lagrangian linearized equations, and the resulting nondimensional trajectory
        is converted back to physical units upon return.

        Args:
            delta (TimeDelta): Dimensional propagation time
            libration_point (LibrationPoint): Selected equilateral equilibrium point (L4 or L5)

        Returns:
            ResultCR3BP: Object containing dimensional time, position, velocity, and integration success flag
        """
        
        common.check_time_delta(delta)
        
        if not self.ready: raise ValueError("Orbit object is not ready")
        
        result: ResultCR3BP = ResultCR3BP()
        
        parameters: OrbitParametersCR3BP = Orbit.orbit_parameters(body_1=self.body_1, body_2=self.body_2)
            
        L: float = bodies.BODIES[self.body_2].semi_major_axis.to_value(u.km)
        
        n: float = parameters.inertial_angular_velocity.to_value(u.rad / u.s)
        
        solution: dict = ode.solve_ivp(fun=self._equations_relative_motion_lagrangian_dimensionless,
                                        t_span=[0, delta.to_value(u.s) * n],
                                        y0=np.concat([self.position / L, self.velocity / L / n]),
                                        method='RK45',
                                        args=(parameters, libration_point),
                                        rtol=1e-12,
                                        atol=1e-12)
        
        result.success = solution['success']
        result.time = solution['t'] / n * u.s
        result.position_x = solution['y'][0, :] * L * u.km
        result.position_y = solution['y'][1, :] * L * u.km
        result.position_z = solution['y'][2, :] * L * u.km
        result.velocity_x = solution['y'][3, :] * n * L * u.km / u.s
        result.velocity_y = solution['y'][4, :] * n * L * u.km / u.s
        result.velocity_z = solution['y'][5, :] * n * L * u.km / u.s
        
        return result
    
    # --- PRIVATE ---
    
    def _equations_relative_motion(self,
                                   t: float,
                                   X: np.ndarray,
                                   orbit_parameters: OrbitParametersCR3BP) -> np.ndarray:
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
    
    def _equations_relative_motion_dimensionless(self,
                                                 t: float,
                                                 X: np.ndarray,
                                                 orbit_parameters: OrbitParametersCR3BP) -> np.ndarray:
        """
        Dimensionless equations of motion for the Circular Restricted Three-Body Problem (CR3BP) in the rotating
        synodic frame.

        The state vector is:
            X = [ξ, η, ζ, v_ξ, v_η, v_ζ]

        where (ξ, η, ζ) are the nondimensional position coordinates and (v_ξ, v_η, v_ζ) are the nondimensional
        velocity components. All quantities are expressed in the standard CR3BP normalization:
        
            - Distance unit: separation between the two primaries
            - Mass unit: total mass of the system
            - Time unit: chosen such that the mean motion n = 1
            - Gravitational parameters satisfy μ₁ = 1 - μ and μ₂ = μ

        The primaries lie on the x-axis at:
            Primary 1 (larger):  ξ = −μ
            Primary 2 (smaller): ξ = 1 - μ

        Distances to the primaries are:
            ρ₁ = sqrt((ξ + μ)² + η² + ζ²)
            ρ₂ = sqrt((ξ - (1 - μ))² + η² + ζ²)

        The dimensionless CR3BP equations in the rotating frame are:

            dξ/dt   = v_ξ
            dη/dt   = v_η
            dζ/dt   = v_ζ

            dv_ξ/dt = + 2 v_η + ξ - (1 - μ) (ξ + μ) / ρ₁³ - μ (ξ - (1 - μ)) / ρ₂³

            dv_η/dt = - 2 v_ξ + η - (1 - μ) η / ρ₁³ - μ η / ρ₂³

            dv_ζ/dt = - (1 - μ) ζ / ρ₁³ - μ ζ / ρ₂³

        These are the standard nondimensional CR3BP equations describing the motion of a massless third body under
        the gravitational influence of two primaries in a rotating frame where the primaries remain fixed.

        Args:
            t (float): Dimensionless time (included for ODE solver compatibility)
            X (np.ndarray): State vector [ξ, η, ζ, v_ξ, v_η, v_ζ]
            orbit_parameters (OrbitParameters): Precomputed CR3BP parameters including μ₂.

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        csi, eta, zeta, v_csi, v_eta, v_zeta = X
        
        mu: float = orbit_parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        drho_1: float = np.sqrt((csi + mu)**2 + eta**2 + zeta**2)
        
        drho_2: float = np.sqrt((csi - (1 - mu))**2 + eta**2 + zeta**2)
        
        dx_dt = np.zeros(shape=(6))
        
        dx_dt[0] = v_csi
        dx_dt[1] = v_eta
        dx_dt[2] = v_zeta
        dx_dt[3] = + 2 * v_eta + csi - (1 - mu) / drho_1**3 * (csi + mu) - mu / drho_2**3 * (csi - (1 - mu))
        dx_dt[4] = - 2 * v_csi + eta - (1 - mu) / drho_1**3 * eta - mu / drho_2**3 * eta
        dx_dt[5] = - (1 - mu) / drho_1**3 * zeta - mu / drho_2**3 * zeta
        
        return dx_dt
    
    def _equations_relative_motion_libration_dimensionless(self,
                                                           t: float,
                                                           X: np.ndarray,
                                                           orbit_parameters: OrbitParametersCR3BP,
                                                           libration_point: LibrationPoint) -> np.ndarray:
        """
        Dimensionless CR3BP equations of motion expressed in a libration-point-centered rotating synodic frame.

        The state vector is:
            X = [ξ, η, ζ, v_ξ, v_η, v_ζ]

        where (ξ, η, ζ) are nondimensional coordinates relative to the chosen libration point, and (v_ξ, v_η, v_ζ) are
        nondimensional velocity components. All quantities follow the standard CR3BP normalization:

            - Distance unit: separation between the primaries (L)
            - Mass unit: total mass of the system
            - Time unit: chosen such that the mean motion n = 1
            - Gravitational parameters: μ₁ = 1 - μ, μ₂ = μ

        The primaries lie at:
            Primary 1: (−μ, 0)
            Primary 2: (1 - μ, 0)

        The libration point coordinates (ξ_L, η_L) are obtained from the supplied OrbitParametersCR3BP object and used
        to shift the frame so that the origin coincides with the selected equilibrium point.

        Distances to the primaries in the libration-centered frame are:

            ρ₁ = sqrt((ξ - ξ₁)² + (η - η₁)² + ζ²)
            ρ₂ = sqrt((ξ - ξ₂)² + (η - η₂)² + ζ²)

        The equations of motion in this shifted rotating frame are:

            dξ/dt   = v_ξ
            dη/dt   = v_η
            dζ/dt   = v_ζ

            dv_ξ/dt = + 2 v_η + ξ + ξ_L - (1 - μ)(ξ - ξ₁)/ρ₁³ - μ(ξ - ξ₂)/ρ₂³

            dv_η/dt = - 2 v_ξ + η + η_L - (1 - μ)(η - η₁)/ρ₁³ - μ(η - η₂)/ρ₂³

            dv_ζ/dt = - (1 - μ) ζ / ρ₁³ - μ ζ / ρ₂³

        These equations describe the motion of a massless particle relative to a libration point in the CR3BP rotating
        frame, preserving the nondimensional structure of the classical formulation.

        Args:
            t (float): Dimensionless time (included for ODE solver compatibility)
            X (np.ndarray): State vector [ξ, η, ζ, v_ξ, v_η, v_ζ]
            orbit_parameters (OrbitParameters): Precomputed CR3BP parameters including μ₂, primaries and libration points

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        x, y, z, v_x, v_y, v_z = X
        
        mu: float = orbit_parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        L: float = orbit_parameters.body_distance.to_value(u.km)
        
        match libration_point:
            
            case LibrationPoint.L1:
            
                csi_L: float = orbit_parameters.lagrangian_equilibrium_point_1[0].to_value(u.km) / L
                eta_L: float = orbit_parameters.lagrangian_equilibrium_point_1[1].to_value(u.km) / L
        
            case LibrationPoint.L2:
            
                csi_L: float = orbit_parameters.lagrangian_equilibrium_point_2[0].to_value(u.km) / L
                eta_L: float = orbit_parameters.lagrangian_equilibrium_point_2[1].to_value(u.km) / L
                
            case LibrationPoint.L3:
            
                csi_L: float = orbit_parameters.lagrangian_equilibrium_point_3[0].to_value(u.km) / L
                eta_L: float = orbit_parameters.lagrangian_equilibrium_point_3[1].to_value(u.km) / L
                
            case LibrationPoint.L4:
            
                csi_L: float = orbit_parameters.lagrangian_equilibrium_point_4[0].to_value(u.km) / L
                eta_L: float = orbit_parameters.lagrangian_equilibrium_point_4[1].to_value(u.km) / L
                
            case LibrationPoint.L5:
            
                csi_L: float = orbit_parameters.lagrangian_equilibrium_point_5[0].to_value(u.km) / L
                eta_L: float = orbit_parameters.lagrangian_equilibrium_point_5[1].to_value(u.km) / L
                
            case _:
                
                csi_L: float = 0
                eta_L: float = 0
        
        rho_L: np.ndarray = np.array([csi_L, eta_L, 0])
        
        csi_1: float = orbit_parameters.body_position_1.to_value(u.km) / L
        eta_1: float = 0
        csi_2: float = orbit_parameters.body_position_2.to_value(u.km) / L
        eta_2: float = 0
        
        x_1: float = csi_1 - csi_L
        y_1: float = eta_1 - eta_L
        x_2: float = csi_2 - csi_L
        y_2: float = eta_2 - eta_L
        
        dr_1: float = np.sqrt((x - x_1)**2 + (y - y_1)**2 + z**2)
        
        dr_2: float = np.sqrt((x - x_2)**2 + (y - y_2)**2 + z**2)
        
        dx_dt = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = + 2 * v_y + x + rho_L[0] - (1 - mu) / dr_1**3 * (x - x_1) - mu / dr_2**3 * (x - x_2)
        dx_dt[4] = - 2 * v_x + y + rho_L[1] - (1 - mu) / dr_1**3 * (y - y_1) - mu / dr_2**3 * (y - y_2)
        dx_dt[5] =                 rho_L[2] - (1 - mu) / dr_1**3 * z         - mu / dr_2**3 * z
        
        return dx_dt
    
    def _equations_relative_motion_eulerian_dimensionless(self,
                                                          t: float,
                                                          X: np.ndarray,
                                                          orbit_parameters: OrbitParametersCR3BP,
                                                          libration_point: LibrationPoint) -> np.ndarray:
        """
        Dimensionless linearized (Eulerian) CR3BP equations of motion about a collinear libration point (L1, L2, or L3)
        in the rotating synodic frame.
        
        This model represents the second-order Taylor expansion of the CR3BP equations around an equilibrium point. The
        nonlinear gravitational terms are replaced by constant coefficients derived from the curvature of the effective
        potential at the selected libration point. The resulting system is linear and captures the local saddle-center
        dynamics characteristic of collinear points.

        The state vector is:
            X = [ξ, η, ζ, v_ξ, v_η, v_ζ]

        where (ξ, η, ζ) are nondimensional displacements from the chosen libration point, and (v_ξ, v_η, v_ζ) are
        nondimensional velocity components. All quantities follow the standard CR3BP normalization:

            - Distance unit: separation between the primaries (L)
            - Time unit: chosen such that the mean motion n = 1
            - Velocity unit: n·L
            - Mass parameters: μ₁ = 1 - μ, μ₂ = μ

        Linearized coefficients:
            The curvature parameter c₂ is selected according to the libration point:

            L1: c₂ = 4 + 6 λ
            L2: c₂ = 4 - 6 λ
            L3: c₂ = 1 + (7/8) μ

        where λ = (μ/3)^(1/3). These values arise from the second derivatives of
        the effective potential evaluated at the collinear equilibrium points.

        Linearized Eulerian equations:

            dξ/dt   = v_ξ
            dη/dt   = v_η
            dζ/dt   = v_ζ

            dv_ξ/dt = + 2 v_η + (1 + 2 c₂) ξ
            dv_η/dt = - 2 v_ξ + (1 - c₂) η
            dv_ζ/dt =         -   c₂ ζ

        These equations describe the local dynamics near a collinear libration point and are commonly used for stability
        analysis, invariant manifold computation, and initialization of periodic orbits.

        Args:
            t (float): Dimensionless time (included for ODE solver compatibility)
            X (np.ndarray): State vector [ξ, η, ζ, v_ξ, v_η, v_ζ]
            orbit_parameters (OrbitParameters): Precomputed CR3BP parameters including μ and libration points

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        x, y, z, v_x, v_y, v_z = X
        
        mu: float = orbit_parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        lambda_: float = (mu / 3)**(1/3)
        
        match libration_point:
            
            case LibrationPoint.L1:
                
                c_2: float = 4 + 6 * lambda_
        
            case LibrationPoint.L2:
            
                c_2: float = 4 - 6 * lambda_
                
            case LibrationPoint.L3:
            
                c_2: float = 1 + 7/8 * mu
                
            case _:
                
                c_2: float = 0.0
        
        dx_dt = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = + 2 * v_y + (1 + 2 * c_2) * x
        dx_dt[4] = - 2 * v_x + (1 - c_2) * y
        dx_dt[5] =           - c_2 * z
        
        return dx_dt
    
    def _equations_relative_motion_lagrangian_dimensionless(self,
                                                            t: float,
                                                            X: np.ndarray,
                                                            orbit_parameters: OrbitParametersCR3BP,
                                                            libration_point: LibrationPoint) -> np.ndarray:
        """
        Dimensionless linearized (Lagrangian) CR3BP equations of motion about an equilateral libration point (L4 or L5)
        in the rotating synodic frame.
        
        This model represents the second-order Taylor expansion of the CR3BP equations around an equilibrium point. The
        nonlinear gravitational terms are replaced by constant coefficients derived from the curvature of the effective
        potential at the selected libration point. The resulting system is linear and captures the local saddle-center
        dynamics characteristic of equilateral points.

        The state vector is:
            X = [ξ, η, ζ, v_ξ, v_η, v_ζ]

        where (ξ, η, ζ) are nondimensional displacements from the chosen libration point, and (v_ξ, v_η, v_ζ) are
        nondimensional velocity components. All quantities follow the standard CR3BP normalization:

            - Distance unit: separation between the primaries (L)
            - Time unit: chosen such that the mean motion n = 1
            - Velocity unit: n·L
            - Mass parameters: μ₁ = 1 - μ, μ₂ = μ
        
        Linearized coefficients:
            For the equilateral points, the coupling coefficient c is:

                L4:  c = -(3√3/4)(1 - 2μ)
                L5:  c = +(3√3/4)(1 - 2μ)

            These values arise from the mixed second derivatives of the effective potential at the triangular
            equilibrium points.

        Linearized Lagrangian equations:

            dξ/dt   = v_ξ
            dη/dt   = v_η
            dζ/dt   = v_ζ

            dv_ξ/dt = + 2 v_η + (3/4) ξ + c η
            dv_η/dt = - 2 v_ξ + (9/4) η + c ξ
            dv_ζ/dt =         - ζ

        These equations describe the local dynamics near an equilateral libration point and are commonly used for
        stability analysis, invariant manifold computation, and initialization of periodic orbits.

        Args:
            t (float): Dimensionless time (included for ODE solver compatibility)
            X (np.ndarray): State vector [ξ, η, ζ, v_ξ, v_η, v_ζ]
            orbit_parameters (OrbitParameters): Precomputed CR3BP parameters including μ and libration points

        Returns:
            np.ndarray: Time derivative dx_dt
        """
        
        x, y, z, v_x, v_y, v_z = X
        
        mu: float = orbit_parameters.dimensionless_mass_ratio_2.to_value(u.one)
        
        c: float = 0
        
        match libration_point:
            
            case LibrationPoint.L4:
                
                c: float = - 3 * np.sqrt(3) * (1 - 2 * mu) / 4
        
            case LibrationPoint.L5:
            
                c: float = + 3 * np.sqrt(3) * (1 - 2 * mu) / 4
                
            case _:
                
                c: float = 0.0
        
        dx_dt = np.zeros(shape=(6))
        
        dx_dt[0] = v_x
        dx_dt[1] = v_y
        dx_dt[2] = v_z
        dx_dt[3] = + 2 * v_y + 3/4 * x + c * y
        dx_dt[4] = - 2 * v_x + 9/4 * y + c * x
        dx_dt[5] =           - z
        
        return dx_dt
