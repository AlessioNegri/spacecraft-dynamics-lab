import * as react from "react"
import * as form from "@radix-ui/react-form"

import http from "@renderer/common/http"
import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

interface IFormIn
{
    attractor: string
    position: IVector3D
    velocity: IVector3D
}

interface IFormOut
{
    conicType: string
    specificAngularMomentum: number
    specificMechanicalEnergy: number
    eccentricity: number
    orbitalPeriod: number
    apoapsisRadius: number
    periapsisRadius: number
    semiMajorAxis: number
    semiMinorAxis: number
    escapeVelocity: number
    infiniteTrueAnomaly: number
    hyperbolaAsymptoteAngle: number
    turnAngle: number
    aimingRadius: number
    hyperbolicExcessSpeed: number
    characteristicEnergy: number
    rightAscension: number
    declination: number
}

const defaultIn: IFormIn =
{
    attractor: "earth",
    position: { x: 8000, y: 0, z: 6000 },
    velocity: { x: 0, y: 7, z: 0 }
}

const defaultOut: IFormOut =
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
    characteristicEnergy: 0,
    rightAscension: 0,
    declination: 0
}

interface CartesianOrbitParametersDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function CartesianOrbitParametersDialog */
export default function CartesianOrbitParametersDialog(props: Readonly<CartesianOrbitParametersDialogProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    const [_, setAxiosError] = react.useState<string>("")

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const validate = () : boolean =>
    {
        const newErrors: Record<string, string> = {}

        if (formIn.position.x == 0 && formIn.position.y == 0 && formIn.position.z == 0)
        {
            newErrors.position = "Position cannot be [0,0,0]"
        }

        if (formIn.velocity.x == 0 && formIn.velocity.y == 0 && formIn.velocity.z == 0)
        {
            newErrors.velocity = "Velocity cannot be [0,0,0]"
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        if (name.includes("."))
        {
            const [ group, axis ] = name.split(".")
    
            setFormIn({ ...formIn, [group]: { ...formIn[group], [axis]: value } })

            return
        }

        setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        if (!validate()) return

        try
        {
            let response: any = await http.api.put(`/tools/convert-cartesian-to-orbit-parameters`, formIn)

            const result: IFormOut = response.data

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
        <DialogRUI
            title="Cartesian → Orbit Parameters"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Cartesian → Orbit Parameters",
                    content:
                        `Given an orbit state vector (position vector & velocity vector) in Geocentric Equatorial
                        frame, it extracts the orbital parameters.`
                }
            }>

            {/* INPUT */}

            <form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <InputField
                    name="attractor"
                    label="Attractor"
                    type="select"
                    value={formIn.attractor}
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
                
                <span className="col-span-3 text-center uppercase font-semibold">Position Vector</span>

                <InputField
                    name="position.x"
                    label="X"
                    unit="KM"
                    value={formIn.position.x}
                    onChange={handleChange}
                />

                <InputField
                    name="position.y"
                    label="Y"
                    unit="KM"
                    value={formIn.position.y}
                    onChange={handleChange}
                />

                <InputField
                    name="position.z"
                    label="Z"
                    unit="KM"
                    value={formIn.position.z}
                    onChange={handleChange}
                />

                {
                    errors.position &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.position}</span>
                }

                <span className="col-span-3 text-center uppercase font-semibold">Velocity Vector</span>

                <InputField
                    name="velocity.x"
                    label="X"
                    unit="KM"
                    value={formIn.velocity.x}
                    onChange={handleChange}
                />

                <InputField
                    name="velocity.y"
                    label="Y"
                    unit="KM"
                    value={formIn.velocity.y}
                    onChange={handleChange}
                />

                <InputField
                    name="velocity.z"
                    label="Z"
                    unit="KM"
                    value={formIn.velocity.z}
                    onChange={handleChange}
                />

                {
                    errors.velocity &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.velocity}</span>
                }

            </form.Root>

            {/* OUTPUT */}
            
            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Orbital Parameters</span>

                <OutputField
                    label="Conic Type"
                    value={formOut.conicType}
                />

                <OutputField
                    label="Angular Momentum"
                    unit="KM^2 / S"
                    value={formOut.specificAngularMomentum}
                />

                <OutputField
                    label="Mechanical Energy"
                    unit="KM^2 / S^2"
                    value={formOut.specificMechanicalEnergy}
                />

                <OutputField
                    label="Eccentricity"
                    value={formOut.eccentricity}
                />

                <OutputField
                    label="Orbital Period"
                    unit="S"
                    value={formOut.orbitalPeriod}
                />

                <OutputField
                    label="Apoapsis Radius"
                    unit="KM"
                    value={formOut.apoapsisRadius}
                />

                <OutputField
                    label="Periapsis Radius"
                    unit="KM"
                    value={formOut.periapsisRadius}
                />

                <OutputField
                    label="Semi-Major Axis"
                    unit="KM"
                    value={formOut.semiMajorAxis}
                />

                <OutputField
                    label="Semi-Minor Axis"
                    unit="KM"
                    value={formOut.semiMinorAxis}
                />

                <OutputField
                    label="Escape Velocity"
                    unit="KM / S"
                    value={formOut.escapeVelocity}
                    disabled={formOut.eccentricity < 1}
                />

                <OutputField
                    label="Infinite True Anomaly"
                    unit="DEG"
                    value={formOut.infiniteTrueAnomaly}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Hyperbola Asymptote Angle"
                    unit="DEG"
                    value={formOut.hyperbolaAsymptoteAngle}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Turn Angle"
                    unit="DEG"
                    value={formOut.turnAngle}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Aiming Radius"
                    unit="KM"
                    value={formOut.aimingRadius}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Hyperbolic Excess Speed"
                    unit="KM / S"
                    value={formOut.hyperbolicExcessSpeed}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Characteristics Energy"
                    unit="KM^2 / S^2"
                    value={formOut.characteristicEnergy}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Right Ascension"
                    unit="DEG"
                    value={formOut.rightAscension}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Declination"
                    unit="DEG"
                    value={formOut.declination}
                    disabled={formOut.eccentricity <= 1}
                />

            </form.Root>

        </DialogRUI>
    )
}