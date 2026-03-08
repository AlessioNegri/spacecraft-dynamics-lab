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