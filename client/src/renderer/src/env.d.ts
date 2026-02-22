/// <reference types="vite/client" />

interface IMenuItem
{
    checkable?: boolean
    checked?: boolean
    label?: string
    shortcut?: string
    separator?: boolean
    action?: () => void
}

interface IMenu
{
    label: string
    items: IMenuItem[]
}

interface ISideBarItem
{
    id: string
    label: string
    icon: string
}

interface IDbOrbit
{
    sma: number
    ecc: number
    inc: number
    raan: number
    aop: number
    tan: number
}

interface IDbStyle
{
    width: number
    color: string
}

interface IDbSpacecraftItem
{
    _id?: string
    name: string
    mass: number
    orbit: IDbOrbit
    style: IDbStyle
    image: string | null
    model: string
    visible: boolean
}

interface ISpacecraftForm
{
    _id?: string
    name: string
    mass: number
    orbit:
    {
        sma: number
        ecc: number
        inc: number
        raan: number
        aop: number
        tan: number
    }
    style:
    {
        width: number
        color: string
    }
    image: File | null
    model: string
}

interface IGlbModel
{
    name: string,
    scale: number,
    minimumPixelSize: number,
    maximumScale: number
}

interface IInterplanetaryMissionForm
{
    departureBody: string
    flybyBody: string
    arrivalBody: string
    launchWindowStart: string
    launchWindowEnd: string
    flybyWindowStart: string
    flybyWindowEnd: string
    arrivalWindowStart: string
    arrivalWindowEnd: string
    gridSize: number
}

interface ISelectionInfo
{
    launchDate: string
    flybyDate?: string
    arrivalDate: string
    dv: number
    dv1: number
    dvGA?: number
    dv2: number
    tof1Days?: number
    tof2Days?: number
    tofDays: number
}

interface IPorkChopData2D
{
    launchDates: string[]
    arrivalDates: string[]
    tofGrid: number[][]
    dv1Grid: number[][]
    dv2Grid: number[][]
    dvGrid: number[][]
}

interface IPorkChopData3D
{
    launchDates: string[]
    flybyDates: string[]
    arrivalDates: string[]
    tof1Grid: number[][]
    tof2Grid: number[][]
    tofGrid: number[][]
    dv1Grid: number[][]
    dvGAGrid: number[][]
    dv2Grid: number[][]
    dvGrid: number[][]
    tof1: number[][][]
    tof2: number[][][]
    dv1: number[][][]
    dvGA: number[][][]
    dv2: number[][][]
}

interface ICartesianOrbitParametersFormIn
{
    attractor: string
    positionX: number
    positionY: number
    positionZ: number
    velocityX: number
    velocityY: number
    velocityZ: number
}

interface ICartesianOrbitParametersFormOut
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
}