import * as react from "react"

const colorMap: Record<string, string> =
{
    neutral: "bg-neutral-800 hover:bg-neutral-800/50",
    red: "bg-red-800 hover:bg-red-800/50",
    green: "bg-green-800 hover:bg-green-800/50",
    blue: "bg-blue-800 hover:bg-blue-800/50",
    cyan: "bg-cyan-800 hover:bg-cyan-800/50",
    orange: "bg-orange-800 hover:bg-orange-800/50",
}

interface FormButtonProps
{
    text: string
    color?: "neutral" | "red" | "green" | "blue" | "cyan" | "orange"
    disabled?: boolean
    type?: "button" | "submit" | "reset"
    form?: string
    onClick?: (e: react.MouseEvent<HTMLButtonElement, MouseEvent>) => void
}

/** @function FormButton */
export default function FormButton(props: Readonly<FormButtonProps>): react.JSX.Element
{
    const css: string = `${colorMap[props.color ?? "neutral"]} cursor-pointer`

    return (
        <button
            type={props.type ?? "button"}
            form={props.form ?? ""}
            disabled={props.disabled}
            onClick={props.onClick}
            className={`px-2 py-2 min-w-20 rounded text-sm font-medium mt-4
                        ${props.disabled ?  'bg-neutral-500 cursor-not-allowed' : css}`}
        >
            {props.text}
        </button>
    )
}