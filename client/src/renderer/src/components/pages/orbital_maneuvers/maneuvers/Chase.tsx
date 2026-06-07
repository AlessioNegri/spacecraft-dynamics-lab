import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IChase =
{
    trueAnomalyTarget: 150,
    dt: 1
}

interface Props
{
    data: IChase
    onChange: (data: IChase) => void
}

/** @function Chase */
export default function Chase(props: Readonly<Props>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IChase>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                type="number"
                name="trueAnomalyTarget"
                label="Target True Anomaly"
                symbol="\theta"
                unit="deg"
                value={data.trueAnomalyTarget}
                onChange={handleChange}
                min={-360}
                max={360}
            />

            <InputField
                type="number"
                name="dt"
                label="Delta Time"
                symbol="\Delta t"
                unit="hours"
                value={data.dt}
                onChange={handleChange}
                min={0.01}
            />
            
        </react.Fragment>
    )
}
