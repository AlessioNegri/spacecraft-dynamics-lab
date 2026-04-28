import * as react from "react"
import * as form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

interface IFormIn
{
    mainAttractor: string
    body: string
}

interface IFormOut
{
    sphereOfInfluence: number
}

const defaultIn: IFormIn =
{
    mainAttractor: "sun",
    body: "earth"
}

const defaultOut: IFormOut =
{
    sphereOfInfluence: 0
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function SphereOfInfluenceDialog */
export default function SphereOfInfluenceDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (formIn.mainAttractor === "sun")
        {
            setFormIn(prev => ({ ...prev, body: "earth" }))
        }
        else if (formIn.mainAttractor === "earth")
        {
            setFormIn(prev => ({ ...prev, body: "moon" }))
        }
    }, [formIn.mainAttractor])

    // --- HANDLE ---

    const validate = () : boolean =>
    {
        const newErrors: Record<string, string> = {}

        if (formIn.body === formIn.mainAttractor)
        {
            newErrors.body = "Body cannot be the same as main attractor"
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        if (!validate()) return

        try
        {
            let response: any = await http.api.put(`/tools/sphere-of-influence`, formIn)

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
            title="Sphere of Influence"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Sphere of Influence",
                    content:
                        `The sphere of influence is the region around a celestial body where its gravitational field
                        dominates over the gravitational field of other bodies.`
                }
            }>

            {/* INPUT */}

            <form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <InputField
                    name="mainAttractor"
                    label="Main Attractor"
                    type="select"
                    value={formIn.mainAttractor}
                    onChange={handleChange}
                    options={
                        [
                            { label: "Sun", value: "sun" },
                            { label: "Earth", value: "earth" }
                        ]}
                />

                <InputField
                    name="body"
                    label="Body"
                    type="select"
                    value={formIn.body}
                    onChange={handleChange}
                    options={
                        formIn.mainAttractor === "sun" ?
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

                {
                    errors.body &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.body}</span>
                }

            </form.Root>

            {/* OUTPUT */}

            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <OutputField label="Sphere of Influence" unit="KM" value={formOut.sphereOfInfluence} />

            </form.Root>

        </DialogRUI>
    )
}