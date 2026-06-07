type IOrbitalManeuverType = 'hohmann' |
                            'bi-elliptic-hohmann' |
                            'phasing' |
                            'non-hohmann' |
                            'apse-line-rotation' |
                            'chase' |
                            'inclination-change' |
                            'plane-change'

type HohmannDirection = 0 | 1

interface IHohmann
{
    sma: number
    ecc: number
    direction: HohmannDirection
}

interface IBiEllipticHohmann
{
    sma: number
    ecc: number
    supportApocenterRadius: number
}

interface IPhasing
{
    targetTrueAnomaly: number
    numRevolutions: number
}

interface INonHohmann
{
    sma: number
    ecc: number
    targetTrueAnomaly: number
}

type IntersectionPoint = 0 | 1

interface IApseLineRotation
{
    aop: number
    intersectionPoint: IntersectionPoint
}

interface IChase
{
    trueAnomalyTarget: number
    dt: number
}

interface IInclinationChange
{
    inc: number
}

interface IPlaneChange
{
    inc: number
    raan: number
}

type IOrbitalManeuverData = IHohmann |
                            IBiEllipticHohmann |
                            IPhasing |
                            INonHohmann |
                            IApseLineRotation |
                            IChase |
                            IInclinationChange |
                            IPlaneChange

interface IOrbitalManeuver
{
    type: IOrbitalManeuverType
    data: IOrbitalManeuverData
}

interface IOrbitalManeuverFormInput
{
    spacecraft:
    {
        mass: number
        specificImpulse: number
        thrust: number
    }
    attractor: string
    orbitalElements: IOrbitalElements
    maneuver: IOrbitalManeuver
}

interface IOrbitalManeuverFormOutput
{
    orbitalElements: IOrbitalElements
    maneuver:
    {
        dv: number
        dt: number
        dm: number
        burnTime: number
    }
    initialOrbit: IVector3D[]
    transferOrbit: IVector3D[]
    finalOrbit: IVector3D[]
}

interface IOrbits
{
    initial: IVector3D[]
    transfer: IVector3D[]
    final: IVector3D[]
}
