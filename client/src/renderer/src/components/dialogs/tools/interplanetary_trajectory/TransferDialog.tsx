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
    departureParkingOrbitHeight: number
    arrivalOrbitalPeriod: number
}

interface IFormOut
{
    departureDeltaV: number
    departureHyperbolaEccentricity: number
    departureHyperbolaAsymptoteAngle: number
    arrivalDeltaV: number
    arrivalHyperbolaEccentricity: number
    arrivalHyperbolaAsymptoteAngle: number
}

const defaultIn: IFormIn =
{
    departurePlanet: "earth",
    arrivalPlanet: "mars",
    departureParkingOrbitHeight: 300,
    arrivalOrbitalPeriod: 7
}

const defaultOut: IFormOut =
{
    departureDeltaV: 0,
    departureHyperbolaEccentricity: 0,
    departureHyperbolaAsymptoteAngle: 0,
    arrivalDeltaV: 0,
    arrivalHyperbolaEccentricity: 0,
    arrivalHyperbolaAsymptoteAngle: 0
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function TransferDialog */
export default function TransferDialog(props: Readonly<Props>): react.JSX.Element
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
            let response: any = await http.api.put(`/tools/transfer`, formIn)

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
            title="Transfer"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Transfer",
                    content:
                        `With the assumption of circular coplanar planetary orbits, the users can
                        compute the departure, rendezvous (with optimal periapse radius), and flyby parameters for
                        interplanetary trajectories.`
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

                <InputField
                    name="departureParkingOrbitHeight"
                    label="Departure Parking Orbit Height"
                    unit="KM"
                    value={String(formIn.departureParkingOrbitHeight)}
                    onChange={handleChange}
                />

                <InputField
                    name="arrivalOrbitalPeriod"
                    label="Arrival Orbital Period"
                    unit="HOURS"
                    value={String(formIn.arrivalOrbitalPeriod)}
                    onChange={handleChange}
                />

                {
                    errors.planets &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.planets}</span>
                }

            </form.Root>

            {/* OUTPUT */}

            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Departure</span>

                <OutputField label="Delta-V" unit="KM / S" value={formOut.departureDeltaV} />

                <OutputField label="Hyperbola Eccentricity" value={formOut.departureHyperbolaEccentricity} />

                <OutputField label="Hyperbola Asymptote Angle" unit="DEG" value={formOut.departureHyperbolaAsymptoteAngle} />

                <span className="col-span-3 text-center uppercase font-semibold">Arrival</span>

                <OutputField label="Delta-V" unit="KM / S" value={formOut.arrivalDeltaV} />

                <OutputField label="Hyperbola Eccentricity" value={formOut.arrivalHyperbolaEccentricity} />

                <OutputField label="Hyperbola Asymptote Angle" unit="DEG" value={formOut.arrivalHyperbolaAsymptoteAngle} />

            </form.Root>

        </DialogRUI>
    )
}