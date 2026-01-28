import * as react from "react";
import * as tooltip from "@radix-ui/react-tooltip"

interface TooltipProps
{
    children: react.ReactNode
    title: string
    side: "bottom" | "top" | "right" | "left" | undefined
}

/** @function Tooltip */
export default function Tooltip(props: Readonly<TooltipProps>): react.JSX.Element
{
    return (
        <tooltip.Root>

            <tooltip.Trigger asChild>

                {props.children}

            </tooltip.Trigger>

            <tooltip.Content
                side={props.side}
                className="bg-stone-700 text-white px-2 py-1 m-2 rounded shadow">

                {props.title}

            </tooltip.Content>


        </tooltip.Root>
    )
}