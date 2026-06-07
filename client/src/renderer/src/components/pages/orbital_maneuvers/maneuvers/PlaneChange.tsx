import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IPlaneChange =
{
    inc: 25.4393,
    raan: 146.024
}

interface Props
{
    data: IPlaneChange
    onChange: (data: IPlaneChange) => void
}

/** @function PlaneChange */
export default function PlaneChange(props: Readonly<Props>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IPlaneChange>(defaultManeuver, props.onChange)

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

            <InputField
                type="number"
                name="raan"
                label="Right Ascension of Ascending Node"
                symbol="\Omega"
                unit="deg"
                value={data.raan}
                onChange={handleChange}
                min={-360}
                max={360}
            />
            
        </react.Fragment>
    )
}
