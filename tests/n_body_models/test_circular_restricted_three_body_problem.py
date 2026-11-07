import astropy.time as time
import astropy.units as u
import numpy as np
import pytest

from spacelab.bodies import Attractor
from spacelab.enums import LibrationPoint
from spacelab.models.orbit_parameters import OrbitParametersCR3BP
from spacelab.n_body_models.circular_restricted_three_body_problem import Orbit

def test_orbit_parameters_1():
    """:cite:`curtis` EXAMPLE 2.16"""

    op: OrbitParametersCR3BP = Orbit.orbit_parameters(body_1=Attractor.EARTH, body_2=Attractor.MOON)
    
    assert np.isclose(op.dimensionless_mass_ratio_2.to_value(u.one), 0.01215, atol=1e-4)
    assert np.isclose(op.libration_point_1[0].to_value(u.km), 32_1760, atol=1e0)
    assert np.isclose(op.libration_point_2[0].to_value(u.km), 444325, atol=1e0)
    assert np.isclose(op.libration_point_3[0].to_value(u.km), -386413, atol=1e0)

def test_orbit_parameters_2():

    op: OrbitParametersCR3BP = Orbit.orbit_parameters(body_1=Attractor.SUN, body_2=Attractor.EARTH)
    
    assert np.isclose(op.libration_point_1[0].to_value(u.km), 148_110_000, atol=1e5)
    assert np.isclose(op.libration_point_2[0].to_value(u.km), 151_100_000, atol=1e5)
    assert np.isclose(op.libration_point_3[0].to_value(u.km), -149_600_000, atol=1e5)


def test_orbit_parameters_preserve_barycenter_and_lagrangian_point_geometry():
    op = Orbit.orbit_parameters(body_1=Attractor.EARTH, body_2=Attractor.MOON)

    assert np.isclose(
        (op.dimensionless_mass_ratio_1 + op.dimensionless_mass_ratio_2).to_value(u.one),
        1,
    )
    assert np.isclose(
        (op.dimensionless_mass_ratio_1 * op.body_position_1
         + op.dimensionless_mass_ratio_2 * op.body_position_2).to_value(u.km),
        0,
        atol=1e-8,
    )
    assert np.isclose(
        (op.gravitational_parameter_1 + op.gravitational_parameter_2).to_value(u.km**3 / u.s**2),
        op.inertial_angular_velocity.to_value(u.rad / u.s)**2 * op.body_distance.to_value(u.km)**3,
        rtol=1e-12,
    )
    assert np.allclose(
        op.libration_point_4.to_value(u.km)[1:],
        [np.sqrt(3) / 2 * op.body_distance.to_value(u.km), 0],
    )
    assert np.allclose(
        op.libration_point_5.to_value(u.km)[1:],
        [-np.sqrt(3) / 2 * op.body_distance.to_value(u.km), 0],
    )
    assert np.isclose(op.libration_point_4[0].to_value(u.km), op.libration_point_5[0].to_value(u.km))


def test_orbit_parameters_invalid_attractor_returns_defaults():
    op = Orbit.orbit_parameters(body_1="Earth", body_2=Attractor.MOON)

    assert isinstance(op, OrbitParametersCR3BP)
    assert op.body_distance == 0 * u.km
    assert op.dimensionless_mass_ratio_1 == 0 * u.one


@pytest.mark.parametrize(
    ("body_1", "body_2", "jacobi_constant"),
    [
        pytest.param("Earth", Attractor.MOON, -1 * u.km**2 / u.s**2, id="invalid-primary"),
        pytest.param(Attractor.EARTH, "Moon", -1 * u.km**2 / u.s**2, id="invalid-secondary"),
        pytest.param(Attractor.EARTH, Attractor.MOON, -1 * u.km, id="invalid-jacobi-unit"),
    ],
)
def test_zero_velocity_curves_invalid_inputs_return_zero_grid(body_1, body_2, jacobi_constant):
    regions = Orbit.zero_velocity_curves(body_1, body_2, jacobi_constant)

    assert regions.shape == (1000, 1000)
    assert np.count_nonzero(regions) == 0


def test_zero_velocity_curves_zero_jacobi_constant_marks_all_grid_points_allowed():
    regions = Orbit.zero_velocity_curves(
        Attractor.EARTH,
        Attractor.MOON,
        0 * u.km**2 / u.s**2,
    )

    assert regions.shape == (1000, 1000)
    assert np.all(regions == 1)


def test_orbit_init_sets_state_and_converts_units():
    orbit = Orbit()
    position = np.array([384400, 0, 0]) * u.km
    velocity = np.array([0, 1, 0]) * u.km / u.s

    orbit.init(Attractor.EARTH, Attractor.MOON, position, velocity)

    assert orbit.ready
    assert orbit.body_1 == Attractor.EARTH
    assert orbit.body_2 == Attractor.MOON
    assert np.array_equal(orbit.position, position.to_value(u.km))
    assert np.array_equal(orbit.velocity, velocity.to_value(u.km / u.s))


def test_orbit_init_invalid_state_remains_not_ready():
    orbit = Orbit()

    orbit.init(
        Attractor.EARTH,
        Attractor.MOON,
        np.array([384400, 0]) * u.km,
        np.array([0, 1, 0]) * u.km / u.s,
    )

    assert not orbit.ready


def test_propagate_for_dimensional_and_dimensionless_results_agree():
    position = np.array([384400, 0, 0]) * u.km
    velocity = np.array([0, 0.01, 0]) * u.km / u.s
    delta = time.TimeDelta(300 * u.s)
    dimensional_orbit = Orbit()
    dimensionless_orbit = Orbit()
    dimensional_orbit.init(Attractor.EARTH, Attractor.MOON, position, velocity)
    dimensionless_orbit.init(Attractor.EARTH, Attractor.MOON, position, velocity)

    dimensional = dimensional_orbit.propagate_for(delta)
    dimensionless = dimensionless_orbit.propagate_for(delta, dimensionless=True)

    assert dimensional.success
    assert dimensionless.success
    assert np.isclose(dimensional.time[-1].to_value(u.s), delta.to_value(u.s), atol=1e-9)
    assert np.isclose(dimensionless.time[-1].to_value(u.s), delta.to_value(u.s), atol=1e-9)
    for field in ("position_x", "position_y", "position_z", "velocity_x", "velocity_y", "velocity_z"):
        assert np.allclose(getattr(dimensional, field)[-1].value, getattr(dimensionless, field)[-1].value, rtol=1e-8, atol=1e-8)


def test_propagate_for_unready_orbit_returns_failure():
    result = Orbit().propagate_for(time.TimeDelta(1 * u.s))

    assert not result.success


@pytest.mark.parametrize(
    ("method_name", "libration_point"),
    [
        pytest.param("propagate_libration_for", LibrationPoint.L1, id="libration"),
        pytest.param("propagate_eulerian_for", LibrationPoint.L1, id="eulerian"),
        pytest.param("propagate_lagrangian_for", LibrationPoint.L4, id="lagrangian"),
    ],
)
def test_specialized_propagation_methods_integrate(method_name, libration_point):
    orbit = Orbit()
    orbit.init(
        Attractor.EARTH,
        Attractor.MOON,
        np.array([1, 2, 3]) * u.km,
        np.array([0.001, 0, 0]) * u.km / u.s,
    )

    result = getattr(orbit, method_name)(time.TimeDelta(1 * u.s), libration_point)

    assert result.success
    assert result.time[-1].to_value(u.s) == pytest.approx(1, abs=1e-8)


@pytest.mark.parametrize(
    ("method_name", "libration_point"),
    [
        pytest.param("propagate_libration_for", "L1", id="libration"),
        pytest.param("propagate_eulerian_for", "L4", id="eulerian"),
        pytest.param("propagate_lagrangian_for", "L1", id="lagrangian"),
    ],
)
def test_specialized_propagation_invalid_libration_point_returns_failure(method_name, libration_point):
    result = getattr(Orbit(), method_name)(time.TimeDelta(1 * u.s), libration_point)

    assert not result.success
