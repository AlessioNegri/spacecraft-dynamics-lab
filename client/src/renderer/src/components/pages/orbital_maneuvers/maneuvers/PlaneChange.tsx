import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IPlaneChange =
{
    inc: 25.4393,
    raan: 146.024
}

interface PlaneChangeProps
{
    data: IPlaneChange
    onChange: (data: IPlaneChange) => void
}

/** @function PlaneChange */
export default function PlaneChange(props: Readonly<PlaneChangeProps>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IPlaneChange>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                name="inc"
                label="Inclination"
                unit="DEG"
                type="text"
                pattern="^(?!0$).*"
                value={data.inc}
                onChange={handleChange}
                min={-360}
                max={360}
            />

            <InputField
                name="raan"
                label="RAAN"
                unit="DEG"
                value={data.raan}
                onChange={handleChange}
                min={-360}
                max={360}
            />
            
        </react.Fragment>
    )
}
