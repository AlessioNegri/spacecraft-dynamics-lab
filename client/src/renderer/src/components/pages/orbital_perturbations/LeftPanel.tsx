import * as react from "react"
import * as iconify from "@iconify/react"
import * as form from "@radix-ui/react-form"
import * as themes from "@radix-ui/themes"

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
        const rmRI = globalThis.window.callback.onReceivedInfo((info: WebSocketInfo) =>
        {
            if (info.source === "orbital-perturbations")
            {
                setRunning(info.running)
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
        <div className={`w-full h-full p-4 overflow-y-auto custom-scrollbar space-y-6 relative`}>

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
                
                <form.Root className="space-y-6">

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
                        value={formIn.startDate}
                        onChange={handleChange}
                    />
    
                    <InputField
                        label="End Date"
                        type="datetime-local"
                        name="endDate"
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

                    <div>
                        <themes.Text as="label" size="2">
                            <themes.Flex as="span" gap="2">
                                <themes.Checkbox
                                    size="3"
                                    variant="soft"
                                    checked={formIn.atmosphericDrag}
                                    onCheckedChange={(checked) => {
                                        setFormIn({ ...formIn, atmosphericDrag: checked as boolean });
                                    }} /> Atmospheric Drag
                            </themes.Flex>
                        </themes.Text>
                    </div>

                    <InputField
                        name="ballisticCoefficient"
                        label="Ballistic Coefficient"
                        unit="M^2 / KG"
                        value={formIn.ballisticCoefficient}
                        onChange={handleChange}
                        min={0}
                        disabled={!formIn.atmosphericDrag}
                    />

                    <div>
                        <themes.Text as="label" size="2">
                            <themes.Flex as="span" gap="2">
                                <themes.Checkbox
                                    size="3"
                                    variant="soft"
                                    checked={formIn.gravitationalPerturbation}
                                    onCheckedChange={(checked) => {
                                        setFormIn({ ...formIn, gravitationalPerturbation: checked as boolean });
                                    }} /> Gravitational Perturbation
                            </themes.Flex>
                        </themes.Text>
                    </div>

                    <div>
                        <themes.Text as="label" size="2">
                            <themes.Flex as="span" gap="2">
                                <themes.Checkbox
                                    size="3"
                                    variant="soft"
                                    checked={formIn.solarRadiationPressure}
                                    onCheckedChange={(checked) => {
                                        setFormIn({ ...formIn, solarRadiationPressure: checked as boolean });
                                    }} /> Solar Radiation Pressure
                            </themes.Flex>
                        </themes.Text>
                    </div>

                    <InputField
                        name="ballisticCoefficientSRP"
                        label="Ballistic Coefficient (SRP)"
                        unit="M^2 / KG"
                        value={formIn.ballisticCoefficientSRP}
                        onChange={handleChange}
                        min={0}
                        disabled={!formIn.solarRadiationPressure}
                    />

                    <div>
                        <themes.Text as="label" size="2">
                            <themes.Flex as="span" gap="2">
                                <themes.Checkbox
                                    size="3"
                                    variant="soft"
                                    checked={formIn.lunarGravity}
                                    onCheckedChange={(checked) => {
                                        setFormIn({ ...formIn, lunarGravity: checked as boolean });
                                    }} /> Lunar Gravity
                            </themes.Flex>
                        </themes.Text>
                    </div>

                    <div>
                        <themes.Text as="label" size="2">
                            <themes.Flex as="span" gap="2">
                                <themes.Checkbox
                                    size="3"
                                    variant="soft"
                                    checked={formIn.solarGravity}
                                    onCheckedChange={(checked) => {
                                        setFormIn({ ...formIn, solarGravity: checked as boolean });
                                    }} /> Solar Gravity
                            </themes.Flex>
                        </themes.Text>
                    </div>

                    {/* Buttons */}
                    
                    <div className="flex justify-between">
        
                        <themes.Button color="green" variant="outline" disabled={running} onClick={handleSubmit}>
                            Run Analysis
                        </themes.Button>
        
                        <themes.Button color="red" variant="outline" disabled={!running} onClick={handleStop}>
                            Stop Analysis
                        </themes.Button>
        
                    </div>

                </form.Root>
            }

        </div>
    )
}
