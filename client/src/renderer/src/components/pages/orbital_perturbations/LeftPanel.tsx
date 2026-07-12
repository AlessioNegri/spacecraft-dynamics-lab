import * as react from "react"
import * as iconify from "@iconify/react"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"

import http from "@renderer/common/http"

import Tooltip from "@renderer/components/Tooltip"
import InputField from "@renderer/components/dialogs/InputField"

const defaultForm: IOrbitalPerturbationsForm =
{
    orbitalElements:
    {
        sam: 55839,//69084.1,
        sma: 8059,//26553.4,
        ecc: 0.17136,//0.741,
        inc: 28,//63.4,
        raan: 45,//0,
        aop: 30,//270,
        ta: 40,//0
    },
    startDate: "2026-01-01T14:45:30",
    endDate: "2026-01-03T14:45:30",
    atmosphericDrag: true,
    ballisticCoefficient: 0.017,
    gravitationalPerturbation: true,
    solarRadiationPressure: true,
    ballisticCoefficientSRP: 4,
    lunarGravity: true,
    solarGravity: true
}

interface Props
{
    onHide: (hide: boolean) => void
}

/** @function LeftPanel */
export default function LeftPanel(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [hide, setHide] = react.useState<boolean>(false)
        
    const [formIn, setFormIn] = react.useState<IOrbitalPerturbationsForm>(defaultForm)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    const [running, setRunning] = react.useState<boolean>(false)

    // --- USE EFFECT ---
    
    react.useEffect(() =>
    {
        const rmRI = globalThis.window.callback.onWebSocketSimulation((sim: WebSocketSimulation) =>
        {
            if (sim.source === "orbital-perturbations")
            {
                setRunning(sim.running)
            }
        })

        return () => { rmRI() }
    }, [])

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

    const validate = () =>
    {
        const newErrors: Record<string, string> = {}

        if (formIn.startDate >= formIn.endDate) newErrors.dates = "Start date must be before end date"

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async (e: react.MouseEvent<HTMLButtonElement, MouseEvent>) =>
    {
        e.preventDefault()

        if (!validate()) return

        try
        {
            let response: any = await http.api.post(`/orbital-perturbations/run`, formIn)

            globalThis.window.api.info(`[${import.meta.url}] ${JSON.stringify(response.data)}`)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    const handleStop = async (e: react.MouseEvent<HTMLButtonElement, MouseEvent>) =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.put(`/ws/stop-simulation`)

            globalThis.window.api.info(`[${import.meta.url}] ${JSON.stringify(response.data)}`)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
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

                    {/* Orbital Elements */}

                    <div className="flex space-x-4 col-span-full justify-center items-center">

                        <iconify.Icon
                            icon="game-icons:orbit"
                            width={32}
                        />

                        <span className="font-bold">ORBITAL ELEMENTS</span>

                    </div>

                    <InputField
                        name="orbitalElements.sma"
                        label="Semimajor Axis"
                        symbol="a"
                        unit="km"
                        type="text"
                        value={formIn.orbitalElements.sma}
                        onChange={handleChange}
                        pattern="^(?!0$).*"
                        tooltip
                    />

                    <InputField
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

                    {/* Dates */}

                    <div className="flex space-x-4 col-span-full justify-center items-center">

                        <iconify.Icon
                            icon="clarity:date-solid"
                            width={32}
                        />

                        <span className="font-bold">DATES</span>

                    </div>

                    <InputField
                        label="Start Date"
                        type="datetime-local"
                        name="startDate"
                        symbol="t_0"
                        value={formIn.startDate}
                        onChange={handleChange}
                    />
    
                    <InputField
                        label="End Date"
                        type="datetime-local"
                        name="endDate"
                        symbol="t_f"
                        value={formIn.endDate}
                        onChange={handleChange}
                    />

                    {
                        errors.dates && <p className="text-red-400 text-sm">{errors.dates}</p>
                    }

                    {/* Perturbations */}

                    <div className="flex space-x-4 col-span-full justify-center items-center">

                        <iconify.Icon
                            icon="mdi:tune"
                            width={32}
                        />

                        <span className="font-bold">PERTURBATIONS</span>

                    </div>

                    <PerturbationToggle
                        label="Atmospheric Drag"
                        value={formIn.atmosphericDrag}
                        onChange={(checked: boolean) => setFormIn({ ...formIn, atmosphericDrag: checked })}
                    />

                    <InputField
                        name="ballisticCoefficient"
                        label="Ballistic Coefficient (Drag)"
                        symbol="B_{DRG}"
                        unit="m^2 / kg"
                        value={formIn.ballisticCoefficient}
                        onChange={handleChange}
                        min={0}
                        disabled={!formIn.atmosphericDrag}
                    />

                    <PerturbationToggle
                        label="Gravitational Perturbation"
                        value={formIn.gravitationalPerturbation}
                        onChange={(checked: boolean) => setFormIn({ ...formIn, gravitationalPerturbation: checked })}
                    />

                    <PerturbationToggle
                        label="Solar Radiation Pressure"
                        value={formIn.solarRadiationPressure}
                        onChange={(checked: boolean) => setFormIn({ ...formIn, solarRadiationPressure: checked })}
                    />

                    <InputField
                        name="ballisticCoefficientSRP"
                        label="Ballistic Coefficient (SRP)"
                        symbol="B_{SRP}"
                        unit="m^2 / kg"
                        value={formIn.ballisticCoefficientSRP}
                        onChange={handleChange}
                        min={0}
                        disabled={!formIn.solarRadiationPressure}
                    />

                    <PerturbationToggle
                        label="Lunar Gravity"
                        value={formIn.lunarGravity}
                        onChange={(checked: boolean) => setFormIn({ ...formIn, lunarGravity: checked })}
                    />

                    <PerturbationToggle
                        label="Solar Gravity"
                        value={formIn.solarGravity}
                        onChange={(checked: boolean) => setFormIn({ ...formIn, solarGravity: checked })}
                    />

                    {/* Buttons */}
                    
                    <div className="flex justify-between">
        
                        <Themes.Button color="green" variant="outline" disabled={running} onClick={handleSubmit}>
                            Run Analysis
                        </Themes.Button>
        
                        <Themes.Button color="red" variant="outline" disabled={!running} onClick={handleStop}>
                            Stop Analysis
                        </Themes.Button>
        
                    </div>

                </Form.Root>
            }

        </div>
    )
}

interface PerturbationToggleProps
{
    label: string
    value: boolean
    onChange: (checked: boolean) => void
}

/** @function PerturbationToggle */
function PerturbationToggle(props: Readonly<PerturbationToggleProps>): react.JSX.Element
{
    return (
        <div>

            <Themes.Text as="label" size="2">

                <Themes.Flex as="span" gap="2">

                <Themes.Checkbox
                    size="3"
                    variant="soft"
                    checked={props.value}
                    onCheckedChange={(checked) => props.onChange(checked as boolean)}
                />

                {props.label}

                </Themes.Flex>

            </Themes.Text>

        </div>
    )
}
