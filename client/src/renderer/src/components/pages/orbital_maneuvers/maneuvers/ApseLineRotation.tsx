import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IApseLineRotation =
{
    aop: 177.9149,
    intersectionPoint: 0
}

interface ApseLineRotationProps
{
    data: IApseLineRotation
    onChange: (data: IApseLineRotation) => void
}

/** @function ApseLineRotation */
export default function ApseLineRotation(props: Readonly<ApseLineRotationProps>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IApseLineRotation>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                name="aop"
                label="Argument Periapsis"
                unit="DEG"
                value={data.aop}
                onChange={handleChange}
                min={-360}
                max={360}
            />

            <InputField
                name="intersectionPoint"
                label="Intersection Point"
                type="select"
                value={data.intersectionPoint}
                onChange={handleChange}
                options={
                    [
                        { label: "First", value: 0 },
                        { label: "Second", value: 1 }
                    ]}
            />
            
        </react.Fragment>
    )
}
