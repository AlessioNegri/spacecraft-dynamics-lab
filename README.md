<!-- markdownlint-disable MD033 -->

# 🛰️ Spacecraft Dynamics Lab (S.D.L.)

> ⚠️ **Important Notice**
> This software is intended for educational, research, and simulation purposes only.
> It must not be used for real spacecraft operations, mission planning, navigation,
> or any safety‑critical decision-making.

Spacecraft Dynamics Lab is an Electron desktop application to simulate spacecraft dynamics.

<p align="center">
    <img src="./docs/images/about.png" width="50%" alt="about">
</p>

## Building **Spacecraft Dynamics Lab**: A Modern App with React, Electron, and Python

Scientific software has a reputation for being powerful but visually outdated. Many tools in orbital mechanics — from GMAT to custom research scripts — rely on legacy UI frameworks, blocking the adoption of modern interaction patterns, responsive layouts, and real‑time visualization.

`Spacecraft Dynamics Lab` (**SDL**) is my attempt to build a modern, engineering‑grade desktop application for orbital mechanics, using a stack that feels more like Linear or Figma than a traditional scientific tool.

I want to explain the architecture, the design decisions, and the lessons learned while building SDL with:

- React for the UI
- Electron for the desktop shell
- TailwindCSS for styling
- Radix UI for accessible primitives
- Python + FastAPI for scientific computation
- Plotly for real‑time visualization

SDL is built on a hybrid architecture:

- Electron
  - Desktop Shell • IPC Bridge
- React (Frontend)
  - UI • Panels • Controls
  - TailwindCSS • Radix UI
- WebSocket
- FastAPI (Backend)
  - Python Astrodynamics API
  - Astropy • NumPy • SciPy
- Simulation Engine

This separation gives me:

- React → modern UI
- Electron → desktop distribution
- Python → scientific correctness
- WebSockets → real‑time streaming
- Plotly → interactive visualization

Spacecraft Dynamics Lab is an experiment:

> Can we build a modern, polished, engineering‑grade scientific tool using web technologies?

## 🔖 References

Here are some references that were used to develop the application:

| **Title** | **Orbital Mechanics for Engineering Students** |
| --- | --- |
| **Authors** | Howard D. Curtis |
| **ISBN** | 9780080977485 |
| **Series** | Aerospace Engineering |
| **Year** | 2013 |
| **Publisher** | Elsevier Science |
| **URL** | [https://www.google.it/books/](https://www.google.it/books/edition/Orbital_Mechanics_for_Engineering_Studen/2U9Z8k0TlTYC?hl=it&gbpv=0) |

| **Title** | **Space Flight Dynamics** |
| --- | --- |
| **Authors** | Craig A. Kluever |
| **ISBN** | 9781119157823 |
| **Series** | Aerospace |
| **Year** | 2018 |
| **Publisher** | Wiley |
| **URL** | [https://www.google.it/books/](https://www.google.it/books/edition/Space_Flight_Dynamics/Cp1PDwAAQBAJ?hl=it&gbpv=0) |

## 📋 Table Of Contents

> Click on the links below to navigate through the documentation.

➡️ [DEPENDENCIES](docs/github/dependencies.md)

➡️ [SCRIPTS](docs/github/scripts.md)

➡️ [STRUCTURE](docs/github/structure.md)

---

➡️ [TOOLS](docs/github/tools.md)

➡️ [SPACECRAFT](docs/github/spacecraft.md)

➡️ [ORBIT](docs/github/orbit.md)

➡️ [ORBITAL MANEUVERS](docs/github/orbital-maneuvers.md)

➡️ [RELATIVE MOTION](docs/github/relative-motion.md)

➡️ [INTERPLANETARY](docs/github/interplanetary.md)

➡️ [ORBITAL PERTURBATIONS](docs/github/orbital-perturbations.md)

➡️ [CIRCULAR RESTRICTED THREE-BODY PROBLEM](docs/github/circular-restricted-three-body-problem.md)

➡️ [SETTINGS](docs/github/settings.md)

## 🖼️ Images

<p align="center">
  <img src="./docs/images/ui.png" width="100%" alt="ui">
</p>

<p align="center">
  <img src="./docs/images/orbit.png" width="100%" alt="orbit">
</p>

<p align="center">
  <img src="./docs/images/pork-chop.png" width="100%" alt="pork-chop">
</p>
