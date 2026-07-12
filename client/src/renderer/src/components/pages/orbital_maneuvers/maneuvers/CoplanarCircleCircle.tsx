import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: ICoplanarCircleCircle =
{
    sma: 20000
}

interface Props
{
    data: ICoplanarCircleCircle
    onChange: (data: ICoplanarCircleCircle) => void
}

/** @function CoplanarCircleCircle */
export default function CoplanarCircleCircle(props: Readonly<Props>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<ICoplanarCircleCircle>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                name="sma"
                label="Target Semimajor Axis"
                symbol="a"
                unit="km"
                type="text"
                pattern="^(?!0$).*"
                value={data.sma}
                onChange={handleChange}
            />

        </react.Fragment>
    )
}
