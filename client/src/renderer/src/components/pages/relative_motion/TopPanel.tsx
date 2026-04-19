import * as react from "react"
import * as form from "@radix-ui/react-form"
import * as themes from "@radix-ui/themes"
import * as iconify from "@iconify/react"

import http from "@renderer/common/http"

import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

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

const defaultOut: IRelativeMotionFormOutput =
{
    linearizedSolution: [],
    clohessyWiltshireSolution: [],
    twoImpulsiveManeuver: [],
    twoImpulsiveManeuverCost: 0
}

interface Props
{
    onSolutionsChange: (solutions: IRelativeMotionFormOutput) => void
}

/** @function TopPanel */
export default function TopPanel(props: Readonly<Props>): react.JSX.Element
{
    // --- USE EFFECT ---

    const [formIn, setFormIn] = react.useState<IRelativeMotionFormInput>(defaultIn)

    const [formOut, setFormOut] = react.useState<IRelativeMotionFormOutput>(defaultOut)

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
            
            setFormOut(result)
        }
        catch (err)
        {
            http.checkError(new URL(import.meta.url).pathname.split('?')[0], err)
        }
    }

    // --- RENDERING ---

    return (
        <form.Root
            className="w-full h-[50%] flex flex-col space-y-4 p-4 overflow-auto custom-scrollbar
                    border-b border-neutral-700">

            <div className="grid grid-flow-row auto-rows-max grid-cols-6 gap-4">

                <div className="flex space-x-4 col-span-full justify-center items-center">

                    <iconify.Icon
                        icon="game-icons:orbit"
                        width={48}
                    />

                    <span className="font-bold">TARGET ORBIT</span>

                </div>

                <InputField
                    className="col-span-3 mx-auto w-64"
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
                    className="col-span-3 mx-auto w-64"
                    name="integrationTime"
                    label="Integration Time"
                    unit="H"
                    value={formIn.integrationTime}
                    onChange={handleChange}
                    min={0.1}
                />

                <InputField
                    name="orbitalElementsTarget.sma"
                    label="Semi-Major Axis"
                    unit="KM"
                    type="text"
                    value={formIn.orbitalElementsTarget.sma}
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

            </div>

            <div className="grid grid-flow-row auto-rows-max grid-cols-6 gap-4">

                <div className="flex space-x-4 col-span-full justify-center items-center">

                    <iconify.Icon
                        icon="game-icons:orbit"
                        width={48}
                    />

                    <span className="font-bold">CHASER ORBIT</span>

                </div>

                <InputField
                    name="orbitalElementsChaser.sma"
                    label="Semi-Major Axis"
                    unit="KM"
                    type="text"
                    value={formIn.orbitalElementsChaser.sma}
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

            </div>

            <div className="grid grid-flow-row auto-rows-max grid-cols-6 gap-4">

                <div className="flex space-x-4 col-span-full justify-center items-center">

                    <iconify.Icon
                        icon="game-icons:rocket-thruster"
                        width={48}
                    />

                    <span className="font-bold">2-IMPULSIVE MANEUVER</span>

                </div>

                <InputField
                    className="col-span-3 mx-auto w-64"
                    name="maneuverTime"
                    label="Maneuver Time"
                    unit="H"
                    type="number"
                    value={formIn.maneuverTime}
                    onChange={handleChange}
                    min={1}
                />

                <OutputField
                    label="Δv"
                    unit="M / S"
                    value={formOut.twoImpulsiveManeuverCost}
                />

            </div>

            <themes.Button variant="outline" color="orange" onClick={handleRun}>
                Run Simulation
            </themes.Button>

        </form.Root>
    )
}
