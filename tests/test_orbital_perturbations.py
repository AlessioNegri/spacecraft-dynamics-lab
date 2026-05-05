import pytest

import astropy.time as t
import astropy.units as u
import numpy as np

import astro.bodies as bd
import astro.orbital_perturbations as op
import astro.orbit_3d as o3d
import astro.orbit_determination as od

def test_density():
    
    rho: u.Quantity = op.OrbitalPerturbations.density(z=1 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 1.068, atol=1e-3)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(z=3.981 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 7.106e-1, atol=1e-4)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(z=15.849 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 1.401e-1, atol=1e-4)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(z=63.096 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 2.059e-4, atol=1e-7)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(z=251.189 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 5.909e-11, atol=1e-14)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(z=1001.0 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 3.561e-15, atol=1e-18)

@pytest.mark.skip(reason="Too long to run")
def test_cowell_method():
    """EXAMPLE 12.1"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_0: np.ndarray = np.array([5873.40, -658.522, 3007.49]) * u.km
    
    v_0: np.ndarray = np.array([-2.89641, 4.09401, 6.14446]) * u.km / u.s
    
    delta: t.TimeDelta = t.TimeDelta(108 * u.day)
    
    drag_coefficient: u.Quantity = 2.2 * u.dimensionless_unscaled
    
    diameter: u.Quantity = 1 * u.m
    
    mass: u.Quantity = 100 * u.kg
    
    ballistic_coefficient: u.Quantity = drag_coefficient * (np.pi * diameter**2 / 4) / mass
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, r=r_0, v=v_0, ballistic_coefficient=ballistic_coefficient)
    orbit.choose_perturbations(atmospheric_drag=True)
    
    result: op.Result = orbit.propagate_cowell_for(delta=delta)
    
    altitude: np.ndarray = np.sqrt(result.r_x**2 + result.r_y**2 + result.r_z**2) - bd.BODIES[attractor].R_E
    
    assert np.isclose(altitude[-1].to_value(u.km), 100, atol=1e-0)

def test_encke_method():
    """EXAMPLE 12.2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_0: np.ndarray = np.array([-2384.46, 5729.01, 3050.46]) * u.km
    
    v_0: np.ndarray = np.array([-7.36138, -2.98997, 1.64354]) * u.km / u.s
    
    delta: t.TimeDelta = t.TimeDelta(48 * u.hour)
    
    step: t.TimeDelta = t.TimeDelta((delta.to_value(u.s) / 1000) * u.s)
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, r=r_0, v=v_0)
    orbit.choose_perturbations(gravitational_perturbation=True)
    
    result: op.Result = orbit.propagate_encke_for(delta=delta, step=step)
    
    draan_dhour: float = (result.oe[-1].raan - result.oe[0].raan).to_value(u.deg) / delta.to_value(u.hour)
    dargp_dhour: float = (result.oe[-1].argp - result.oe[0].argp).to_value(u.deg) / delta.to_value(u.hour)
    
    assert np.isclose(draan_dhour, -0.166, atol=1e-3)
    assert np.isclose(dargp_dhour, 0.263, atol=1e-3)

def test_gauss_method_gravitational_perturbation():
    """EXAMPLE 12.6"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_0: np.ndarray = np.array([-2384.46, 5729.01, 3050.46]) * u.km
    
    v_0: np.ndarray = np.array([-7.36138, -2.98997, 1.64354]) * u.km / u.s
    
    delta: t.TimeDelta = t.TimeDelta(48 * u.hour)
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, r=r_0, v=v_0)
    orbit.choose_perturbations(gravitational_perturbation=True)
    
    result: op.Result = orbit.propagate_gauss_for(delta=delta)
    
    draan_dhour: float = (result.oe[-1].raan - result.oe[0].raan).to_value(u.deg) / delta.to_value(u.hour)
    dargp_dhour: float = (result.oe[-1].argp - result.oe[0].argp).to_value(u.deg) / delta.to_value(u.hour)
    
    assert np.isclose(draan_dhour, -0.172, atol=1e-3)
    assert np.isclose(dargp_dhour, 0.282, atol=1e-3)

def test_sun_position():
    """EXAMPLE 12.7"""
    
    timestamp: t.Time = t.Time('2013-07-25T08:00:00', format='isot', scale='utc')
    
    r_sun, lambda_, epsilon = op.OrbitalPerturbations.sun_position(timestamp=timestamp)
    
    assert np.isclose(lambda_.to_value(u.deg), 122.549, atol=1e-3)
    assert np.isclose(epsilon.to_value(u.deg), 23.4372, atol=1e-4)
    assert np.isclose(r_sun[0].to_value(u.km), -81_752_385, atol=1e-0)
    assert np.isclose(r_sun[1].to_value(u.km), 117_517_729, atol=1e-0)
    assert np.isclose(r_sun[2].to_value(u.km), 50_944_632, atol=1e-0)

def test_earth_shadow():
    """EXAMPLE 12.8"""
    
    r_sc: u.Quantity = np.array([2817.899, -14110.473, -7502.672]) * u.km
    
    r_sun: u.Quantity = np.array([-11_747_041, 139_486_985, 60_472_278]) * u.km
    
    condition: int = op.OrbitalPerturbations.earth_shadow(r_sc=r_sc, r_sun=r_sun)
    
    assert condition == 0

@pytest.mark.skip(reason="Too long to run")
def test_gauss_method_solar_radiation_pressure():
    """EXAMPLE 12.9"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    oe_0: o3d.OrbitalElements = o3d.OrbitalElements(h=63383.4 * u.km**2 / u.s,
                                                    a=0 * u.km,
                                                    ecc=0.025422 * u.dimensionless_unscaled,
                                                    inc=88.3924 * u.deg,
                                                    raan=45.3812 * u.deg,
                                                    argp=227.493 * u.deg,
                                                    nu=343.427 * u.deg)
    
    r_0, v_0 = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe_0)
    
    JD_0: float = 2_438_400.5
    
    delta: t.TimeDelta = t.TimeDelta(200 * u.day)
    
    radiation_pressure_coefficient: u.Quantity = 2 * u.dimensionless_unscaled
    
    frontal_area: u.Quantity = 200 * u.m**2
    
    mass: u.Quantity = 100 * u.kg
    
    ballistic_coefficient_srp: u.Quantity = radiation_pressure_coefficient * frontal_area / mass
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, r=r_0, v=v_0, julian_day=JD_0, ballistic_coefficient_srp=ballistic_coefficient_srp)
    orbit.choose_perturbations(solar_radiation_pressure=True)
    
    result: op.Result = orbit.propagate_gauss_for(delta=delta)
    
    delta_raan: float = (result.oe[-1].raan - result.oe[0].raan).to_value(u.deg)
    delta_argp: float = (result.oe[-1].argp - result.oe[0].argp).to_value(u.deg)
    delta_a: float = (result.oe[-1].a - result.oe[0].a).to_value(u.km)
    print(delta_raan, delta_argp, delta_a)
    assert np.isclose(delta_raan, -0.035, atol=1e-3)
    assert np.isclose(delta_argp, -84.27, atol=1e-2)

def test_moon_position():
    """EXAMPLE 12.10"""
    
    timestamp: t.Time = t.Time('2013-07-25T08:00:00', format='isot', scale='utc')
    
    r_moon: u.Quantity = op.OrbitalPerturbations.moon_position(timestamp=timestamp)
    
    assert np.isclose(r_moon[0].to_value(u.km), 341_381, atol=1e-0)
    assert np.isclose(r_moon[1].to_value(u.km), -138_215, atol=1e-0)
    assert np.isclose(r_moon[2].to_value(u.km), -27_696, atol=1e-0)

@pytest.mark.skip(reason="Too long to run")
def test_gauss_method_lunar_gravity():
    """EXAMPLE 12.11"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    oe_0: o3d.OrbitalElements = o3d.OrbitalElements(h=69084.1 * u.km**2 / u.s,
                                                    a=26553.4 * u.km,
                                                    ecc=0.741 * u.dimensionless_unscaled,
                                                    inc=63.4 * u.deg,
                                                    raan=0 * u.deg,
                                                    argp=270 * u.deg,
                                                    nu=0 * u.deg)
    
    r_0, v_0 = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe_0)
    
    JD_0: float = 2_454_283.0
    
    delta: t.TimeDelta = t.TimeDelta(10 * u.day)
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, r=r_0, v=v_0, julian_day=JD_0)
    orbit.choose_perturbations(lunar_gravity=True)
    
    result: op.Result = orbit.propagate_gauss_for(delta=delta)
    
    delta_raan: float = (result.oe[-1].raan - oe_0.raan).to_value(u.deg)
    delta_argp: float = (result.oe[-1].argp - oe_0.argp).to_value(u.deg)
    delta_inc: float = (result.oe[-1].inc - oe_0.inc).to_value(u.deg)
    print(delta_raan, delta_argp, delta_inc)
    assert np.isclose(delta_raan, -0.035, atol=1e-3)
    assert np.isclose(delta_argp, -84.27, atol=1e-2)

@pytest.mark.skip(reason="Too long to run")
def test_gauss_method_sun_gravity():
    """EXAMPLE 12.12"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    oe_0: o3d.OrbitalElements = o3d.OrbitalElements(h=69084.1 * u.km**2 / u.s,
                                                    a=26553.4 * u.km,
                                                    ecc=0.741 * u.dimensionless_unscaled,
                                                    inc=63.4 * u.deg,
                                                    raan=0 * u.deg,
                                                    argp=270 * u.deg,
                                                    nu=0 * u.deg)
    
    r_0, v_0 = o3d.Orbit3D.perifocal_to_geocentric_equatorial(attractor=attractor, oe=oe_0)
    
    JD_0: float = 2_454_283.0
    
    delta: t.TimeDelta = t.TimeDelta(200 * u.day)
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, r=r_0, v=v_0, julian_day=JD_0)
    orbit.choose_perturbations(solar_gravity=True)
    
    result: op.Result = orbit.propagate_gauss_for(delta=delta)
    
    delta_raan: float = (result.oe[-1].raan - oe_0.raan).to_value(u.deg)
    delta_argp: float = (result.oe[-1].argp - oe_0.argp).to_value(u.deg)
    delta_inc: float = (result.oe[-1].inc - oe_0.inc).to_value(u.deg)
    print(delta_raan, delta_argp, delta_inc)
    assert np.isclose(delta_raan, -0.15, atol=1e-2)
    assert np.isclose(delta_argp, 0.2, atol=1e-2)
