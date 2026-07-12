import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IInclinationChangeNonImpulsive =
{
    inc: 169
}

interface Props
{
    data: IInclinationChangeNonImpulsive
    onChange: (data: IInclinationChangeNonImpulsive) => void
}

/** @function InclinationChangeNonImpulsive */
export default function InclinationChangeNonImpulsive(props: Readonly<Props>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IInclinationChangeNonImpulsive>(defaultManeuver, props.onChange)

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
                min={0}
                max={180}
            />
            
        </react.Fragment>
    )
}
