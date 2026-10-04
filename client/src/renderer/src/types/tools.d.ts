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

interface IVector3D
{
    x: number
    y: number
    z: number
}

interface IOrbitalElements
{
    sam: number // ? Specific Angular Momentum
    sma: number // ? Semi-Major Axis
    ecc: number // ? Eccentricity
    inc: number // ? Inclination
    raan: number // ? Right Ascension Ascending Node
    aop: number // ? Argument Of Periapsis
    ta: number // ? True Anomaly
}

interface IVectorRepresentationsFormInput
{
    orbitalElements: IOrbitalElements
    flightPathAngle: number
    positionMagnitude: number
    velocityMagnitude: number
}

interface IVectorRepresentationsFormOutput
{
    positionIJK: IVector3D
    positionPQW: IVector3D
    positionNTW: IVector3D
    positionRSW: IVector3D
    velocityIJK: IVector3D
    velocityPQW: IVector3D
    velocityNTW: IVector3D
    velocityRSW: IVector3D
}
