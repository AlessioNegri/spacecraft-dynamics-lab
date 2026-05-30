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

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function CartesianPerifocalDialog */
export default function CartesianPerifocalDialog(props: Readonly<Props>): react.JSX.Element
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
            let response: any = await http.api.put(`/tools/convert-cartesian-to-perifocal`, formIn)

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
            
            <Form.Root className="grid grid-cols-2 gap-4 mb-4">

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Perifocal Position Vector</span>
                
                    <OutputField
                        symbol="r_x^{PF}"
                        unit="km"
                        value={formOut.position.x}
                    />

                    <OutputField
                        symbol="r_y^{PF}"
                        unit="km"
                        value={formOut.position.y}
                    />

                    <OutputField
                        symbol="r_z^{PF}"
                        unit="km"
                        value={formOut.position.z}
                    />

                </div>

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Perifocal Velocity Vector</span>

                    <OutputField
                        symbol="v_x^{PF}"
                        unit="km/s"
                        value={formOut.velocity.x}
                    />

                    <OutputField
                        symbol="v_y^{PF}"
                        unit="km/s"
                        value={formOut.velocity.y}
                    />

                    <OutputField
                        symbol="v_z^{PF}"
                        unit="km/s"
                        value={formOut.velocity.z}
                    />

                </div>

            </Form.Root>

        </DialogRUI>
    )
}