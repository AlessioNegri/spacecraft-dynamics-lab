import * as react from "react"

interface FormSectionProps
{
    children: react.ReactNode
    title: string
}

/** @function FormSection */
export default function FormSection(props: Readonly<FormSectionProps>): react.JSX.Element
{
    return (
        <section className="space-y-1">

                <h2 className="text-sm font-semibold text-neutral-300 mb-2">{props.title}</h2>

                {props.children}
                
        </section>
    )
}