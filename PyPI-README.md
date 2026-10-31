<!-- markdownlint-disable MD033 -->

# SpaceLab

<p align="center">
  <img
    src="./spacelab-logo.png"
    width="25%"
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

## Models

The `spacelab.models` package provides shared data structures and physical models used throughout the library. It includes:

- Orbital elements and orbit parameters for two-body, hyperbolic, and CR3BP analyses
- Result containers for dynamics, maneuvers, and perturbation calculations
- A rocket motor model for maneuver and propellant calculations
- Atmospheric density models, including USSA76 and CIRA-72
- Earth gravitational multipole coefficients for perturbation analysis

Many model values use `astropy.units.Quantity` so calculations can retain and validate physical units.

## Installation

```bash
pip install space-laboratory
```

## Quick Start

```python
from spacelab.orbital_maneuvers import OrbitalManeuvers
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
