import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface IFormIn
{
    attractor: string
    oe: IOrbitalElements
}

interface IFormOut
{
    position: IVector3D
    velocity: IVector3D
}

const defaultIn: IFormIn =
{
    attractor: "earth",
    oe:
    {
        sam: 0,
        sma: 8350,
        ecc: 0.1976,
        inc: 60,
        raan: 270,
        aop: 45,
        ta: 230
    }
}

const defaultOut: IFormOut =
{
    position: { x: 0, y: 0, z: 0 },
    velocity: { x: 0, y: 0, z: 0 }
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function KeplerianCartesianDialog */
export default function KeplerianCartesianDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

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

        try
        {
            let response: any = await http.api.put(`/tools/convert-keplerian-to-cartesian`, formIn)

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
            title="Keplerian → Cartesian"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Keplerian → Cartesian",
                    content:
                        `Convert the Keplerian parameters into Cartesian state vectors (position & velocity) in
                        Inertial Reference Frame.`
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
                
                <span className="col-span-3 text-center uppercase font-semibold">Orbital Elements</span>

                <InputField
                    name="oe.sma"
                    label="Semimajor Axis"
                    symbol="a"
                    unit="km"
                    type="text"
                    value={String(formIn.oe.sma)}
                    onChange={handleChange}
                    pattern="^(?!0$).*"
                />

                <InputField
                    name="oe.ecc"
                    label="Eccentricity"
                    symbol="e"
                    unit=""
                    value={formIn.oe.ecc}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    type="number"
                    name="oe.inc"
                    label="Inclination"
                    symbol="i"
                    unit="deg"
                    value={formIn.oe.inc}
                    onChange={handleChange}
                    min={0}
                    max={180}
                />

                <InputField
                    type="number"
                    name="oe.raan"
                    label="Right Ascension of Ascending Node"
                    symbol="\Omega"
                    unit="deg"
                    value={formIn.oe.raan}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    type="number"
                    name="oe.aop"
                    label="Argument Of Periapsis"
                    symbol="\omega"
                    unit="deg"
                    value={formIn.oe.aop}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    type="number"
                    name="oe.ta"
                    label="True Anomaly"
                    symbol="\theta"
                    unit="deg"
                    value={formIn.oe.ta}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

            </Form.Root>

            {/* OUTPUT */}
            
            <Form.Root className="grid grid-cols-2 gap-4 mb-4">

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Position Vector</span>
                
                    <OutputField
                        symbol="r_x"
                        unit="km"
                        value={formOut.position.x}
                    />

                    <OutputField
                        symbol="r_y"
                        unit="km"
                        value={formOut.position.y}
                    />

                    <OutputField
                        symbol="r_z"
                        unit="km"
                        value={formOut.position.z}
                    />

                </div>

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Velocity Vector</span>

                    <OutputField
                        symbol="v_x"
                        unit="km / s"
                        value={formOut.velocity.x}
                    />

                    <OutputField
                        symbol="v_y"
                        unit="km / s"
                        value={formOut.velocity.y}
                    />

                    <OutputField
                        symbol="v_z"
                        unit="km / s"
                        value={formOut.velocity.z}
                    />

                </div>

            </Form.Root>

        </DialogRUI>
    )
}