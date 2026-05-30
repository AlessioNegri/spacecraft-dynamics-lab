import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"
import ErrorText from "@renderer/components/dialogs/ErrorText"

interface IFormIn
{
    position1: IVector3D
    position2: IVector3D
    position3: IVector3D
}

interface IFormOut
{
    oe: IOrbitalElements
}

const defaultIn: IFormIn =
{
    position1: { x: -294.32, y: 4265.1, z: 5986.7 },
    position2: { x: -1365.5, y: 3637.6, z: 6346.8 },
    position3: { x: -2940.3, y: 2473.7, z: 6555.8 }
}

const defaultOut: IFormOut =
{
    oe: { sam: 0, sma: 0, ecc: 0, inc: 0, raan: 0, aop: 0, ta: 0 }
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

export default function GibbsMethodDialog(props: Readonly<Props>): react.JSX.Element
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

        if (formIn.position1.x == 0 && formIn.position1.y == 0 && formIn.position1.z == 0)
        {
            newErrors.position1 = "Position cannot be [0,0,0]"
        }

        if (formIn.position2.x == 0 && formIn.position2.y == 0 && formIn.position2.z == 0)
        {
            newErrors.position2 = "Position cannot be [0,0,0]"
        }

        if (formIn.position3.x == 0 && formIn.position3.y == 0 && formIn.position3.z == 0)
        {
            newErrors.position3 = "Position cannot be [0,0,0]"
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        const [ group, axis ] = name.split(".")

        setFormIn({ ...formIn, [group]: { ...formIn[group], [axis]: value } })
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        if (!validate()) return

        try
        {
            let response: any = await http.api.put(`/tools/gibbs-method`, formIn)

            const result: IFormOut = { oe: response.data }
            
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
            title="Gibbs Method"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Gibbs Method",
                    content:
                        `Given 3 position vectors in the Inertial Reference Frame, compute the orbital elements.`
                }
            }>

            {/* INPUT */}

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Position Vector 1</span>

                    <InputField
                        name="position1.x"
                        symbol="r_x"
                        unit="km"
                        value={formIn.position1.x}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position1.y"
                        symbol="r_y"
                        unit="km"
                        value={formIn.position1.y}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position1.z"
                        symbol="r_z"
                        unit="km"
                        value={formIn.position1.z}
                        onChange={handleChange}
                    />

                    { errors.position1 && <ErrorText text={errors.position1} /> }
                
                </div>

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Position Vector 2</span>

                    <InputField
                        name="position2.x"
                        symbol="r_x"
                        unit="km"
                        value={formIn.position2.x}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position2.y"
                        symbol="r_y"
                        unit="km"
                        value={formIn.position2.y}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position2.z"
                        symbol="r_z"
                        unit="km"
                        value={formIn.position2.z}
                        onChange={handleChange}
                    />

                    { errors.position2 && <ErrorText text={errors.position2} /> }

                </div>

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Position Vector 3</span>

                    <InputField
                        name="position3.x"
                        symbol="r_x"
                        unit="km"
                        value={formIn.position3.x}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position3.y"
                        symbol="r_y"
                        unit="km"
                        value={formIn.position3.y}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position3.z"
                        symbol="r_z"
                        unit="km"
                        value={formIn.position3.z}
                        onChange={handleChange}
                    />

                    { errors.position3 && <ErrorText text={errors.position3} /> }

                </div>
                
            </Form.Root>

            {/* OUTPUT */}

            <Form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Orbital Elements</span>

                <OutputField
                    label="Semimajor Axis"
                    symbol="a"
                    unit="km"
                    value={formOut.oe.sma}
                />

                <OutputField
                    label="Eccentricity"
                    symbol="e"
                    unit=""
                    value={formOut.oe.ecc}
                />

                <OutputField
                    label="Inclination"
                    symbol="i"
                    unit="deg"
                    value={formOut.oe.inc}
                />

                <OutputField
                    label="RAAN"
                    symbol="\Omega"
                    unit="deg"
                    value={formOut.oe.raan}
                />

                <OutputField
                    label="Argument Periapsis"
                    symbol="\omega"
                    unit="deg"
                    value={formOut.oe.aop}
                />

                <OutputField
                    label="True Anomaly"
                    symbol="\theta"
                    unit="deg"
                    value={formOut.oe.ta}
                />

            </Form.Root>

        </DialogRUI>
    )
}
