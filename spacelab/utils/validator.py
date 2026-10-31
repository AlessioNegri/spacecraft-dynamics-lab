import astropy.units as u

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
