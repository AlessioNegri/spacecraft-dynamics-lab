import astropy.units as u
import astropy.time as t

from spacelab.bodies import Attractor, BODIES

def validate_quantity(name: str, value: u.Quantity, unit: u.Unit) -> str | None:
    """
    Validates the astropy Quantity value.

    :param name: Name of the value variable
    :type name: str
    :param value: Value
    :type value: u.Quantity
    :param unit: Unit of the value
    :type unit: u.Unit
    :return: Error message (None if ok)
    :rtype: str | None
    """
    
    if not isinstance(value, u.Quantity):
        
        return f"'{name}' expected {str(u.Quantity)}, got {type(value)}"
    
    if not value.unit.is_equivalent(unit):
        
        return f"'{name}' expected {type(unit)} = '{unit}', got '{str(value.unit)}'"
    
    return None

def validate_quantity_vector(name: str, value: u.Quantity, unit: u.Unit, size: int) -> str | None:
    """
    Validates the astropy Quantity vector value.

    :param name: Name of the value variable
    :type name: str
    :param value: Value
    :type value: u.Quantity
    :param unit: Unit of the value
    :type unit: u.Unit
    :param size: Expected size of the vector
    :type size: int
    :return: Error message (None if ok)
    :rtype: str | None
    """
    
    err_msg: str | None = validate_quantity(name, value, unit)
    
    if err_msg != None: return err_msg
        
    if value.to_value(unit).shape != (size,):
        
        return f"'{name}' must have shape = ({size},)"

def validate_quantity_angle(name: str, value: u.Quantity) -> str | None:
    """
    Validates the astropy Quantity angle value.

    :param name: Name of the value variable
    :type name: str
    :param value: Value
    :type value: u.Quantity
    :return: Error message (None if ok)
    :rtype: str | None
    """
    
    err_msg: str | None = validate_quantity(name, value, u.deg)
    
    if err_msg != None: return err_msg
        
    if not (-360 <= value.to_value(u.deg) <= 360):
        
        return f"'{name} = {value.to_value(u.deg)} deg' must be in [-360, +360] deg"

def validate_attractor(attractor: Attractor) -> str | None:
    """
    Validates the attractor.

    :param attractor: Main attractor
    :type attractor: Attractor
    :return: Error message (None if ok)
    :rtype: str | None
    """
    
    if not isinstance(attractor, Attractor):
        
        return f"'attractor' expected {str(Attractor)}, got {type(attractor)}"
        
    if attractor not in BODIES:
        
        return f"'attractor' {attractor} not in {list(BODIES.keys())}"
    
    return None

def validate_type(name: str, value: bool, expected_type: type) -> str | None:
    """
    Validates the value.

    :param name: Name of the value variable
    :type name: str
    :param value: Value
    :type attractor: bool
    :return: Error message (None if ok)
    :rtype: str | None
    """
    
    if not isinstance(value, expected_type):
        
        return f"'{name}' expected {expected_type}, got {type(value)}"
        
    return None

def validate_time(name: str, time: t.Time) -> str | None:
    """
    Validates the time.

    :param name: Name of the time variable
    :type name: str
    :param time: Time
    :type time: t.Time
    :return: Error message (None if ok)
    :rtype: str | None
    """
    
    if not isinstance(time, t.Time):
        
        return f"{name} expected {str(t.Time)}, got {type(time)}"

    return None

def validate_time_delta(name: str, delta: t.TimeDelta) -> str | None:
    """
    Validates the delta time.

    :param name: Name of the delta variable
    :type name: str
    :param delta: Time delta
    :type delta: t.TimeDelta
    :return: Error message (None if ok)
    :rtype: str | None
    """
    
    if not isinstance(delta, t.TimeDelta):
        
        return f"{name} expected {str(t.TimeDelta)}, got {type(delta)}"

    return None
