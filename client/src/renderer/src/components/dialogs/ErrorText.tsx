import * as react from "react"
import * as Themes from "@radix-ui/themes"

/** @function ErrorText */
export default function ErrorText(props: Readonly<{ text: string }>): react.JSX.Element
{
    return (
        <Themes.Text className="col-span-3 text-center text-sm text-red-400">{props.text}</Themes.Text>
    )
}
