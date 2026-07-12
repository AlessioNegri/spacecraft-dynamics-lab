import * as react from "react"
import * as iconify from "@iconify/react"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"

import http from "@renderer/common/http"

import Tooltip from "@renderer/components/Tooltip"
import InputField from "@renderer/components/dialogs/InputField"

const defaultIn: IRelativeMotionFormInput =
{
    attractor: "earth",
    orbitalElementsTarget: {
        sam: 0,
        sma: 6678,
        ecc: 0,
        inc: 40,
        raan: 20,
        aop: 0,
        ta: 60
    },
    orbitalElementsChaser: {
        sam: 0,
        sma: 6795,
        ecc: 0.01426028,
        inc: 40.13,
        raan: 19.819,
        aop: 70.662,
        ta: 349.65
    },
    integrationTime: 0.5,
    maneuverTime: 8
}

interface Props
{
    onHide: (hide: boolean) => void
    onSolutionsChange: (solutions: IRelativeMotionFormOutput) => void
}

/** @function LeftPanel */
export default function LeftPanel(props: Readonly<Props>): react.JSX.Element
{
    // --- USE EFFECT ---

    const [hide, setHide] = react.useState<boolean>(false)

    const [formIn, setFormIn] = react.useState<IRelativeMotionFormInput>(defaultIn)

    // --- USE EFFECT ---
    
    react.useEffect(() => { props.onHide(hide) }, [hide])

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

    const handleRun = async (e: react.MouseEvent<HTMLButtonElement>) =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.put('/relative-motion/comparison', formIn)

            const result: IRelativeMotionFormOutput = response.data

            props.onSolutionsChange(result)
        }
        catch (err)
        {
            http.checkError(new URL(import.meta.url).pathname.split('?')[0], err)
        }
    }

    // --- RENDERING ---

    return (
        <div className="w-full h-full p-4 overflow-y-auto custom-scrollbar space-y-6 relative">
                
            <Tooltip title={hide ? "Show" : "Hide"} side="top">

                <iconify.Icon
                    icon={hide ? "tabler:layout-sidebar" : "tabler:layout-sidebar-filled"}
                    width={20}
                    className="absolute top-2 right-2 cursor-pointer hover:text-orange-300"
                    onClick={() => setHide(prev => !prev)}
                />

            </Tooltip>

        {
                !hide && 

                <Form.Root className="space-y-6">

                    <div className="flex space-x-4 justify-center items-center">

                        <iconify.Icon icon="game-icons:orbit" width={32} />

                        <span className="font-bold">TARGET ORBIT</span>

                    </div>

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
                        name="integrationTime"
                        label="Integration Time"
                        symbol="t_{int}"
                        unit="hours"
                        value={formIn.integrationTime}
                        onChange={handleChange}
                        min={0.1}
                    />

                    <InputField
                        name="orbitalElementsTarget.sma"
                        label="Semimajor Axis"
                        symbol="a"
                        unit="km"
                        value={formIn.orbitalElementsTarget.sma}
                        onChange={handleChange}
                        pattern="^(?!0$).*"
                        tooltip
                    />

                    <InputField
                        type="number"
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
                        min={0}
                        max={180}
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
                        label="Argument of Periapsis"
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

                    <div className="flex space-x-4 justify-center items-center">

                        <iconify.Icon icon="game-icons:orbit" width={32} />

                        <span className="font-bold">CHASER ORBIT</span>

                    </div>

                    <InputField
                        name="orbitalElementsChaser.sma"
                        label="Semimajor Axis"
                        symbol="a"
                        unit="km"
                        value={formIn.orbitalElementsChaser.sma}
                        onChange={handleChange}
                        pattern="^(?!0$).*"
                        tooltip
                    />

                    <InputField
                        type="number"
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
                        min={0}
                        max={180}
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
                        label="Argument of Periapsis"
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

                    <div className="flex space-x-4 justify-center items-center">

                        <iconify.Icon icon="game-icons:rocket-thruster" width={32} />

                        <span className="font-bold">2-IMPULSIVE MANEUVER</span>

                    </div>

                    <InputField
                        type="number"
                        name="maneuverTime"
                        label="Maneuver Time"
                        symbol="t_{man}"
                        unit="hours"
                        value={formIn.maneuverTime}
                        onChange={handleChange}
                        min={1}
                    />

                    <div className="flex justify-center">

                        <Themes.Button variant="outline" color="orange" onClick={handleRun}>
                            Run Simulation
                        </Themes.Button>

                    </div>

                </Form.Root>
            }

        </div>
    )
}
