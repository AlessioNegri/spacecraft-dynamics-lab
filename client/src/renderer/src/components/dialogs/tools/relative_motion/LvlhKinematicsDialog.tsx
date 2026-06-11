import * as react from "react"
import * as form from "@radix-ui/react-form"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

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

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function LvlhKinematicsDialog */
export default function LvlhKinematicsDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [kinematics, setKinematics] = react.useState<plotly.Data[]>()

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- USE MEMO ---

    const layout: any = react.useMemo(() => ( //plotly.Layout
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
    }), [])

    const axes = react.useMemo(() =>
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

        return [axisX, axisY, axisZ]
    }, [])

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
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

        setKinematics([...axes, trajectory])
    }, [axes, formOut])

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
            let response: any = await http.api.put(`/relative-motion/lvlh-kinematics`, formIn)

            const result: IFormOut = response.data

            setFormOut(result)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- RENDERING ---

    const config: any = //plotly.Config
    {
        responsive: true,
        displaylogo: false,
        scrollZoom: true
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
                className="grid grid-cols-2 gap-4 border-b pb-4 mb-4">

                <div className="col-span-full flex justify-center">

                    <InputField
                        className="w-[50%]"
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

                </div>

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Target Orbital Elements</span>

                    <InputField
                        name="orbitalElementsTarget.sma"
                        label="Semimajor Axis"
                        symbol="a"
                        unit="km"
                        type="text"
                        value={String(formIn.orbitalElementsTarget.sma)}
                        onChange={handleChange}
                        pattern="^(?!0$).*"
                        tooltip
                    />

                    <InputField
                        name="orbitalElementsTarget.ecc"
                        label="Eccentricity"
                        symbol="e"
                        unit=""
                        value={formIn.orbitalElementsTarget.ecc}
                        onChange={handleChange}
                        min={0}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElementsTarget.inc"
                        label="Inclination"
                        symbol="i"
                        unit="deg"
                        value={formIn.orbitalElementsTarget.inc}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElementsTarget.raan"
                        label="Right Ascension of Ascending Node"
                        symbol="\Omega"
                        unit="deg"
                        value={formIn.orbitalElementsTarget.raan}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElementsTarget.aop"
                        label="Argument Of Periapsis"
                        symbol="\omega"
                        unit="deg"
                        value={formIn.orbitalElementsTarget.aop}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElementsTarget.ta"
                        label="True Anomaly"
                        symbol="\theta"
                        unit="deg"
                        value={formIn.orbitalElementsTarget.ta}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                </div>

                <div className="flex flex-col gap-4">

                    <span className="col-span-3 text-center uppercase font-semibold">Chaser Orbital Elements</span>

                    <InputField
                        name="orbitalElementsChaser.sma"
                        label="Semimajor Axis"
                        symbol="a"
                        unit="km"
                        type="text"
                        value={String(formIn.orbitalElementsChaser.sma)}
                        onChange={handleChange}
                        pattern="^(?!0$).*"
                        tooltip
                    />

                    <InputField
                        name="orbitalElementsChaser.ecc"
                        label="Eccentricity"
                        symbol="e"
                        unit=""
                        value={formIn.orbitalElementsChaser.ecc}
                        onChange={handleChange}
                        min={0}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElementsChaser.inc"
                        label="Inclination"
                        symbol="i"
                        unit="deg"
                        value={formIn.orbitalElementsChaser.inc}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElementsChaser.raan"
                        label="Right Ascension of Ascending Node"
                        symbol="\Omega"
                        unit="deg"
                        value={formIn.orbitalElementsChaser.raan}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElementsChaser.aop"
                        label="Argument Of Periapsis"
                        symbol="\omega"
                        unit="deg"
                        value={formIn.orbitalElementsChaser.aop}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElementsChaser.ta"
                        label="True Anomaly"
                        symbol="\theta"
                        unit="deg"
                        value={formIn.orbitalElementsChaser.ta}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                </div>

            </form.Root>

            {/* OUTPUT */}

            <form.Root className="grid grid-cols-[120px_1fr_1fr_1fr] gap-4 mb-4 items-center">

                <span className="text-center uppercase font-semibold text-xs">Position</span>

                <OutputField symbol="r_x" unit="km" value={formOut.position.x} />

                <OutputField symbol="r_y" unit="km" value={formOut.position.y} />

                <OutputField symbol="r_z" unit="km" value={formOut.position.z} />

                <span className="text-center uppercase font-semibold text-xs">Velocity</span>

                <OutputField symbol="v_x" unit="km / s" value={formOut.velocity.x} />

                <OutputField symbol="v_y" unit="km / s" value={formOut.velocity.y} />

                <OutputField symbol="v_z" unit="km / s" value={formOut.velocity.z} />

                <span className="text-center uppercase font-semibold text-xs">Acceleration</span>

                <OutputField symbol="a_x" unit="km / s^2" value={formOut.acceleration.x} />

                <OutputField symbol="a_y" unit="km / s^2" value={formOut.acceleration.y} />

                <OutputField symbol="a_z" unit="km / s^2" value={formOut.acceleration.z} />

                <span className="text-center uppercase font-semibold text-xs">Angular Velocity</span>

                <OutputField symbol="\Omega_x" unit="deg / s" value={formOut.angularVelocity.x} />

                <OutputField symbol="\Omega_y" unit="deg / s" value={formOut.angularVelocity.y} />

                <OutputField symbol="\Omega_z" unit="deg / s" value={formOut.angularVelocity.z} />

            </form.Root>

            <Plot
                className="border-2 border-neutral-300 rounded-xl"
                data={kinematics ?? []}
                layout={layout}
                config={config}
                style={{ width: "100%", height: "500px" }}
            />

        </DialogRUI>
    )
}