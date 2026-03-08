interface ICartesianFormIn
{
    attractor: string
    positionX: number
    positionY: number
    positionZ: number
    velocityX: number
    velocityY: number
    velocityZ: number
}

interface IKeplerianFormIn
{
    attractor: string
    semiMajorAxis: number
    eccentricity: number
    inclination: number
    rightAscensionOfAscendingNode: number
    argumentOfPeriapsis: number
    trueAnomaly: number
    deltaTime?: number
}

interface IOrbitParametersFormOut
{
    conicType: string
    specificAngularMomentum: number
    specificMechanicalEnergy: number
    eccentricity: number
    orbitalPeriod: number
    apoapsisRadius: number
    periapsisRadius: number
    semiMajorAxis: number
    semiMinorAxis: number
    escapeVelocity: number
    infiniteTrueAnomaly: number
    hyperbolaAsymptoteAngle: number
    turnAngle: number
    aimingRadius: number
    hyperbolicExcessSpeed: number
    characteristicEnergy: number
    rightAscension: number
    declination: number
}

interface IKeplerianFormOut
{
    specificAngularMomentum: number
    semiMajorAxis: number
    eccentricity: number
    inclination: number
    rightAscensionOfAscendingNode: number
    argumentOfPeriapsis: number
    trueAnomaly: number
}

interface IPerifocalFormOut
{
    positionX: number
    positionY: number
    velocityX: number
    velocityY: number
}

interface IGeocentricEquatorialFormOut
{
    positionX: number
    positionY: number
    positionZ: number
    velocityX: number
    velocityY: number
    velocityZ: number
}

interface IGroundTrackFormOut
{
    rightAscensionOfAscendingNodeVariation: number
    argumentOfPeriapsisVariation: number
    rightAscension: number
    declination: number
}