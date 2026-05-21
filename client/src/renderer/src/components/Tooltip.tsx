import * as react from "react"
import * as tooltip from "@radix-ui/react-tooltip"

interface Props
{
    children: react.ReactNode
    title: string
    side: "bottom" | "top" | "right" | "left" | undefined
}

/** @function Tooltip */
export default function Tooltip(props: Readonly<Props>): react.JSX.Element
{
    return (
        <tooltip.Root>

            <tooltip.Trigger asChild>

                {props.children}

            </tooltip.Trigger>

            <tooltip.Portal>

                <tooltip.Content
                    side={props.side}
                    className="bg-orange-900 text-white border border-orange-400 px-2 py-1 m-0 rounded shadow font-mono">

                    {props.title}

                    <tooltip.Arrow className="fill-orange-400" />

                </tooltip.Content>
                
            </tooltip.Portal>


        </tooltip.Root>
    )
}