import astropy.units as u

import spacelab.utils.logger as sl_logger
import spacelab.utils.validator as sl_validator

def wrap_angle(angle: u.Quantity, low: u.Quantity = 0 * u.deg, high: u.Quantity = 360 * u.deg) -> u.Quantity:
    """
    Wraps the angle in the range [low, high) degrees.

    :param angle: Angle to wrap
    :type angle: u.Quantity
    :param low: Lower bound of the range, defaults to 0 * u.deg
    :type low: u.Quantity, optional
    :param high: Upper bound of the range, defaults to 360 * u.deg
    :type high: u.Quantity, optional
    :return: Wrapped angle
    :rtype: u.Quantity
    """
    
    err_msg: str | None = sl_validator.validate_quantity("wrapped angle", angle, u.deg)
    
    if err_msg != None: sl_logger.logger.warning(err_msg); return 0 * u.deg
    
    wrapped_angle: u.Quantity = (((angle - low) % (high - low)) + low)
    
    return wrapped_angle
