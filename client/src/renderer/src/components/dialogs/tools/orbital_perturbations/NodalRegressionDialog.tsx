import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface IFormIn
{
    attractor: string
    orbitalElements: IOrbitalElements
}

interface IFormOut
{
    gravitational: number
    lunar: number
    solar: number
}

const defaultIn: IFormIn =
{
    attractor: "earth",
    orbitalElements:
    {
        sam: 0,
        sma: 8059,
        ecc: 0.15,
        inc: 20,
        raan: 0,
        aop: 0,
        ta: 0
    }
}

const defaultOut: IFormOut =
{
    gravitational: 0,
    lunar: 0,
    solar: 0
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function NodalRegressionDialog */
export default function NodalRegressionDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

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
            let response: any = await http.api.put(`/orbital-perturbations/nodal-regression-rate`, formIn)

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
            title="Nodal Regression"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={{
                title: "Nodal Regression",
                content: `Compute the nodal regression rates (deg/day) due to J2, lunar and solar gravity.`
                }}
        >

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

                <span className="col-span-3"></span>

                <InputField
                    name="orbitalElements.sma"
                    label="Semimajor Axis"
                    symbol="a"
                    unit="km"
                    type="text"
                    value={String(formIn.orbitalElements.sma)}
                    onChange={handleChange}
                    pattern="^(?!0$).*"
                />

                <InputField
                    name="orbitalElements.ecc"
                    label="Eccentricity"
                    symbol="e"
                    unit=""
                    value={String(formIn.orbitalElements.ecc)}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    type="number"
                    name="orbitalElements.inc"
                    label="Inclination"
                    symbol="i"
                    unit="deg"
                    value={formIn.orbitalElements.inc}
                    onChange={handleChange}
                    min={-90}
                    max={90}
                />

            </Form.Root>

            <Form.Root className="grid grid-cols-3 gap-4 mb-4">

                <OutputField
                    label="J2 Nodal Regression Rate"
                    symbol="\dot{\Omega}_{J2}"
                    unit="deg / day"
                    value={formOut.gravitational}
                    maximumFractionDigits={7}
                />

                <OutputField
                    label="Lunar Nodal Regression Rate"
                    symbol="\dot{\Omega}_{L}"
                    unit="deg / day"
                    value={formOut.lunar}
                    maximumFractionDigits={7}
                />

                <OutputField
                    label="Solar Nodal Regression Rate"
                    symbol="\dot{\Omega}_{S}"
                    unit="deg / day"
                    value={formOut.solar}
                    maximumFractionDigits={7}
                />

            </Form.Root>

        </DialogRUI>
    )
}
