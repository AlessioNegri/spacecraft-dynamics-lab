import * as react from "react"

import InputField from "@renderer/components/dialogs/InputField"

import useManeuverState from "./Common"

const defaultManeuver: IBiEllipticHohmann =
{
    sma: 34754,
    ecc: 0.1218,
    supportApocenterRadius: 82002
}

interface BiEllipticHohmannProps
{
    data: IBiEllipticHohmann
    onChange: (data: IBiEllipticHohmann) => void
}

/** @function BiEllipticHohmann */
export default function BiEllipticHohmann(props: Readonly<BiEllipticHohmannProps>): react.JSX.Element
{
    const { data, handleChange } = useManeuverState<IBiEllipticHohmann>(defaultManeuver, props.onChange)

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
                name="supportApocenterRadius"
                label="Support Apocenter"
                unit="KM"
                value={data.supportApocenterRadius}
                onChange={handleChange}
                min={0}
            />
            
        </react.Fragment>
    )
}
