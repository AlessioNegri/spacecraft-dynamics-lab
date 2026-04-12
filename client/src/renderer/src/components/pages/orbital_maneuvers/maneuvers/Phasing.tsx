import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IPhasing =
{
    targetTrueAnomaly: 115.9266,
    numRevolutions: 1
}

interface PhasingProps
{
    data: IPhasing
    onChange: (data: IPhasing) => void
}

/** @function Phasing */
export default function Phasing(props: Readonly<PhasingProps>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IPhasing>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                name="targetTrueAnomaly"
                label="Target True Anomaly"
                unit="DEG"
                value={data.targetTrueAnomaly}
                onChange={handleChange}
                min={-360}
                max={360}
            />

            <InputField
                name="numRevolutions"
                label="Number of Revolutions"
                type="text"
                value={data.numRevolutions}
                onChange={handleChange}
                min={1}
            />
            
        </react.Fragment>
    )
}
