"""
This module contains utilities to convert **times** in different formats.

📌 **Notes**
    
The **Julian day** number is the number of days since noon UT on 1 January 4713 BC. The origin of this time scale is
placed in antiquity so that, except for prehistoric events, we do not have to deal with positive and negative dates. The
Julian day count is uniform and continuous and does not involve leap years or different numbers of days in different
months. The Julian day begins at noon rather than at midnight so that astronomers observing the heavens at night would
not have to deal with a change of date during their watch.

📖 **References**

- :cite:`curtis`
    - Chapter 5 *Preliminary Orbit Determination*
- :cite:`kluever`
    - Chapter 10 *Interplanetary Trajectories*
- :cite:`walter`
    - Chapter 13 *Reference Frames*
"""

import astropy.time as time
import astropy.units as u
import numpy as np
import typing as ty

import spacelab.utils.angle as sl_angle
import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

J2000: int = 2_451_545 # * Current Julian epoch noon on 1 January 2000

# * curtis

def timestamp_2_julian_day(timestamp: time.Time) -> ty.Optional[float]:
    """
    Converts the given timestamp in Julian day.

    :param timestamp: Timestamp
    :type timestamp: time.Time
    :return: Julian day number [number of days]
    :rtype: ty.Optional[float]
    
    📌 **Notes**
    
    :math:`J_0` is the symbol for the Julian day number at 0 hr UT (which is half way into the Julian day).
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.4 *Sidereal time*
    - :cite:`kluever`
        - Section 10.5 *Interplanetary Trajectories*
        - Section 10.5.2 *Julian Date*
    - :cite:`walter`
        - Section 13.2 *Time Frames*
    """
    
    # >>> Validation
    
    # * timestamp
    
    err_msg: str | None = sl_validator.validate_time("timestamp", timestamp)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    year: int = timestamp.ymdhms.year
    month: int = timestamp.ymdhms.month
    day: int = timestamp.ymdhms.day
    hour: int = timestamp.ymdhms.hour
    minute: int = timestamp.ymdhms.minute
    second: int = timestamp.ymdhms.second
    
    # ? 1. Checks
    
    if year < 1901 or year > 2099:
        
        sl_logger.logger.warning("'year' must be in range 1901 - 2099")
    
        return None
    
    # ? 2. Julian day at 0 h UT
    
    J0: float = 367 * year - int(7/4 * (year + int((month + 9) / 12))) + int(275/9 * month) + day + 1_721_013.5
    
    # ? 3. Universal Time
    
    UT: float = hour + minute / 60 + second / 3600
    
    # ? 4. Julian day number
    
    return J0 + UT / 24

def frac_day_2_hms(frac_day: float) -> ty.Optional[ty.List[int]]:
    """
    Split the fractional day in hour - minute - second.

    :param frac_day: Fraction of day
    :type frac_day: float
    :return: [hour, minute, second]
    :rtype: ty.Optional[ty.List[int]]
    
    📌 **Notes**
    
    The fractional part of the JD beyond noon GMT is given by :math:`JD_{fraction} = JD - |JD| \\in (0, 1)`
    
    📖 **References**
    
    - :cite:`kluever`
        - Section 10.5 *Interplanetary Trajectories*
        - Section 10.5.2 *Julian Date*
    """
    
    # >>> Validation
    
    # * frac_day
    
    err_msg: str | None = sl_validator.validate_type("frac_day", frac_day, float)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    temp: float = frac_day * 24.0
    
    hour: int = int(np.fix(temp))
    
    minute: int = int(np.fix((temp - hour) * 60))
    
    second: int = int((temp - hour - minute / 60) * 3600)
    
    return [hour, minute, second]

def julian_day_2_timestamp(julian_day: float) -> ty.Optional[time.Time]:
    """
    Converts the Julian day in timestamp (Fliegel-Van Flandern algorithm).

    :param julian_day: Julian Day
    :type julian_day: float
    :return: Timestamp
    :rtype: ty.Optional[time.Time]
    
    📌 **Notes**
    
    Because a Julian date is a large number (greater than 2.4 million), it is common to use a JD with fewer digits. One
    variant is the *modified Julian date* (*MJD*), which has five digits to the left of the decimal point. We can
    compute the MJD by subtracting 2,400,000.5 from the JD. Thus, the MJD is a continuous count of days starting from
    midnight November 17, 1858.
    
    📖 **References**
    
    - :cite:`kluever`
        - Section 10.5 *Interplanetary Trajectories*
        - Section 10.5.2 *Julian Date*
    """
    
    # >>> Validation
    
    # * julian_day
    
    err_msg: str | None = sl_validator.validate_type("julian_day", julian_day, float)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    # ? 1. Shift the Julian Day and extract the integer part
    
    # * 0.5 shifts the start of the day from noon (JD convention) to midnight
    # * 32044 converts from Julian calendar to the proleptic Gregorian calendar epoch
    
    j: int = np.floor(julian_day + 0.5) + 32_044
    
    # ? 2. Break the integer day into Gregorian cycles
    
    # * Decompose the integer day into cycles of:
    # * - 400‑year Gregorian cycles (except every 400 years → leap again)
    # * - 100‑year subcycles (except every 100 years → not leap)
    # * - 4‑year subcycles (every 4 years → leap year)
    # * - 1‑year subcycles
    
    g: int = np.floor(j / 146_097) # * Number of 400-year cycles
    
    dg: int = np.mod(j, 146_097)
    
    c: int = np.floor((np.floor(dg / 36_524) + 1) * 3/4)
    
    dc: int = dg - c * 36_524
    
    b: int = np.floor(dc / 1_461) # * Number of 4-year cycles
    
    db: int = np.mod(dc, 1_461)
    
    a: int = np.floor((np.floor(db / 365) + 1) * 3/4)
    
    da: int = db - a * 365
    
    # ? 3. Convert the year offset, month index, and day index in year, mont and day (Gregorian date)
    
    y: int = g * 400 + c * 100 + b * 4 + a
    
    m: int = np.floor((da * 5 + 308) / 153) - 2
    
    d: int = da - np.floor((m + 4) * 153/5) + 122
    
    year: int = int(y - 4800 + np.floor((m + 2) / 12))
    
    month: int = int(np.mod((m + 2), 12) + 1)
    
    day: int = int(np.floor(d + 1))
    
    # ? 4. Extract the fractional day → hour, minute, second
    
    hour, minute, second = frac_day_2_hms(np.mod(julian_day + 0.5, np.floor(julian_day + 0.5)))
    
    # ? 5. Create the timestamp
    
    timestamp: time.Time = time.Time(
        {
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'minute': minute,
            'second': second
        })
    
    return timestamp

def modified_julian_day(julian_day: float) -> ty.Optional[float]:
    """
    Converts the Julian day (JD) in **Modified Julian day** (MJD).

    :param julian_day: Julian day
    :type julian_day: float
    :return: Modified Julian day
    :rtype: ty.Optional[float]
    
    📌 **Notes**
    
    Because a Julian date is a large number (greater than 2.4 million), it is common to use a JD with fewer digits. One
    variant is the *modified Julian date* (*MJD*), which has five digits to the left of the decimal point. We can
    compute the MJD by subtracting 2,400,000.5 from the JD. Thus, the MJD is a continuous count of days starting from
    midnight November 17, 1858.
    
    📖 **References**
    
    - :cite:`kluever`
        - Section 10.5 *Interplanetary Trajectories*
        - Section 10.5.2 *Julian Date*
    - :cite:`walter`
        - Section 13.2 *Time Frames*
    """
    
    return julian_day - 2_400_000.5

def local_sidereal_time(timestamp: time.Time, longitude: u.Quantity) -> ty.Optional[u.Quantity]:
    """
    Calculates the **local sidereal time** :math:`\\theta` from given timestamp and longitude (Astronomical Almanac).

    :param timestamp: Timestamp
    :type timestamp: time.Time
    :param longitude: East longitude
    :type longitude: u.Quantity
    :return: Local sidereal time
    :rtype: ty.Optional[u.Quantity]
    
    📖 **References**
    
    - :cite:`curtis`
        - Section 5.4 *Sidereal time*
    - :cite:`walter`
        - Section 13.2 *Time Frames*
    """
    
    # >>> Validation
    
    # * timestamp
    
    err_msg: str | None = sl_validator.validate_time("timestamp", timestamp)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # * longitude
    
    err_msg = sl_validator.validate_quantity_angle("longitude", longitude)
    
    if err_msg: sl_logger.logger.warning(err_msg); return None
    
    # >>> Algorithm
    
    year: int = timestamp.ymdhms.year
    month: int = timestamp.ymdhms.month
    day: int = timestamp.ymdhms.day
    hour: int = timestamp.ymdhms.hour
    minute: int = timestamp.ymdhms.minute
    second: int = timestamp.ymdhms.second
    
    # ? 0. Checks
    
    if year < 1901 or year > 2099:
        
        sl_logger.logger.warning("'year' must be in range 1901 - 2099")
        
        return None
    
    UT: float = hour + minute / 60 + second / 3600 # * Universal Time
    
    # ? 1. Julian day at 0 h UT
    
    J0: float = 367 * year - int(7/4 * (year + int((month + 9) / 12 ))) + int(275/9 * month) + day + 1_721_013.5
    
    # ? 2. Time between J0 and J2000 (Julian centuries)
    
    T0: float = (J0 - J2000) / 36_525
    
    # ? 3. Greenwich sideral time at 0 h UT [deg] (Greenwich Mean Sidereal Time - GMST)
    
    theta_g0: float = 100.4606184 + 36000.77004 * T0 + 0.000387933 * T0**2 - 2.583e-8 * T0**3 # * theta_G0
    
    theta_g0 = sl_angle.wrap_angle(theta_g0 * u.deg).to_value(u.deg)
    
    # ? 4. Greenwich sideral time [deg]
    
    theta_g: float = theta_g0 + 360.98564724 * UT / 24 # * theta_G
    
    # ? 5. Local sidereal time
    
    theta: u.Quantity = theta_g * u.deg + longitude.to(u.deg)
    
    theta = sl_angle.wrap_angle(theta)
    
    return theta
