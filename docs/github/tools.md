<!-- markdownlint-disable MD033 -->

# 🛠️ Tools

<style>
  .side-view {
    width: 80%;
    margin: 0 auto 20px auto;
    display: flex;
    align-items: flex-start;
    gap: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid white;
  }

  .side-view p {
    text-align: justify;
  }

  .side-view img {
    width: 40%;
  }
</style>

⬅️ [HOME](../../README.md)

Under the menu option **Tools**, the user can take advantage of a series of instruments.

## ♻️ Orbit Representation

The `Orbit Representation` dialog furnishes different utilities to convert orbital data in different formats and representations.

<div class="side-view">

  <div>
    <h3>Cartesian → Orbit Parameters</h3>
    <p>
      Given a main <strong>attractor</strong> and the <strong>cartesian parameters</strong> (position and velocity) of an orbit, the converter calculates the <strong>orbit parameters</strong> with conic type classification.
    </p>
  </div>

  <img src="../images/tools-page/cartesian-orbit-parameters.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Cartesian → Keplerian</h3>
    <p>
      Given a main <strong>attractor</strong> and the <strong>cartesian parameters</strong> (position and velocity) of an orbit, the converter calculates the <strong>keplerian parameters</strong> of the orbit.
    </p>
  </div>

  <img src="../images/tools-page/cartesian-keplerian.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Cartesian → Perifocal</h3>
    <p>
      Given a main <strong>attractor</strong> and the <strong>cartesian parameters</strong> (position and velocity) of an orbit, the converter calculates the <strong>perifocal parameters</strong> (position and velocity) of the orbit.
    </p>
  </div>

  <img src="../images/tools-page/cartesian-perifocal.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Keplerian → Cartesian</h3>
    <p>
      Given a main <strong>attractor</strong> and the <strong>keplerian parameters</strong> of an orbit, the converter calculates the <strong>inertial reference frame parameters</strong> (position and velocity) of the orbit.
    </p>
  </div>

  <img src="../images/tools-page/keplerian-cartesian.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Ground Track Propagation</h3>
    <p>
      Given a main <strong>attractor</strong> and the <strong>keplerian parameters</strong> of an orbit, the converter calculates the <strong>right ascension</strong> and <strong>declination</strong> of the satellite on the propagated position, with the oblateness effect of the selected planet.
    </p>
  </div>

  <img src="../images/tools-page/ground-track-propagation.png" alt="image">

</div>

## 🔭 Orbit Determination

The `Orbit Determination` dialogs furnishes different utilities to convert predict an orbit from available data.

<div class="side-view">

  <div>
    <h3>Gibbs Method</h3>
    <p>
      Given 3 position vectors in the <strong>Inertial Reference Frame</strong>, compute the orbital elements.
    </p>
  </div>

  <img src="../images/tools-page/gibbs-method.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Julian Day</h3>
    <p>
      Converters between UTC timestamp and <strong>Julian Day</strong>.
    </p>
  </div>

  <img src="../images/tools-page/julian-day.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Topocentric Frame</h3>
    <p>
      Given the Geocentric Equatorial Position vector of an earth-based tracking station (for which the altitude, latitude, and local sidereal times are known), compute the derived position vectors and the orientation in the sky.
    </p>
  </div>

  <img src="../images/tools-page/topocentric-frame.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Angle Range</h3>
    <p>
      Given the range, azimuth, angular elevation together with their rates relative to an earth-based tracking station (for which the altitude, latitude, and local sidereal times are known), calculate the state vectors in the geocentric equatorial frame.
    </p>
  </div>

  <img src="../images/tools-page/angle-range.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Gauss Method</h3>
    <p>
      Given the direction cosine vectors and the observer's position vectors at 3 times (for which the altitude and latitude are known), compute the orbital elements.
    </p>
  </div>

  <img src="../images/tools-page/gauss-method.png" alt="image">

</div>

## 🌀 Orbital Perturbations

The `Orbital Perturbations` dialogs furnishes different utilities to analyse the effects of various forces on orbital
motion.

<div class="side-view">

  <div>
    <h3>Nodal Regression</h3>
    <p>
      Analyse the secular effect of the Earth's oblateness (J₂) and third-body perturbations (lunar and solar) on the
      right ascension of the ascending node.
    </p>
  </div>

  <img src="../images/tools-page/nodal-regression.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Apsidal Rotation</h3>
    <p>
      Analyse the secular effect of the Earth's oblateness (J₂) and third-body perturbations (lunar and solar) on the
      argument of periapsis.
    </p>
  </div>

  <img src="../images/tools-page/apsidal-rotation.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Sun-Synchronous Orbit</h3>
    <p>
      Compute the inclination conditions for maintaining a sun-synchronous orbit, considering the Earth's oblateness (J₂).
    </p>
  </div>

  <img src="../images/tools-page/sun-synchronous-orbit.png" alt="image">

</div>

## 🎯 Relative Motion

The `Relative Motion` dialogs furnishes different utilities to convert between Local Vertical Local Horizontal and
Geocentric Equatorial frames.

<div class="side-view">

  <div>
    <h3>LVLH Kinematics</h3>
    <p>
      Given the state vectors of the <strong>target spacecraft</strong> and of the <strong>chaser spacecraft</strong>,
      find the position, velocity, and acceleration of Chaser relative to Target along the
      <strong>Local Vertical Local Horizontal</strong> (LVLH) axes attached to the Target.
    </p>
  </div>

  <img src="../images/tools-page/lvlh-kinematics.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Geocentric Equatorial Kinematics</h3>
    <p>
      Given the state vectors of the <strong>target spacecraft</strong> and the state vector of the <strong>chaser
      spacecraft</strong> relative to Target along the <strong>Local Vertical Local Horizontal</strong> (LVLH) axes
      attached to the Target, find the position and velocity of Chaser in the Geocentric Equatorial frame.
    </p>
  </div>

  <img src="../images/tools-page/geocentric-equatorial-kinematics.png" alt="image">

</div>

## 🎯 Interplanetary Trajectory

The `Interplanetary Trajectory` dialogs furnishes different utilities used in interplanetary mission design and analysis, under the assumption of circular, coplanar orbits.

<div class="side-view">

  <div>
    <h3>Synodic Period</h3>
    <p>
      The synodic period is the time interval between two successive conjunctions or oppositions of two celestial bodies. It is assumed that the planetary orbits are circular to simplify the calculations.
    </p>
  </div>

  <img src="../images/tools-page/synodic-period.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Sphere Of Influence</h3>
    <p>
      The sphere of influence is the region around a celestial body where its gravitational field dominates over the gravitational field of other bodies.
    </p>
  </div>

  <img src="../images/tools-page/sphere-of-influence.png" alt="image">

</div>

<div class="side-view">

  <div>
    <h3>Transfer</h3>
    <p>
      With the assumption of circular coplanar planetary orbits, the users can compute the departure, rendezvous (with optimal periapse radius), and flyby parameters for interplanetary trajectories.
    </p>
  </div>

  <img src="../images/tools-page/transfer.png" alt="image">

</div>
