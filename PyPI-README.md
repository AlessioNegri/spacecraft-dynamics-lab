<!-- markdownlint-disable MD033 -->

# SpaceLab

<p align="center">
  <img
    src="./spacelab-logo.png"
    width="256px"
    alt="ui"
    style="border-radius: 20px"
  >
</p>

<table align="center">

  <td align="center">
    <img
      src="https://img.shields.io/badge/python_3.14+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"
      alt="logo"
      style="border-radius: 10px;"
      />
  </td>

  <td align="center">
    <img
      src="https://img.shields.io/badge/coloredlogs_15.0-%233670A0.svg?style=for-the-badge&logo=gitbook&logoColor=f0f0f0"
      alt="logo"
      style="border-radius: 10px;"
      />
  </td>

  <td align="center">
    <img
      src="https://img.shields.io/badge/numpy_2.3+-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white"
      alt="logo"
      style="border-radius: 10px;"
      />
  </td>

  <td align="center">
    <img
      src="https://img.shields.io/badge/SciPy_1.17+-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=%white"
      alt="logo"
      style="border-radius: 10px;"
      />
  </td>

  <td align="center">
    <img
      src="https://img.shields.io/badge/astropy_7.2+-%232C2052.svg?style=for-the-badge&logo=astro&logoColor=white"
      alt="logo"
      style="border-radius: 10px;"
      />
  </td>

</table>

**Space Laboratory** (*SpaceLab*) is an open-source Python library for astrodynamics, spacecraft dynamics, orbit determination, and mission analysis.

The library provides algorithms commonly used in spacecraft engineering and orbital mechanics, including orbital maneuvers, relative motion, perturbation analysis, three-body dynamics, and interplanetary trajectory design.

## Features

- Two-body orbital dynamics
- Orbital maneuvers
- Relative motion analysis
- Orbit determination
- Orbital perturbations
- Circular Restricted Three-Body Problem (CR3BP)
- Interplanetary trajectories
- Planetary flyby analysis
- Atmospheric models
- Two-body and restricted three-body orbit propagation

## Models

The `spacelab.models` package provides shared data structures and physical models used throughout the library. It includes:

- Orbital elements and orbit parameters for two-body, hyperbolic, and CR3BP analyses
- Result containers for dynamics, maneuvers, and perturbation calculations
- A rocket motor model for maneuver and propellant calculations
- Atmospheric density models, including USSA76 and CIRA-72
- Earth gravitational multipole coefficients for perturbation analysis

Many model values use `astropy.units.Quantity` so calculations can retain and validate physical units.

For example, create a unit-aware set of classical orbital elements:

```python
from astropy import units as u
from spacelab.models.orbital_elements import OrbitalElements

elements = OrbitalElements(
  semimajor_axis=7000 * u.km,
  eccentricity=0.01 * u.one,
  inclination=28.5 * u.deg,
)
```

## N-Body Models

The `spacelab.n_body_models` package currently provides two-body and circular restricted three-body problem (CR3BP) models; it does not implement a general solver for an arbitrary number of mutually interacting bodies.

- **Two-body orbits:** initialize from Cartesian position and velocity, then propagate to a time interval or epoch. Propagation supports optional rocket-motor thrust and maneuver controls.
- **Universal-variable methods:** convert Cartesian states to orbital parameters and propagate position and velocity with Lagrange coefficients across conic orbit types.
- **CR3BP:** initialize a spacecraft state relative to two primary bodies; calculate the five libration points and zero-velocity curves; and propagate in dimensional or dimensionless form, including around libration points.

For example, initialize an Earth orbit from Cartesian state vectors and propagate it for 60 seconds:

```python
import numpy as np
from astropy import units as u
from astropy.time import TimeDelta
from spacelab.bodies import Attractor
from spacelab.n_body_models.two_body_problem import Orbit

orbit = Orbit()
orbit.from_cartesian(
  attractor=Attractor.EARTH,
  position=np.array([7000, 0, 0]) * u.km,
  velocity=np.array([0, 7.5, 0]) * u.km / u.s,
)

result = orbit.propagate_for(TimeDelta(60 * u.s))
if result.success:
  print(result.position_x[-1], result.position_y[-1], result.position_z[-1])
```

## Orbit

The `spacelab.orbit` package provides coordinate, time, frame, representation, position, and preliminary orbit-determination utilities:

- Convert between Cartesian, Keplerian, equinoctial, perifocal, and geocentric equatorial representations
- Convert timestamps to Julian and Modified Julian dates and calculate local sidereal time
- Calculate circular, elliptical, parabolic, and hyperbolic anomaly/time relationships
- Transform geocentric equatorial, topocentric equatorial, and topocentric horizon coordinates
- Estimate orbits with Gibbs, Lambert, Gauss, extended Gauss, and Herrick-Gibbs methods
- Calculate ground tracks, horizon footprints, eclipses, right ascension, declination, latitude, and longitude

For example, convert a Cartesian Earth-state vector to classical Keplerian elements:

```python
import numpy as np
from astropy import units as u
from spacelab.bodies import Attractor
from spacelab.orbit.representation import cartesian_to_keplerian

position = np.array([7000, 0, 0]) * u.km
velocity = np.array([0, 7.5, 0]) * u.km / u.s

elements = cartesian_to_keplerian(
  attractor=Attractor.EARTH,
  position=position,
  velocity=velocity,
)

print(elements.semimajor_axis)
print(elements.eccentricity)
```

## Maneuvers

The `spacelab.maneuvers` package provides impulsive and continuous-thrust orbital maneuver calculations:

- Hohmann and bi-elliptic Hohmann transfers
- Phasing, rendezvous, apse-line rotation, and plane-change maneuvers
- One-impulse and RAAN-change maneuvers
- Super-synchronous, non-Hohmann, and circular-orbit transfers
- Constant-tangential-thrust spiral transfers and inclination changes
- Lambert targeting and transfer solutions
- Propellant mass and spacecraft mass calculations

For example, calculate a constant-tangential-thrust spiral from a given burn time:

```python
import astropy.units as u
import copy

from spacelab.bodies import Attractor
from spacelab.enums import SpiralDirection
from spacelab.maneuvers.continuous_thrust import constant_tangential_thrust_transfer_from_time
from spacelab.models.rocket_motor import RocketMotor

motor = RocketMotor(
  specific_impulse=10000 * u.s,
  thrust=2500e-6 * u.kN,
  spacecraft_mass=1000 * u.kg,
)

final_radius, propellant_mass = constant_tangential_thrust_transfer_from_time(
  attractor=Attractor.EARTH,
  rocket_motor=copy.deepcopy(motor),
  initial_radius=6678 * u.km,
  time_of_flight=21.03 * u.day,
  direction=SpiralDirection.OUTWARD,
)

print(final_radius)
print(propellant_mass)
```

## Installation

```bash
pip install space-laboratory
```

## Quick Start

```python
from spacelab.maneuvers.impulsive import hohmann_transfer
```

## Documentation

Documentation is under active development.

## Project Structure

SpaceLab is the computational core of the Spacecraft Dynamics Lab ecosystem.

```text
SpacecraftDynamicsLab
├── Desktop Application
├── Backend Service
└── Space Laboratory
```

## Requirements

- Python 3.14+
- ColoredLogs 15.0+
- NumPy 7.2+
- SciPy 2.3+
- Astropy 1.17+

## License

SpaceLab is distributed under the MIT license.

## Author

Alessio Negri

## Project Status

This project is under active development. APIs may evolve before the first stable 1.0 release.
