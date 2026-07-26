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
    file?: File
    min?: number
    max?: number
    step?: number
    disabled?: boolean
    pattern?: string
    options?: Array<{ label: string; value: string | number }>
    groups?: Array<{ caption: string; options: Array<{ label: string; value: string | number }> }>
    onChange?: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
    onSelectChange?: (value: string) => void
    className?: string
    tooltip?: boolean
    placeholder?: string
    showSides?: boolean
    optional?: boolean
}

/** @function InputField */
export default function InputField(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [icon, setIcon] = react.useState<string | null>(null)

    // --- USE REF ---

    const inputRef = react.useRef<HTMLInputElement>(null)

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

    let fieldContent: react.ReactNode

    if (props.type === "select")
    {
        fieldContent = (
            <Themes.Flex direction={"column"} gap={"2"}>

                <Themes.Text className="flex justify-between text-sm text-neutral-300">

                    {props.label}

                    {icon && <img src={icon} alt="icon" width={20} />}

                </Themes.Text>

                <Themes.Select.Root
                    required
                    disabled={props.disabled}
                    name={props.name}
                    value={typeof props.value === "string" ? String(props.value) : ""}
                    onValueChange={(value: string) =>
                    {
                        props.onChange?.({ target: { name: props.name, value } } as any)

                        props.onSelectChange?.(value)
                    }}
                >

                    <Themes.Select.Trigger variant="soft" style={{ fontFamily: "Oxanium" }} />

                    <Themes.Select.Content
                        position="popper"
                        className="p-2"
                        style={{ maxHeight: "300px", overflowY: "auto" }}
                    >

                        {
                            props.options?.map(option =>
                                <Themes.Select.Item key={option.value} value={String(option.value)}>
                                    {option.label}
                                </Themes.Select.Item>
                            )
                        }

                        {
                            props.groups?.map((group, index) =>
                                <Themes.Select.Group key={group.caption}>

                                    <Themes.Select.Label className="uppercase">{group.caption}</Themes.Select.Label>

                                    {
                                        group.options.map(option =>
                                            <Themes.Select.Item key={option.value} value={String(option.value)}>
                                                {option.label}
                                            </Themes.Select.Item>
                                        )
                                    }

                                    {
                                        props.groups && index < props.groups?.length - 1 &&
                                        <Themes.Select.Separator />
                                    }

                                </Themes.Select.Group>
                            )
                        }

                    </Themes.Select.Content>

                </Themes.Select.Root>

            </Themes.Flex>
        )
    }
    else if (props.type === "range")
    {
        fieldContent = (
            <Themes.Flex direction={"column"} gap={"2"}>

                {props.label && (
                    <Themes.Text className="flex justify-between text-sm text-neutral-300">
                        {props.label}
                        {icon && <img src={icon} alt="icon" width={20} />}
                    </Themes.Text>
                )}

                <div
                    className={utility.cn(
                        "flex items-center rounded bg-orange-400/10 h-8 overflow-hidden",
                        "focus-within:ring-2 focus-within:ring-orange-400/50 focus-within:border-orange-400",
                        "transition mx-0.5",
                        props.disabled && "opacity-50 cursor-not-allowed"
                    )}
                >

                    {/* LEFT SLOT (symbol) */}
                    <div className="bg-orange-900 px-2 h-8 flex items-center text-sm">
                        <katex.InlineMath math={String.raw`\mathbf{${props.symbol ?? ''}}`} />
                    </div>

                    {/* RANGE INPUT */}
                    <Form.Control asChild>
                        <input
                            style={{ fontFamily: "Oxanium" }}
                            required
                            disabled={props.disabled}
                            name={props.name}
                            type="range"
                            value={props.value}
                            onChange={props.onChange}
                            min={props.min}
                            max={props.max}
                            step={props.step ?? "any"}
                            list={`${props.name}-ticks`}
                            className="w-full bg-transparent outline-none accent-orange-400 mx-4"
                        />
                    </Form.Control>

                    {/* INLINE VALUE DISPLAY */}
                    <div className="px-2 h-8 flex items-center text-sm text-orange-300 font-mono">
                        {Number(props.value).toFixed(3)}
                    </div>

                    {/* RIGHT SLOT (unit) */}
                    <div className="bg-orange-900 px-2 h-8 flex items-center text-xs">
                        <katex.InlineMath math={String.raw`\mathbf{${props.unit ?? ''}}`} />
                    </div>

                </div>

            </Themes.Flex>
        )
    }
    else if (props.type === "checkbox")
    {
        fieldContent = (
            <Themes.Text as="label" size="3" className="h-8 pt-8">

                <Themes.Flex as="span" gap="2" className="text-neutral-300">

                    <Themes.Checkbox
                        size="3"
                        variant="soft"
                        checked={Boolean(props.value)}
                        disabled={props.disabled}
                        defaultChecked
                        onCheckedChange={(checked: boolean) =>
                            props.onChange?.({ target: { name: props.name, value: checked as boolean } } as any)
                        }
                    />

                    {props.label}

                </Themes.Flex>

            </Themes.Text>
        )
    }
    else if (props.type === "color")
    {
        fieldContent = (
            <Themes.Flex direction={"column"} gap={"2"}>

                {
                    props.label &&

                    <Themes.Text className="flex justify-between text-sm text-neutral-300">

                        {props.label}

                        {icon && <img src={icon} alt="icon" width={20} />}

                    </Themes.Text>
                }

                <div
                    className={utility.cn(
                        "rounded bg-transparent h-8 mx-0.5",
                        props.disabled && "opacity-50 cursor-not-allowed"
                    )}
                >

                    <button
                        onClick={(e) => { e.preventDefault(); inputRef.current?.click() }}
                        className="w-full h-7.5 rounded cursor-pointer border
                                    border-gray-700 text-black font-bold uppercase
                                    transition-transform duration-75
                                    active:scale-[0.97]"
                        style={{ backgroundColor: String(props.value) }}>

                        {props.value}

                    </button>

                    <Form.Control asChild>

                        <input
                            ref={inputRef}
                            style={{ fontFamily: "Oxanium" }}
                            required
                            disabled={props.disabled}
                            name={props.name}
                            type="color"
                            value={props.value}
                            onChange={props.onChange}
                            className="w-full h-full opacity-0 bg-transparent outline-none text-orange-200"
                        />

                    </Form.Control>

                </div>

            </Themes.Flex>
        )
    }
    else if (props.type === "file")
    {
        fieldContent = (
            <Themes.Flex direction={"column"} gap={"2"}>

                {
                    props.label &&

                    <Themes.Text className="flex justify-between text-sm text-neutral-300">

                        {props.label}

                        {icon && <img src={icon} alt="icon" width={20} />}

                    </Themes.Text>
                }

                <div
                    className={utility.cn(
                        "rounded bg-transparent h-8 mx-0.5",
                        props.disabled && "opacity-50 cursor-not-allowed"
                    )}
                >

                    <Form.Control asChild>

                        <input
                            ref={inputRef}
                            style={{ fontFamily: "Oxanium", ['--file-text' as any]: "Select file" }}
                            disabled={props.disabled}
                            name={props.name}
                            type="file"
                            onChange={props.onChange}
                            className="w-full h-full bg-transparent outline-none text-orange-200
                            file:bg-orange-900 file:text-orange-200 file:border-none
                            file:px-3 file:py-1 file:rounded-l
                            file:cursor-pointer
                            file:uppercase file:font-bold
                            file:transition-transform file:duration-75
                            file:active:scale-[0.97]"
                        />

                    </Form.Control>

                </div>

            </Themes.Flex>
        )
    }
    else
    {
        fieldContent = (
            <Themes.Flex direction={"column"} gap={"2"}>

            {
                (!props.tooltip && props.label) &&

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
                        props.showSides !== false && (
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
                        )
                    }

                    {/* INPUT */}

                    <Form.Control asChild>
                        <input
                            style={{ fontFamily: "Oxanium" }}
                            required
                            disabled={props.disabled}
                            name={props.name}
                            type={props.type ?? "text"}
                            placeholder={props.placeholder ?? "Insert value..."}
                            value={props.value}
                            onChange={props.onChange}
                            min={props.min}
                            max={props.max}
                            pattern={props.pattern}
                            step={props.step ?? "any"}
                            className="w-full px-2 bg-transparent outline-none text-orange-200"
                        />
                    </Form.Control>

                    {/* RIGHT SLOT (unit) */}

                    {
                        props.showSides !== false &&
                        <div className="bg-orange-900 px-2 h-8 flex items-center text-xs">
                            <katex.InlineMath math={String.raw`\mathbf{${props.unit ?? ''}}`} />
                        </div>
                    }

                </div>

            </Themes.Flex>
        )
    }

    return (
        <Form.Field name={props.name} className={`flex flex-col space-y-2 ${props.className ?? ""}`}>

            {/* <div className="flex justify-between">

                <form.Label className="text-sm text-neutral-300">{props.label}</form.Label>

                <form.Label className="text-sm text-orange-300/75 font-bold">{props.unit ?? ''}</form.Label>
                
                {
                    icon && <img src={icon} alt="icon" width={20} />
                }

            </div> */}

            { fieldContent }

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
