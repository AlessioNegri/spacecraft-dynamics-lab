import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: INonHohmann =
{
    targetRadius: 10000,
    targetTrueAnomaly: 115.9266
}

interface NonHohmannProps
{
    data: INonHohmann
    onChange: (data: INonHohmann) => void
}

/** @function NonHohmann */
export default function NonHohmann(props: Readonly<NonHohmannProps>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<INonHohmann>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                name="targetRadius"
                label="Target Radius"
                unit="KM"
                type="text"
                pattern="^(?!0$).*"
                value={data.targetRadius}
                onChange={handleChange}
            />

            <InputField
                name="targetTrueAnomaly"
                label="Target True Anomaly"
                unit="DEG"
                value={data.targetTrueAnomaly}
                onChange={handleChange}
                min={-360}
                max={360}
            />
            
        </react.Fragment>
    )
}
