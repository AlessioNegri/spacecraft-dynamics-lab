import * as react from "react"

export interface OptionProps
{
    name: string
    value: string
}

interface FormSelectProps
{
    label: string
    name: string
    value: any
    options: OptionProps[]
    error?: string
    setValue: (e: react.ChangeEvent<HTMLSelectElement>) => void
}

/** @function FormSelect */
export default function FormSelect(props: Readonly<FormSelectProps>): react.JSX.Element
{
    return (
        <div className="mb-2">

            <label htmlFor={props.name} className="block text-xs text-neutral-400 mb-1">{props.label}</label>

            <select
                name={props.name}
                value={props.value}
                onChange={props.setValue}
                className="w-full bg-neutral-800 border border-neutral-700 rounded px-2 py-1 text-sm"
            >

            {
                props.options.map((e: OptionProps) =>
                    <option key={e.value} value={e.value}>{e.name}</option>
                )
            }

            </select>

        {
            props.error && <p className="text-red-400 text-sm">{props.error}</p>
        }

        </div>
    )
}