import * as react from "react"
import * as iconify from "@iconify/react"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"

import http from "@renderer/common/http"

import Tooltip from "@renderer/components/Tooltip"
import InputField from "@renderer/components/dialogs/InputField"
import ErrorText from "@renderer/components/dialogs/ErrorText"

const defaultMission: IInterplanetaryMissionForm =
{
    departureBody: "earth",
    flybyBody: " ",
    arrivalBody: "mars",//"neptune",
    launchWindowStart: "2005-05-03",//"2020-01-01",
    launchWindowEnd: "2005-11-06",//"2021-12-31",
    flybyWindowStart: "2005-10-01",//"2025-01-01",
    flybyWindowEnd: "2005-12-31",//"2025-12-31",
    arrivalWindowStart: "2005-11-26",//"2030-01-01",
    arrivalWindowEnd: "2007-02-19",//"2040-12-31",
    gridSize: 1
}

interface Props
{
    onBodies: (departure: string, flyby: string, arrival: string) => void
    onHide: (hide: boolean) => void
}

/** @function InterplanetaryLeftBar */
export default function InterplanetaryLeftBar(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [hide, setHide] = react.useState<boolean>(false)
    
    const [formIn, setFormIn] = react.useState<IInterplanetaryMissionForm>(defaultMission)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    const [running, setRunning] = react.useState<boolean>(false)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmRI = globalThis.window.callback.onWebSocketSimulation((sim: WebSocketSimulation) =>
        {
            if (sim.source === "interplanetary")
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

        setFormIn({ ...formIn, [name]: value })
    }

    const validate = () =>
    {
        const newErrors: Record<string, string> = {}

        if (formIn.departureBody === formIn.arrivalBody)    newErrors.bodies = "Choose different bodies"
        if (formIn.flybyBody === formIn.departureBody)      newErrors.bodies = "Choose different bodies"
        if (formIn.flybyBody === formIn.arrivalBody)        newErrors.bodies = "Choose different bodies"

        if (!formIn.launchWindowStart)    newErrors.windows = "Choose valid launch start window"
        if (!formIn.launchWindowEnd)      newErrors.windows = "Choose valid launch end window"
        if (!formIn.flybyWindowStart)     newErrors.windows = "Choose valid launch start window"
        if (!formIn.flybyWindowEnd)       newErrors.windows = "Choose valid launch end window"
        if (!formIn.arrivalWindowStart)   newErrors.windows = "Choose valid arrival start window"
        if (!formIn.arrivalWindowEnd)     newErrors.windows = "Choose valid arrival end window"

        if (formIn.launchWindowStart >= formIn.launchWindowEnd)
            newErrors.windows = "Launch window start < launch window end"

        if (formIn.arrivalWindowStart >= formIn.arrivalWindowEnd)
            newErrors.windows = "Arrival window start < arrival window end"

        if (formIn.launchWindowStart >= formIn.arrivalWindowStart)
            newErrors.windows = "Launch window start < arrival window start"
        
        if (formIn.flybyBody.trim() !== "")
        {
            if (formIn.flybyWindowStart >= formIn.flybyWindowEnd)
                newErrors.windows = "Flyby window start < flyby window end"

            if (formIn.flybyWindowStart >= formIn.arrivalWindowStart)
                newErrors.windows = "Flyby window start < arrival window start"

            if (formIn.launchWindowStart >= formIn.flybyWindowStart)
                newErrors.windows = "Launch window start < flyby window start"
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async (e: react.MouseEvent<HTMLButtonElement, MouseEvent>) =>
    {
        e.preventDefault()

        if (!validate()) return

        props.onBodies(formIn.departureBody, formIn.flybyBody.trim(), formIn.arrivalBody)

        try
        {
            let response: any = await http.api.post(`/interplanetary/run`, formIn)

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

                {/* Bodies */}

                <div className="flex space-x-4 col-span-full justify-center items-center">
                
                    <iconify.Icon
                        icon="game-icons:solar-system"
                        width={32}
                    />

                    <span className="font-bold">BODIES</span>

                </div>

                <InputField
                    label="Departure Body"
                    name="departureBody"
                    type="select"
                    value={formIn.departureBody}
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
                    label="Flyby Body"
                    name="flybyBody"
                    type="select"
                    value={formIn.flybyBody}
                    onChange={handleChange}
                    options={
                        [
                            { label: "None", value: " " },
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
                    label="Arrival Body"
                    name="arrivalBody"
                    type="select"
                    value={formIn.arrivalBody}
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

                { errors.bodies && <ErrorText text={errors.bodies} /> }

                {/* Date Ranges */}

                <div className="flex space-x-4 col-span-full justify-center items-center">
                
                    <iconify.Icon
                        icon="clarity:date-solid"
                        width={32}
                    />

                    <span className="font-bold">DATES</span>

                </div>

                <InputField
                    label="Launch Window Start"
                    type="date"
                    name="launchWindowStart"
                    symbol="t_0^{LW}"
                    value={formIn.launchWindowStart}
                    onChange={handleChange}
                />

                <InputField
                    label="Launch Window End"
                    type="date"
                    name="launchWindowEnd"
                    symbol="t_f^{LW}"
                    value={formIn.launchWindowEnd}
                    onChange={handleChange}
                />

                {
                    formIn.flybyBody.trim() !== "" &&
                    
                    <>

                        <InputField
                            label="Flyby Window Start"
                            type="date"
                            name="flybyWindowStart"
                            symbol="t_0^{FB}"
                            value={formIn.flybyWindowStart}
                            onChange={handleChange}
                        />

                        <InputField
                            label="Flyby Window End"
                            type="date"
                            name="flybyWindowEnd"
                            symbol="t_f^{FB}"
                            value={formIn.flybyWindowEnd}
                            onChange={handleChange}
                        />

                    </>
                }

                <InputField
                    label="Arrival Window Start"
                    type="date"
                    name="arrivalWindowStart"
                    symbol="t_0^{AW}"
                    value={formIn.arrivalWindowStart}
                    onChange={handleChange}
                />

                <InputField
                    label="Arrival Window End"
                    type="date"
                    name="arrivalWindowEnd"
                    symbol="t_f^{AW}"
                    value={formIn.arrivalWindowEnd}
                    onChange={handleChange}
                />

                { errors.windows && <ErrorText text={errors.windows} /> }

                {/* Settings */}

                <div className="flex space-x-4 col-span-full justify-center items-center">
                
                    <iconify.Icon
                        icon="mdi:settings"
                        width={32}
                    />

                    <span className="font-bold">SETTINGS</span>

                </div>

                <InputField
                    type="number"
                    label="Grid Size"
                    name="gridSize"
                    symbol="s"
                    unit="days"
                    min={1}
                    max={200}
                    value={formIn.gridSize}
                    onChange={handleChange}
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
