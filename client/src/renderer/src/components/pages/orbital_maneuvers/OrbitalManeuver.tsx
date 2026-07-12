import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import Hohmann from "./maneuvers/Hohmann"
import BiEllipticHohmann from "./maneuvers/BiEllipticHohmann"
import Phasing from "./maneuvers/Phasing"
import NonHohmann from "./maneuvers/NonHohmann"
import ApseLineRotation from "./maneuvers/ApseLineRotation"
import Chase from "./maneuvers/Chase"
import PlaneChange from "./maneuvers/PlaneChange"
import InclinationChange from "./maneuvers/InclinationChange"
import CoplanarCircleCircle from "./maneuvers/CoplanarCircleCircle"
import InclinationChangeNonImpulsive from "./maneuvers/InclinationChangeNonImpulsive"

interface Props
{
    maneuver: IOrbitalManeuver
    result: IOrbitalManeuverFormOutput
    onChange: (maneuver: IOrbitalManeuver) => void
}

/** @function OrbitalManeuver */
export default function OrbitalManeuver(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [maneuver, setManeuver] = react.useState<IOrbitalManeuver>(props.maneuver)

    const [_, setResult] = react.useState<IOrbitalManeuverFormOutput>(props.result)

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
        <div className="space-y-6">
            
            <InputField
                name="type"
                label="Maneuver Type"
                type="select"
                value={maneuver.type}
                onChange={(e) => setManeuver({...maneuver, type: e.target.value as IOrbitalManeuverType})}
                groups={
                    [
                        {
                            caption: "Impulsive Maneuvers",
                            options:
                            [
                                { label: "Hohmann", value: 'hohmann' },
                                { label: "Bi-Elliptic Hohmann", value: 'bi-elliptic-hohmann' },
                                { label: "Phasing", value: 'phasing' },
                                { label: "Non-Hohmann", value: 'non-hohmann' },
                                { label: "Apse Line Rotation", value: 'apse-line-rotation' },
                                { label: "Chase", value: 'chase' },
                                { label: "Inclination Change", value: 'inclination-change' },
                                { label: "Plane Change", value: 'plane-change' }
                            ]
                        },
                        {
                            caption: "Non-Impulsive Maneuvers",
                            options:
                            [
                                { label: "Coplanar Circle-to-Circle", value: "coplanar-circle-circle" },
                                { label: "Inclination Change", value: "inclination-change-non-impulsive" }
                            ]
                        }
                    ]}
            />

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
                maneuver.type === 'inclination-change' &&
                <InclinationChange data={maneuver.data as IInclinationChange} onChange={handleChange} />
            }

            {
                maneuver.type === 'plane-change' &&
                <PlaneChange data={maneuver.data as IPlaneChange} onChange={handleChange} />
            }

            {
                maneuver.type === 'coplanar-circle-circle' &&
                <CoplanarCircleCircle data={maneuver.data as ICoplanarCircleCircle} onChange={handleChange} />
            }

            {
                maneuver.type === 'inclination-change-non-impulsive' &&
                <InclinationChangeNonImpulsive data={maneuver.data as IInclinationChangeNonImpulsive} onChange={handleChange} />
            }

        </div>
    )
}
