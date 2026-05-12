interface IOrbitalPerturbationsForm
{
    orbitalElements: IOrbitalElements
    startDate: string
    endDate: string
    atmosphericDrag: boolean
    ballisticCoefficient: number
    gravitationalPerturbation: boolean
    solarRadiationPressure: boolean
    ballisticCoefficientSRP: number
    lunarGravity: boolean
    solarGravity: boolean
}