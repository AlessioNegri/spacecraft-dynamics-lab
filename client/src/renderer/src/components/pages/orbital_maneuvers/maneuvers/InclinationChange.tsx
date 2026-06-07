import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IInclinationChange =
{
    inc: 10
}

interface Props
{
    data: IInclinationChange
    onChange: (data: IInclinationChange) => void
}

/** @function InclinationChange */
export default function InclinationChange(props: Readonly<Props>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IInclinationChange>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                type="number"
                name="inc"
                label="Inclination"
                symbol="i"
                unit="deg"
                value={data.inc}
                onChange={handleChange}
                min={-360}
                max={360}
            />
            
        </react.Fragment>
    )
}
