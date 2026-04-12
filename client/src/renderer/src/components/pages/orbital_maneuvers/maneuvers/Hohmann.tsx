import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IHohmann =
{
    sma: 34754,
    ecc: 0.1218,
    direction: 0
}

interface HohmannProps
{
    data: IHohmann
    onChange: (data: IHohmann) => void
}

/** @function Hohmann */
export default function Hohmann(props: Readonly<HohmannProps>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IHohmann>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                name="sma"
                label="Semi-Major Axis"
                unit="KM"
                type="text"
                pattern="^(?!0$).*"
                value={data.sma}
                onChange={handleChange}
            />

            <InputField
                name="ecc"
                label="Eccentricity"
                unit="KM"
                value={data.ecc}
                onChange={handleChange}
                min={0}
            />

            <InputField
                name="direction"
                label="Direction"
                type="select"
                value={data.direction}
                onChange={handleChange}
                options={
                    [
                        { label: "Pericenter → Apocenter", value: 0 },
                        { label: "Apocenter → Pericenter", value: 1 }
                    ]}
            />
            
        </react.Fragment>
    )
}
