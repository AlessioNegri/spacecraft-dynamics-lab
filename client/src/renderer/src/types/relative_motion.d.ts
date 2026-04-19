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
    clohessyWiltshireSolution: IVector3D[]
    twoImpulsiveManeuver: IVector3D[]
    twoImpulsiveManeuverCost: number
}
