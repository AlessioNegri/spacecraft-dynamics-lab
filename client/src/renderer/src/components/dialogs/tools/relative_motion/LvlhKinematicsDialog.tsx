import * as react from "react"
import * as form from "@radix-ui/react-form"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"
import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

interface IFormIn
{
    attractor: string
    orbitalElementsTarget: IOrbitalElements
    orbitalElementsChaser: IOrbitalElements
}

interface IFormOut
{
    position: IVector3D
    velocity: IVector3D
    acceleration: IVector3D
    angularVelocity: IVector3D
    x: number[]
    y: number[]
    z: number[]
}

const defaultIn: IFormIn =
{
    attractor: "earth",
    orbitalElementsTarget:
    {
        sam: 52059,
        sma: 6810,
        ecc: 0.025724,
        inc: 60,
        raan: 40,
        aop: 30,
        ta: 40
    },
    orbitalElementsChaser:
    {
        sam: 52362,
        sma: 6880,
        ecc: 0.0072696,
        inc: 50,
        raan: 40,
        aop: 120,
        ta: 40
    }
}

const defaultOut: IFormOut =
{
    position: { x: 0, y: 0, z: 0 },
    velocity: { x: 0, y: 0, z: 0 },
    acceleration: { x: 0, y: 0, z: 0 },
    angularVelocity: { x: 0, y: 0, z: 0 },
    x: [],
    y: [],
    z: []
}

interface LvlhKinematicsDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function LvlhKinematicsDialog */
export default function LvlhKinematicsDialog(props: Readonly<LvlhKinematicsDialogProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [kinematics, setKinematics] = react.useState<plotly.Data[]>()

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    react.useEffect(() =>
    {
        const axisX: plotly.Data =
        {
            x: [0, 10000],
            y: [0, 0],
            z: [0, 0],
            type: "scatter3d",
            mode: "lines",
            line: { color: "#ff0000", width: 3, dash: "longdashdot" },
            name: "X",
        }

        const axisY: plotly.Data =
        {
            x: [0, 0],
            y: [0, 10000],
            z: [0, 0],
            type: "scatter3d",
            mode: "lines",
            line: { color: "#00ff00", width: 3, dash: "longdashdot" },
            name: "Y",
        }

        const axisZ: plotly.Data =
        {
            x: [0, 0],
            y: [0, 0],
            z: [0, 10000],
            type: "scatter3d",
            mode: "lines",
            line: { color: "#00A0ff", width: 3, dash: "longdashdot" },
            name: "Z",
        }

        const trajectory: plotly.Data =
        {
            x: formOut.x,
            y: formOut.y,
            z: formOut.z,
            type: "scatter3d",
            mode: "lines",
            line: { color: "#ffffff", width: 3 },
            name: "Kinematics",
        }

        setKinematics([axisX, axisY, axisZ, trajectory])
    }, [formOut])

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
            let response: any = await http.api.put(`/tools/lvlh-kinematics`, formIn)

            const result: IFormOut = response.data

            setFormOut(result)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- RENDERING ---

    const layout: any = //plotly.Layout
    {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 50, r: 50, t: 50, b: 50 },
        title:
        {
            text: "LVLH Kinematics",
            font:
            {
                color: "#FFFFFF",
                size: 20,
                family: "Lucida Console"
            }
        },
        scene:
        {
            aspectmode: "data",
            xaxis: { visible: false },
            yaxis: { visible: false },
            zaxis: { visible: false }
        }
    }

    return (
        <DialogRUI
            title="LVLH Kinematics"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "LVLH Kinematics",
                    content:
                        `Given the state vectors of the target spacecraft and of the chaser spacecraft, find the
                        position, velocity, and acceleration of Chaser relative to Target along the
                        Local Vertical Local Horizontal (LVLH) axes attached to the Target.`
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

                <span className="col-span-3 text-center uppercase font-semibold">Target Orbital Elements</span>

                <InputField
                    name="orbitalElementsTarget.sma"
                    label="Semi-Major Axis"
                    unit="KM"
                    type="text"
                    value={String(formIn.orbitalElementsTarget.sma)}
                    onChange={handleChange}
                    pattern="^(?!0$).*"
                />

                <InputField
                    name="orbitalElementsTarget.ecc"
                    label="Eccentricity"
                    unit="KM"
                    value={formIn.orbitalElementsTarget.ecc}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    name="orbitalElementsTarget.inc"
                    label="Inclination"
                    unit="DEG"
                    value={formIn.orbitalElementsTarget.inc}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElementsTarget.raan"
                    label="RAAN"
                    unit="DEG"
                    value={formIn.orbitalElementsTarget.raan}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElementsTarget.aop"
                    label="Argument Periapsis"
                    unit="DEG"
                    value={formIn.orbitalElementsTarget.aop}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElementsTarget.ta"
                    label="True Anomaly"
                    unit="DEG"
                    value={formIn.orbitalElementsTarget.ta}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <span className="col-span-3 text-center uppercase font-semibold">Chaser Orbital Elements</span>

                <InputField
                    name="orbitalElementsChaser.sma"
                    label="Semi-Major Axis"
                    unit="KM"
                    type="text"
                    value={String(formIn.orbitalElementsChaser.sma)}
                    onChange={handleChange}
                    pattern="^(?!0$).*"
                />

                <InputField
                    name="orbitalElementsChaser.ecc"
                    label="Eccentricity"
                    unit="KM"
                    value={formIn.orbitalElementsChaser.ecc}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    name="orbitalElementsChaser.inc"
                    label="Inclination"
                    unit="DEG"
                    value={formIn.orbitalElementsChaser.inc}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElementsChaser.raan"
                    label="RAAN"
                    unit="DEG"
                    value={formIn.orbitalElementsChaser.raan}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElementsChaser.aop"
                    label="Argument Periapsis"
                    unit="DEG"
                    value={formIn.orbitalElementsChaser.aop}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElementsChaser.ta"
                    label="True Anomaly"
                    unit="DEG"
                    value={formIn.orbitalElementsChaser.ta}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

            </form.Root>

            {/* OUTPUT */}

            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Position Vector</span>

                <OutputField label="X" unit="KM" value={formOut.position.x} />

                <OutputField label="Y" unit="KM" value={formOut.position.y} />

                <OutputField label="Z" unit="KM" value={formOut.position.z} />

                <span className="col-span-3 text-center uppercase font-semibold">Velocity Vector</span>

                <OutputField label="X" unit="KM / S" value={formOut.velocity.x} />

                <OutputField label="Y" unit="KM / S" value={formOut.velocity.y} />

                <OutputField label="Z" unit="KM / S" value={formOut.velocity.z} />

                <span className="col-span-3 text-center uppercase font-semibold">Acceleration Vector</span>

                <OutputField label="X" unit="KM / S^2" value={formOut.acceleration.x} />

                <OutputField label="Y" unit="KM / S^2" value={formOut.acceleration.y} />

                <OutputField label="Z" unit="KM / S^2" value={formOut.acceleration.z} />

                <span className="col-span-3 text-center uppercase font-semibold">Angular Velocity Vector</span>

                <OutputField label="X" unit="DEG / S" value={formOut.angularVelocity.x} />

                <OutputField label="Y" unit="DEG / S" value={formOut.angularVelocity.y} />

                <OutputField label="Z" unit="DEG / S" value={formOut.angularVelocity.z} />

                <div className="col-span-full flex flex-col space-y-4 p-4">

                    <Plot
                        data={kinematics ?? []}
                        layout={layout}
                        style={{ width: "100%", height: "100%" }}
                    />

                </div>

            </form.Root>

        </DialogRUI>
    )
}