import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface IFormIn
{
    body1: string
    body2: string
}

interface IFormOut
{
    inertialAngularVelocity: number
    dimensionlessMassRatio1: number
    dimensionlessMassRatio2: number
    gravitationalParameter1: number
    gravitationalParameter2: number
    bodyPosition1: number
    bodyPosition2: number
    lagrangianPoint1: number[]
    lagrangianPoint2: number[]
    lagrangianPoint3: number[]
    lagrangianPoint4: number[]
    lagrangianPoint5: number[]
}

const defaultIn: IFormIn =
{
    body1: "earth",
    body2: "moon"
}

const defaultOut: IFormOut =
{
    inertialAngularVelocity: 0,
    dimensionlessMassRatio1: 0,
    dimensionlessMassRatio2: 0,
    gravitationalParameter1: 0,
    gravitationalParameter2: 0,
    bodyPosition1: 0,
    bodyPosition2: 0,
    lagrangianPoint1: [0, 0, 0],
    lagrangianPoint2: [0, 0, 0],
    lagrangianPoint3: [0, 0, 0],
    lagrangianPoint4: [0, 0, 0],
    lagrangianPoint5: [0, 0, 0]
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function OrbitParametersDialog */
export default function OrbitParametersDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [distance, setDistance] = react.useState<number>(1)

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (formIn.body1 === "sun")
        {
            setFormIn(prev => ({ ...prev, body2: "earth" }))
        }
        else if (formIn.body1 === "earth")
        {
            setFormIn(prev => ({ ...prev, body2: "moon" }))
        }
    }, [formIn.body1])

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            const response: any = await http.api.put(`/circular-restricted-three-body-problem/orbit-parameters`, formIn)

            const x1: number = response.data.bodyPosition1
            const x2: number = response.data.bodyPosition2

            setDistance(Math.abs(x2 - x1))

            setFormOut(response.data)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Orbit Parameters"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={{
                title: "Orbit Parameters",
                content: `Compute the circular restricted three-body problem parameters for a selected pair of
                    primaries, including the mass ratios, angular velocity, body positions, and Lagrange points.`
            }}
        >

            {/* INPUT */}

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-2 gap-4 border-b pb-4 mb-4">
                
                <InputField
                    name="body1"
                    label="Primary Body"
                    type="select"
                    value={formIn.body1}
                    onChange={handleChange}
                    options={
                        [
                            { label: "Sun", value: "sun" },
                            { label: "Earth", value: "earth" }
                        ]}
                />

                <InputField
                    name="body2"
                    label="Secondary Body"
                    type="select"
                    value={formIn.body2}
                    onChange={handleChange}
                    options={
                        formIn.body1 === "sun" ?
                        [
                            { label: "Mercury", value: "mercury" },
                            { label: "Venus", value: "venus" },
                            { label: "Earth", value: "earth" },
                            { label: "Mars", value: "mars" },
                            { label: "Jupiter", value: "jupiter" },
                            { label: "Saturn", value: "saturn" },
                            { label: "Uranus", value: "uranus" },
                            { label: "Neptune", value: "neptune" }
                        ]
                        :
                        [
                            { label: "Moon", value: "moon" }
                        ]
                    }
                />

            </Form.Root>

            {/* OUTPUT */}

            <Form.Root className="grid grid-cols-2 gap-4 mb-4">

                <OutputField
                    label="Inertial Angular Velocity"
                    symbol="\Omega"
                    unit="deg/day"
                    value={formOut.inertialAngularVelocity}
                />

                <span></span>

                <OutputField
                    label="Mass Ratio 1"
                    symbol="\pi_1"
                    unit=""
                    value={formOut.dimensionlessMassRatio1}
                />

                <OutputField
                    label="Mass Ratio 2"
                    symbol="\pi_2"
                    unit=""
                    value={formOut.dimensionlessMassRatio2}
                />

                <OutputField
                    label="Gravitational Parameter 1"
                    symbol="\mu_1"
                    unit="km^3/s^2"
                    value={formOut.gravitationalParameter1}
                />

                <OutputField
                    label="Gravitational Parameter 2"
                    symbol="\mu_2"
                    unit="km^3/s^2"
                    value={formOut.gravitationalParameter2}
                />

                <OutputField
                    label="Body Position 1"
                    symbol="x_1"
                    unit="km"
                    value={formOut.bodyPosition1}
                />

                <OutputField
                    label="Body Position 2"
                    symbol="x_2"
                    unit="km"
                    value={formOut.bodyPosition2}
                />

            </Form.Root>

            <Form.Root className="grid grid-cols-2 gap-4">

                <span className="col-span-full text-center uppercase font-semibold">Lagrange Points</span>

                <OutputField
                    symbol="L_1 / (x_2 - x_1)"
                    unit=""
                    value={formOut.lagrangianPoint1.map((v: number) => (v / distance).toFixed(5)).join(", ")}
                />

                <OutputField
                    symbol="L_2 / (x_2 - x_1)"
                    value={formOut.lagrangianPoint2.map((v: number) => (v / distance).toFixed(5)).join(", ")}
                />

                <OutputField
                    symbol="L_3 / (x_2 - x_1)"
                    value={formOut.lagrangianPoint3.map((v: number) => (v / distance).toFixed(5)).join(", ")}
                />

                <OutputField
                    symbol="L_4 / (x_2 - x_1)"
                    value={formOut.lagrangianPoint4.map((v: number) => (v / distance).toFixed(5)).join(", ")}
                />

                <OutputField
                    symbol="L_5 / (x_2 - x_1)"
                    value={formOut.lagrangianPoint5.map((v: number) => (v / distance).toFixed(5)).join(", ")}
                />

            </Form.Root>

        </DialogRUI>
    )
}
