import * as Cesium from "cesium"

/**
 * @description Generate orbit positions in ECEF frame
 * 
 * @param orbit Obit parameters
 * @param samples Number of samples to generate
 * @returns Cartesian3[] Array of positions in ECEF frame
 */
export function generateOrbitPositions(orbit: IDbOrbit, samples = 360)
{
    const positions: Cesium.Cartesian3[] = []

    const { sma, ecc, inc, raan, aop } = orbit

    // * Precompute rotation matrices (perifocal → ECI)

    const cosO: number = Math.cos(raan)
    const sinO: number = Math.sin(raan)
    const cosi: number = Math.cos(inc)
    const sini: number = Math.sin(inc)
    const cosw: number = Math.cos(aop)
    const sinw: number = Math.sin(aop)

    const PQW_to_ECI: Cesium.Matrix3 = new Cesium.Matrix3(
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

    const time: Cesium.JulianDate = Cesium.JulianDate.now()

    // * Samples

    let first: boolean = true

    const firstPosition: Cesium.Cartesian3 = new Cesium.Cartesian3()

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

        const perifocal: Cesium.Cartesian3 = new Cesium.Cartesian3(x, y, z)

        const eci: Cesium.Cartesian3 = Cesium.Matrix3.multiplyByVector(PQW_to_ECI, perifocal, new Cesium.Cartesian3())

        // * Rotate from ECI → ECEF

        const icrfToFixed: Cesium.Matrix3 = Cesium.Transforms.computeIcrfToFixedMatrix(time) ||
                                            Cesium.Transforms.computeTemeToPseudoFixedMatrix(time) ||
                                            Cesium.Matrix3.IDENTITY

        const ecef: Cesium.Cartesian3 = Cesium.Matrix3.multiplyByVector(icrfToFixed, eci, new Cesium.Cartesian3())

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