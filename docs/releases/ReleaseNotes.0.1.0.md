# 🛰️ SpacecraftDynamicsLab v0.1.0

This is the first public release of `SpacecraftDynamicsLab`, a scientific toolkit for spacecraft dynamics and analysis.

## ✨ Features

- Core
  - Orbital mechanics library (`astro`)
  - 3D orbit visualization

- Orbit representation & conversions
  - Cartesian ↔ Keplerian conversions
  - Perifocal frame conversions
  - Orbit parameters (conic type, specific energy, apoapsis/periapsis, etc.)

- Orbit determination & prediction
  - Gibbs method
  - Gauss method (extended)
  - Angle-range prediction
  - Timestamp ↔ Julian day conversion and sidereal time
  - Topocentric frame computations

- Orbital maneuvers (with simulation outputs)
  - Hohmann transfer
  - Bi-elliptic Hohmann transfer
  - Phasing maneuver
  - Non-Hohmann transfer
  - Apse-line rotation
  - Chase maneuver
  - Inclination change
  - Plane change
  - Simulation outputs: initial/transfer/final orbit traces, Δv, burn time, propellant usage

- Relative motion & rendezvous
  - LVLH kinematics
  - Clohessy–Wiltshire linearized solution
  - Two-impulse rendezvous maneuvers
  - Geocentric–equatorial kinematics
  - Comparative analyses between methods

- Interplanetary transfers
  - Pork‑chop analysis (Δv / time-of-flight grids)
  - Optimal transfer computations
  - Synodic period and wait-time calculations
  - Sphere of influence and simple transfer approximations

- Orbital perturbations
  - Full perturbation simulation (drag, J2, SRP, lunar, solar effects) with streaming results
  - Nodal regression rate
  - Apsidal rotation rate
  - Sun-synchronous inclination computation

- Spacecraft management & persistence
  - Spacecraft CRUD API with image and 3D model upload (MongoDB-backed)

- Real-time integrations
  - WebSocket streaming for simulation progress and status updates

- Utilities & additional tools
  - Ground-track propagation and planet-oblateness effects
  - Orbit propagation and orbit parameter utilities
  - Orbit determination helpers and time utilities

## ⚠️ Disclaimer

This software is intended for educational and research purposes only. It must not be used for
real spacecraft operations, mission planning, navigation, or any safety‑critical decision-making.

## 📦 Notes

This release includes compiled binaries for Windows.
