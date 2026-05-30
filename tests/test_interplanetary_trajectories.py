import astropy.time as time
import astropy.units as u
import numpy as np

import astro.bodies as bd
import astro.interplanetary_trajectories as it
import astro.orbital_maneuvers as om

def test_synodic_period():
    """EXAMPLE 8.1"""
    
    departure_planet: bd.Attractor = bd.Attractor.EARTH
    
    arrival_planet: bd.Attractor = bd.Attractor.MARS
    
    T_S: u.Quantity = it.InterplanetaryTrajectories.synodic_period(departure_planet=departure_planet,
                                                                   arrival_planet=arrival_planet)
    
    assert np.isclose(T_S.to_value(u.day), 779.9, atol=1e-1)

def test_wait_time():
    """EXAMPLE 8.2"""
    
    departure_planet: bd.Attractor = bd.Attractor.EARTH
    
    arrival_planet: bd.Attractor = bd.Attractor.MARS
    
    _, phi_f, t_wait = it.InterplanetaryTrajectories.wait_time(departure_planet=departure_planet,
                                                                   arrival_planet=arrival_planet)
    
    assert np.isclose(phi_f.to_value(u.rad), -1.3107, atol=1e-0)
    assert np.isclose(t_wait.to_value(u.day), 454.4, atol=1e-1)

def test_sphere_of_influence():
    """EXAMPLE 8.3"""
    
    soi: u.Quantity = it.InterplanetaryTrajectories.sphere_of_influence(body=bd.Attractor.EARTH,
                                                                        main_attractor=bd.Attractor.SUN)
    
    assert np.isclose(soi.to_value(u.km), 925000, atol=1e3)
    
    soi: u.Quantity = it.InterplanetaryTrajectories.sphere_of_influence(body=bd.Attractor.MOON,
                                                                        main_attractor=bd.Attractor.EARTH)
    
    assert np.isclose(soi.to_value(u.km), 66200, atol=1e0)

def test_departure():
    """EXAMPLE 8.4"""
    
    dv, hyperbola = it.InterplanetaryTrajectories.departure(departure_planet=bd.Attractor.EARTH,
                                                                          arrival_planet=bd.Attractor.MARS,
                                                                          periapse_radius=(6378 + 300) * u.km)
    
    assert np.isclose(dv.to_value(u.km / u.s), 3.590, atol=1e-3)
    assert np.isclose(hyperbola.asymptote_angle.to_value(u.deg), 29.17, atol=1e-2)

def test_rendezvous():
    """EXAMPLE 8.5"""
    
    dv, hyperbola, oe = it.InterplanetaryTrajectories.rendezvous(departure_planet=bd.Attractor.EARTH,
                                                                 arrival_planet=bd.Attractor.MARS,
                                                                 orbit_period=7 * u.hour)
    
    assert np.isclose(dv.to_value(u.km / u.s), 1.472, atol=1e-3)
    assert np.isclose(hyperbola.periapse_radius.to_value(u.km), 5456, atol=1e0)
    assert np.isclose(hyperbola.aiming_radius.to_value(u.km), 9817, atol=1e0)
    assert np.isclose(hyperbola.asymptote_angle.to_value(u.deg), 58.13, atol=1e-2)
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 8832, atol=1e0)
    assert np.isclose(oe.eccentricity.to_value(), 0.3822, atol=1e-4)

def test_flyby():
    """EXAMPLE 8.6"""
    
    oe_1, hyperbola_params, oe_2 = it.InterplanetaryTrajectories.flyby(departure_planet=bd.Attractor.EARTH,
                                                                       arrival_planet=bd.Attractor.VENUS,
                                                                       periapse_radius=(6052 + 300) * u.km,
                                                                       nu_1=-30 * u.deg,
                                                                       side=it.FlybySide.DARK_SIDE)
    
    assert np.isclose(oe_1.specific_angular_momentum.to_value(u.km**2 / u.s), 4.059e9, atol=1e6)
    assert np.isclose(oe_1.eccentricity.to_value(), 0.1702, atol=1e-4)
    assert np.isclose(hyperbola_params.specific_angular_momentum.to_value(u.km**2 / u.s), 68480, atol=1e0)
    assert np.isclose(hyperbola_params.eccentricity.to_value(), 1.272, atol=1e-3)
    assert np.isclose(hyperbola_params.turn_angle.to_value(u.deg), 103.6, atol=1e-1)
    assert np.isclose(hyperbola_params.aiming_radius.to_value(u.km), 18342, atol=1e0)
    assert np.isclose(oe_2.specific_angular_momentum.to_value(u.km**2 / u.s), 3.434e9, atol=1e6)
    assert np.isclose(oe_2.eccentricity.to_value(), 0.1847, atol=1e-4)
    
    oe_1, hyperbola_params, oe_2 = it.InterplanetaryTrajectories.flyby(departure_planet=bd.Attractor.EARTH,
                                                                       arrival_planet=bd.Attractor.VENUS,
                                                                       periapse_radius=(6052 + 300) * u.km,
                                                                       nu_1=-30 * u.deg,
                                                                       side=it.FlybySide.SUNLIT_SIDE)
    
    assert np.isclose(oe_1.specific_angular_momentum.to_value(u.km**2 / u.s), 4.059e9, atol=1e6)
    assert np.isclose(oe_1.eccentricity.to_value(), 0.1702, atol=1e-4)
    assert np.isclose(hyperbola_params.specific_angular_momentum.to_value(u.km**2 / u.s), 68480, atol=1e0)
    assert np.isclose(hyperbola_params.eccentricity.to_value(), 1.272, atol=1e-3)
    assert np.isclose(hyperbola_params.turn_angle.to_value(u.deg), 103.6, atol=1e-1)
    assert np.isclose(hyperbola_params.aiming_radius.to_value(u.km), 18342, atol=1e0)
    assert np.isclose(oe_2.specific_angular_momentum.to_value(u.km**2 / u.s), 4.019e9, atol=1e6)
    assert np.isclose(oe_2.eccentricity.to_value(), 0.1556, atol=1e-4)

def test_ephemeris():
    """EXAMPLE 8.7"""
    
    timestamp: time.Time = time.Time('2003-08-27T12:00:00', format='isot', scale='utc')
    
    r_earth, v_earth = it.InterplanetaryTrajectories.ephemeris(planet=bd.Attractor.EARTH, timestamp=timestamp)
    
    assert np.isclose(r_earth[0].to_value(u.km), 135.59e6, atol=1e4)
    assert np.isclose(r_earth[1].to_value(u.km), -66.803e6, atol=1e3)
    assert np.isclose(r_earth[2].to_value(u.km), +0.00056916e6, atol=1e-2)
    assert np.isclose(v_earth[0].to_value(u.km / u.s), 12.680, atol=1e-3)
    assert np.isclose(v_earth[1].to_value(u.km / u.s), 26.610, atol=1e-3)
    assert np.isclose(v_earth[2].to_value(u.km / u.s), -0.00022672, atol=1e-8)
    
    r_mars, v_mars = it.InterplanetaryTrajectories.ephemeris(planet=bd.Attractor.MARS, timestamp=timestamp)
    
    assert np.isclose(r_mars[0].to_value(u.km), 185.95e6, atol=1e4)
    assert np.isclose(r_mars[1].to_value(u.km), -89.959e6, atol=1e3)
    assert np.isclose(r_mars[2].to_value(u.km), -6.4534e6, atol=1e-2)
    assert np.isclose(v_mars[0].to_value(u.km / u.s), 11.478, atol=1e-3)
    assert np.isclose(v_mars[1].to_value(u.km / u.s), 23.881, atol=1e-3)
    assert np.isclose(v_mars[2].to_value(u.km / u.s), 0.21828, atol=1e-5)

def test_optimal_transfer():
    """EXAMPLE 8.8 - 8.9"""
    
    departure_timestamp: time.Time = time.Time('1996-11-07T00:00:00', format='isot', scale='utc')
    
    arrival_timestamp: time.Time = time.Time('1997-09-12T00:00:00', format='isot', scale='utc')
    
    result = it.InterplanetaryTrajectories.optimal_transfer(departure_planet=bd.Attractor.EARTH,
                                                            arrival_planet=bd.Attractor.MARS,
                                                            departure_timestamp=departure_timestamp,
                                                            arrival_timestamp=arrival_timestamp,
                                                            departure_parking_orbit_radius=(bd.BODIES[bd.Attractor.EARTH].R_E + 180 * u.km),
                                                            arrival_orbit_period=48 * u.hour,
                                                            arrival_periapse_radius=(bd.BODIES[bd.Attractor.MARS].R_E + 300 * u.km))
        
    assert np.isclose(result[0].to_value(u.km / u.s), 3.674, atol=1e-3)
    assert np.isclose(result[1].to_value(u.km / u.s), 0.9400, atol=1e-4)
