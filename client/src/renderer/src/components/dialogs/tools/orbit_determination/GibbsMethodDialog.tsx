import * as react from "react"
import * as form from "@radix-ui/react-form"

import http from "@renderer/common/http"
import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

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

interface GibbsMethodDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

export default function GibbsMethodDialog(props: Readonly<GibbsMethodDialogProps>): react.JSX.Element
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
            const message: string | null = http.checkError(import.meta.url, err)

            if (message) setAxiosError(message)
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
                        `Given 3 position vectors in the Geocentric Equaorial Frame, compute the orbital elements.`
                }
            }>

            {/* INPUT */}

            <form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Position Vector 1</span>

                <InputField
                    name="position1.x"
                    label="X"
                    unit="KM"
                    value={formIn.position1.x}
                    onChange={handleChange}
                />

                <InputField
                    name="position1.y"
                    label="Y"
                    unit="KM"
                    value={formIn.position1.y}
                    onChange={handleChange}
                />

                <InputField
                    name="position1.z"
                    label="Z"
                    unit="KM"
                    value={formIn.position1.z}
                    onChange={handleChange}
                />

                {
                    errors.position1 &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.position1}</span>
                }

                <span className="col-span-3 text-center uppercase font-semibold">Position Vector 2</span>

                <InputField
                    name="position2.x"
                    label="X"
                    unit="KM"
                    value={formIn.position2.x}
                    onChange={handleChange}
                />

                <InputField
                    name="position2.y"
                    label="Y"
                    unit="KM"
                    value={formIn.position2.y}
                    onChange={handleChange}
                />

                <InputField
                    name="position2.z"
                    label="Z"
                    unit="KM"
                    value={formIn.position2.z}
                    onChange={handleChange}
                />

                {
                    errors.position2 &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.position2}</span>
                }

                <span className="col-span-3 text-center uppercase font-semibold">Position Vector 3</span>

                <InputField
                    name="position3.x"
                    label="X"
                    unit="KM"
                    value={formIn.position3.x}
                    onChange={handleChange}
                />

                <InputField
                    name="position3.y"
                    label="Y"
                    unit="KM"
                    value={formIn.position3.y}
                    onChange={handleChange}
                />

                <InputField
                    name="position3.z"
                    label="Z"
                    unit="KM"
                    value={formIn.position3.z}
                    onChange={handleChange}
                />

                {
                    errors.position3 &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.position3}</span>
                }
                
            </form.Root>

            {/* OUTPUT */}

            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Orbital Elements</span>

                <OutputField name="sma" label="Semi-Major Axis" unit="KM" value={formOut.oe.sma} />

                <OutputField name="ecc" label="Eccentricity" value={formOut.oe.ecc} />

                <OutputField name="inc" label="Inclination" unit="DEG" value={formOut.oe.inc} />

                <OutputField name="raan" label="RAAN" unit="DEG" value={formOut.oe.raan} />

                <OutputField name="aop" label="Argument Periapsis" unit="DEG" value={formOut.oe.aop} />

                <OutputField name="ta" label="True Anomaly" unit="DEG" value={formOut.oe.ta} />
                    
            </form.Root>

        </DialogRUI>
    )
}
