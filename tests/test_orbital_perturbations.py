import pytest

import astropy.time as t
import astropy.units as u
import numpy as np

import astro.bodies as bd
import astro.orbital_perturbations as op
import astro.orbit_3d as o3d
import astro.orbit_determination as od

def test_density():
    
    rho: u.Quantity = op.OrbitalPerturbations.density(altitude=1 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 1.068, atol=1e-3)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(altitude=3.981 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 7.106e-1, atol=1e-4)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(altitude=15.849 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 1.401e-1, atol=1e-4)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(altitude=63.096 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 2.059e-4, atol=1e-7)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(altitude=251.189 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 5.909e-11, atol=1e-14)
    
    rho: u.Quantity = op.OrbitalPerturbations.density(altitude=1001.0 * u.km)
    
    assert np.isclose(rho.to_value(u.kg / u.m**3), 3.561e-15, atol=1e-18)

@pytest.mark.skip(reason="Too long to run")
def test_cowell_method_atmospheric_drag():
    """EXAMPLE 12.1"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_0: np.ndarray = np.array([5873.40, -658.522, 3007.49]) * u.km
    
    v_0: np.ndarray = np.array([-2.89641, 4.09401, 6.14446]) * u.km / u.s
    
    delta: t.TimeDelta = t.TimeDelta(108 * u.day)
    
    drag_coefficient: u.Quantity = 2.2 * u.one
    
    diameter: u.Quantity = 1 * u.m
    
    mass: u.Quantity = 100 * u.kg
    
    ballistic_coefficient: u.Quantity = drag_coefficient * (np.pi * diameter**2 / 4) / mass
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, position=r_0, velocity=v_0, ballistic_coefficient=ballistic_coefficient)
    orbit.choose_perturbations(atmospheric_drag=True)
    
    result: op.ResultOP = orbit.propagate_cowell_for(delta=delta)
    
    altitude: np.ndarray = np.sqrt(result.position_x**2 + result.position_y**2 + result.position_z**2) -\
        bd.BODIES[attractor].R_E
    
    assert np.isclose(altitude[-1].to_value(u.km), 100, atol=1e-0)

def test_cowell_method_gravitational_perturbation():
    """EXAMPLE 5.1 - BOOK 2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_0: np.ndarray = np.array([-5134.41, 4405.01, 2420.05]) * u.km
    
    v_0: np.ndarray = np.array([-5.5265, -5.5142, 0.7385]) * u.km / u.s
    
    delta: t.TimeDelta = t.TimeDelta(10 * u.hour)
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, position=r_0, velocity=v_0)
    orbit.choose_perturbations(gravitational_perturbation=True)
    
    result: op.ResultOP = orbit.propagate_cowell_for(delta=delta)
    
    r_f: np.ndarray = np.array([result.position_x[-1].to_value(u.km),
                                result.position_y[-1].to_value(u.km),
                                result.position_z[-1].to_value(u.km)])
    
    v_f: np.ndarray = np.array([result.velocity_x[-1].to_value(u.km / u.s),
                                result.velocity_y[-1].to_value(u.km / u.s),
                                result.velocity_z[-1].to_value(u.km / u.s)])
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor,
                                                                 position=r_f * u.km,
                                                                 velocity=v_f * u.km / u.s)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 8059, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.15, atol=1e-2)
    assert np.isclose(oe.inclination.to_value(u.deg), 20, atol=1e-0)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 58.25, atol=1e-1)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 33.25, atol=1e-1)

def test_nodal_regression():
    """EXAMPLE 5.2 - BOOK 2"""
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                  semimajor_axis=6790.6 * u.km,
                                                  eccentricity=0.0005 * u.one,
                                                  inclination=51.65 * u.deg,
                                                  right_ascension_of_ascending_node=295 * u.deg,
                                                  argument_of_periapsis=0 * u.deg,
                                                  true_anomaly=0 * u.deg)
    
    dOmega_dt_g, _, _ = op.OrbitalPerturbations.nodal_regression_rate(attractor=bd.Attractor.EARTH,
                                                                      orbital_elements=oe)
    
    Omega_final: u.Quantity = oe.right_ascension_of_ascending_node + dOmega_dt_g * t.TimeDelta(7 * u.day)
    
    assert np.isclose(Omega_final.to_value(u.deg), 260.245, atol=1e-3)

def test_sun_synchronous_inclination():
    """EXAMPLE 5.3 - BOOK 2"""
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                  semimajor_axis=(6378 + 400) * u.km,
                                                  eccentricity=0 * u.one,
                                                  inclination=0 * u.deg,
                                                  right_ascension_of_ascending_node=0 * u.deg,
                                                  argument_of_periapsis=0 * u.deg,
                                                  true_anomaly=0 * u.deg)
    
    inc: u.Quantity = op.OrbitalPerturbations.sun_synchronous_inclination(attractor=bd.Attractor.EARTH,
                                                                          orbital_elements=oe,
                                                                          nodal_regression_rate=1.991021e-7 * u.rad / u.s)
    
    assert np.isclose(inc.to_value(u.deg), 97, atol=1e-0)

def test_apsidal_rotation_rate():
    """EXAMPLE 5.3 - BOOK 2"""
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                  semimajor_axis=8059 * u.km,
                                                  eccentricity=0.15 * u.one,
                                                  inclination=20 * u.deg,
                                                  right_ascension_of_ascending_node=0 * u.deg,
                                                  argument_of_periapsis=0 * u.deg,
                                                  true_anomaly=0 * u.deg)
    
    domega_dt, _, _ = op.OrbitalPerturbations.apsidal_rotation_rate(attractor=bd.Attractor.EARTH,
                                                                          orbital_elements=oe)
    
    assert np.isclose(domega_dt.to_value(u.deg / u.day), 7.85, atol=1e-2)

def test_lunar_solar_regressions():
    """EXAMPLE 5.5 - BOOK 2"""
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                  semimajor_axis=8059 * u.km,
                                                  eccentricity=0.15 * u.one,
                                                  inclination=20 * u.deg,
                                                  right_ascension_of_ascending_node=0 * u.deg,
                                                  argument_of_periapsis=0 * u.deg,
                                                  true_anomaly=0 * u.deg)
    
    _, dOmega_dt_l, dOmega_dt_s = op.OrbitalPerturbations.nodal_regression_rate(attractor=bd.Attractor.EARTH,
                                                                                orbital_elements=oe)
    
    _, domega_dt_l, domega_dt_s = op.OrbitalPerturbations.apsidal_rotation_rate(attractor=bd.Attractor.EARTH,
                                                                                orbital_elements=oe)
    
    assert np.isclose(dOmega_dt_l.to_value(u.deg / u.day), -0.0002647, atol=1e-7)
    assert np.isclose(dOmega_dt_s.to_value(u.deg / u.day), -0.0001206, atol=1e-7)
    assert np.isclose(domega_dt_l.to_value(u.deg / u.day), +0.0004810, atol=1e-7)
    assert np.isclose(domega_dt_s.to_value(u.deg / u.day), +0.0002191, atol=1e-7)

def test_encke_method():
    """EXAMPLE 12.2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_0: np.ndarray = np.array([-2384.46, 5729.01, 3050.46]) * u.km
    
    v_0: np.ndarray = np.array([-7.36138, -2.98997, 1.64354]) * u.km / u.s
    
    delta: t.TimeDelta = t.TimeDelta(48 * u.hour)
    
    step: t.TimeDelta = t.TimeDelta((delta.to_value(u.s) / 1000) * u.s)
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, position=r_0, velocity=v_0)
    orbit.choose_perturbations(gravitational_perturbation=True)
    
    result: op.ResultOP = orbit.propagate_encke_for(delta=delta, step=step)
    
    oe_i: o3d.OrbitalElements = result.orbital_elements[0]
    oe_f: o3d.OrbitalElements = result.orbital_elements[-1]
    
    delta_raan: float = (oe_f.right_ascension_of_ascending_node - oe_i.right_ascension_of_ascending_node).to_value(u.deg)
    delta_argp: float = (oe_f.argument_of_periapsis - oe_i.argument_of_periapsis).to_value(u.deg)
    
    draan_dhour: float = delta_raan / delta.to_value(u.hour)
    dargp_dhour: float = delta_argp / delta.to_value(u.hour)
    
    assert np.isclose(draan_dhour, -0.166, atol=1e-3)
    assert np.isclose(dargp_dhour, 0.263, atol=1e-3)

def test_gauss_method_atmospheric_drag():
    """EXAMPLE 5.6 - BOOK 2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    oe: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=0 * u.km**2 / u.s,
                                                  semimajor_axis=(6378 + 300) * u.km,
                                                  eccentricity=0.000001 * u.one,
                                                  inclination=0.000001 * u.deg,
                                                  right_ascension_of_ascending_node=0 * u.deg,
                                                  argument_of_periapsis=0 * u.deg,
                                                  true_anomaly=0 * u.deg)
    
    r_0, v_0 = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe)
    
    delta: t.TimeDelta = t.TimeDelta(45 * u.day)
    
    drag_coefficient: u.Quantity = 2 * u.one
    
    area: u.Quantity = 367 * u.m**2
    
    mass: u.Quantity = 90_000 * u.kg
    
    ballistic_coefficient: u.Quantity = drag_coefficient * area / mass
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, position=r_0, velocity=v_0, ballistic_coefficient=ballistic_coefficient)
    orbit.choose_perturbations(atmospheric_drag=True)
    
    result: op.ResultOP = orbit.propagate_gauss_for(delta=delta)
    
    assert np.isclose(result.orbital_elements[-1].semimajor_axis.to_value(u.km), 6378 + 257, atol=1e-0)

def test_gauss_method_gravitational_perturbation():
    """EXAMPLE 12.6"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_0: np.ndarray = np.array([-2384.46, 5729.01, 3050.46]) * u.km
    
    v_0: np.ndarray = np.array([-7.36138, -2.98997, 1.64354]) * u.km / u.s
    
    delta: t.TimeDelta = t.TimeDelta(48 * u.hour)
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, position=r_0, velocity=v_0)
    orbit.choose_perturbations(gravitational_perturbation=True)
    
    result: op.ResultOP = orbit.propagate_gauss_for(delta=delta)
    
    oe_i: o3d.OrbitalElements = result.orbital_elements[0]
    oe_f: o3d.OrbitalElements = result.orbital_elements[-1]
    
    delta_raan: float = (oe_f.right_ascension_of_ascending_node - oe_i.right_ascension_of_ascending_node).to_value(u.deg)
    delta_argp: float = (oe_f.argument_of_periapsis - oe_i.argument_of_periapsis).to_value(u.deg)
    
    draan_dhour: float = delta_raan / delta.to_value(u.hour)
    dargp_dhour: float = delta_argp / delta.to_value(u.hour)
    
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
    
    condition: int = op.OrbitalPerturbations.earth_shadow(spacecraft_position=r_sc, sun_position=r_sun)
    
    assert condition == 0

@pytest.mark.skip(reason="Too long to run")
def test_gauss_method_solar_radiation_pressure():
    """EXAMPLE 12.9"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    oe_0: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=63383.4 * u.km**2 / u.s,
                                                    semimajor_axis=0 * u.km,
                                                    eccentricity=0.025422 * u.dimensionless_unscaled,
                                                    inclination=88.3924 * u.deg,
                                                    right_ascension_of_ascending_node=45.3812 * u.deg,
                                                    argument_of_periapsis=227.493 * u.deg,
                                                    true_anomaly=343.427 * u.deg)
    
    r_0, v_0 = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_0)
    
    JD_0: float = 2_438_400.5
    
    delta: t.TimeDelta = t.TimeDelta(200 * u.day)
    
    radiation_pressure_coefficient: u.Quantity = 2 * u.dimensionless_unscaled
    
    frontal_area: u.Quantity = 200 * u.m**2
    
    mass: u.Quantity = 100 * u.kg
    
    B_srp: u.Quantity = radiation_pressure_coefficient * frontal_area / mass
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, position=r_0, velocity=v_0, julian_day=JD_0, ballistic_coefficient_srp=B_srp)
    orbit.choose_perturbations(solar_radiation_pressure=True)
    
    result: op.ResultOP = orbit.propagate_gauss_for(delta=delta)
    
    oe_i: o3d.OrbitalElements = result.orbital_elements[0]
    oe_f: o3d.OrbitalElements = result.orbital_elements[-1]
    
    delta_raan: float = (oe_f.right_ascension_of_ascending_node - oe_i.right_ascension_of_ascending_node).to_value(u.deg)
    delta_argp: float = (oe_f.argument_of_periapsis - oe_i.argument_of_periapsis).to_value(u.deg)
    
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
    
    oe_0: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=69084.1 * u.km**2 / u.s,
                                                    semimajor_axis=26553.4 * u.km,
                                                    eccentricity=0.741 * u.dimensionless_unscaled,
                                                    inclination=63.4 * u.deg,
                                                    right_ascension_of_ascending_node=0 * u.deg,
                                                    argument_of_periapsis=270 * u.deg,
                                                    true_anomaly=0 * u.deg)
    
    r_0, v_0 = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_0)
    
    JD_0: float = 2_454_283.0
    
    delta: t.TimeDelta = t.TimeDelta(10 * u.day)
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, position=r_0, velocity=v_0, julian_day=JD_0)
    orbit.choose_perturbations(lunar_gravity=True)
    
    result: op.ResultOP = orbit.propagate_gauss_for(delta=delta)
    
    oe_i: o3d.OrbitalElements = result.orbital_elements[0]
    oe_f: o3d.OrbitalElements = result.orbital_elements[-1]
    
    delta_raan: float = (oe_f.right_ascension_of_ascending_node - oe_i.right_ascension_of_ascending_node).to_value(u.deg)
    delta_argp: float = (oe_f.argument_of_periapsis - oe_i.argument_of_periapsis).to_value(u.deg)
    
    assert np.isclose(delta_raan, -0.035, atol=1e-3)
    assert np.isclose(delta_argp, -84.27, atol=1e-2)

@pytest.mark.skip(reason="Too long to run")
def test_gauss_method_sun_gravity():
    """EXAMPLE 12.12"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    oe_0: o3d.OrbitalElements = o3d.OrbitalElements(specific_angular_momentum=69084.1 * u.km**2 / u.s,
                                                    semimajor_axis=26553.4 * u.km,
                                                    eccentricity=0.741 * u.dimensionless_unscaled,
                                                    inclination=63.4 * u.deg,
                                                    right_ascension_of_ascending_node=0 * u.deg,
                                                    argument_of_periapsis=270 * u.deg,
                                                    true_anomaly=0 * u.deg)
    
    r_0, v_0 = o3d.Orbit3D.keplerian_to_cartesian(attractor=attractor, orbital_elements=oe_0)
    
    JD_0: float = 2_454_283.0
    
    delta: t.TimeDelta = t.TimeDelta(200 * u.day)
    
    orbit: op.OrbitalPerturbations = op.OrbitalPerturbations()
    
    orbit.init(attractor=attractor, position=r_0, velocity=v_0, julian_day=JD_0)
    orbit.choose_perturbations(solar_gravity=True)
    
    result: op.ResultOP = orbit.propagate_gauss_for(delta=delta)
    
    oe_i: o3d.OrbitalElements = result.orbital_elements[0]
    oe_f: o3d.OrbitalElements = result.orbital_elements[-1]
    
    delta_raan: float = (oe_f.right_ascension_of_ascending_node - oe_i.right_ascension_of_ascending_node).to_value(u.deg)
    delta_argp: float = (oe_f.argument_of_periapsis - oe_i.argument_of_periapsis).to_value(u.deg)
    
    assert np.isclose(delta_raan, -0.15, atol=1e-2)
    assert np.isclose(delta_argp, 0.2, atol=1e-2)
