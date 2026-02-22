import * as react from "react"

import http from "@renderer/common/http"

import Dialog from "./Dialog"
import FormButton from "./FormButton"
import FormSection from "./FormSection"
import FormInput from "./FormInput"
import FormSelect from "./FormSelect"

const defaultIn: ICartesianOrbitParametersFormIn =
{
    attractor: "earth",
    positionX: 8000,
    positionY: 0,
    positionZ: 6000,
    velocityX: 0,
    velocityY: 7,
    velocityZ: 0
}

const defaultOut: ICartesianOrbitParametersFormOut =
{
    conicType: "",
    specificAngularMomentum: 0,
    specificMechanicalEnergy: 0,
    eccentricity: 0,
    orbitalPeriod: 0,
    apoapsisRadius: 0,
    periapsisRadius: 0,
    semiMajorAxis: 0,
    semiMinorAxis: 0,
    escapeVelocity: 0,
    infiniteTrueAnomaly: 0,
    hyperbolaAsymptoteAngle: 0,
    turnAngle: 0,
    aimingRadius: 0,
    hyperbolicExcessSpeed: 0,
    characteristicEnergy: 0
}

interface CartesianToOrbitParametersDialogProps
{
    onClose: () => void
    onOk: () => void
}

/** @function DeleteSpacecraftDialog */
export default function CartesianToOrbitParametersDialog(props: Readonly<CartesianToOrbitParametersDialogProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<ICartesianOrbitParametersFormIn>(defaultIn)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    const [formOut, setFormOut] = react.useState<ICartesianOrbitParametersFormOut>(defaultOut)

    const [axiosError, setAxiosError] = react.useState<string>("")

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        setFormIn(defaultIn)
        setFormOut(defaultOut)
    }, [])

    // --- HANDLE ---

    const validate = () =>
    {
        const newErrors: Record<string, string> = {}

        if (!String(formIn.positionX).trim()) newErrors.positionX = "Position X is required"
        if (!String(formIn.positionY).trim()) newErrors.positionY = "Position Y is required"
        if (!String(formIn.positionZ).trim()) newErrors.positionZ = "Position Z is required"

        if (!String(formIn.velocityX).trim()) newErrors.velocityX = "Velocity X is required"
        if (!String(formIn.velocityY).trim()) newErrors.velocityY = "Velocity Y is required"
        if (!String(formIn.velocityZ).trim()) newErrors.velocityZ = "Velocity Z is required"

        if (formIn.positionX == 0 && formIn.positionY == 0 && formIn.positionZ == 0)
        {
            newErrors.positionX = newErrors.positionY = newErrors.positionZ = "Position cannot be 0"
        }

        if (formIn.velocityX == 0 && formIn.velocityY == 0 && formIn.velocityZ == 0)
        {
            newErrors.velocityX = newErrors.velocityY = newErrors.velocityZ = "Velocity cannot be 0"
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setFormIn({ ...formIn, [name]: value })
    }

    const handleConvert = async (e: React.FormEvent) =>
    {
        e.preventDefault()

        setAxiosError("")

        if (!validate()) return

        const data = new FormData()

        data.append("attractor", formIn.attractor)

        data.append("positionX", String(formIn.positionX))
        data.append("positionY", String(formIn.positionY))
        data.append("positionZ", String(formIn.positionZ))

        data.append("velocityX", String(formIn.velocityX))
        data.append("velocityY", String(formIn.velocityY))
        data.append("velocityZ", String(formIn.velocityZ))

        try
        {
            let response: any = await http.api.put(`/tools/convert-cartesian-to-orbit-parameters`, data)

            const result: ICartesianOrbitParametersFormOut =
            {
                conicType:                  response.data["conicType"],
                specificAngularMomentum:    response.data["specificAngularMomentum"],
                specificMechanicalEnergy:   response.data["specificMechanicalEnergy"],
                eccentricity:               response.data["eccentricity"],
                orbitalPeriod:              response.data["orbitalPeriod"],
                apoapsisRadius:             response.data["apoapsisRadius"],
                periapsisRadius:            response.data["periapsisRadius"],
                semiMajorAxis:              response.data["semiMajorAxis"],
                semiMinorAxis:              response.data["semiMinorAxis"],
                escapeVelocity:             response.data["escapeVelocity"],
                infiniteTrueAnomaly:        response.data["infiniteTrueAnomaly"],
                hyperbolaAsymptoteAngle:    response.data["hyperbolaAsymptoteAngle"],
                turnAngle:                  response.data["turnAngle"],
                aimingRadius:               response.data["aimingRadius"],
                hyperbolicExcessSpeed:      response.data["hyperbolicExcessSpeed"],
                characteristicEnergy:       response.data["characteristicEnergy"]
            }

            setFormOut(result)
        }
        catch (err)
        {
            const message: string | null = http.checkError(import.meta.url, err)

            if (message) setAxiosError(message)
        }
    }

    // --- RENDERING ---

    return (
        <Dialog title={`Cartesian → Orbit Parameters`} onClose={() => { props.onClose() }} >

            <form
                id="conversion-form"
                onSubmit={handleConvert}
                className="mx-auto p-6 bg-neutral-800 text-neutral-100 rounded-lg shadow-lg space-y-6 overflow-auto
                            max-h-[80vh] custom-scrollbar">

                <FormSelect
                    label="Attractor"
                    name="attractor"
                    value={formIn.attractor}
                    setValue={handleChange}
                    options={
                        [
                            { name: "Mercury", value: "mercury" },
                            { name: "Venus", value: "venus" },
                            { name: "Earth", value: "earth" },
                            { name: "Mars", value: "mars" },
                            { name: "Jupiter", value: "jupiter" },
                            { name: "Saturn", value: "saturn" },
                            { name: "Uranus", value: "uranus" },
                            { name: "Neptune", value: "neptune" }
                        ]}
                />

                <FormSection title="Position Vector" className="grid grid-cols-3 space-x-4 mt-4">

                    <FormInput
                        label="Position X"
                        type="number"
                        name="positionX"
                        value={formIn.positionX}
                        error={errors.positionX}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="Position Y"
                        type="number"
                        name="positionY"
                        value={formIn.positionY}
                        error={errors.positionY}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="Position Z"
                        type="number"
                        name="positionZ"
                        value={formIn.positionZ}
                        error={errors.positionZ}
                        setValue={handleChange}
                    />

                </FormSection>

                <FormSection title="Velocity Vector" className="grid grid-cols-3 space-x-4">

                    <FormInput
                        label="Velocity X"
                        type="number"
                        name="velocityX"
                        value={formIn.velocityX}
                        error={errors.velocityX}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="Velocity Y"
                        type="number"
                        name="velocityY"
                        value={formIn.velocityY}
                        error={errors.velocityY}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="Velocity Z"
                        type="number"
                        name="velocityZ"
                        value={formIn.velocityZ}
                        error={errors.velocityZ}
                        setValue={handleChange}
                    />

                </FormSection>

                <p className="border-b-2 border-neutral-300"></p>

                <FormSection title="Orbit Parameters" className="grid grid-cols-2 space-x-4 space-y-4">

                    <FormInput
                        label="Conic Type"
                        type="text"
                        readonly={true}
                        value={formOut.conicType}
                    />

                    <FormInput
                        label="Specific Angular Momentum [ km^2 / s ]"
                        type="number"
                        readonly={true}
                        value={formOut.specificAngularMomentum}
                    />

                    <FormInput
                        label="Specific Mechanical Energy [ km^2 / s^2 ]"
                        type="number"
                        readonly={true}
                        value={formOut.specificMechanicalEnergy}
                    />

                    <FormInput
                        label="Eccentricity"
                        type="number"
                        readonly={true}
                        value={formOut.eccentricity}
                    />

                    <FormInput
                        label="Orbital Period [ s ]"
                        type="number"
                        readonly={true}
                        value={formOut.orbitalPeriod}
                    />

                    <FormInput
                        label="Apoapsis Radius [ km ]"
                        type="number"
                        readonly={true}
                        value={formOut.apoapsisRadius}
                    />

                    <FormInput
                        label="Periapsis Radius [ km ]"
                        type="number"
                        readonly={true}
                        value={formOut.periapsisRadius}
                    />

                    <FormInput
                        label="Semi-Major Axis [ km ]"
                        type="number"
                        readonly={true}
                        value={formOut.semiMajorAxis}
                    />

                    <FormInput
                        label="Semi-Minor Axis [ km ]"
                        type="number"
                        readonly={true}
                        value={formOut.semiMinorAxis}
                    />

                    <FormInput
                        label="Escape Velocity [ km / s ]"
                        type="number"
                        readonly={true}
                        disable={formOut.eccentricity < 1}
                        value={formOut.escapeVelocity}
                    />

                    <FormInput
                        label="Infinite True Anomaly [ rad ]"
                        type="number"
                        readonly={true}
                        disable={formOut.eccentricity <= 1}
                        value={formOut.infiniteTrueAnomaly}
                    />

                    <FormInput
                        label="Hyperbola Asymptote Angle [ deg ]"
                        type="number"
                        readonly={true}
                        disable={formOut.eccentricity <= 1}
                        value={formOut.hyperbolaAsymptoteAngle}
                    />

                    <FormInput
                        label="Turn Angle [ deg ]"
                        type="number"
                        readonly={true}
                        disable={formOut.eccentricity <= 1}
                        value={formOut.turnAngle}
                    />

                    <FormInput
                        label="Aiming Radius [ km ]"
                        type="number"
                        readonly={true}
                        disable={formOut.eccentricity <= 1}
                        value={formOut.aimingRadius}
                    />

                    <FormInput
                        label="Hyperbolic Excess Speed [ km / s ]"
                        type="number"
                        readonly={true}
                        disable={formOut.eccentricity <= 1}
                        value={formOut.hyperbolicExcessSpeed}
                    />

                    <FormInput
                        label="Characteristic Energy [ km^2 / s^2 ]"
                        type="number"
                        readonly={true}
                        disable={formOut.eccentricity <= 1}
                        value={formOut.characteristicEnergy}
                    />

                    <span></span>

                </FormSection>

            </form>

            <div className="flex justify-center">
            
                <FormButton text="Convert" color="blue" type="submit" form="conversion-form" onClick={() => {}} />

            </div>

            {
                axiosError && <p className="text-red-400 text-sm select-text">{axiosError}</p>
            }

        </Dialog>
    )
}