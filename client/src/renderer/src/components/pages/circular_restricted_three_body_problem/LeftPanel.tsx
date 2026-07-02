import * as react from "react"
import * as iconify from "@iconify/react"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"

import http from "@renderer/common/http"

import Tooltip from "@renderer/components/Tooltip"
import InputField from "@renderer/components/dialogs/InputField"

const defaultForm: ICircularRestrictedThreeBodyProblemForm =
{
    body1: "earth",
    body2: "moon",
    integrationTime: 2400,
    lagrangePoint: "L1",
    position:
    {
        x: 0,
        y: 0,
        z: 0
    },
    velocity:
    {
        x: 0,
        y: 0,
        z: 0.03
    }
}

interface Props
{
    onHide: (hide: boolean) => void
    onSelectedLagrangePoint: (point: string) => void
}

/** @function LeftPanel */
export default function LeftPanel(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [hide, setHide] = react.useState<boolean>(false)
        
    const [formIn, setFormIn] = react.useState<ICircularRestrictedThreeBodyProblemForm>(defaultForm)

    const [running, setRunning] = react.useState<boolean>(false)

    // --- USE EFFECT ---
        
    react.useEffect(() =>
    {
        const rmRI = globalThis.window.callback.onWebSocketSimulation((sim: WebSocketSimulation) =>
        {
            if (sim.source === "circular-restricted-three-body-problem")
            {
                setRunning(sim.running)
            }
        })

        return () => { rmRI() }
    }, [])

    react.useEffect(() => { props.onHide(hide) }, [hide])

    react.useEffect(() =>
    {
        if (formIn.body1 === "sun")
        {
            setFormIn(prev => ({ ...prev, body2: "earth" }))
        }
        else if (formIn.body1 === "earth")
        {
            setFormIn(prev => ({ ...prev, body2: "moon" }))
        }
    }, [formIn.body1])

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

    const handleSubmit = async (e: react.MouseEvent<HTMLButtonElement, MouseEvent>) =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.post(`/circular-restricted-three-body-problem/run`, formIn)

            globalThis.window.api.info(`[${import.meta.url}] ${JSON.stringify(response.data)}`)

            props.onSelectedLagrangePoint(formIn.lagrangePoint)
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

                    {/* Bodies */}
                    
                    <div className="flex space-x-4 col-span-full justify-center items-center">
                    
                        <iconify.Icon
                            icon="game-icons:solar-system"
                            width={32}
                        />
    
                        <span className="font-bold">BODIES</span>
    
                    </div>

                    <InputField
                        name="body1"
                        label="Primary Body"
                        type="select"
                        value={formIn.body1}
                        onChange={handleChange}
                        options={
                            [
                                { label: "Sun", value: "sun" },
                                { label: "Earth", value: "earth" }
                            ]}
                    />
    
                    <InputField
                        name="body2"
                        label="Secondary Body"
                        type="select"
                        value={formIn.body2}
                        onChange={handleChange}
                        options={
                            formIn.body1 === "sun"
                                ? [
                                    { label: "Mercury", value: "mercury" },
                                    { label: "Venus", value: "venus" },
                                    { label: "Earth", value: "earth" },
                                    { label: "Mars", value: "mars" },
                                    { label: "Jupiter", value: "jupiter" },
                                    { label: "Saturn", value: "saturn" },
                                    { label: "Uranus", value: "uranus" },
                                    { label: "Neptune", value: "neptune" }
                                ]
                                : [
                                    { label: "Moon", value: "moon" }
                                ]}
                    />

                    <div className="flex space-x-4 col-span-full justify-center items-center">
                    
                        <iconify.Icon
                            icon="gis:position"
                            width={32}
                        />
    
                        <span className="font-bold">RELATIVE POSITION VECTOR</span>
    
                    </div>

                    <InputField
                        name="lagrangePoint"
                        label="Lagrange Point"
                        type="select"
                        value={formIn.lagrangePoint}
                        onChange={handleChange}
                        options={
                            [
                                { label: "L1", value: "L1" },
                                { label: "L2", value: "L2" },
                                { label: "L3", value: "L3" },
                                { label: "L4", value: "L4" },
                                { label: "L5", value: "L5" }
                            ]}
                    />

                    <InputField
                        name="position.x"
                        symbol="r_x"
                        unit="km"
                        value={formIn.position.x}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position.y"
                        symbol="r_y"
                        unit="km"
                        value={formIn.position.y}
                        onChange={handleChange}
                    />

                    <InputField
                        name="position.z"
                        symbol="r_z"
                        unit="km"
                        value={formIn.position.z}
                        onChange={handleChange}
                    />

                    <div className="flex space-x-4 col-span-full justify-center items-center">
                    
                        <iconify.Icon
                            icon="material-symbols:speed"
                            width={32}
                        />
    
                        <span className="font-bold">VELOCITY VECTOR</span>
    
                    </div>

                    <InputField
                        name="velocity.x"
                        symbol="v_x"
                        unit="km/s"
                        value={formIn.velocity.x}
                        onChange={handleChange}
                    />

                    <InputField
                        name="velocity.y"
                        symbol="v_y"
                        unit="km/s"
                        value={formIn.velocity.y}
                        onChange={handleChange}
                    />

                    <InputField
                        name="velocity.z"
                        symbol="v_z"
                        unit="km/s"
                        value={formIn.velocity.z}
                        onChange={handleChange}
                    />

                    {/* Settings */}
                    
                    <div className="flex space-x-4 col-span-full justify-center items-center">
                    
                        <iconify.Icon
                            icon="mdi:settings"
                            width={32}
                        />
    
                        <span className="font-bold">SETTINGS</span>
    
                    </div>

                    <InputField
                        name="integrationTime"
                        label="Integration Time"
                        symbol="t_{int}"
                        unit="hours"
                        value={formIn.integrationTime}
                        onChange={handleChange}
                        min={1}
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
