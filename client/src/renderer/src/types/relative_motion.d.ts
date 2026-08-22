interface IRelativeMotionFormInput
{
    attractor: string
    orbitalElementsTarget: IOrbitalElements
    orbitalElementsChaser: IOrbitalElements
    integrationTime: number // ? Hours
    maneuverTime: number // ? Hours
}

interface IRelativeMotionFormOutput
{
    linearizedSolution: IVector3D[]
    nearCircularSolution: IVector3D[]
    clohessyWiltshireSolution: IVector3D[]
    twoImpulsiveManeuver: IVector3D[]
    twoImpulsiveManeuverCost: number
}

interface IRendezvousAndDockingFormInput
{
    timestamp: string
    launchSiteLatitude: number
    launchSiteLongitude: number
    targetInclination: number
    targetRaan: number
    chaserSemimajorAxis: number
    targetSemimajorAxis: number
    closingDistance: number
    closingStrategy: "R_BAR_POS" | "R_BAR_NEG" | "V_BAR_POS" | "V_BAR_NEG"
    closingTrajectory: "ELLIPTIC" | "CYCLOIDAL"
    cycloidalRevolutions: number
    closingInitialVelocity: number
    finalApproachDistance: number
    finalApproachTime: number
    finalApproachStrategy: "R_BAR_POS" | "R_BAR_NEG" | "V_BAR_POS" | "V_BAR_NEG"
}

interface IRendezvousAndDockingFormOutput
{
    launchPhaseAscending: number
    launchPhaseDescending: number
    phasingAngle: number
    phasingDistance: number
    homingAngle: number
    homingDeltaVelocity: number
    closingDeltaVelocity: number
    finalApproachDeltaVelocity: number
}
