import * as react from "react"
import * as form from "@radix-ui/react-form"
import * as themes from "@radix-ui/themes"
import * as iconify from "@iconify/react"

import http from "@renderer/common/http"
import InputField from "@renderer/components/dialogs/InputField"

import OrbitalManeuver from "./OrbitalManeuver"

const defaultIn: IOrbitalManeuverFormInput =
{
    spacecraft:
    {
        mass: 2000,
        specificImpulse: 300,
        thrust: 10000
    },
    attractor: "earth",
    orbitalElements:
    {
        sam: 0,
        sma: 10048,
        ecc: 0.1983,
        inc: 159.2479,
        raan: 79.7271,
        aop: 165.9057,
        ta: 74.9314
    },
    maneuver:
    {
        type: "hohmann",
        data:
        {
            sma: 34754,
            ecc: 0.1218,
            direction: 0
        }
    }
}

const defaultOutput: IOrbitalManeuverFormOutput =
{
    orbitalElements:
    {
        sam: 0,
        sma: 0,
        ecc: 0,
        inc: 0,
        raan: 0,
        aop: 0,
        ta: 0
    },
    maneuver:
    {
        dv: 0,
        dt: 0,
        dm: 0
    },
    initialOrbit: [],
    transferOrbit: [],
    finalOrbit: []
}

interface LeftPanelProps
{
    onOrbitsChange: (orbits: IOrbits) => void
}

/** @function LeftPanel */
export default function LeftPanel(props: Readonly<LeftPanelProps>): react.JSX.Element
{
    // --- USE EFFECT ---

    const [formIn, setFormIn] = react.useState<IOrbitalManeuverFormInput>(defaultIn)

    const [formOut, setFormOut] = react.useState<IOrbitalManeuverFormOutput>(defaultOutput)

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

    const handleManeuverChange = (maneuver: IOrbitalManeuver) =>
    {
        setFormIn({ ...formIn, maneuver: maneuver })
    }

    const handleRun = async (e: react.MouseEvent<HTMLButtonElement>) =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.put(`/orbital-maneuvers/${formIn.maneuver.type}`, formIn)

            const result: IOrbitalManeuverFormOutput = response.data

            props.onOrbitsChange(
            {
                initial: result.initialOrbit,
                transfer: result.transferOrbit,
                final: result.finalOrbit
            })
            
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
            className="w-[50%] h-full flex flex-col space-y-4 p-4 overflow-auto custom-scrollbar
                border-r border-neutral-700">

            <div className="grid grid-flow-row auto-rows-max grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

                <div className="flex space-x-4 col-span-full justify-center items-center">

                    <iconify.Icon
                        icon="emojione-monotone:satellite"
                        width={48}
                    />

                    <span className="font-bold">SPACECRAFT</span>

                </div>

                <InputField
                    name="spacecraft.mass"
                    label="Spacecraft Mass"
                    unit="KG"
                    value={formIn.spacecraft.mass}
                    onChange={handleChange}
                />

                <InputField
                    name="spacecraft.specificImpulse"
                    label="Specific Impulse"
                    unit="S"
                    value={formIn.spacecraft.specificImpulse}
                    onChange={handleChange}
                />

                <InputField
                    name="spacecraft.thrust"
                    label="Thrust"
                    unit="N"
                    value={formIn.spacecraft.thrust}
                    onChange={handleChange}
                />

                <div className="flex space-x-4 col-span-full justify-center items-center">

                    <iconify.Icon
                        icon="game-icons:orbit"
                        width={48}
                    />

                    <span className="font-bold">ORBIT</span>

                </div>

                <InputField
                    className=""
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

                <span></span>

                <span></span>

                <InputField
                    name="orbitalElements.sma"
                    label="Semi-Major Axis"
                    unit="KM"
                    type="text"
                    value={formIn.orbitalElements.sma}
                    onChange={handleChange}
                    pattern="^(?!0$).*"
                />

                <InputField
                    name="orbitalElements.ecc"
                    label="Eccentricity"
                    unit="KM"
                    value={formIn.orbitalElements.ecc}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    name="orbitalElements.inc"
                    label="Inclination"
                    unit="DEG"
                    value={formIn.orbitalElements.inc}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElements.raan"
                    label="RAAN"
                    unit="DEG"
                    value={formIn.orbitalElements.raan}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElements.aop"
                    label="Argument Periapsis"
                    unit="DEG"
                    value={formIn.orbitalElements.aop}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

                <InputField
                    name="orbitalElements.ta"
                    label="True Anomaly"
                    unit="DEG"
                    value={formIn.orbitalElements.ta}
                    onChange={handleChange}
                    min={-360}
                    max={360}
                />

            </div>

            <div className="flex space-x-4 col-span-full justify-center items-center">

                <iconify.Icon
                    icon="game-icons:rocket-thruster"
                    width={48}
                />

                <span className="font-bold">MANEUVER</span>

            </div>

            <OrbitalManeuver
                maneuver={formIn.maneuver}
                result={formOut}
                onChange={handleManeuverChange} />
                    
            <themes.Button variant="outline" color="orange" onClick={handleRun}>
                Run Simulation
            </themes.Button>

        </form.Root>
    )
}
