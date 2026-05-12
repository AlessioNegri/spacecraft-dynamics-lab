import * as react from "react"
import * as form from "@radix-ui/react-form"

import earth from "../../assets/planets/earth.png"
import jupiter from "../../assets/planets/jupiter.png"
import mars from "../../assets/planets/mars.png"
import mercury from "../../assets/planets/mercury.png"
import moon from "../../assets/planets/moon.png"
import neptune from "../../assets/planets/neptune.png"

import pluto from "../../assets/planets/pluto.png"
import saturn from "../../assets/planets/saturn.png"
import sun from "../../assets/planets/sun.png"
import uranus from "../../assets/planets/uranus.png"
import venus from "../../assets/planets/venus.png"

interface InputFieldProps
{
    name: string
    label: string
    unit?: string
    type?: react.HTMLInputTypeAttribute | "select"
    value: number | string
    min?: number
    max?: number
    disabled?: boolean
    pattern?: string
    options?: Array<{ label: string; value: string | number }>
    onChange?: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
    className?: string
}

/** @function InputField */
export default function InputField(props: Readonly<InputFieldProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [icon, setIcon] = react.useState<string | null>(null)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        switch (props.value)
        {
            case "mercury": setIcon(mercury); break
            case "venus": setIcon(venus); break
            case "earth": setIcon(earth); break
            case "mars": setIcon(mars); break
            case "jupiter": setIcon(jupiter); break
            case "saturn": setIcon(saturn); break
            case "uranus": setIcon(uranus); break
            case "neptune": setIcon(neptune); break
            case "pluto": setIcon(pluto); break

            case "sun": setIcon(sun); break
            case "moon": setIcon(moon); break

            default: setIcon(null); break
        }
    }, [props.value])

    // --- RENDERING ---

    return (
        <form.Field name={props.name} className={`flex flex-col space-y-2 ${props.className ?? ""}`}>

            <div className="flex justify-between">

                <form.Label className="text-sm text-neutral-300">{props.label}</form.Label>

                <form.Label className="text-sm text-orange-300/75 font-bold">{props.unit ?? ''}</form.Label>
                
                {
                    icon && <img src={icon} alt="icon" width={20} />
                }

            </div>

            {
                props.type === "select"

                ?

                <select
                    required
                    disabled={props.disabled}
                    name={props.name}
                    className="bg-neutral-700 border-2 border-neutral-600 rounded px-2 py-1 font-mono
                            focus:outline-none focus:ring-2 focus:ring-orange-400/40 focus:border-orange-400
                            transition h-8"
                    value={String(props.value)}
                    onChange={props.onChange}
                >

                    {props.options?.map(opt => (<option key={opt.value} value={String(opt.value)}>{opt.label}</option>))}

                </select>

                :

                <form.Control asChild>

                    <input
                        required
                        disabled={props.disabled}
                        name={props.name}
                        type={props.type ?? "text"}
                        className="bg-neutral-700 border-2 border-neutral-600 rounded px-2 py-1 font-mono
                            focus:outline-none focus:ring-2 focus:ring-orange-400/40 focus:border-orange-400
                            transition h-8"
                        placeholder="Insert value..."
                        value={props.value}
                        onChange={props.onChange}
                        min={props.min}
                        max={props.max}
                        pattern={props.pattern}
                    />

                </form.Control>

            }

            <form.Message className="text-sm text-red-400" match="valueMissing">Required</form.Message>

            <form.Message className="text-sm text-red-400" match="rangeUnderflow">Underflow</form.Message>

            <form.Message className="text-sm text-red-400" match="rangeOverflow">Overflow</form.Message>

            <form.Message className="text-sm text-red-400" match="patternMismatch">
                {`Patter Mismatch ${props.pattern}`}
            </form.Message>

        </form.Field>
    )
}