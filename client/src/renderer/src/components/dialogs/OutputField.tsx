import * as react from "react"
import * as form from "@radix-ui/react-form"

interface OutputFieldProps
{
    name?: string
    label: string
    unit?: string
    type?: react.HTMLInputTypeAttribute
    value: number | string
    disabled?: boolean
}

/** @function Field */
export default function OutputField(props: Readonly<OutputFieldProps>): react.JSX.Element
{
    return (
        <form.Field name={props.name ?? "undefined"} className="flex flex-col space-y-2">

            <div className="flex justify-between">
            
                <form.Label className="text-sm text-neutral-300">{props.label}</form.Label>

                <form.Label className="text-sm text-orange-300/75 font-bold">{props.unit ?? ''}</form.Label>

            </div>

            <form.Control asChild>

                <input
                    readOnly
                    type={props.type ?? "text"}
                    disabled={props.disabled}
                    value={
                        (!props.type || props.type === "text") && !Number.isNaN(Number(props.value))
                        ?
                        Number(props.value).toLocaleString("it-IT", {minimumFractionDigits: 5, maximumFractionDigits: 5})
                        :
                        props.value
                    }
                    style={{ fontFamily: "Orbitron" }}
                    className={`bg-neutral-900 border-2 border-neutral-700 rounded px-2 py-1 text-right font-mono
                            text-orange-300 tracking-wider shadow-inner focus:outline-none
                            ${props.type === "datetime-local" ?
                                "[appearance:textfield] [&::-webkit-calendar-picker-indicator]:hidden pr-0" :
                                ""}
                            ${props.disabled ? "bg-red-950" : ""}`}

                />

            </form.Control>

        </form.Field>
    )
}