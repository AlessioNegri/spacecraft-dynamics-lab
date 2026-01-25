import * as react from "react"

interface FormInputProps
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
export default function FormInput(props: Readonly<FormInputProps>): react.JSX.Element
{
    // --- USE REF ---

    const inputRef = react.useRef<HTMLInputElement>(null)

    // --- GENERIC ---

    const openPicker = (e: React.MouseEvent<HTMLButtonElement>) => { e.preventDefault(); inputRef.current?.click() }

    // --- RENDERING ---
    
    // * CSS default style
    
    const cssDefault: string = `w-full px-3 py-2 rounded focus:outline-none \
                                bg-stone-700 border border-gray-700 focus:border-orange-500`

    // * CSS style for type "file"

    const cssFile: string = "w-full text-gray-300"

    // * CSS style for type "color"

    const cssColor: string = "w-full opacity-0"

    // * Select active style

    let css: string = cssDefault

    if (props.type == "file") css = cssFile
    if (props.type == "color") css = cssColor

    return (
        <div>

            <label className="block mb-1 font-medium">{props.label}</label>

            {
                props.type === "color" && 
                <button
                    onClick={openPicker}
                    className="w-full h-11 rounded cursor-pointer border
                                border-gray-700 focus:border-orange-500 text-black font-bold uppercase"
                    style={{ backgroundColor: props.value }}>

                    {props.value}

                </button>
            }

            <input
                ref={inputRef}
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