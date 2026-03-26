import * as react from "react"
import * as form from "@radix-ui/react-form"

import http from "@renderer/common/http"
import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

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

interface KeplerianCartesianDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function KeplerianCartesianDialog */
export default function KeplerianCartesianDialog(props: Readonly<KeplerianCartesianDialogProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [_, setAxiosError] = react.useState<string>("")

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
            const message: string | null = http.checkError(import.meta.url, err)

            if (message) setAxiosError(message)
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
                        Geocentric Equatorial frame.`
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
                
                <span className="col-span-3 text-center uppercase font-semibold">Orbital Elements</span>

                <InputField
                    name="oe.sma"
                    label="Semi-Major Axis"
                    unit="KM"
                    type="text"
                    value={String(formIn.oe.sma)}
                    onChange={handleChange}
                    pattern="^(?!0$).*"
                />

                <InputField
                    name="oe.ecc"
                    label="Eccentricity"
                    unit="KM"
                    value={formIn.oe.ecc}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    name="oe.inc"
                    label="Inclination"
                    unit="DEG"
                    value={formIn.oe.inc}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="oe.raan"
                    label="RAAN"
                    unit="DEG"
                    value={formIn.oe.raan}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="oe.aop"
                    label="Argument Periapsis"
                    unit="DEG"
                    value={formIn.oe.aop}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="oe.ta"
                    label="True Anomaly"
                    unit="DEG"
                    value={formIn.oe.ta}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

            </form.Root>

            {/* OUTPUT */}
            
            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Position Vector</span>
                
                <OutputField label="X" unit="KM" value={formOut.position.x} />

                <OutputField label="Y" unit="KM" value={formOut.position.y} />

                <OutputField label="Z" unit="KM" value={formOut.position.z} />

                <span className="col-span-3 text-center uppercase font-semibold">Velocity Vector</span>

                <OutputField label="X" unit="KM / S" value={formOut.velocity.x} />

                <OutputField label="Y" unit="KM / S" value={formOut.velocity.y} />

                <OutputField label="Z" unit="KM / S" value={formOut.velocity.z} />

            </form.Root>

        </DialogRUI>
    )
}