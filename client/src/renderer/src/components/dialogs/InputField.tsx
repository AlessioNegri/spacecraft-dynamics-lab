import * as react from "react"
import * as katex from "react-katex"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"

import Tooltip from "@renderer/components/Tooltip"

import earth from "@renderer/assets/planets/earth.png"
import jupiter from "@renderer/assets/planets/jupiter.png"
import mars from "@renderer/assets/planets/mars.png"
import mercury from "@renderer/assets/planets/mercury.png"
import moon from "@renderer/assets/planets/moon.png"
import neptune from "@renderer/assets/planets/neptune.png"
import pluto from "@renderer/assets/planets/pluto.png"
import saturn from "@renderer/assets/planets/saturn.png"
import sun from "@renderer/assets/planets/sun.png"
import uranus from "@renderer/assets/planets/uranus.png"
import venus from "@renderer/assets/planets/venus.png"
import utility from "@renderer/common/utility"

interface Props
{
    name: string
    label?: string
    symbol?: string
    unit?: string
    type?: react.HTMLInputTypeAttribute | "select"
    value: number | string
    min?: number
    max?: number
    disabled?: boolean
    pattern?: string
    options?: Array<{ label: string; value: string | number }>
    onChange?: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
    className?: string
    tooltip?: boolean
}

/** @function InputField */
export default function InputField(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [icon, setIcon] = react.useState<string | null>(null)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        switch (props.value)
        {
            case "mercury": setIcon(mercury); break
            case "venus": setIcon(venus); break
            case "earth": setIcon(earth); break
            case "mars": setIcon(mars); break
            case "jupiter": setIcon(jupiter); break
            case "saturn": setIcon(saturn); break
            case "uranus": setIcon(uranus); break
            case "neptune": setIcon(neptune); break
            case "pluto": setIcon(pluto); break

            case "sun": setIcon(sun); break
            case "moon": setIcon(moon); break

            default: setIcon(null); break
        }
    }, [props.value])

    // --- RENDERING ---

    return (
        <Form.Field name={props.name} className={`flex flex-col space-y-2 ${props.className ?? ""}`}>

            {/* <div className="flex justify-between">

                <form.Label className="text-sm text-neutral-300">{props.label}</form.Label>

                <form.Label className="text-sm text-orange-300/75 font-bold">{props.unit ?? ''}</form.Label>
                
                {
                    icon && <img src={icon} alt="icon" width={20} />
                }

            </div> */}

            {
                props.type === "select"

                ?

                <Themes.Flex direction={"column"} gap={"2"}>

                    <Themes.Text className="flex justify-between text-sm text-neutral-300">

                        {props.label}

                        {icon && <img src={icon} alt="icon" width={20} />}

                    </Themes.Text>

                    <Themes.Select.Root
                        required
                        disabled={props.disabled}
                        name={props.name}
                        value={String(props.value)}
                        onValueChange={(value: string) =>
                            props.onChange?.({ target: { name: props.name, value } } as any) }
                    >

                        <Themes.Select.Trigger variant="soft" style={{ fontFamily: "Oxanium" }} />

                        <Themes.Select.Content>

                            {props.options?.map(opt =>
                                <Themes.Select.Item
                                    key={opt.value}
                                    value={String(opt.value)}
                                >
                                    {opt.label}
                                </Themes.Select.Item>)
                            }

                        </Themes.Select.Content>

                    </Themes.Select.Root>

                </Themes.Flex>

                :

                <Themes.Flex direction={"column"} gap={"2"}>

                {
                    !props.tooltip &&

                    <Themes.Text className="flex justify-between text-sm text-neutral-300">

                        {props.label}

                        {icon && <img src={icon} alt="icon" width={20} />}

                    </Themes.Text>

                }

                    <div
                        className={utility.cn(
                            "flex items-center rounded bg-orange-400/10 h-8 overflow-hidden",
                            "focus-within:ring-2 focus-within:ring-orange-400/50 focus-within:border-orange-400",
                            "transition mx-0.5",
                            props.disabled && "opacity-50 cursor-not-allowed"
                        )}
                        >

                        {/* LEFT SLOT (symbol) */}

                        {
                            props.tooltip
                            
                            ?
                            
                            <Tooltip title={props.label ?? ""} side="top">

                                <div className="bg-orange-900 px-2 h-8 flex items-center text-sm">
                                    <katex.InlineMath math={String.raw`\mathbf{${props.symbol ?? ''}}`} />
                                </div>

                            </Tooltip>

                            :
                            
                            <div className="bg-orange-900 px-2 h-8 flex items-center text-sm">
                                <katex.InlineMath math={String.raw`\mathbf{${props.symbol ?? ''}}`} />
                            </div>
                        }

                        {/* INPUT */}

                        <Form.Control asChild>
                            <input
                                style={{ fontFamily: "Oxanium" }}
                                required
                                disabled={props.disabled}
                                name={props.name}
                                type={props.type ?? "text"}
                                placeholder="Insert value..."
                                value={props.value}
                                onChange={props.onChange}
                                min={props.min}
                                max={props.max}
                                pattern={props.pattern}
                                step="any"
                                className="w-full px-2 bg-transparent outline-none text-orange-200"
                            />
                        </Form.Control>

                        {/* RIGHT SLOT (unit) */}

                        <div className="bg-orange-900 px-2 h-8 flex items-center text-xs">
                            <katex.InlineMath math={String.raw`\mathbf{${props.unit ?? ''}}`} />
                        </div>

                    </div>

                </Themes.Flex>

            }

            <Form.Message className="text-sm text-red-400" match="valueMissing">Required</Form.Message>

            <Form.Message className="text-sm text-red-400" match="rangeUnderflow">
                {`Underflow ${props.min}`}
            </Form.Message>

            <Form.Message className="text-sm text-red-400" match="rangeOverflow">
                {`Overflow ${props.max}`}
            </Form.Message>

            <Form.Message className="text-sm text-red-400" match="patternMismatch">
                {`Pattern Mismatch ${props.pattern}`}
            </Form.Message>

        </Form.Field>
    )
}

/*
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

<select
    required
    disabled={props.disabled}
    name={props.name}
    className="bg-neutral-700 border-2 border-neutral-600 rounded px-2 py-1 font-mono
            focus:outline-none focus:ring-2 focus:ring-orange-400/40 focus:border-orange-400
            transition h-8"
    value={String(props.value)}
    onChange={props.onChange}
>

    {props.options?.map(opt => (<option key={opt.value} value={String(opt.value)}>{opt.label}</option>))}

</select>


<input
    required
    disabled={props.disabled}
    name={props.name}
    type={props.type ?? "text"}
    className="bg-neutral-700 border-2 border-neutral-600 rounded px-2 py-1 font-mono
        focus:outline-none focus:ring-2 focus:ring-orange-400/40 focus:border-orange-400
        transition h-8"
    placeholder="Insert value..."
    value={props.value}
    onChange={props.onChange}
    min={props.min}
    max={props.max}
    pattern={props.pattern}
/>

<Form.Control asChild>

    <Themes.Flex direction={"column"} gap={"2"}>

        {
            props.label &&
            <Themes.Text className="text-sm text-neutral-300">{props.label}</Themes.Text>
        }

        <Themes.TextField.Root
            className="textfield-padding"
            variant="soft"
            size={"2"}
            style={{ fontFamily: "Oxanium" }}
            required
            disabled={props.disabled}
            name={props.name}
            type={allowedTypes.find(t => t === props.type) ?? "text"}
            placeholder="Insert value..."
            value={props.value}
            onChange={props.onChange}
            min={props.min}
            max={props.max}
            pattern={props.pattern}
        >

            <Themes.TextField.Slot className="bg-orange-900 rounded-l">
                <katex.InlineMath math={String.raw`\mathbf{${props.symbol ?? ''}}`} />
            </Themes.TextField.Slot>

            <Themes.TextField.Slot className="bg-orange-900 rounded-r text-xs">
                <katex.InlineMath math={String.raw`\mathbf{${props.unit ?? ''}}`} />
            </Themes.TextField.Slot>

        </Themes.TextField.Root>

    </Themes.Flex>                    

</Form.Control>
*/
