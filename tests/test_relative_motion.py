import astropy.units as u
import numpy as np

import astro.bodies as bd
import astro.orbit_3d as o3d
import astro.relative_motion as rm

def test_lvlh_kinematics_and_geocentric_equatorial_kinematics():
    """EXAMPLE 7.1"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    oe_target: o3d.OrbitalElements = o3d.OrbitalElements(h=52059 * u.km**2 / u.s,
                                                         ecc=0.025724 * u.dimensionless_unscaled,
                                                         inc=60 * u.deg,
                                                         raan=40 * u.deg,
                                                         argp=30 * u.deg,
                                                         nu=40 * u.deg)
    
    r_target, v_target = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe_target)
    
    oe_chaser: o3d.OrbitalElements = o3d.OrbitalElements(h=52362 * u.km**2 / u.s,
                                                         ecc=0.0072696 * u.dimensionless_unscaled,
                                                         inc=50 * u.deg,
                                                         raan=40 * u.deg,
                                                         argp=120 * u.deg,
                                                         nu=40 * u.deg)
    
    r_chaser, v_chaser = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe_chaser)
    
    kinematics = rm.RelativeMotion.lvlh_kinematics(attractor=attractor, oe_target=oe_target, oe_chaser=oe_chaser)
    
    r_rel_lvlh: u.Quantity = kinematics[0]
    v_rel_lvlh: u.Quantity = kinematics[1]
    a_rel_lvlh: u.Quantity = kinematics[2]
    
    assert np.isclose(r_rel_lvlh[0].to_value(u.km), -6701.20, atol=1e-2)
    assert np.isclose(r_rel_lvlh[1].to_value(u.km), +6828.30, atol=1e-2)
    assert np.isclose(r_rel_lvlh[2].to_value(u.km), -0406.26, atol=1e-2)
    
    assert np.isclose(v_rel_lvlh[0].to_value(u.km / u.s), 0.31667, atol=1e-5)
    assert np.isclose(v_rel_lvlh[1].to_value(u.km / u.s), 0.11199, atol=1e-5)
    assert np.isclose(v_rel_lvlh[2].to_value(u.km / u.s), 1.24696, atol=1e-5)
    
    assert np.isclose(a_rel_lvlh[0].to_value(u.km / u.s**2), -0.00022222, atol=1e-8)
    assert np.isclose(a_rel_lvlh[1].to_value(u.km / u.s**2), -0.00018074, atol=1e-8)
    assert np.isclose(a_rel_lvlh[2].to_value(u.km / u.s**2), +0.00050593, atol=1e-8)
    
    kinematics = rm.RelativeMotion.geocentric_equatorial_kinematics(r_target=r_target,
                                                                    v_target=v_target,
                                                                    r_rel_lvlh=r_rel_lvlh,
                                                                    v_rel_lvlh=v_rel_lvlh)
    
    assert np.isclose(kinematics[0][0].to_value(u.km), r_chaser[0].to_value(u.km), atol=1e-2)
    assert np.isclose(kinematics[0][1].to_value(u.km), r_chaser[1].to_value(u.km), atol=1e-2)
    assert np.isclose(kinematics[0][2].to_value(u.km), r_chaser[2].to_value(u.km), atol=1e-2)
    
    assert np.isclose(kinematics[1][0].to_value(u.km / u.s), v_chaser[0].to_value(u.km / u.s), atol=1e-2)
    assert np.isclose(kinematics[1][1].to_value(u.km / u.s), v_chaser[1].to_value(u.km / u.s), atol=1e-2)
    assert np.isclose(kinematics[1][2].to_value(u.km / u.s), v_chaser[2].to_value(u.km / u.s), atol=1e-2)

def test_two_impulsive_rendezvous_maneuver():
    """EXAMPLE 7.4"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    radius: float = bd.BODIES[attractor].R_E.to_value(u.km)
    
    oe_target: o3d.OrbitalElements = o3d.OrbitalElements(h=0 * u.km**2 / u.s,
                                                         ecc=0 * u.dimensionless_unscaled,
                                                         inc=40 * u.deg,
                                                         raan=20 * u.deg,
                                                         argp=0 * u.deg,
                                                         nu=60 * u.deg)
    
    oe_target.update_from_perigee_apogee(r_p=(radius + 300) * u.km, r_a=(radius + 300) * u.km)
    
    oe_chaser: o3d.OrbitalElements = o3d.OrbitalElements(h=0 * u.km**2 / u.s,
                                                         ecc=0 * u.dimensionless_unscaled,
                                                         inc=40.130 * u.deg,
                                                         raan=19.819 * u.deg,
                                                         argp=70.662 * u.deg,
                                                         nu=349.65 * u.deg)
    
    oe_chaser.update_from_perigee_apogee(r_p=(radius + 320.06) * u.km, r_a=(radius + 513.86) * u.km)
    
    dv_tot, _, _, _ = rm.RelativeMotion.two_impulsive_rendezvous_maneuver(attractor=attractor,
                                                                             oe_target=oe_target,
                                                                             oe_chaser=oe_chaser,
                                                                             t_maneuver=8 * u.hour)
    
    assert np.isclose(dv_tot.to_value(u.m / u.s), 111.24, atol=1e-2)

def test_clohessy_wiltshire_matrices():
    """EXAMPLE 7.5"""
    
    n: u.Quantity = 0.0011569 * u.rad / u.s
    
    t: u.Quantity = 1.49 * u.hour
    
    phi_rr, phi_rv, phi_vr, phi_vv = rm.RelativeMotion.clohessy_wiltshire_matrices(n=n, t=t)
    
    assert np.isclose(phi_rr[0,0], +1.0090, atol=1e-4)
    assert np.isclose(phi_rr[0,1], +0.0000, atol=1e-4)
    assert np.isclose(phi_rr[1,0], -37.699, atol=1e-3)
    assert np.isclose(phi_rr[1,1], +1.0000, atol=1e-4)
    assert np.isclose(phi_rr[2,2], +0.9970, atol=1e-4)
    
    assert np.isclose(phi_rv[0,0], -66.986, atol=1e-3)
    assert np.isclose(phi_rv[0,1], +5.1989, atol=1e-4)
    assert np.isclose(phi_rv[1,0], -5.1989, atol=1e-4)
    assert np.isclose(phi_rv[1,1], -16360., atol=1e-0)
    assert np.isclose(phi_rv[2,2], -66.986, atol=1e-3)
    
    assert np.isclose(phi_vr[0,0], -2.6897e-4, atol=1e-8)
    assert np.isclose(phi_vr[0,1], +0.0000, atol=1e-4)
    assert np.isclose(phi_vr[1,0], -2.0875e-5, atol=1e-9)
    assert np.isclose(phi_vr[1,1], +0.0000, atol=1e-4)
    assert np.isclose(phi_vr[2,2], +8.9655e-5, atol=1e-9)
    
    assert np.isclose(phi_vv[0,0], +0.9970, atol=1e-4)
    assert np.isclose(phi_vv[0,1], -0.1549, atol=1e-4)
    assert np.isclose(phi_vv[1,0], +0.1549, atol=1e-4)
    assert np.isclose(phi_vv[1,1], +0.98798, atol=1e-5)
    assert np.isclose(phi_vv[2,2], +0.9970, atol=1e-4)