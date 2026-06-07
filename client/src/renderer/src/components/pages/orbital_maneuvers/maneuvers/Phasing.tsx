import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IPhasing =
{
    targetTrueAnomaly: 115.9266,
    numRevolutions: 1
}

interface Props
{
    data: IPhasing
    onChange: (data: IPhasing) => void
}

/** @function Phasing */
export default function Phasing(props: Readonly<Props>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IPhasing>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

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

            <InputField
                type="number"
                name="numRevolutions"
                label="Number of Revolutions"
                symbol="n"
                unit=""
                value={data.numRevolutions}
                onChange={handleChange}
                min={1}
            />
            
        </react.Fragment>
    )
}
