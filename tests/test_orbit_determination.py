import astropy.time as time
import astropy.units as u
import numpy as np

import astro.bodies as bd
import astro.orbit_3d as o3d
import astro.orbit_determination as od
import astro.orbital_position as op
import astro.two_body_problem as tbp

def test_gibbs_method():
    """EXAMPLE 5.1"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_1: u.Quantity = np.array([-294.32, 4265.1, 5986.7]) * u.km
    r_2: u.Quantity = np.array([-1365.5, 3637.6, 6346.8]) * u.km
    r_3: u.Quantity = np.array([-2940.3, 2473.7, 6555.8]) * u.km
    
    oe: o3d.OrbitalElements = od.OrbitDetermination.gibbs_method(attractor=attractor,
                                                                 position_1=r_1,
                                                                 position_2=r_2,
                                                                 position_3=r_3)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 8001, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.1, atol=1e-1)
    assert np.isclose(oe.inclination.to_value(u.deg), 60, atol=1e-0)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 40, atol=1e-0)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 30, atol=1e-0)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 50, atol=1e-0)

def test_lambert():
    """EXAMPLE 5.2"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r_1: u.Quantity = np.array([5_000, 10_000, 2_100]) * u.km
    r_2: u.Quantity = np.array([-14_600, 2_500, 7_000]) * u.km
    
    v_1, v_2, oe, _ = od.OrbitDetermination.lambert(attractor=attractor,
                                                    departure_position=r_1,
                                                    arrival_position=r_2,
                                                    delta_time=time.TimeDelta(u.Quantity(1, u.hour)))
    
    orb_par: tbp.OrbitParameters = tbp.Orbit.cartesian_to_orbit_parameters(attractor=attractor,
                                                                           position=r_1,
                                                                           velocity=v_1)
    
    t_1: u.Quantity = op.OrbitalPosition.elliptical_orbit_time(true_anomaly=oe.true_anomaly,
                                                               period=orb_par.period,
                                                               eccentricity=oe.eccentricity)
    
    assert np.isclose(v_1[0].to_value(u.km / u.s), -5.9925, atol=1e-4)
    assert np.isclose(v_1[1].to_value(u.km / u.s), 1.9254, atol=1e-4)
    assert np.isclose(v_1[2].to_value(u.km / u.s), 3.2456, atol=1e-4)
    
    assert np.isclose(v_2[0].to_value(u.km / u.s), -3.3125, atol=1e-4)
    assert np.isclose(v_2[1].to_value(u.km / u.s), -4.1966, atol=1e-4)
    assert np.isclose(v_2[2].to_value(u.km / u.s), -0.38529, atol=1e-5)
    
    assert np.isclose(oe.specific_angular_momentum.to_value(u.km**2 / u.s), 80_466, atol=1e-0)
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 20_003, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.4335, atol=1e-4)
    assert np.isclose(oe.inclination.to_value(u.deg), 30.19, atol=1e-2)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 44.60, atol=1e-2)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 30.71, atol=1e-2)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 350.8, atol=1e-1)
    
    assert np.isclose(t_1.to_value(u.s), -256.1, atol=1e-1)

def test_timestamp_2_julian_day_1():
    """EXAMPLE 5.4"""
    
    timestamp: time.Time = time.Time({ 'year': 2004, 'month': 5, 'day': 12, 'hour': 14, 'minute': 45, 'second': 30 })
    
    jd: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp=timestamp)
    
    assert np.isclose(jd, 2_453_138.115, 1e-3)
    assert np.isclose(timestamp.to_value("jd"), 2_453_138.115, 1e-3)

def test_timestamp_2_julian_day_2():
    """EXAMPLE 5.5"""
    
    timestamp_1: time.Time = time.Time({ 'year': 2004, 'month': 5, 'day': 12, 'hour': 14, 'minute': 45, 'second': 30 })
    timestamp_2: time.Time = time.Time({ 'year': 1957, 'month': 10, 'day': 4, 'hour': 19, 'minute': 26, 'second': 24 })
    
    jd_1: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp=timestamp_1)
    jd_2: float = od.OrbitDetermination.timestamp_2_julian_day(timestamp=timestamp_2)
    
    assert np.isclose(jd_1 - jd_2, 17_021.805, 1e-3)
    assert np.isclose(timestamp_1.to_value("jd") - timestamp_2.to_value("jd"), 17_021.805, 1e-3)

def test_julian_day_2_timestamp_1():
    """EXAMPLE 5.4"""
    
    jd: float = 2_453_138.115
    
    timestamp_1: time.Time = od.OrbitDetermination.julian_day_2_timestamp(julian_day=jd)
    
    timestamp_2: time.Time = time.Time(jd, format="jd")
    
    assert np.isclose(timestamp_1.ymdhms.year, 2004, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.month, 5, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.day, 12, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.hour, 14, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.minute, 45, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.second, 30, 1e-0)
    
    assert np.isclose(timestamp_2.ymdhms.year, 2004, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.month, 5, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.day, 12, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.hour, 14, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.minute, 45, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.second, 30, 1e-0)

def test_julian_day_2_timestamp_2():
    """EXAMPLE - BOOK 2"""
    
    jd: float = 2_457_665.0
    
    timestamp_1: time.Time = od.OrbitDetermination.julian_day_2_timestamp(julian_day=jd)
    
    timestamp_2: time.Time = time.Time(jd, format="jd")
    
    assert np.isclose(timestamp_1.ymdhms.year, 2016, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.month, 10, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.day, 3, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.hour, 12, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.minute, 0, 1e-0)
    assert np.isclose(timestamp_1.ymdhms.second, 0, 1e-0)
    
    assert np.isclose(timestamp_2.ymdhms.year, 2016, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.month, 10, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.day, 3, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.hour, 12, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.minute, 0, 1e-0)
    assert np.isclose(timestamp_2.ymdhms.second, 0, 1e-0)

def test_local_sidereal_time():
    """EXAMPLE 5.6"""
    
    timestamp: time.Time = time.Time({ 'year': 2004, 'month': 3, 'day': 3, 'hour': 4, 'minute': 30, 'second': 0 })
    
    longitude: u.Quantity = 139.80 * u.deg
    
    theta: u.Quantity = od.OrbitDetermination.local_sidereal_time(timestamp=timestamp, longitude=longitude)
    
    assert np.isclose(theta.to_value(u.deg), 8.59, 1e-2)

def test_geocentric_equatorial_position_vector():
    """EXAMPLE 5.7"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    theta: u.Quantity = 186.7 * u.deg
    
    phi: u.Quantity = 20 * u.deg
    
    R: u.Quantity = od.OrbitDetermination.geocentric_equatorial_position_vector(attractor=attractor,
                                                                                local_sidereal_time=theta,
                                                                                latitude=phi)
    
    assert np.isclose(R[0].to_value(u.km), -5955, 1e-0)
    assert np.isclose(R[1].to_value(u.km), -699.5, 1e-1)
    assert np.isclose(R[2].to_value(u.km), 2168, 1e-0)

def test_topocentric_equatorial_position_vector():
    """EXAMPLE 5.7"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r: u.Quantity = np.array([-5368, -1784, 3691]) * u.km
    
    theta: u.Quantity = 186.7 * u.deg
    
    phi: u.Quantity = 20 * u.deg
    
    rho: u.Quantity = od.OrbitDetermination.topocentric_equatorial_position_vector(attractor=attractor,
                                                                                   position=r,
                                                                                   local_sidereal_time=theta,
                                                                                   latitude=phi)
    
    assert np.isclose(rho[0].to_value(u.km), 586.8, 1e-1)
    assert np.isclose(rho[1].to_value(u.km), -1084, 1e-0)
    assert np.isclose(rho[2].to_value(u.km), 1523, 1e-0)
    
    alpha, delta = o3d.Orbit3D.right_ascension_declination(position=rho)
    
    assert np.isclose(alpha.to_value(u.deg), 298.4, 1e-1)
    assert np.isclose(delta.to_value(u.deg), 51.01, 1e-2)

def test_topocentric_horizon_position_vector():
    """EXAMPLE 5.9"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    r: u.Quantity = np.array([-2032.4, 4591.2, -4544.8]) * u.km
    
    theta: u.Quantity = 110 * u.deg
    
    phi: u.Quantity = -40 * u.deg
    
    rho, A, a = od.OrbitDetermination.topocentric_horizon_position_vector(attractor=attractor,
                                                                          position=r,
                                                                          local_sidereal_time=theta,
                                                                          latitude=phi)
    
    assert np.isclose(rho[0].to_value(u.km), 339.5, 1e-1)
    assert np.isclose(rho[1].to_value(u.km), -282.6, 1e-1)
    assert np.isclose(rho[2].to_value(u.km), 389.6, 1e-1)
    assert np.isclose(A.to_value(u.deg), 129.8, 1e-1)
    assert np.isclose(a.to_value(u.deg), 41.41, 1e-2)

def test_topocentric_equatorial_right_ascension_declination():
    """EXAMPLE 5.8"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    theta: u.Quantity = 215.1 * u.deg
    
    phi: u.Quantity = 38 * u.deg
    
    A: u.Quantity = 214.3 * u.deg
    
    a: u.Quantity = 43 * u.deg
    
    rho, alpha, delta = od.OrbitDetermination.topocentric_equatorial_right_ascension_declination(attractor=attractor,
                                                                                                 local_sidereal_time=theta,
                                                                                                 latitude=phi,
                                                                                                 azimuth=A,
                                                                                                 elevation=a)
    
    assert np.isclose(rho[0].to_value(), -0.9810, 1e-4)
    assert np.isclose(rho[1].to_value(), -0.1857, 1e-4)
    assert np.isclose(rho[2].to_value(), -0.05621, atol=1e-5)
    assert np.isclose(alpha.to_value(u.deg), 190.7, 1e-1)
    assert np.isclose(delta.to_value(u.deg), -3.222, 1e-3)

def test_predict_from_angle_range():
    """EXAMPLE 5.10"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    rho: u.Quantity = 2551 * u.km
    
    A: u.Quantity = 90 * u.deg
    
    a: u.Quantity = 30 * u.deg
    
    drho_dt: u.Quantity = 0 * u.km / u.s
    
    dA_dt: u.Quantity = 1.973e-3 * u.rad / u.s
    
    da_dt: u.Quantity = 9.864e-4 * u.rad / u.s
    
    theta: u.Quantity = 300 * u.deg
    
    phi: u.Quantity = 60 * u.deg
    
    r, v = od.OrbitDetermination.predict_from_angle_range(attractor=attractor,
                                                          slant_range=rho,
                                                          azimuth=A,
                                                          elevation=a,
                                                          range_rate=drho_dt,
                                                          azimuth_rate=dA_dt,
                                                          elevation_rate=da_dt,
                                                          local_sidereal_time=theta,
                                                          latitude=phi)
    
    assert np.isclose(r[0].to_value(u.km), 3831, atol=1e-0)
    assert np.isclose(r[1].to_value(u.km), -2216, atol=1e-0)
    assert np.isclose(r[2].to_value(u.km), 6605, atol=1e-0)
    assert np.isclose(v[0].to_value(u.km / u.s), 1.504, atol=1e-3)
    assert np.isclose(v[1].to_value(u.km / u.s), -4.562, atol=1e-3)
    assert np.isclose(v[2].to_value(u.km / u.s), -0.2920, atol=1e-3)
    
    oe: o3d.OrbitalElements = o3d.Orbit3D.cartesian_to_keplerian(attractor=attractor, position=r, velocity=v)
    
    assert np.isclose(oe.semimajor_axis.to_value(u.km), 5170, atol=1e-0)
    assert np.isclose(oe.eccentricity.to_value(), 0.6195, atol=1e-4)
    assert np.isclose(oe.inclination.to_value(u.deg), 113.4, atol=1e-1)
    assert np.isclose(oe.right_ascension_of_ascending_node.to_value(u.deg), 109.8, atol=1e-1)
    assert np.isclose(oe.argument_of_periapsis.to_value(u.deg), 309.8, atol=1e-1)
    assert np.isclose(oe.true_anomaly.to_value(u.deg), 165.3, atol=1e-1)

def test_predict_from_gauss_method():
    """EXAMPLE 5.11"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    phi: u.Quantity = 40 * u.deg
    
    theta: u.Quantity = np.array([44.506, 45.000, 45.499]) * u.deg
    
    alpha: u.Quantity = np.array([43.537, 54.420, 64.318]) * u.deg
    
    delta: u.Quantity = np.array([-8.7833, -12.074, -15.105]) * u.deg
    
    t: u.Quantity = np.array([0, 118.10, 237.58]) * u.s
    
    H: u.Quantity = 1 * u.km
    
    r, v = od.OrbitDetermination.predict_from_gauss_method(attractor=attractor,
                                                           latitude=phi,
                                                           local_sidereal_time_list=theta,
                                                           right_ascension_list=alpha,
                                                           declination_list=delta,
                                                           observation_time_list=t,
                                                           site_altitude=H)
    
    assert np.isclose(r[0].to_value(u.km), 5659.8, atol=1e-1)
    assert np.isclose(r[1].to_value(u.km), 6534.8, atol=1e-1)
    assert np.isclose(r[2].to_value(u.km), 3270.1, atol=1e-1)
    assert np.isclose(v[0].to_value(u.km / u.s), -3.8791, atol=1e-4)
    assert np.isclose(v[1].to_value(u.km / u.s), 5.1196, atol=1e-4)
    assert np.isclose(v[2].to_value(u.km / u.s), -2.2409, atol=1e-4)

def test_predict_from_gauss_method_extended():
    """EXAMPLE 5.12"""
    
    attractor: bd.Attractor = bd.Attractor.EARTH
    
    phi: u.Quantity = 40 * u.deg
    
    theta: u.Quantity = np.array([44.506, 45.000, 45.499]) * u.deg
    
    alpha: u.Quantity = np.array([43.537, 54.420, 64.318]) * u.deg
    
    delta: u.Quantity = np.array([-8.7833, -12.074, -15.105]) * u.deg
    
    t: u.Quantity = np.array([0, 118.10, 237.58]) * u.s
    
    H: u.Quantity = 1 * u.km
    
    r, v = od.OrbitDetermination.predict_from_gauss_method_extended(attractor=attractor,
                                                                    latitude=phi,
                                                                    local_sidereal_time_list=theta,
                                                                    right_ascension_list=alpha,
                                                                    declination_list=delta,
                                                                    observation_time_list=t,
                                                                    site_altitude=H)
    
    assert np.isclose(r[0].to_value(u.km), 5662.8, atol=1e-1)
    assert np.isclose(r[1].to_value(u.km), 6539.0, atol=1e-1)
    assert np.isclose(r[2].to_value(u.km), 3269.0, atol=1e-1)
    assert np.isclose(v[0].to_value(u.km / u.s), -3.8848, atol=1e-4)
    assert np.isclose(v[1].to_value(u.km / u.s), 5.1254, atol=1e-4)
    assert np.isclose(v[2].to_value(u.km / u.s), -2.2446, atol=1e-4)