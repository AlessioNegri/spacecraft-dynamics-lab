import * as react from "react"
import * as form from "@radix-ui/react-form"

import http from "@renderer/common/http"
import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

interface IFormIn
{
    attractor: string
    orbitalElementsTarget: IOrbitalElements
    lvlhPosition: IVector3D,
    lvlhVelocity: IVector3D
}

interface IFormOut
{
    orbitalElementsChaser: IOrbitalElements
}

const defaultIn: IFormIn =
{
    attractor: "earth",
    orbitalElementsTarget:
    {
        sam: 52059,
        sma: 6810,
        ecc: 0.025724,
        inc: 60,
        raan: 40,
        aop: 30,
        ta: 40
    },
    lvlhPosition:
    {
        x: -1,
        y: 0,
        z: 0
    },
    lvlhVelocity:
    {
        x: 0,
        y: 1,
        z: 0
    }
}

const defaultOut: IFormOut =
{
    orbitalElementsChaser:
    {
        sam: 0,
        sma: 0,
        ecc: 0,
        inc: 0,
        raan: 0,
        aop: 0,
        ta: 0
    }
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function GeocentricEquatorialKinematicsDialog */
export default function GeocentricEquatorialKinematicsDialog(props: Readonly<Props>): react.JSX.Element
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

        if (formIn.lvlhPosition.x == 0 && formIn.lvlhPosition.y == 0 && formIn.lvlhPosition.z == 0)
        {
            newErrors.lvlhPosition = "Position cannot be [0,0,0]"
        }

        if (formIn.lvlhVelocity.x == 0 && formIn.lvlhVelocity.y == 0 && formIn.lvlhVelocity.z == 0)
        {
            newErrors.lvlhVelocity = "Velocity cannot be [0,0,0]"
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
            let response: any = await http.api.put(`/tools/geocentric-equatorial-kinematics`, formIn)

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
            title="Geocentric Equatorial Kinematics"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Geocentric Equatorial Kinematics",
                    content:
                        `Given the state vectors of the target spacecraft and the state vector of the chaser spacecraft
                        relative to Target along the Local Vertical Local Horizontal (LVLH) axes attached to the Target,
                        find the position and velocity of Chaser in the Geocentric Equatorial frame.`
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

                <span className="col-span-3 text-center uppercase font-semibold">Target Orbital Elements</span>

                <InputField
                    name="orbitalElementsTarget.sma"
                    label="Semi-Major Axis"
                    unit="KM"
                    type="text"
                    value={String(formIn.orbitalElementsTarget.sma)}
                    onChange={handleChange}
                    pattern="^(?!0$).*"
                />

                <InputField
                    name="orbitalElementsTarget.ecc"
                    label="Eccentricity"
                    unit="KM"
                    value={formIn.orbitalElementsTarget.ecc}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    name="orbitalElementsTarget.inc"
                    label="Inclination"
                    unit="DEG"
                    value={formIn.orbitalElementsTarget.inc}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElementsTarget.raan"
                    label="RAAN"
                    unit="DEG"
                    value={formIn.orbitalElementsTarget.raan}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElementsTarget.aop"
                    label="Argument Periapsis"
                    unit="DEG"
                    value={formIn.orbitalElementsTarget.aop}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElementsTarget.ta"
                    label="True Anomaly"
                    unit="DEG"
                    value={formIn.orbitalElementsTarget.ta}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <span className="col-span-3 text-center uppercase font-semibold">LVLH Position Vector</span>

                <InputField
                    name="lvlhPosition.x"
                    label="X"
                    unit="KM"
                    value={formIn.lvlhPosition.x}
                    onChange={handleChange}
                />

                <InputField
                    name="lvlhPosition.y"
                    label="Y"
                    unit="KM"
                    value={formIn.lvlhPosition.y}
                    onChange={handleChange}
                />

                <InputField
                    name="lvlhPosition.z"
                    label="Z"
                    unit="KM"
                    value={formIn.lvlhPosition.z}
                    onChange={handleChange}
                />

                {
                    errors.lvlhPosition &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.lvlhPosition}</span>
                }

                <span className="col-span-3 text-center uppercase font-semibold">LVLH Velocity Vector</span>
                
                <InputField
                    name="lvlhVelocity.x"
                    label="X"
                    unit="KM"
                    value={formIn.lvlhVelocity.x}
                    onChange={handleChange}
                />

                <InputField
                    name="lvlhVelocity.y"
                    label="Y"
                    unit="KM"
                    value={formIn.lvlhVelocity.y}
                    onChange={handleChange}
                />

                <InputField
                    name="lvlhVelocity.z"
                    label="Z"
                    unit="KM"
                    value={formIn.lvlhVelocity.z}
                    onChange={handleChange}
                />

                {
                    errors.lvlhVelocity &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.lvlhVelocity}</span>
                }

            </form.Root>

            {/* OUTPUT */}

            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Chaser Orbital Elements</span>

                <OutputField name="sma" label="Semi-Major Axis" unit="KM" value={formOut.orbitalElementsChaser.sma} />
                
                <OutputField name="ecc" label="Eccentricity" value={formOut.orbitalElementsChaser.ecc} />

                <OutputField name="inc" label="Inclination" unit="DEG" value={formOut.orbitalElementsChaser.inc} />

                <OutputField name="raan" label="RAAN" unit="DEG" value={formOut.orbitalElementsChaser.raan} />

                <OutputField name="aop" label="Argument Periapsis" unit="DEG" value={formOut.orbitalElementsChaser.aop} />

                <OutputField name="ta" label="True Anomaly" unit="DEG" value={formOut.orbitalElementsChaser.ta} />

            </form.Root>

        </DialogRUI>
    )
}