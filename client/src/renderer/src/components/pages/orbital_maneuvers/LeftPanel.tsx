import * as react from "react"
import * as iconify from "@iconify/react"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"

import http from "@renderer/common/http"

import Tooltip from "@renderer/components/Tooltip"
import InputField from "@renderer/components/dialogs/InputField"
import ErrorText from "@renderer/components/dialogs/ErrorText"

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
        dm: 0,
        burnTime: 0
    },
    initialOrbit: [],
    transferOrbit: [],
    finalOrbit: []
}

interface Props
{
    onHide: (hide: boolean) => void
    onOrbitsChange: (orbits: IOrbits) => void
    onResultChange: (result: IOrbitalManeuverFormOutput) => void
}

/** @function LeftPanel */
export default function LeftPanel(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [hide, setHide] = react.useState<boolean>(false)

    const [formIn, setFormIn] = react.useState<IOrbitalManeuverFormInput>(defaultIn)

    const [formOut, setFormOut] = react.useState<IOrbitalManeuverFormOutput>(defaultOutput)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    // --- USE EFFECT ---

    react.useEffect(() => { props.onHide(hide) }, [hide])

    // --- HANDLE ---

    const validate = () : boolean =>
    {
        const newErrors: Record<string, string> = {}

        if (formIn.maneuver.type === "non-hohmann")
        {
            const data: INonHohmann = formIn.maneuver.data as INonHohmann

            if (data.targetTrueAnomaly - formIn.orbitalElements.ta < 15)
            {
                newErrors.generic = "Target true anomaly should be at least 15 degress ahead"
            }
        }

        if (formIn.maneuver.type === "coplanar-circle-circle" ||
            formIn.maneuver.type === "inclination-change-non-impulsive")
        {
            if (Math.abs(formIn.orbitalElements.ecc) > 1e-6)
            {
                newErrors.eccentricity = "Initial orbit should be circular"
            }
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

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

        if (!validate()) return

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

            props.onResultChange(result)
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

                        <iconify.Icon icon="emojione-monotone:satellite" width={32} />

                        <span className="font-bold">SPACECRAFT</span>

                    </div>

                    <InputField
                        type="number"
                        name="spacecraft.mass"
                        label="Spacecraft Mass"
                        symbol="m_{SC}"
                        unit="kg"
                        value={formIn.spacecraft.mass}
                        onChange={handleChange}
                        min={1}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="spacecraft.specificImpulse"
                        label="Specific Impulse"
                        symbol="I_{SP}"
                        unit="s"
                        value={formIn.spacecraft.specificImpulse}
                        onChange={handleChange}
                        min={1}
                        tooltip
                    />

                    <InputField
                        name="spacecraft.thrust"
                        label="Thrust"
                        symbol="T"
                        unit="N"
                        value={formIn.spacecraft.thrust}
                        onChange={handleChange}
                        min={1}
                        tooltip
                    />

                    <div className="flex space-x-4 justify-center items-center">

                        <iconify.Icon
                            icon="game-icons:orbit"
                            width={32}
                        />

                        <span className="font-bold">ORBIT</span>

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
                        name="orbitalElements.sma"
                        label="Semimajor Axis"
                        symbol="a"
                        unit="km"
                        value={formIn.orbitalElements.sma}
                        onChange={handleChange}
                        pattern="^(?!0$).*"
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElements.ecc"
                        label="Eccentricity"
                        symbol="e"
                        unit=""
                        value={formIn.orbitalElements.ecc}
                        onChange={handleChange}
                        min={0}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElements.inc"
                        label="Inclination"
                        symbol="i"
                        unit="deg"
                        value={formIn.orbitalElements.inc}
                        onChange={handleChange}
                        min={0}
                        max={180}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElements.raan"
                        label="Right Ascension of Ascending Node"
                        symbol="\Omega"
                        unit="deg"
                        value={formIn.orbitalElements.raan}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElements.aop"
                        label="Argument of Periapsis"
                        symbol="\omega"
                        unit="deg"
                        value={formIn.orbitalElements.aop}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                    <InputField
                        type="number"
                        name="orbitalElements.ta"
                        label="True Anomaly"
                        symbol="\theta"
                        unit="deg"
                        value={formIn.orbitalElements.ta}
                        onChange={handleChange}
                        min={-360}
                        max={360}
                        tooltip
                    />

                    { errors.eccentricity && <ErrorText text={errors.eccentricity} /> }

                    <div className="flex space-x-4 justify-center items-center">

                        <iconify.Icon
                            icon="game-icons:rocket-thruster"
                            width={32}
                        />

                        <span className="font-bold">MANEUVER</span>

                    </div>

                    <OrbitalManeuver
                        maneuver={formIn.maneuver}
                        result={formOut}
                        onChange={handleManeuverChange}
                    />

                    { errors.generic && <ErrorText text={errors.generic} /> }
                    
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
