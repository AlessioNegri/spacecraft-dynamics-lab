import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"
import ErrorText from "@renderer/components/dialogs/ErrorText"

interface IFormIn
{
    departurePlanet: string
    arrivalPlanet: string
    departureParkingOrbitHeight: number
    arrivalParkingOrbitHeight: number
}

interface IHyperbola
{
    specificAngularMomentum: number
    eccentricity: number
    periapsisRadius: number
    asymptoteAngle: number
    turningAngle: number
    aimingRadius: number
    specificEnergy: number
    hyperbolicExcessSpeed: number
    characteristicEnergy: number
    timeOfFlight: number
}

interface IFormOut
{
    departureDeltaV: number
    departureHyperbola: IHyperbola
    arrivalDeltaV: number
    arrivalHyperbola: IHyperbola
}

const defaultIn: IFormIn =
{
    departurePlanet: "earth",
    arrivalPlanet: "mars",
    departureParkingOrbitHeight: 300,
    arrivalParkingOrbitHeight: 180
}

const defaultHyperbola: IHyperbola =
{
    specificAngularMomentum: 0,
    eccentricity: 0,
    periapsisRadius: 0,
    asymptoteAngle: 0,
    turningAngle: 0,
    aimingRadius: 0,
    specificEnergy: 0,
    hyperbolicExcessSpeed: 0,
    characteristicEnergy: 0,
    timeOfFlight: 0
}

const defaultOut: IFormOut =
{
    departureDeltaV: 0,
    departureHyperbola: defaultHyperbola,
    arrivalDeltaV: 0,
    arrivalHyperbola: defaultHyperbola
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

    const handleChange = (e: react.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
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
            let response: any = await http.api.put(`/interplanetary/transfer`, formIn)

            const data = response.data

            const result: IFormOut = {
                departureDeltaV: data.departureDeltaV ?? 0,
                departureHyperbola: {
                    specificAngularMomentum: data.departureHyperbola?.specificAngularMomentum ?? 0,
                    eccentricity: data.departureHyperbola?.eccentricity ?? 0,
                    periapsisRadius: data.departureHyperbola?.periapsisRadius ?? 0,
                    asymptoteAngle: data.departureHyperbola?.asymptoteAngle ?? 0,
                    turningAngle: data.departureHyperbola?.turningAngle ?? 0,
                    aimingRadius: data.departureHyperbola?.aimingRadius ?? 0,
                    specificEnergy: data.departureHyperbola?.specificEnergy ?? 0,
                    hyperbolicExcessSpeed: data.departureHyperbola?.hyperbolicExcessSpeed ?? 0,
                    characteristicEnergy: data.departureHyperbola?.characteristicEnergy ?? 0,
                    timeOfFlight: data.departureHyperbola?.timeOfFlight ?? 0
                },
                arrivalDeltaV: data.arrivalDeltaV ?? 0,
                arrivalHyperbola: {
                    specificAngularMomentum: data.arrivalHyperbola?.specificAngularMomentum ?? 0,
                    eccentricity: data.arrivalHyperbola?.eccentricity ?? 0,
                    periapsisRadius: data.arrivalHyperbola?.periapsisRadius ?? 0,
                    asymptoteAngle: data.arrivalHyperbola?.asymptoteAngle ?? 0,
                    turningAngle: data.arrivalHyperbola?.turningAngle ?? 0,
                    aimingRadius: data.arrivalHyperbola?.aimingRadius ?? 0,
                    specificEnergy: data.arrivalHyperbola?.specificEnergy ?? 0,
                    hyperbolicExcessSpeed: data.arrivalHyperbola?.hyperbolicExcessSpeed ?? 0,
                    characteristicEnergy: data.arrivalHyperbola?.characteristicEnergy ?? 0,
                    timeOfFlight: data.arrivalHyperbola?.timeOfFlight ?? 0
                }
            }

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
                        compute the departure and rendezvous for interplanetary trajectories.`
                }
            }>

            {/* INPUT */}

            <Form.Root
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

                <span></span>

                <InputField
                    type="number"
                    name="departureParkingOrbitHeight"
                    label="Departure Parking Orbit Height"
                    symbol="H_{D}"
                    unit="km"
                    value={String(formIn.departureParkingOrbitHeight)}
                    onChange={handleChange}
                    min={1}
                />

                <InputField
                    type="number"
                    name="arrivalParkingOrbitHeight"
                    label="Arrival Parking Orbit Height"
                    symbol="H_{A}"
                    unit="km"
                    value={String(formIn.arrivalParkingOrbitHeight)}
                    onChange={handleChange}
                    min={1}
                />

                { errors.planets && <ErrorText text={errors.planets} /> }

            </Form.Root>

            {/* OUTPUT */}

            <Form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Departure</span>

                <OutputField
                    label="Delta Velocity"
                    symbol="\Delta v"
                    unit="km / s"
                    value={formOut.departureDeltaV}
                />

                <OutputField
                    label="Specific Angular Momentum"
                    symbol="h"
                    unit="km^2 / s"
                    value={formOut.departureHyperbola.specificAngularMomentum}
                />

                <OutputField
                    label="Eccentricity"
                    symbol="e"
                    value={formOut.departureHyperbola.eccentricity}
                />

                <OutputField
                    label="Periapsis Radius"
                    symbol="r_p"
                    unit="km"
                    value={formOut.departureHyperbola.periapsisRadius}
                />

                <OutputField
                    label="Asymptote Angle"
                    symbol="\beta"
                    unit="deg"
                    value={formOut.departureHyperbola.asymptoteAngle}
                />

                <OutputField
                    label="Turning Angle"
                    symbol="\delta"
                    unit="deg"
                    value={formOut.departureHyperbola.turningAngle}
                />

                <OutputField
                    label="Aiming Radius"
                    symbol="\Delta"
                    unit="km"
                    value={formOut.departureHyperbola.aimingRadius}
                />

                <OutputField
                    label="Specific Energy"
                    symbol="\varepsilon"
                    unit="km^2 / s^2"
                    value={formOut.departureHyperbola.specificEnergy}
                />

                <OutputField
                    label="Hyperbolic Excess Speed"
                    symbol="v_\infty"
                    unit="km / s"
                    value={formOut.departureHyperbola.hyperbolicExcessSpeed}
                />

                <OutputField
                    label="Characteristic Energy"
                    symbol="C_3"
                    unit="km^2 / s^2"
                    value={formOut.departureHyperbola.characteristicEnergy}
                />

                <OutputField
                    label="Time Of Flight"
                    symbol="TOF"
                    unit="day"
                    value={formOut.departureHyperbola.timeOfFlight}
                />

                <span className="col-span-3 text-center uppercase font-semibold">Arrival</span>

                <OutputField
                    label="Delta Velocity"
                    symbol="\Delta v"
                    unit="km / s"
                    value={formOut.arrivalDeltaV}
                />

                <OutputField
                    label="Specific Angular Momentum"
                    symbol="h"
                    unit="km^2 / s"
                    value={formOut.arrivalHyperbola.specificAngularMomentum}
                />

                <OutputField
                    label="Eccentricity"
                    symbol="e"
                    value={formOut.arrivalHyperbola.eccentricity}
                />

                <OutputField
                    label="Periapsis Radius"
                    symbol="r_p"
                    unit="km"
                    value={formOut.arrivalHyperbola.periapsisRadius}
                />

                <OutputField
                    label="Asymptote Angle"
                    symbol="\beta"
                    unit="deg"
                    value={formOut.arrivalHyperbola.asymptoteAngle}
                />

                <OutputField
                    label="Turning Angle"
                    symbol="\delta"
                    unit="deg"
                    value={formOut.arrivalHyperbola.turningAngle}
                />

                <OutputField
                    label="Aiming Radius"
                    symbol="\Delta"
                    unit="km"
                    value={formOut.arrivalHyperbola.aimingRadius}
                />

                <OutputField
                    label="Specific Energy"
                    symbol="\epsilon"
                    unit="km^2 / s^2"
                    value={formOut.arrivalHyperbola.specificEnergy}
                />

                <OutputField
                    label="Hyperbolic Excess Speed"
                    symbol="v_\infty"
                    unit="km / s"
                    value={formOut.arrivalHyperbola.hyperbolicExcessSpeed}
                />

                <OutputField
                    label="Characteristic Energy"
                    symbol="C_3"
                    unit="km^2 / s^2"
                    value={formOut.arrivalHyperbola.characteristicEnergy}
                />

                <OutputField
                    label="Time Of Flight"
                    symbol="TOF"
                    unit="day"
                    value={formOut.arrivalHyperbola.timeOfFlight}
                />

            </Form.Root>

        </DialogRUI>
    )
}
