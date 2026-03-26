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
    deltaTime: number
}

interface IFormOut
{
    draan_dt: number // ? RAAN variation
    daop_dt: number // ? Argument Of Periapsis variation
    alpha: number // ? Right Ascension
    delta: number // ? Declination
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
    },
    deltaTime: 45 * 60
}

const defaultOut: IFormOut =
{
    draan_dt: 0,
    daop_dt: 0,
    alpha: 0,
    delta: 0
}

interface GroundTrackPropagationDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function GroundTrackPropagationDialog */
export default function GroundTrackPropagationDialog(props: Readonly<GroundTrackPropagationDialogProps>): react.JSX.Element
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
            let response: any = await http.api.put(`/tools/propagate-ground-track`, formIn)

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
            title="Ground Track Propagation"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Ground Track Propagation",
                    content:
                        `Given the initial orbital elements of a satellite relative to the Geocentric Equatorial frame,
                        compute the right ascension and declination relative to the rotating earth after a given time
                        interval.`
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

                <InputField
                    name="deltaTime"
                    label="Time Delta"
                    unit="S"
                    value={formIn.deltaTime}
                    onChange={handleChange}
                    min={0}
                />

            </form.Root>

            {/* OUTPUT */}
            
            <form.Root className="grid grid-cols-2 gap-4 mb-4">
                
                <OutputField label="RAAN Variation" unit="DEG / DAY" value={formOut.draan_dt} />

                <OutputField label="Argument Periapsis Variation" unit="DEG / DAY" value={formOut.daop_dt} />

                <OutputField label="Right Ascension" unit="DEG" value={formOut.alpha} />

                <OutputField label="Declination" unit="DEG" value={formOut.delta} />

            </form.Root>

        </DialogRUI>
    )
}