import * as react from "react"
import * as katex from "react-katex"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"

import utility from "@renderer/common/utility"

type AllowedTextFieldType =
    | "text"
    | "number"
    | "email"
    | "password"
    | "search"
    | "tel"
    | "url"
    | "date"
    | "time"
    | "datetime-local"
    | "month"
    | "week"

const allowedTypes: AllowedTextFieldType[] =
[
    "text",
    "number",
    "email",
    "password",
    "search",
    "tel",
    "url",
    "date",
    "time",
    "datetime-local",
    "month",
    "week"
]

interface Props
{
    name?: string
    label?: string
    symbol?: string
    unit?: string
    type?: react.HTMLInputTypeAttribute
    value: number | string
    disabled?: boolean
    minimumFractionDigits?: number
    maximumFractionDigits?: number
}

/** @function OutputField */
export default function OutputField(props: Readonly<Props>): react.JSX.Element
{
    return (
        <Form.Field name={props.name ?? "undefined"} className="flex flex-col space-y-2">

            <Themes.Flex direction={"column"} gap={"2"}>
            
                {
                    props.label &&
                    <Themes.Text className="text-sm text-neutral-300">{props.label}</Themes.Text>
                }

                <Themes.TextField.Root
                    className={utility.cn("textfield-padding",
                        props.type === "datetime-local" ? "textfield-calendar-none" : "")}
                    variant="soft"
                    color={props.disabled ? "red" : "cyan"}
                    size={"2"}
                    style={{ fontFamily: "Oxanium" }}
                    disabled={props.disabled}
                    type={allowedTypes.find(t => t === props.type) ?? "text"}
                    value={
                        (!props.type || props.type === "text") &&
                        !Number.isNaN(Number(props.value)) &&
                        typeof props.value !== "string"
                        ?
                        Number(props.value).toLocaleString("it-IT",
                            {
                                minimumFractionDigits: props.minimumFractionDigits ?? 0,
                                maximumFractionDigits: props.maximumFractionDigits ?? 5
                            })
                        :
                        props.value
                    }
                    onChange={() => {}}
                >

                    <Themes.TextField.Slot
                        className={utility.cn(props.disabled ? "bg-red-900" : "bg-cyan-900", "rounded-l")}
                    >

                        <katex.InlineMath math={String.raw`\mathbf{${props.symbol ?? ''}}`} />

                    </Themes.TextField.Slot>

                    <Themes.TextField.Slot
                        className={utility.cn(props.disabled ? "bg-red-900" : "bg-cyan-900", "rounded-r text-xs")}
                    >

                        <katex.InlineMath math={String.raw`\mathbf{${props.unit ?? ''}}`} />

                    </Themes.TextField.Slot>

                </Themes.TextField.Root>

            </Themes.Flex>

            {/*  */}

            {/* <div className="flex justify-between">
            
                <form.Label className="text-sm text-neutral-300">{props.label}</form.Label>

                <form.Label className="text-sm text-orange-300/75 font-bold">{props.unit ?? ''}</form.Label>

            </div>

            <form.Control asChild>

                <input
                    readOnly
                    type={props.type ?? "text"}
                    disabled={props.disabled}
                    value={
                        (!props.type || props.type === "text") && !Number.isNaN(Number(props.value))
                        ?
                        Number(props.value).toLocaleString("it-IT", {minimumFractionDigits: 5, maximumFractionDigits: 5})
                        :
                        props.value
                    }
                    style={{ fontFamily: "Orbitron" }}
                    className={`bg-neutral-900 border-2 border-neutral-700 rounded px-2 py-1 text-right font-mono
                            text-orange-300 tracking-wider shadow-inner focus:outline-none
                            ${props.type === "datetime-local" ?
                                "[appearance:textfield] [&::-webkit-calendar-picker-indicator]:hidden pr-0" :
                                ""}
                            ${props.disabled ? "bg-red-950" : ""}`}

                />

            </form.Control> */}

        </Form.Field>
    )
}