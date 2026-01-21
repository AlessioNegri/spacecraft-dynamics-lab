import * as react from "react"

interface FormStringProps
{
    label: string
    type: react.HTMLInputTypeAttribute
    name: string
    value: any
    placeholder?: string
    error?: string
    setValue: (e: react.ChangeEvent<HTMLInputElement>) => void
}

/** @function FormInput */
export default function FormInput(props: Readonly<FormStringProps>): react.JSX.Element
{
    // * CSS default style
    
    const cssDefault: string = `w-full px-3 py-2 rounded focus:outline-none \
                                bg-stone-700 border border-gray-700 focus:border-orange-500`

    // * CSS style for type "file"

    const cssFile: string = "w-full text-gray-300"

    // * Select active style

    let css: string = cssDefault

    if (props.type == "file") css = cssFile

    return (
        <div>

            <label className="block mb-1 font-medium">{props.label}</label>

            <input
                type={props.type}
                name={props.name}
                onChange={props.setValue}
                placeholder={props.placeholder}
                className={css}
                {...(props.type === "file" ? {} : { value: props.value })} />

        {
            props.error && <p className="text-red-400 text-sm">{props.error}</p>
        }

        </div>
    )
}