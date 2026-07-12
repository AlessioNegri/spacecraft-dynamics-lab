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

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function GroundTrackPropagationDialog */
export default function GroundTrackPropagationDialog(props: Readonly<Props>): react.JSX.Element
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
            let response: any = await http.api.put(`/tools/propagate-ground-track`, formIn)

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
            title="Ground Track Propagation"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Ground Track Propagation",
                    content:
                        `Given the initial orbital elements of a satellite relative to the Inertial Reference Frame,
                        compute the right ascension and declination relative to the rotating earth after a given time
                        interval.`
                }
            }>

            {/* INPUT */}

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4 items-end">

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

                <InputField
                    name="deltaTime"
                    label="Time Delta"
                    symbol="\Delta t"
                    unit="s"
                    value={formIn.deltaTime}
                    onChange={handleChange}
                    min={0}
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
                
                <OutputField
                    label="Right Ascension of Ascending Node Variation"
                    symbol="d\Omega / dt"
                    unit="deg / day"
                    value={formOut.draan_dt}
                />

                <OutputField
                    label="Argument Of Periapsis Variation"
                    symbol="d\omega / dt"
                    unit="deg / day"
                    value={formOut.daop_dt}
                />

                <OutputField
                    label="Right Ascension"
                    symbol="\alpha"
                    unit="deg"
                    value={formOut.alpha}
                />

                <OutputField
                    label="Declination"
                    symbol="\delta"
                    unit="deg"
                    value={formOut.delta}
                />

            </Form.Root>

        </DialogRUI>
    )
}