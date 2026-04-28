import * as react from "react"
import * as merge from "tailwind-merge"

interface FormSectionProps
{
    children: react.ReactNode
    title: string
    className?: string
}

/** @function FormSection */
export default function FormSection(props: Readonly<FormSectionProps>): react.JSX.Element
{
    return (
        <section className={merge.twMerge("space-y-2", props.className)}>

                <h2 className="text-base font-semibold text-neutral-300 mb-2 col-span-full">
                    {props.title}
                </h2>

                {props.children}
                
        </section>
    )
}