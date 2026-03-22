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
    position: IVector3D
    velocity: IVector3D
}

const defaultIn: IFormIn =
{
    attractor: "earth",
    position: { x: 8000, y: 0, z: 6000 },
    velocity: { x: 0, y: 7, z: 0 }
}

const defaultOut: IFormOut =
{
    position: { x: 0, y: 0, z: 0 },
    velocity: { x: 0, y: 0, z: 0 }
}

interface CartesianPerifocalDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function CartesianPerifocalDialog */
export default function CartesianPerifocalDialog(props: Readonly<CartesianPerifocalDialogProps>): react.JSX.Element
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
            let response: any = await http.api.put(`/tools/convert-cartesian-to-perifocal`, formIn)

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
            title="Cartesian → Perifocal"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Cartesian → Perifocal",
                    content:
                        `Convert a given orbit state vector (position vector & velocity vector) in Geocentric Equatorial
                        frame, into Perifocal one.`
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

                <span className="col-span-3 text-center uppercase font-semibold">Perifocal Position Vector</span>
                
                <OutputField label="X" unit="KM" value={formOut.position.x} />

                <OutputField label="Y" unit="KM" value={formOut.position.y} />

                <OutputField label="Z" unit="KM" value={formOut.position.z} />

                <span className="col-span-3 text-center uppercase font-semibold">Perifocal Velocity Vector</span>

                <OutputField label="X" unit="KM / S" value={formOut.velocity.x} />

                <OutputField label="Y" unit="KM / S" value={formOut.velocity.y} />

                <OutputField label="Z" unit="KM / S" value={formOut.velocity.z} />

            </form.Root>

        </DialogRUI>
    )
}