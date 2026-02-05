import * as react from "react"

interface FormButtonProps
{
    text: string
    disabled?: boolean
    onClick: (e: react.MouseEvent<HTMLButtonElement, MouseEvent>) => void
}

/** @function FormButton */
export default function FormButton(props: Readonly<FormButtonProps>): react.JSX.Element
{
    return (
        <button
            disabled={props.disabled}
            onClick={props.onClick}
            className={`w-full py-2 rounded text-sm font-medium mt-4
                        ${props.disabled ? 
                            'bg-neutral-500 cursor-not-allowed' :
                            'bg-orange-300/25 hover:bg-orange-300/50 cursor-pointer'}`}
        >
            {props.text}
        </button>
    )
}