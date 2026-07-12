import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

const defaultInCoplanar: IToolsCoplanarCircleCircleFormInput =
{
    attractor: "earth",
    spacecraft:
    {
        mass: 2500,
        specificImpulse: 1700,
        thrust: 0.6
    },
    initialRadius: 6678,
    finalRadius: 42161,
    earthShadow: false
}

const defaultInInclined: IToolsInclinationChangeInModelInfo =
{
    attractor: "earth",
    spacecraft:
    {
        mass: 2500,
        specificImpulse: 1700,
        thrust: 0.6
    },
    radius: 10000,
    initialInclination: 0,
    finalInclination: 20
}

const defaultInCoplanarInclined: IToolsInclinedCircularOrbitsInModelInfo =
{
    attractor: "earth",
    spacecraft:
    {
        mass: 2500,
        specificImpulse: 1700,
        thrust: 0.6
    },
    initialRadius: 6678,
    finalRadius: 42161,
    initialInclination: 28.5,
    finalInclination: 0
}

const defaultOut: INonImpulsiveFormOut =
{
    timeOfFlight: 0,
    propellantMass: 0,
    deltaVelocity: 0
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function NonImpulsiveManeuversDialog */
export default function NonImpulsiveManeuversDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formInCoplanar, setFormInCoplanar] = react.useState<IToolsCoplanarCircleCircleFormInput>(defaultInCoplanar)

    const [formOutCoplanar, setFormOutCoplanar] = react.useState<INonImpulsiveFormOut>(defaultOut)

    const [formInInclined, setFormInInclined] = react.useState<IToolsInclinationChangeInModelInfo>(defaultInInclined)

    const [formOutInclined, setFormOutInclined] = react.useState<INonImpulsiveFormOut>(defaultOut)

    const [formInCoplanarInclined, setFormInCoplanarInclined] = react.useState<IToolsInclinedCircularOrbitsInModelInfo>(defaultInCoplanarInclined)

    const [formOutCoplanarInclined, setFormOutCoplanarInclined] = react.useState<INonImpulsiveFormOut>(defaultOut)

    const [maneuver, setManeuver] = react.useState<string>("coplanar-circle-circle")

    // --- USE REF ---

    const formRefCoplanar = react.useRef<HTMLFormElement>(null)
    
    const formRefInclined = react.useRef<HTMLFormElement>(null)

    const formRefCoplanarInclined = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        if (name.includes("."))
        {
            const [group, axis] = name.split(".")

            maneuvers[maneuver].setFormIn(prev => ({ ...prev, [group]: { ...prev[group], [axis]: value } }))
            
            return
        }

        maneuvers[maneuver].setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.put(`/orbital-maneuvers/tools/${maneuver}`, maneuvers[maneuver].formIn)

            const result: INonImpulsiveFormOut = response.data

            maneuvers[maneuver].setFormOut(result)
        }
        catch (err)
        {
            console.error(err)
        }
    }

    // --- RENDERING ---

    const maneuvers =
    {
        "coplanar-circle-circle":
        {
            formIn: formInCoplanar,
            setFormIn: setFormInCoplanar,
            formOut: formOutCoplanar,
            setFormOut: setFormOutCoplanar,
            submit: handleSubmit,
            ref: formRefCoplanar
        },
        "inclination-change":
        {
            formIn: formInInclined,
            setFormIn: setFormInInclined,
            formOut: formOutInclined,
            setFormOut: setFormOutInclined,
            submit: handleSubmit,
            ref: formRefInclined
        },
        "inclined-circular-orbits":
        {
            formIn: formInCoplanarInclined,
            setFormIn: setFormInCoplanarInclined,
            formOut: formOutCoplanarInclined,
            setFormOut: setFormOutCoplanarInclined,
            submit: handleSubmit,
            ref: formRefCoplanarInclined
        }
    }

    const active = maneuvers[maneuver]

    return (
        <DialogRUI
            title="Non-Impulsive Maneuvers"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => maneuvers[maneuver].ref.current?.requestSubmit()}
            popup={
                {
                    title: "Non-Impulsive Maneuvers",
                    content:
                        `Compute non-impulsive maneuvers, including coplanar circle-to-circle transfers, inclination
                        changes, and transfers between inclined circular orbits.`,
                }
            }
        >

            {/* Maneuver */}

            <Form.Root className="border-b pb-4 mb-4">

                <InputField
                    name="maneuver"
                    label="Maneuver"
                    type="select"
                    value={maneuver}
                    onChange={ e => setManeuver(e.target.value) }
                    options={
                        [
                            { label: "Coplanar Circle-to-Circle", value: "coplanar-circle-circle" },
                            { label: "Inclination Change", value: "inclination-change" },
                            { label: "Inclined Circular Orbits", value: "inclined-circular-orbits" }
                        ]}
                />

            </Form.Root>

            {/* Input */}

            {
                maneuver === "coplanar-circle-circle" &&
                <CoplanarCircleCircle
                    formIn={active.formIn}
                    setFormIn={active.setFormIn}
                    formOut={active.formOut}
                    setFormOut={active.setFormOut}
                    submit={active.submit}
                    ref={active.ref}
                    onChange={handleChange}
                />
            }

            {
                maneuver === "inclination-change" &&
                <InclinationChange
                    formIn={active.formIn}
                    setFormIn={active.setFormIn}
                    formOut={active.formOut}
                    setFormOut={active.setFormOut}
                    submit={active.submit}
                    ref={active.ref}
                    onChange={handleChange}
                />
            }

            {
                maneuver === "inclined-circular-orbits" &&
                <InclinedCircularOrbits
                    formIn={active.formIn}
                    setFormIn={active.setFormIn}
                    formOut={active.formOut}
                    setFormOut={active.setFormOut}
                    submit={active.submit}
                    ref={active.ref}
                    onChange={handleChange}
                />
            }

            {/* Output */}

            <Form.Root className="grid grid-cols-2 gap-4 mb-4">

                <OutputField
                    label="Time of Flight"
                    symbol="TOF"
                    unit="s"
                    value={maneuvers[maneuver].formOut.timeOfFlight / 86400}
                    maximumFractionDigits={3}
                />

                <OutputField
                    label="Propellant Mass"
                    symbol="m_p"
                    unit="kg"
                    value={maneuvers[maneuver].formOut.propellantMass}
                    maximumFractionDigits={3}
                />

                <OutputField
                    label="Delta Velocity"
                    symbol="Δv"
                    unit="km/s"
                    value={maneuvers[maneuver].formOut.deltaVelocity}
                    maximumFractionDigits={3}
                />

            </Form.Root>

        </DialogRUI>
    )
}

// ---------------------------------------------------------------------------------------------------------------------

interface CoplanarCircleCircleProps
{
    formIn: IToolsCoplanarCircleCircleFormInput
    setFormIn: React.Dispatch<React.SetStateAction<IToolsCoplanarCircleCircleFormInput>>
    formOut: INonImpulsiveFormOut
    setFormOut: React.Dispatch<React.SetStateAction<INonImpulsiveFormOut>>
    submit: (e: React.FormEvent) => void
    ref: React.RefObject<HTMLFormElement>
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
}

/** @function CoplanarCircleCircle */
function CoplanarCircleCircle(props: Readonly<CoplanarCircleCircleProps>): react.JSX.Element
{
    const { formIn, submit, ref, onChange } = props

    return (
        <Form.Root
            ref={ref}
            onSubmit={submit}
            className="grid grid-cols-3 gap-4 border-b pb-4 mb-4"
        >

            <InputField
                name="attractor"
                label="Attractor"
                type="select"
                value={formIn.attractor}
                onChange={onChange}
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

            <span className="col-span-3"></span>

            <InputField
                name="spacecraft.mass"
                label="Spacecraft Mass"
                symbol="m_{SC}"
                unit="kg"
                type="number"
                value={formIn.spacecraft.mass}
                onChange={onChange}
            />

            <InputField
                name="spacecraft.specificImpulse"
                label="Specific Impulse"
                symbol="I_{SP}"
                unit="s"
                type="number"
                value={formIn.spacecraft.specificImpulse}
                onChange={onChange}
            />

            <InputField
                name="spacecraft.thrust"
                label="Thrust"
                symbol="T"
                unit="N"
                type="number"
                value={formIn.spacecraft.thrust}
                onChange={onChange}
            />

            <InputField
                name="initialRadius"
                label="Initial Radius"
                symbol="r_0"
                unit="km"
                type="number"
                value={formIn.initialRadius}
                onChange={onChange}
            />

            <InputField
                name="finalRadius"
                label="Final Radius"
                symbol="r_f"
                unit="km"
                type="number"
                value={formIn.finalRadius}
                onChange={onChange}
            />

            <InputField
                name="earthShadow"
                label="Earth Shadow"
                symbol=""
                unit=""
                type="checkbox"
                value={Number(formIn.earthShadow)}
                onChange={onChange}
            />

        </Form.Root>
    )
}

// ---------------------------------------------------------------------------------------------------------------------

interface InclinationChangeProps
{
    formIn: IToolsInclinationChangeInModelInfo
    setFormIn: React.Dispatch<React.SetStateAction<IToolsInclinationChangeInModelInfo>>
    formOut: INonImpulsiveFormOut
    setFormOut: React.Dispatch<React.SetStateAction<INonImpulsiveFormOut>>
    submit: (e: React.FormEvent) => void
    ref: React.RefObject<HTMLFormElement>
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
}

/** @function InclinationChange */
function InclinationChange(props: Readonly<InclinationChangeProps>): react.JSX.Element
{
    const { formIn, submit, ref, onChange } = props

    return (
        <Form.Root
            ref={ref}
            onSubmit={submit}
            className="grid grid-cols-3 gap-4 border-b pb-4 mb-4"
        >

            <InputField
                name="attractor"
                label="Attractor"
                type="select"
                value={formIn.attractor}
                onChange={onChange}
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

            <span className="col-span-3"></span>

            <InputField
                name="spacecraft.mass"
                label="Spacecraft Mass"
                symbol="m_{SC}"
                unit="kg"
                type="number"
                value={formIn.spacecraft.mass}
                onChange={onChange}
            />

            <InputField
                name="spacecraft.specificImpulse"
                label="Specific Impulse"
                symbol="I_{SP}"
                unit="s"
                type="number"
                value={formIn.spacecraft.specificImpulse}
                onChange={onChange}
            />

            <InputField
                name="spacecraft.thrust"
                label="Thrust"
                symbol="T"
                unit="N"
                type="number"
                value={formIn.spacecraft.thrust}
                onChange={onChange}
            />

            <InputField
                name="radius"
                label="Radius"
                symbol="r"
                unit="km"
                type="number"
                value={formIn.radius}
                onChange={onChange}
            />

            <InputField
                name="initialInclination"
                label="Initial Inclination"
                symbol="i_0"
                unit="deg"
                type="number"
                value={formIn.initialInclination}
                onChange={onChange}
            />

            <InputField
                name="finalInclination"
                label="Final Inclination"
                symbol="i_f"
                unit="deg"
                type="number"
                value={formIn.finalInclination}
                onChange={onChange}
            />

        </Form.Root>
    )
}

// ---------------------------------------------------------------------------------------------------------------------

interface InclinedCircularOrbitsProps
{
    formIn: IToolsInclinedCircularOrbitsInModelInfo
    setFormIn: React.Dispatch<React.SetStateAction<IToolsInclinedCircularOrbitsInModelInfo>>
    formOut: INonImpulsiveFormOut
    setFormOut: React.Dispatch<React.SetStateAction<INonImpulsiveFormOut>>
    submit: (e: React.FormEvent) => void
    ref: React.RefObject<HTMLFormElement>
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
}

/** @function InclinedCircularOrbits */
function InclinedCircularOrbits(props: Readonly<InclinedCircularOrbitsProps>): react.JSX.Element
{
    const { formIn, submit, ref, onChange } = props

    return (
        <Form.Root
            ref={ref}
            onSubmit={submit}
            className="grid grid-cols-3 gap-4 border-b pb-4 mb-4"
        >

            <InputField
                name="attractor"
                label="Attractor"
                type="select"
                value={formIn.attractor}
                onChange={onChange}
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

            <span className="col-span-3"></span>

            <InputField
                name="spacecraft.mass"
                label="Spacecraft Mass"
                symbol="m_{SC}"
                unit="kg"
                type="number"
                value={formIn.spacecraft.mass}
                onChange={onChange}
            />

            <InputField
                name="spacecraft.specificImpulse"
                label="Specific Impulse"
                symbol="I_{SP}"
                unit="s"
                type="number"
                value={formIn.spacecraft.specificImpulse}
                onChange={onChange}
            />

            <InputField
                name="spacecraft.thrust"
                label="Thrust"
                symbol="T"
                unit="N"
                type="number"
                value={formIn.spacecraft.thrust}
                onChange={onChange}
            />

            <InputField
                name="initialRadius"
                label="Initial Radius"
                symbol="r_0"
                unit="km"
                type="number"
                value={formIn.initialRadius}
                onChange={onChange}
            />

            <InputField
                name="finalRadius"
                label="Final Radius"
                symbol="r_f"
                unit="km"
                type="number"
                value={formIn.finalRadius}
                onChange={onChange}
            />

            <InputField
                name="initialInclination"
                label="Initial Inclination"
                symbol="i_0"
                unit="deg"
                type="number"
                value={formIn.initialInclination}
                onChange={onChange}
            />

            <InputField
                name="finalInclination"
                label="Final Inclination"
                symbol="i_f"
                unit="deg"
                type="number"
                value={formIn.finalInclination}
                onChange={onChange}
            />

        </Form.Root>
    )
}
