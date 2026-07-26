import astropy.units as u
import numpy as np

import astro.bodies as bd
import astro.circular_restricted_three_body_problem as cr3bp

def test_orbit_parameters_1():
    """EXAMPLE 2.16"""
    
    body_1: bd.Attractor = bd.Attractor.EARTH
    
    body_2: bd.Attractor = bd.Attractor.MOON

    op: cr3bp.OrbitParametersCR3BP = cr3bp.Orbit.orbit_parameters(body_1=body_1, body_2=body_2)
    
    assert np.isclose(op.dimensionless_mass_ratio_2.to_value(u.one), 0.01215, atol=1e-4)
    assert np.isclose(op.lagrangian_equilibrium_point_1[0].to_value(u.km), 32_1760, atol=1e0)
    assert np.isclose(op.lagrangian_equilibrium_point_2[0].to_value(u.km), 444325, atol=1e0)
    assert np.isclose(op.lagrangian_equilibrium_point_3[0].to_value(u.km), -386413, atol=1e0)

def test_orbit_parameters_2():
    """"""
    
    body_1: bd.Attractor = bd.Attractor.SUN
    
    body_2: bd.Attractor = bd.Attractor.EARTH

    op: cr3bp.OrbitParametersCR3BP = cr3bp.Orbit.orbit_parameters(body_1=body_1, body_2=body_2)
    
    assert np.isclose(op.lagrangian_equilibrium_point_1[0].to_value(u.km), 148_110_000, atol=1e5)
    assert np.isclose(op.lagrangian_equilibrium_point_2[0].to_value(u.km), 151_100_000, atol=1e5)
    assert np.isclose(op.lagrangian_equilibrium_point_3[0].to_value(u.km), -149_600_000, atol=1e5)
