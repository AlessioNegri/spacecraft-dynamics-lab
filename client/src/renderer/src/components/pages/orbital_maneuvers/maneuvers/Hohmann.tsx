import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IHohmann =
{
    sma: 34754,
    ecc: 0.1218,
    direction: 0
}

interface Props
{
    data: IHohmann
    onChange: (data: IHohmann) => void
}

/** @function Hohmann */
export default function Hohmann(props: Readonly<Props>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IHohmann>(defaultManeuver, props.onChange)

    return (
        <react.Fragment>

            <InputField
                name="sma"
                label="Semimajor Axis"
                symbol="a"
                unit="km"
                type="text"
                pattern="^(?!0$).*"
                value={data.sma}
                onChange={handleChange}
            />

            <InputField
                type="number"
                name="ecc"
                label="Eccentricity"
                symbol="e"
                unit=""
                value={data.ecc}
                onChange={handleChange}
                min={0}
            />

            <InputField
                name="direction"
                label="Direction"
                type="select"
                value={String(data.direction)}
                onChange={handleChange}
                options={
                    [
                        { label: "Pericenter → Apocenter", value: "0" },
                        { label: "Apocenter → Pericenter", value: "1" }
                    ]}
            />
            
        </react.Fragment>
    )
}
