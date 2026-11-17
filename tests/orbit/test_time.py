import astropy.time as time
import astropy.units as u
import numpy as np

import spacelab.orbit.time as sl_time

def test_timestamp_2_julian_day_1():
    """:cite:`curtis` EXAMPLE 5.4"""
    
    timestamp = time.Time({ 'year': 2004, 'month': 5, 'day': 12, 'hour': 14, 'minute': 45, 'second': 30 })
    
    jd: float = sl_time.timestamp_2_julian_day(timestamp=timestamp)
    
    assert np.isclose(jd, 2_453_138.115, 1e-3)
    assert np.isclose(timestamp.to_value("jd"), 2_453_138.115, 1e-3)

def test_timestamp_2_julian_day_2():
    """:cite:`curtis` EXAMPLE 5.5"""
    
    timestamp_1: time.Time = time.Time({ 'year': 2004, 'month': 5, 'day': 12, 'hour': 14, 'minute': 45, 'second': 30 })
    timestamp_2: time.Time = time.Time({ 'year': 1957, 'month': 10, 'day': 4, 'hour': 19, 'minute': 26, 'second': 24 })
    
    jd_1: float = sl_time.timestamp_2_julian_day(timestamp=timestamp_1)
    jd_2: float = sl_time.timestamp_2_julian_day(timestamp=timestamp_2)
    
    assert np.isclose(jd_1 - jd_2, 17_021.805, 1e-3)
    assert np.isclose(timestamp_1.to_value("jd") - timestamp_2.to_value("jd"), 17_021.805, 1e-3)

def test_timestamp_2_julian_day_3():
    """:cite:`kluever` EXAMPLE 10.5.2"""
    
    timestamp = time.Time({ 'year': 2024, 'month': 5, 'day': 16, 'hour': 0, 'minute': 0, 'second': 0 })
    
    jd: float = sl_time.timestamp_2_julian_day(timestamp=timestamp)
    
    assert np.isclose(jd, 2_460_446.5, 1e-1)
    assert np.isclose(timestamp.to_value("jd"), 2_460_446.5, 1e-1)

def test_julian_day_2_timestamp_1():
    """:cite:`curtis` EXAMPLE 5.4"""
    
    jd: float = 2_453_138.115
    
    timestamp_1: time.Time = sl_time.julian_day_2_timestamp(julian_day=jd)
    
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
    """:cite:`kluever` EXAMPLE 10.5.2"""
    
    jd: float = 2_457_665.0
    
    timestamp_1: time.Time = sl_time.julian_day_2_timestamp(julian_day=jd)
    
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

def test_fractional_day_to_hms():
    assert sl_time.frac_day_2_hms(0.25) == [6, 0, 0]
    assert sl_time.frac_day_2_hms(0.5 + 1/48) == [12, 30, 0]


def test_fractional_day_to_hms_rejects_invalid_type():
    assert sl_time.frac_day_2_hms(0.25 * u.one) is None


def test_modified_julian_day():
    assert np.isclose(sl_time.modified_julian_day(2455155.0), 55154.5)


def test_julian_day_and_timestamp_round_trip():
    timestamp = time.Time("2024-05-16 00:00:00", scale="utc")
    julian_day = sl_time.timestamp_2_julian_day(timestamp)

    assert julian_day is not None
    restored = sl_time.julian_day_2_timestamp(julian_day)

    assert restored is not None
    assert restored.ymdhms.year == 2024
    assert restored.ymdhms.month == 5
    assert restored.ymdhms.day == 16
    assert restored.ymdhms.hour == 0
    assert restored.ymdhms.minute == 0
    assert restored.ymdhms.second == 0


def test_timestamp_converters_reject_year_outside_supported_range():
    timestamp = time.Time("2100-01-01 00:00:00", scale="utc")

    assert sl_time.timestamp_2_julian_day(timestamp) is None
    assert sl_time.local_sidereal_time(timestamp, 0 * u.deg) is None


def test_local_sidereal_time():
    """:cite:`curtis` EXAMPLE 5.6"""
    
    timestamp = time.Time({ 'year': 2004, 'month': 3, 'day': 3, 'hour': 4, 'minute': 30, 'second': 0 })
    
    theta: u.Quantity = sl_time.local_sidereal_time(timestamp=timestamp, longitude=139.80 * u.deg)
    
    assert np.isclose(theta.to_value(u.deg), 8.59, 1e-2)
