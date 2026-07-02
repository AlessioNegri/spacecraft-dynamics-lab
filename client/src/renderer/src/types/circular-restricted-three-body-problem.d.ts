interface ICircularRestrictedThreeBodyProblemForm
{
    body1: string
    body2: string
    integrationTime: number
    lagrangePoint: string
    position:
    {
        x: number,
        y: number,
        z: number
    }
    velocity:
    {
        x: number,
        y: number,
        z: number
    }
}