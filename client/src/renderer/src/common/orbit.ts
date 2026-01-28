import * as cesium from "cesium"

/**
 * @description Generate orbit positions in ECEF frame
 * 
 * @param orbit Obit parameters
 * @param samples Number of samples to generate
 * @returns Cartesian3[] Array of positions in ECEF frame
 */
function generateOrbitPositions(orbit: IDbOrbit, samples = 360)
{
    const positions: cesium.Cartesian3[] = []

    const { sma, ecc, inc, raan, aop } = orbit

    // * Precompute rotation matrices (perifocal → ECI)

    const cosO: number = Math.cos(raan)
    const sinO: number = Math.sin(raan)
    const cosi: number = Math.cos(inc)
    const sini: number = Math.sin(inc)
    const cosw: number = Math.cos(aop)
    const sinw: number = Math.sin(aop)

    const PQW_to_ECI: cesium.Matrix3 = new cesium.Matrix3(
                                                            cosO * cosw - sinO * sinw * cosi,
                                                            -cosO * sinw - sinO * cosw * cosi,
                                                            sinO * sini,

                                                            sinO * cosw + cosO * sinw * cosi,
                                                            -sinO * sinw + cosO * cosw * cosi,
                                                            -cosO * sini,

                                                            sinw * sini,
                                                            cosw * sini,
                                                            cosi
                                                        )

    // * Use a single timestamp for the whole orbit

    const time: cesium.JulianDate = cesium.JulianDate.now()

    // * Samples

    let first: boolean = true

    const firstPosition: cesium.Cartesian3 = new cesium.Cartesian3()

    for (let i = 0; i < samples; i++)
    {
        // * True anomaly

        const f: number = (i / samples) * 2 * Math.PI

        // * Radius in perifocal frame

        const r: number = sma * (1 - ecc * ecc) / (1 + ecc * Math.cos(f))

        // * Perifocal coordinates
        
        const x: number = r * Math.cos(f)
        const y: number = r * Math.sin(f)
        const z: number = 0

        // * Rotate from perifocal → ECI

        const perifocal: cesium.Cartesian3 = new cesium.Cartesian3(x, y, z)

        const eci: cesium.Cartesian3 = cesium.Matrix3.multiplyByVector(PQW_to_ECI, perifocal, new cesium.Cartesian3())

        // * Rotate from ECI → ECEF

        const icrfToFixed: cesium.Matrix3 = cesium.Transforms.computeIcrfToFixedMatrix(time) ||
                                            cesium.Transforms.computeTemeToPseudoFixedMatrix(time) ||
                                            cesium.Matrix3.IDENTITY

        const ecef: cesium.Cartesian3 = cesium.Matrix3.multiplyByVector(icrfToFixed, eci, new cesium.Cartesian3())

        positions.push(ecef)

        if (first)
        {
            first = false

            firstPosition.x = ecef.x
            firstPosition.y = ecef.y
            firstPosition.z = ecef.z
        }
    }

    positions.push(firstPosition) // ? Close the orbit loop

    return positions
}

/**
 * @description Build a SampledPositionProperty from an array of Cartesian3 positions for simulating orbits
 * 
 * @param positions Positions array
 * @returns SampledPositionProperty
 */
function buildSampledPosition(positions: cesium.Cartesian3[]): cesium.SampledPositionProperty
{
    const property: cesium.SampledPositionProperty = new cesium.SampledPositionProperty()

    const start: cesium.JulianDate = cesium.JulianDate.now()

    const step = 10 // ? Seconds between samples

    positions.forEach((pos: cesium.Cartesian3, i: number) =>
    {
        const time: cesium.JulianDate = cesium.JulianDate.addSeconds(start, i * step, new cesium.JulianDate())

        property.addSample(time, pos)
    })

    return property
}

const orbit =
{
    generateOrbitPositions,
    buildSampledPosition
}

export default orbit