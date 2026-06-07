import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: INonHohmann =
{
    sma: 34754,
    ecc: 0.1218,
    targetTrueAnomaly: 155.9266
}

interface Props
{
    data: INonHohmann
    onChange: (data: INonHohmann) => void
}

/** @function NonHohmann */
export default function NonHohmann(props: Readonly<Props>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<INonHohmann>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                name="sma"
                label="Semimajor Axis"
                symbol="a"
                unit="km"
                type="text"
                pattern="^(?!0$).*"
                value={data.sma}
                onChange={handleChange}
            />

            <InputField
                type="number"
                name="ecc"
                label="Eccentricity"
                symbol="e"
                unit=""
                value={data.ecc}
                onChange={handleChange}
                min={0}
            />

            <InputField
                type="number"
                name="targetTrueAnomaly"
                label="Target True Anomaly"
                symbol="\theta"
                unit="deg"
                value={data.targetTrueAnomaly}
                onChange={handleChange}
                min={-360}
                max={360}
            />
            
        </react.Fragment>
    )
}
