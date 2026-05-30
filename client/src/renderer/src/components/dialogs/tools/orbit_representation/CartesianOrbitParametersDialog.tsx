import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"
import ErrorText from "@renderer/components/dialogs/ErrorText"

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

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function CartesianOrbitParametersDialog */
export default function CartesianOrbitParametersDialog(props: Readonly<Props>): react.JSX.Element
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
            http.checkError(import.meta.url, err)
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
                        `Given an orbit state vector (position vector & velocity vector) in an Inertial Reference Frame,
                        it extracts the orbital parameters.`
                }
            }>

            {/* INPUT */}

            <Form.Root
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

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Position Vector</span>

                    <InputField
                        name="position.x"
                        symbol="r_x"
                        unit="km"
                        value={formIn.position.x}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position.y"
                        symbol="r_y"
                        unit="km"
                        value={formIn.position.y}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position.z"
                        symbol="r_z"
                        unit="km"
                        value={formIn.position.z}
                        onChange={handleChange}
                    />

                    { errors.position && <ErrorText text={errors.position} /> }

                </div>

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Velocity Vector</span>

                    <InputField
                        name="velocity.x"
                        symbol="v_x"
                        unit="km/s"
                        value={formIn.velocity.x}
                        onChange={handleChange}
                    />

                    <InputField
                        name="velocity.y"
                        symbol="v_y"
                        unit="km/s"
                        value={formIn.velocity.y}
                        onChange={handleChange}
                    />

                    <InputField
                        name="velocity.z"
                        symbol="v_z"
                        unit="km/s"
                        value={formIn.velocity.z}
                        onChange={handleChange}
                    />

                    { errors.velocity && <ErrorText text={errors.velocity} /> }

                </div>

            </Form.Root>

            {/* OUTPUT */}
            
            <Form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Orbital Parameters</span>

                <OutputField
                    label="Conic Type"
                    value={formOut.conicType}
                />

                <OutputField
                    label="Specific Angular Momentum"
                    symbol="h"
                    unit="km^2 / s"
                    value={formOut.specificAngularMomentum}
                />

                <OutputField
                    label="Specific Mechanical Energy"
                    symbol="\varepsilon"
                    unit="km^2 / s^2"
                    value={formOut.specificMechanicalEnergy}
                />

                <OutputField
                    label="Eccentricity"
                    symbol="e"
                    value={formOut.eccentricity}
                />

                <OutputField
                    label="Orbital Period"
                    symbol="T"
                    unit="s"
                    value={formOut.orbitalPeriod}
                />

                <OutputField
                    label="Apoapsis Radius"
                    symbol="r_a"
                    unit="km"
                    value={formOut.apoapsisRadius}
                />

                <OutputField
                    label="Periapsis Radius"
                    symbol="r_p"
                    unit="km"
                    value={formOut.periapsisRadius}
                />

                <OutputField
                    label="Semimajor Axis"
                    symbol="a"
                    unit="km"
                    value={formOut.semiMajorAxis}
                />

                <OutputField
                    label="Semiminor Axis"
                    symbol="b"
                    unit="km"
                    value={formOut.semiMinorAxis}
                />

                <OutputField
                    label="Escape Velocity"
                    symbol="v_{esc}"
                    unit="km / s"
                    value={formOut.escapeVelocity}
                    disabled={formOut.eccentricity < 1}
                />

                <OutputField
                    label="Asymptotic True Anomaly"
                    symbol="\theta_\infty"
                    unit="deg"
                    value={formOut.infiniteTrueAnomaly}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Asymptote Angle"
                    symbol="\beta"
                    unit="deg"
                    value={formOut.hyperbolaAsymptoteAngle}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Turn Angle"
                    symbol="\delta"
                    unit="deg"
                    value={formOut.turnAngle}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Aiming Radius"
                    symbol="\Delta"
                    unit="km"
                    value={formOut.aimingRadius}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Hyperbolic Excess Speed"
                    symbol="v_{\infty}"
                    unit="km / s"
                    value={formOut.hyperbolicExcessSpeed}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Characteristics Energy"
                    symbol="C_3"
                    unit="km^2 / s^2"
                    value={formOut.characteristicEnergy}
                    disabled={formOut.eccentricity <= 1}
                />

                <OutputField
                    label="Right Ascension"
                    symbol="\alpha"
                    unit="deg"
                    value={formOut.rightAscension}
                />

                <OutputField
                    label="Declination"
                    symbol="\delta"
                    unit="deg"
                    value={formOut.declination}
                />

            </Form.Root>

        </DialogRUI>
    )
}
