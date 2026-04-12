import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IChase =
{
    trueAnomalyTarget: 150,
    dt: 1
}

interface ChaseProps
{
    data: IChase
    onChange: (data: IChase) => void
}

/** @function Chase */
export default function Chase(props: Readonly<ChaseProps>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IChase>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                name="trueAnomalyTarget"
                label="Target True Anomaly"
                unit="DEG"
                value={data.trueAnomalyTarget}
                onChange={handleChange}
                min={-360}
                max={360}
            />

            <InputField
                name="dt"
                label="Delta Time"
                unit="H"
                value={data.dt}
                onChange={handleChange}
            />
            
        </react.Fragment>
    )
}
