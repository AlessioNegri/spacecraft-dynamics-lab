import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface IFormIn
{
    attractor: string
    positions: [IVector3D, IVector3D, IVector3D]
    times: [number, number, number]
}

interface IFormOut
{
    oe: IOrbitalElements
}

const defaultIn: IFormIn =
{
    attractor: "earth",
    positions: [
        { x: -294.32, y: 4265.1, z: 5986.7 },
        { x: -1365.5, y: 3637.6, z: 6346.8 },
        { x: -2940.3, y: 2473.7, z: 6555.8 }
    ],
    times: [0, 118.1, 237.58]
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

/** @function HerrickGibbsMethodDialog */
export default function HerrickGibbsMethodDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>): void =>
    {
        const { name, value } = e.target
        
        const [group, index, axis] = name.split(".")

        if (group === "positions")
        {
            setFormIn(prev => ({
                ...prev,
                positions: prev.positions.map((position, i) => i === Number(index)
                    ? { ...position, [axis]: Number(value) }
                    : position) as IFormIn["positions"]
            }))
            return
        }

        if (group === "times")
        {
            setFormIn(prev => ({
                ...prev,
                times: prev.times.map((time, i) => i === Number(index) ? Number(value) : time) as IFormIn["times"]
            }))
            return
        }

        setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            const response = await http.api.put<IOrbitalElements>("/tools/herrick-gibbs-method", formIn)

            setFormOut({ oe: response.data })
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Herrick-Gibbs Method"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={{
                title: "Herrick-Gibbs Method",
                content: `Given three position vectors and their observation times, compute the orbital elements.
                    Valid for three subsequent measurements that are less apart than 15° for LEO and 6° for GSO.`
            }}
        >

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4"
            >

                <InputField
                    name="attractor"
                    label="Attractor"
                    type="select"
                    value={formIn.attractor}
                    onChange={handleChange}
                    options={[
                        { label: "Sun", value: "sun" },
                        { label: "Mercury", value: "mercury" },
                        { label: "Venus", value: "venus" },
                        { label: "Earth", value: "earth" },
                        { label: "Moon", value: "moon" },
                        { label: "Mars", value: "mars" },
                        { label: "Jupiter", value: "jupiter" },
                        { label: "Saturn", value: "saturn" },
                        { label: "Uranus", value: "uranus" },
                        { label: "Neptune", value: "neptune" },
                        { label: "Pluto", value: "pluto" }
                    ]}
                />

                <span></span>
                <span></span>

                {[0, 1, 2].map((index: number) =>
                    <div key={index} className="flex flex-col gap-4 border-2 border-neutral-700 rounded p-2">

                        <span className="text-center uppercase font-semibold">Observation {index + 1}</span>

                        <InputField
                            type="number"
                            name={`times.${index}`}
                            label="Time"
                            symbol="t"
                            unit="s"
                            value={formIn.times[index]}
                            onChange={handleChange}
                        />

                        {(["x", "y", "z"] as const).map((axis: string) =>
                            <InputField
                                key={axis}
                                type="number"
                                name={`positions.${index}.${axis}`}
                                label={`Position ${axis.toUpperCase()}`}
                                symbol={`r_${axis}`}
                                unit="km"
                                value={formIn.positions[index][axis]}
                                onChange={handleChange}
                            />
                        )}
                    </div>
                )}

            </Form.Root>

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
