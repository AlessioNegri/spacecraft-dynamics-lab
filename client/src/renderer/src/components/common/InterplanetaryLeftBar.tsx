import * as react from "react"

import api from "@renderer/common/api"
import checkError from "@renderer/common/error"

import FormSection from "../dialogs/FormSection"
import FormInput from "../dialogs/FormInput"
import FormSelect from "../dialogs/FormSelect"
import FormButton from "../dialogs/FormButton"

const defaultMission: IInterplanetaryMissionForm =
{
    departureBody: "earth",
    flybyBody: "",
    arrivalBody: "neptune",
    launchWindowStart: "2020-01-01",//new Date().toISOString().slice(0, 10),
    launchWindowEnd: "2021-12-31",//new Date().toISOString().slice(0, 10),
    flybyWindowStart: "2025-01-01",
    flybyWindowEnd: "2025-12-31",
    arrivalWindowStart: "2030-01-01",//new Date().toISOString().slice(0, 10),
    arrivalWindowEnd: "2040-12-31",//new Date().toISOString().slice(0, 10),
    gridSize: 1
}

/** @function InterplanetaryLeftBar */
export default function InterplanetaryLeftBar(): react.JSX.Element
{
    // --- USE STATE ---
    
    const [form, setForm] = react.useState<IInterplanetaryMissionForm>(defaultMission)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    const [running, setRunning] = react.useState<boolean>(false)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmRI = globalThis.window.callback.onReceivedInfo((info: WebSocketInfo) =>
        {
            if (info.source === "interplanetary")
            {
                setRunning(info.running)
            }
        })

        return () => { rmRI() }
    }, [])
    
    // --- HANDLE ---

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    {
        const { name, value } = e.target

        setForm({ ...form, [name]: value })
    }

    const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setForm({ ...form, [name]: value })
    }

    const validate = () =>
    {
        const newErrors: Record<string, string> = {}

        if (form.departureBody === form.arrivalBody)    newErrors.bodies = "Choose different bodies"
        if (form.flybyBody === form.departureBody)      newErrors.bodies = "Choose different bodies"
        if (form.flybyBody === form.arrivalBody)        newErrors.bodies = "Choose different bodies"

        if (!form.launchWindowStart)    newErrors.windows = "Choose valid launch start window"
        if (!form.launchWindowEnd)      newErrors.windows = "Choose valid launch end window"
        if (!form.flybyWindowStart)     newErrors.windows = "Choose valid launch start window"
        if (!form.flybyWindowEnd)       newErrors.windows = "Choose valid launch end window"
        if (!form.arrivalWindowStart)   newErrors.windows = "Choose valid arrival start window"
        if (!form.arrivalWindowEnd)     newErrors.windows = "Choose valid arrival end window"

        if (form.launchWindowStart >= form.launchWindowEnd)     newErrors.windows = "Launch window start < launch window end"
        if (form.arrivalWindowStart >= form.arrivalWindowEnd)   newErrors.windows = "Arrival window start < arrival window end"
        if (form.launchWindowStart >= form.arrivalWindowStart)  newErrors.windows = "Launch window start < arrival window start"
        
        if (form.flybyBody != "")
        {
            if (form.flybyWindowStart >= form.flybyWindowEnd)       newErrors.windows = "Flyby window start < flyby window end"
            if (form.flybyWindowStart >= form.arrivalWindowStart)   newErrors.windows = "Flyby window start < arrival window start"
            if (form.launchWindowStart >= form.flybyWindowStart)    newErrors.windows = "Launch window start < flyby window start"
        }

        if (form.gridSize < 1 || form.gridSize > 200) newErrors.resolution = "Grid size must be between 1 and 200"

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async (e: react.MouseEvent<HTMLButtonElement, MouseEvent>) =>
    {
        e.preventDefault()

        if (!validate()) return

        try
        {
            let response: any = await api.post(`/interplanetary/run`, form)

            globalThis.window.api.info(`[${import.meta.url}] ${JSON.stringify(response.data)}`)
        }
        catch (err)
        {
            const message: string | null = checkError(import.meta.url, err)

            if (message) globalThis.window.api.error(`[${import.meta.url}] ${message}`)
        }
    }

    const handleStop = async (e: react.MouseEvent<HTMLButtonElement, MouseEvent>) =>
    {
        e.preventDefault()

        try
        {
            let response: any = await api.put(`/ws/stop-simulation`)

            globalThis.window.api.info(`[${import.meta.url}] ${JSON.stringify(response.data)}`)
        }
        catch (err)
        {
            const message: string | null = checkError(import.meta.url, err)

            if (message) globalThis.window.api.error(`[${import.meta.url}] ${message}`)
        }
    }

    // --- RENDERING ---

    return (
        <div className="w-full h-full bg-neutral-900 p-4 overflow-y-auto space-y-6">

            {/* Mission Section */}

            <FormSection title="Mission">

                <FormSelect
                    label="Departure Body"
                    name="departureBody"
                    value={form.departureBody}
                    setValue={handleSelectChange}
                    options={
                        [
                            { name: "Mercury", value: "mercury" },
                            { name: "Venus", value: "venus" },
                            { name: "Earth", value: "earth" },
                            { name: "Mars", value: "mars" },
                            { name: "Jupiter", value: "jupiter" },
                            { name: "Saturn", value: "saturn" },
                            { name: "Uranus", value: "uranus" },
                            { name: "Neptune", value: "neptune" }
                        ]}
                />

                <FormSelect
                    label="Flyby Body"
                    name="flybyBody"
                    value={form.flybyBody}
                    setValue={handleSelectChange}
                    options={
                        [
                            { name: "None", value: "" },
                            { name: "Mercury", value: "mercury" },
                            { name: "Venus", value: "venus" },
                            { name: "Earth", value: "earth" },
                            { name: "Mars", value: "mars" },
                            { name: "Jupiter", value: "jupiter" },
                            { name: "Saturn", value: "saturn" },
                            { name: "Uranus", value: "uranus" },
                            { name: "Neptune", value: "neptune" }
                        ]}
                />

                <FormSelect
                    label="Arrival Body"
                    name="arrivalBody"
                    value={form.arrivalBody}
                    setValue={handleSelectChange}
                    options={
                        [
                            { name: "Mercury", value: "mercury" },
                            { name: "Venus", value: "venus" },
                            { name: "Earth", value: "earth" },
                            { name: "Mars", value: "mars" },
                            { name: "Jupiter", value: "jupiter" },
                            { name: "Saturn", value: "saturn" },
                            { name: "Uranus", value: "uranus" },
                            { name: "Neptune", value: "neptune" }
                        ]}
                />

            {
                errors.bodies && <p className="text-red-400 text-sm">{errors.bodies}</p>
            }

            </FormSection>

            {/* Date Ranges */}

            <FormSection title="Date Ranges">

                <FormInput
                    label="Launch Window Start"
                    type="date"
                    name="launchWindowStart"
                    value={form.launchWindowStart}
                    setValue={handleInputChange}
                />

                <FormInput
                    label="Launch Window End"
                    type="date"
                    name="launchWindowEnd"
                    value={form.launchWindowEnd}
                    setValue={handleInputChange}
                />

                {
                    form.flybyBody !== "" &&
                    
                    <>

                        <FormInput
                            label="Flyby Window Start"
                            type="date"
                            name="flybyWindowStart"
                            value={form.flybyWindowStart}
                            setValue={handleInputChange}
                        />

                        <FormInput
                            label="Flyby Window End"
                            type="date"
                            name="flybyWindowEnd"
                            value={form.flybyWindowEnd}
                            setValue={handleInputChange}
                        />

                    </>
                }

                <FormInput
                    label="Arrival Window Start"
                    type="date"
                    name="arrivalWindowStart"
                    value={form.arrivalWindowStart}
                    setValue={handleInputChange}
                />

                <FormInput
                    label="Arrival Window End"
                    type="date"
                    name="arrivalWindowEnd"
                    value={form.arrivalWindowEnd}
                    setValue={handleInputChange}
                />

            {
                errors.windows && <p className="text-red-400 text-sm">{errors.windows}</p>
            }

            </FormSection>

            {/* Resolution */}

            <FormSection title="Resolution">

                <FormInput
                    label="Grid Size (days)"
                    type="number"
                    name="gridSize"
                    min={1}
                    max={200}
                    value={form.gridSize}
                    setValue={handleInputChange}
                />

            {
                errors.resolution && <p className="text-red-400 text-sm">{errors.resolution}</p>
            }

            </FormSection>

            {/* Run Button */}

            <div>

                <FormButton text="Run Analysis" disabled={running} onClick={handleSubmit} />

                <FormButton text="Stop Analysis" disabled={!running} onClick={handleStop} />

            </div>
            
        </div>
    )
}