<!-- markdownlint-disable MD033 -->

# 🛠️ Tools

⬅️ [HOME](../../README.md)

Under the menu option **Tools**, the user can take advantage of a series of instruments.

## ♻️ Orbit Representation

The `Orbit Representation` dialog furnishes different utilities to convert orbital data in different formats and representations.

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Cartesian → Orbit Parameters</h3>
    <p style="text-align: justify;">
      Given a main <strong>attractor</strong> and the <strong>cartesian parameters</strong> (position and velocity) of an orbit, the converter calculates the <strong>orbit parameters</strong> with conic type classification.
    </p>
  </div>

  <img src="../images/tools-page/cartesian-orbit-parameters.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Cartesian → Keplerian</h3>
    <p style="text-align: justify;">
      Given a main <strong>attractor</strong> and the <strong>cartesian parameters</strong> (position and velocity) of an orbit, the converter calculates the <strong>keplerian parameters</strong> of the orbit.
    </p>
  </div>

  <img src="../images/tools-page/cartesian-keplerian.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Cartesian → Perifocal</h3>
    <p style="text-align: justify;">
      Given a main <strong>attractor</strong> and the <strong>cartesian parameters</strong> (position and velocity) of an orbit, the converter calculates the <strong>perifocal parameters</strong> (position and velocity) of the orbit.
    </p>
  </div>

  <img src="../images/tools-page/cartesian-perifocal.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Keplerian → Cartesian</h3>
    <p style="text-align: justify;">
      Given a main <strong>attractor</strong> and the <strong>keplerian parameters</strong> of an orbit, the converter calculates the <strong>geocentric equatorial parameters</strong> (position and velocity) of the orbit.
    </p>
  </div>

  <img src="../images/tools-page/keplerian-cartesian.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;">

  <div>
    <h3>Ground Track Propagation</h3>
    <p style="text-align: justify;">
      Given a main <strong>attractor</strong> and the <strong>keplerian parameters</strong> of an orbit, the converter calculates the <strong>right ascension</strong> and <strong>declination</strong> of the satellite on the propagated position, with the oblateness effect of the selected planet.
    </p>
  </div>

  <img src="../images/tools-page/ground-track-propagation.png" width="30%" alt="image">
</div>

## 🔭 Orbit Determination

The `Orbit Determination` dialogs furnishes different utilities to convert predict an orbit from available data.

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Gibbs Method</h3>
    <p style="text-align: justify;">
      Given 3 position vectors in the <strong>Geocentric Equaorial Frame</strong>, compute the orbital elements.
    </p>
  </div>

  <img src="../images/tools-page/gibbs-method.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Julian Day</h3>
    <p style="text-align: justify;">
      Converters between UTC timestamp and <strong>Julian Day</strong>.
    </p>
  </div>

  <img src="../images/tools-page/julian-day.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Topocentric Frame</h3>
    <p style="text-align: justify;">
      Given the Geocentric Equatorial Position vector of an earth-based tracking station (for which the altitude, latitude, and local sidereal times are known), compute the derived position vectors and the orientation in the sky.
    </p>
  </div>

  <img src="../images/tools-page/topocentric-frame.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Angle Range</h3>
    <p style="text-align: justify;">
      Given the range, azimuth, angular elevation together with their rates relative to an earth-based tracking station (for which the altitude, latitude, and local sidereal times are known), calculate the state vectors in the geocentric equatorial frame.
    </p>
  </div>

  <img src="../images/tools-page/angle-range.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Gauss Method</h3>
    <p style="text-align: justify;">
      Given the direction cosine vectors and the observer's position vectors at 3 times (for which the altitude and latitude are known), compute the orbital elements.
    </p>
  </div>

  <img src="../images/tools-page/gauss-method.png" width="30%" alt="image">
</div>

## 🎯 Relative Motion

The `Relative Motion` dialogs furnishes different utilities to convert between Local Vertical Local Horizontal and
Geocentric Equatorial frames.

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>LVLH Kinematics</h3>
    <p style="text-align: justify;">
      Given the state vectors of the <strong>target spacecraft</strong> and of the <strong>chaser spacecraft</strong>,
      find the position, velocity, and acceleration of Chaser relative to Target along the
      <strong>Local Vertical Local Horizontal</strong> (LVLH) axes attached to the Target.
    </p>
  </div>

  <img src="../images/tools-page/lvlh-kinematics.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>LVLH Kinematics</h3>
    <p style="text-align: justify;">
      Given the state vectors of the <strong>target spacecraft</strong> and the state vector of the <strong>chaser
      spacecraft</strong> relative to Target along the <strong>Local Vertical Local Horizontal</strong> (LVLH) axes
      attached to the Target, find the position and velocity of Chaser in the Geocentric Equatorial frame.
    </p>
  </div>

  <img src="../images/tools-page/geocentric-equatorial-kinematics.png" width="30%" alt="image">
</div>

## 🎯 Interplanetary Trajectory

The `Interplanetary Trajectory` dialogs furnishes different utilities used in interplanetary mission design and analysis, under the assumption of circular, coplanar orbits.

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Synodic Period</h3>
    <p style="text-align: justify;">
      The synodic period is the time interval between two successive conjunctions or oppositions of two celestial bodies. It is assumed that the planetary orbits are circular to simplify the calculations.
    </p>
  </div>

  <img src="../images/tools-page/synodic-period.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Sphere Of Influence</h3>
    <p style="text-align: justify;">
      The sphere of influence is the region around a celestial body where its gravitational field dominates over the gravitational field of other bodies.
    </p>
  </div>

  <img src="../images/tools-page/sphere-of-influence.png" width="30%" alt="image">
</div>

<div style="width: 80%;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding-bottom: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid white;">

  <div>
    <h3>Transfer</h3>
    <p style="text-align: justify;">
      With the assumption of circular coplanar planetary orbits, the users can compute the departure, rendezvous (with optimal periapse radius), and flyby parameters for interplanetary trajectories.
    </p>
  </div>

  <img src="../images/tools-page/transfer.png" width="30%" alt="image">
</div>
