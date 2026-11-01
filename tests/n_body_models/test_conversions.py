import astropy.units as u
import numpy as np
import pytest

import spacelab.bodies as sl_bodies
import spacelab.models.orbit_parameters as sl_orbit_parameters
import spacelab.n_body_models.conversions as sl_conversions

def test_cartesian_to_orbit_parameters_circle():
    """:cite:`curtis` EXAMPLE 2.5"""
    
    r_geo: float = np.cbrt(398_600 / (72.9217e-6)**2)
    v_geo: float = np.sqrt(398_600 / r_geo)
    period_geo: float = 2 * np.pi * r_geo**(3/2) / np.sqrt(398_600)

    op: sl_orbit_parameters.OrbitParameters =\
        sl_conversions.cartesian_to_orbit_parameters(
            attractor=sl_bodies.Attractor.EARTH,
            position=np.array([r_geo, 0, 0]) * u.km,
            velocity=np.array([0, v_geo, 0]) * u.km / u.s)
    
    assert op.conic_type == "circle"
    assert np.isclose(op.specific_angular_momentum.to_value(), r_geo * v_geo, atol=1e-1)
    assert np.isclose(op.eccentricity, 0, atol=1e-4)
    assert np.isclose(op.periapsis_radius.to_value(), r_geo, atol=1e-1)
    assert np.isclose(op.apoapsis_radius.to_value(), r_geo, atol=1e-1)
    assert np.isclose(op.semimajor_axis.to_value(), r_geo, atol=1e-1)
    assert np.isclose(op.semiminor_axis.to_value(), r_geo, atol=1e-1)
    assert np.isclose(op.period.to_value(), period_geo, atol=1e-1)
    
def test_cartesian_to_orbit_parameters_ellipse():
    """:cite:`curtis` EXAMPLE 2.7"""

    op: sl_orbit_parameters.OrbitParameters =\
        sl_conversions.cartesian_to_orbit_parameters(
            attractor=sl_bodies.Attractor.EARTH,
            position=np.array([6778, 0, 0]) * u.km,
            velocity=np.array([0, 8.435, 0]) * u.km / u.s)

    assert op.conic_type == "ellipse"
    assert np.isclose(op.specific_angular_momentum.to_value(), 57172, atol=1e-1)
    assert np.isclose(op.eccentricity, 0.2098, atol=1e-4)
    assert np.isclose(op.periapsis_radius.to_value(), 6778, atol=1e-1)
    assert np.isclose(op.apoapsis_radius.to_value(), 10378, atol=1e-0)
    assert np.isclose(op.semimajor_axis.to_value(), 8578, atol=1e-0)
    assert np.isclose(op.period.to_value(), 7907, atol=1e-0)
    
def test_cartesian_to_orbit_parameters_parabola():
    """:cite:`curtis` EXAMPLE 2.9"""

    op: sl_orbit_parameters.OrbitParameters =\
        sl_conversions.cartesian_to_orbit_parameters(
            attractor=sl_bodies.Attractor.EARTH,
            position=np.array([7000, 0, 0]) * u.km,
            velocity=np.array([0, 74700 / 7000, 0]) * u.km / u.s)
    
    assert op.conic_type == "parabola"
    assert np.isclose(op.specific_angular_momentum.to_value(), 74700, atol=1e-1)
    assert np.isclose(op.eccentricity, 1.0, atol=1e-1)
    
def test_cartesian_to_orbit_parameters_hyperbola():
    """:cite:`curtis` EXAMPLE 2.10"""

    op: sl_orbit_parameters.OrbitParameters =\
        sl_conversions.cartesian_to_orbit_parameters(
            attractor=sl_bodies.Attractor.EARTH,
            position=np.array([6986, 0, 0]) * u.km,
            velocity=np.array([0, 80708 / 6986, 0]) * u.km / u.s)
    
    assert op.conic_type == "hyperbola"
    assert np.isclose(op.specific_angular_momentum.to_value(), 80708, atol=1e-1)
    assert np.isclose(op.eccentricity, 1.3393, atol=1e-4)
    assert np.isclose(op.periapsis_radius.to_value(), 6986, atol=1e-1)
    assert np.isclose(op.semimajor_axis.to_value(), -20590, atol=1e1)
    assert np.isclose(op.escape_velocity.to_value(), 10.682, atol=1e-3)
    assert np.isclose(op.turning_angle.to_value(), 96.60, atol=1e-1)
    assert np.isclose(op.aiming_radius.to_value(), 18340, atol=1e1)
    assert np.isclose(op.hyperbolic_excess_speed.to_value(), np.sqrt(19.36), atol=1e-0)
    assert np.isclose(op.characteristic_energy.to_value(), 19.36, atol=1e-2)

def test_cartesian_to_orbit_parameters_line():
    """EXAMPLE 2.7"""

    op: sl_orbit_parameters.OrbitParameters =\
        sl_conversions.cartesian_to_orbit_parameters(
            attractor=sl_bodies.Attractor.EARTH,
            position=np.array([6778, 0, 0]) * u.km,
            velocity=np.array([8.435, 0 , 0]) * u.km / u.s)

    assert op.conic_type == "line"


@pytest.mark.parametrize(
    ("attractor", "position", "velocity"),
    [
        pytest.param("Earth", np.array([7000, 0, 0]) * u.km,
                     np.array([0, 7.5, 0]) * u.km / u.s, id="invalid-attractor"),
        pytest.param(sl_bodies.Attractor.EARTH, np.array([7000, 0, 0]) * u.s,
                     np.array([0, 7.5, 0]) * u.km / u.s, id="invalid-position-unit"),
        pytest.param(sl_bodies.Attractor.EARTH, np.array([7000, 0]) * u.km,
                     np.array([0, 7.5, 0]) * u.km / u.s, id="invalid-position-shape"),
        pytest.param(sl_bodies.Attractor.EARTH, np.array([7000, 0, 0]) * u.km,
                     np.array([0, 7.5, 0]) * u.km, id="invalid-velocity-unit"),
        pytest.param(sl_bodies.Attractor.EARTH, np.array([7000, 0, 0]) * u.km,
                     np.array([0, 7.5]) * u.km / u.s, id="invalid-velocity-shape"),
    ],
)
def test_cartesian_to_orbit_parameters_returns_defaults_for_invalid_inputs(attractor, position, velocity):
    op = sl_conversions.cartesian_to_orbit_parameters(attractor, position, velocity)

    assert isinstance(op, sl_orbit_parameters.OrbitParameters)
    assert op.conic_type == ""
    assert op.specific_angular_momentum == 0 * u.km**2 / u.s
    assert op.semimajor_axis == 0 * u.km
    assert op.eccentricity == 0 * u.one
