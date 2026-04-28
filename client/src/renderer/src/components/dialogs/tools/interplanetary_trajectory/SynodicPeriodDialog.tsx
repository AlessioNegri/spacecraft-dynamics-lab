import * as react from "react"
import * as form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

interface IFormIn
{
    departurePlanet: string
    arrivalPlanet: string
}

interface IFormOut
{
    synodicPeriod: number,
    initialPhaseAngle: number,
    finalPhaseAngle: number,
    waitTime: number
}

const defaultIn: IFormIn =
{
    departurePlanet: "earth",
    arrivalPlanet: "mars"
}

const defaultOut: IFormOut =
{
    synodicPeriod: 0,
    initialPhaseAngle: 0,
    finalPhaseAngle: 0,
    waitTime: 0
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function SynodicPeriodDialog */
export default function SynodicPeriodDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const validate = () : boolean =>
    {
        const newErrors: Record<string, string> = {}

        if (formIn.arrivalPlanet === formIn.departurePlanet)
        {
            newErrors.planets = "Arrival planet cannot be the same as departure planet"
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        if (!validate()) return

        try
        {
            let response: any = await http.api.put(`/tools/synodic-period`, formIn)

            const result: IFormOut = response.data

            setFormOut(result)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Synodic Period"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Synodic Period",
                    content:
                        `The synodic period is the time interval between two successive conjunctions or oppositions of
                        two celestial bodies. It is assumed that the planetary orbits are circular to simplify the
                        calculations.`
                }
            }>

            {/* INPUT */}

            <form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <InputField
                    name="departurePlanet"
                    label="Departure Planet"
                    type="select"
                    value={formIn.departurePlanet}
                    onChange={handleChange}
                    options={
                        [
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
                    name="arrivalPlanet"
                    label="Arrival Planet"
                    type="select"
                    value={formIn.arrivalPlanet}
                    onChange={handleChange}
                    options={
                        [
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

                {
                    errors.planets &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.planets}</span>
                }

            </form.Root>

            {/* OUTPUT */}

            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <OutputField label="Synodic Period" unit="DAYS" value={formOut.synodicPeriod} />

                <OutputField label="Initial Phase Angle" unit="DEG" value={formOut.initialPhaseAngle} />

                <OutputField label="Final Phase Angle" unit="DEG" value={formOut.finalPhaseAngle} />

                <OutputField label="Wait Time" unit="DAYS" value={formOut.waitTime} />

            </form.Root>

        </DialogRUI>
    )
}