import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface IFormIn
{
    attractor: string
    altitude: number
    inclination: number
    rightAscensionAscendingNode: number
    rightAscensionSun: number
}

interface IFormOut
{
    beta: number
    eclipse: boolean
    eclipseDuration: number
    hotCase: boolean
}

const defaultIn: IFormIn =
{
    attractor: "earth",
    altitude: 35788,
    inclination: 60,
    rightAscensionAscendingNode: 270,
    rightAscensionSun: 0
}

const defaultOut: IFormOut =
{
    beta: 0,
    eclipse: false,
    eclipseDuration: 0,
    hotCase: false
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function EclipseDurationDialog */
export default function EclipseDurationDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)
    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>): void =>
    {
        const { name, value } = e.target

        setFormIn(prev => ({ ...prev, [name]: name === "attractor" ? value : Number(value) }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            const response = await http.api.put<IFormOut>("/tools/eclipse-duration", formIn)

            setFormOut(response.data)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Eclipse Duration"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={{
                title: "Eclipse Duration",
                content: `Compute the orbit beta angle, eclipse status and duration, and hot-case status for a circular
                    orbit.`
            }}
        >

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4"
            >

                <InputField
                    name="attractor"
                    label="Attractor"
                    type="select"
                    value={formIn.attractor}
                    onChange={handleChange}
                    options={[
                        { label: "Mercury", value: "mercury" },
                        { label: "Venus", value: "venus" },
                        { label: "Earth", value: "earth" },
                        { label: "Mars", value: "mars" },
                        { label: "Jupiter", value: "jupiter" },
                        { label: "Saturn", value: "saturn" },
                        { label: "Uranus", value: "uranus" },
                        { label: "Neptune", value: "neptune" }
                    ]}
                />

                <InputField
                    name="altitude"
                    label="Altitude"
                    symbol="h"
                    unit="km"
                    type="number"
                    value={formIn.altitude}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    name="inclination"
                    label="Inclination"
                    symbol="i"
                    unit="deg"
                    type="number"
                    value={formIn.inclination}
                    onChange={handleChange}
                    min={0}
                    max={180}
                />

                <InputField
                    name="rightAscensionAscendingNode"
                    label="Right Ascension of Ascending Node"
                    symbol="\Omega"
                    unit="deg"
                    type="number"
                    value={formIn.rightAscensionAscendingNode}
                    onChange={handleChange}
                    min={0}
                    max={360}
                />

                <InputField
                    name="rightAscensionSun"
                    label="Sun Right Ascension"
                    symbol="\alpha_☉"
                    unit="deg"
                    type="number"
                    value={formIn.rightAscensionSun}
                    onChange={handleChange}
                    min={0}
                    max={360}
                />
            </Form.Root>

            <Form.Root className="grid grid-cols-2 gap-4">

                <OutputField
                    label="Beta Angle"
                    symbol="\beta"
                    unit="deg"
                    value={formOut.beta}
                />
                
                <OutputField
                    label="Eclipse"
                    value={formOut.eclipse ? "Yes" : "No"}
                />
                
                <OutputField
                    label="Eclipse Duration"
                    symbol="t_e"
                    unit="min"
                    value={formOut.eclipseDuration}
                />
                
                <OutputField
                    label="Hot Case"
                    value={formOut.hotCase ? "Yes" : "No"}
                />

            </Form.Root>
            
        </DialogRUI>
    )
}
