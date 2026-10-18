import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface IFormIn
{
    semimajorAxis: number
    eccentricity: number
    ballisticCoefficient: number
}

interface IFormOut
{
    circularizationTimeDays: number
    circularizationTimeYears: number
    orbitLifetimeDays: number
    orbitLifetimeYears: number
}

const defaultIn: IFormIn =
{
    semimajorAxis: 24456,
    eccentricity: 0.729,
    ballisticCoefficient: 0.015
}

const defaultOut: IFormOut =
{
    circularizationTimeDays: 0,
    circularizationTimeYears: 0,
    orbitLifetimeDays: 0,
    orbitLifetimeYears: 0
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function DragOrbitTimesDialog */
export default function DragOrbitTimesDialog(props: Readonly<Props>): react.JSX.Element
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

        setFormIn(prev => ({ ...prev, [name]: Number(value) }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            const response = await http.api.put<IFormOut>("/orbital-perturbations/drag-orbit-times", formIn)

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
            title="Drag Orbit Times"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={{
                title: "Drag Orbit Times",
                content:
                    `Estimate elliptical-orbit circularization time and circular-orbit lifetime due to atmospheric drag.`
            }}
        >
            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4"
            >
            
                <InputField
                    name="semimajorAxis"
                    label="Semimajor Axis"
                    symbol="a"
                    unit="km"
                    type="number"
                    value={formIn.semimajorAxis}
                    onChange={handleChange}
                    min={6378.1363}
                />

                <InputField
                    name="eccentricity"
                    label="Eccentricity"
                    symbol="e"
                    type="number"
                    value={formIn.eccentricity}
                    onChange={handleChange}
                    min={0}
                    max={0.999999}
                />

                <InputField
                    name="ballisticCoefficient"
                    label="Ballistic Coefficient"
                    symbol="B"
                    unit="m² / kg"
                    type="number"
                    value={formIn.ballisticCoefficient}
                    onChange={handleChange}
                    min={0.000001}
                />

            </Form.Root>

            <Form.Root className="grid grid-cols-2 gap-4">

                <OutputField
                    label="Circularization Time"
                    symbol="t_c"
                    unit="days"
                    value={formOut.circularizationTimeDays}
                />

                <OutputField
                    label="Circular Orbit Lifetime"
                    symbol="t_l"
                    unit="days"
                    value={formOut.orbitLifetimeDays}
                />

                <OutputField
                    label="Circularization Time"
                    symbol="t_c"
                    unit="years"
                    value={formOut.circularizationTimeYears}
                />

                <OutputField
                    label="Circular Orbit Lifetime"
                    symbol="t_l"
                    unit="years"
                    value={formOut.orbitLifetimeYears}
                />

            </Form.Root>

        </DialogRUI>
    )
}
