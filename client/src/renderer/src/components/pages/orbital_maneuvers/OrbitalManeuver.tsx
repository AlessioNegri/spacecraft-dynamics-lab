import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

import Hohmann from "./maneuvers/Hohmann"
import BiEllipticHohmann from "./maneuvers/BiEllipticHohmann"
import Phasing from "./maneuvers/Phasing"
import NonHohmann from "./maneuvers/NonHohmann"
import ApseLineRotation from "./maneuvers/ApseLineRotation"
import Chase from "./maneuvers/Chase"
import PlaneChange from "./maneuvers/PlaneChange"

interface OrbitalManeuverProps
{
    maneuver: IOrbitalManeuver
    result: IOrbitalManeuverFormOutput
    onChange: (maneuver: IOrbitalManeuver) => void
}

/** @function OrbitalManeuver */
export default function OrbitalManeuver(props: Readonly<OrbitalManeuverProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [maneuver, setManeuver] = react.useState<IOrbitalManeuver>(props.maneuver)

    const [result, setResult] = react.useState<IOrbitalManeuverFormOutput>(props.result)

    // --- USE EFFECT ---

    react.useEffect(() => setResult(props.result), [props.result])

    // --- HANDLE ---

    const handleChange = (data: IOrbitalManeuverData) =>
    {
        setManeuver({ ...maneuver, data: data })

        props.onChange({ ...maneuver, data: data })
    }

    // --- RENDERING ---

    return (
        <div className="grid grid-flow-row auto-rows-max grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            
            <InputField
                name="type"
                label="Maneuver Type"
                type="select"
                value={maneuver.type}
                onChange={(e) => setManeuver({...maneuver, type: e.target.value as IOrbitalManeuverType})}
                options={
                    [
                        { label: "Hohmann", value: 'hohmann' },
                        { label: "Bi-Elliptic Hohmann", value: 'bi-elliptic-hohmann' },
                        { label: "Phasing", value: 'phasing' },
                        { label: "Non-Hohmann", value: 'non-hohmann' },
                        { label: "Apse Line Rotation", value: 'apse-line-rotation' },
                        { label: "Chase", value: 'chase' },
                        { label: "Plane Change", value: 'plane-change' }
                    ]}
            />

            <span></span>
            <span></span>

            {
                maneuver.type === 'hohmann' &&
                <Hohmann data={maneuver.data as IHohmann} onChange={handleChange} />
            }

            {
                maneuver.type === 'bi-elliptic-hohmann' &&
                <BiEllipticHohmann data={maneuver.data as IBiEllipticHohmann} onChange={handleChange} />
            }

            {
                maneuver.type === 'phasing' &&
                <Phasing data={maneuver.data as IPhasing} onChange={handleChange} />
            }

            {
                maneuver.type === 'non-hohmann' &&
                <NonHohmann data={maneuver.data as INonHohmann} onChange={handleChange} />
            }

            {
                maneuver.type === 'apse-line-rotation' &&
                <ApseLineRotation data={maneuver.data as IApseLineRotation} onChange={handleChange} />
            }

            {
                maneuver.type === 'chase' &&
                <Chase data={maneuver.data as IChase} onChange={handleChange} />
            }

            {
                maneuver.type === 'plane-change' &&
                <PlaneChange data={maneuver.data as IPlaneChange} onChange={handleChange} />
            }

            <span className="col-span-full border-b-2 border-dashed border-neutral-500"></span>

            <OutputField
                label="Semi-Major Axis"
                unit="KM"
                value={result.orbitalElements.sma}
            />
            
            <OutputField
                label="Eccentricity"
                value={result.orbitalElements.ecc}
            />

            <OutputField
                label="Inclination"
                unit="DEG"
                value={result.orbitalElements.inc}
            />

            <OutputField
                label="RAAN"
                unit="DEG"
                value={result.orbitalElements.raan}
            />

            <OutputField
                label="Argument Periapsis"
                unit="DEG"
                value={result.orbitalElements.aop}
            />

            <OutputField
                label="True Anomaly"
                unit="DEG"
                value={result.orbitalElements.ta}
            />

            <OutputField
                label="Δv"
                unit="KM / S"
                value={result.maneuver.dv}
            />
            
            <OutputField
                label="Δt"
                unit="H"
                value={result.maneuver.dt}
            />

            <OutputField
                label="Δm"
                unit="KG"
                value={result.maneuver.dm}
            />

        </div>
    )
}
