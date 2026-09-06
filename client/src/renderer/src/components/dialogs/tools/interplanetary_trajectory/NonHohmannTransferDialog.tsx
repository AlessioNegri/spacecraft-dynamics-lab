import * as react from "react"
import * as Form from "@radix-ui/react-form"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import ErrorText from "@renderer/components/dialogs/ErrorText"

interface IFormIn
{
    departurePlanet: string
    arrivalPlanet: string
    numPoints: number
}

interface IFormOut
{
    hyperbolicExcessVelocities: number[]
    timeOfFlights: number[]
    trueAnomalies: number[]
}

const defaultIn: IFormIn =
{
    departurePlanet: "earth",
    arrivalPlanet: "mars",
    numPoints: 200
}

const defaultOut: IFormOut =
{
    hyperbolicExcessVelocities: [],
    timeOfFlights: [],
    trueAnomalies: []
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function NonHohmannTransferDialog */
export default function NonHohmannTransferDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [data, setData] = react.useState<plotly.Data[]>([])

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const validate = (): boolean =>
    {
        const newErrors: Record<string, string> = {}

        if (formIn.arrivalPlanet === formIn.departurePlanet)
        {
            newErrors.planets = "Arrival planet cannot be the same as departure planet"
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        if (!validate()) return

        try
        {
            const response: any = await http.api.put(`/interplanetary/non-hohmann-transfer`, formIn)

            const result: IFormOut =
            {
                hyperbolicExcessVelocities: response.data.hyperbolicExcessVelocities ?? [],
                timeOfFlights: response.data.timeOfFlights ?? [],
                trueAnomalies: response.data.trueAnomalies ?? []
            }

            setFormOut(result)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const traceHohmann: plotly.Data =
        {
            x: [formOut.hyperbolicExcessVelocities[0], formOut.hyperbolicExcessVelocities[0]],
            y: [Math.min(...formOut.timeOfFlights), Math.max(...formOut.timeOfFlights)],
            type: "scatter",
            mode: "lines",
            name: "Hohmann Transfer",
            marker: { color: "#ff0000", size: 10, symbol: "x" }
        }

        const traceTof: plotly.Data =
        {
            x: formOut.hyperbolicExcessVelocities,
            y: formOut.timeOfFlights,
            type: "scatter",
            mode: "lines+markers",
            name: "Time of Flight",
            line: { color: "#00ccff", width: 2 },
            marker: { color: "#ff9900", size: 6 }
        }

        const traceTrueAnomaly: plotly.Data =
        {
            x: formOut.hyperbolicExcessVelocities,
            y: formOut.trueAnomalies,
            type: "scatter",
            mode: "lines+markers",
            name: "True Anomaly",
            yaxis: "y2",
            line: { color: "#7ae582", width: 2 },
            marker: { color: "#5eead4", size: 5 }
        }

        setData([traceHohmann, traceTof, traceTrueAnomaly])
    }, [formOut])

    // --- USE MEMO ---

    const config = react.useMemo(() => ( //plotly.Config
    {
        responsive: true,
        displaylogo: false,
        scrollZoom: true,
        staticPlot: false
    }), [])

    const layout = react.useMemo(() => ( //plotly.Layout
    {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        showlegend: true,
        legend: { font: { color: "#e5e5e5" } },
        font: { color: "#e5e5e5" },
        margin: { l: 60, r: 60, t: 40, b: 50 },
        title: { text: "Non-Hohmann Transfer Family", font: { color: "#ffffff", size: 18 } },
        xaxis: {
            title: { text: "Hyperbolic excess velocity v_∞ (km/s)", font: { color: "#e5e5e5" } },
            gridcolor: "#323232",
            zerolinecolor: "#555555",
            color: "#e5e5e5"
        },
        yaxis: {
            title: { text: "Time of flight (day)", font: { color: "#e5e5e5" } },
            gridcolor: "#323232",
            zerolinecolor: "#555555",
            color: "#e5e5e5"
        },
        yaxis2: {
            title: { text: "True anomaly (deg)", font: { color: "#e5e5e5" } },
            overlaying: "y",
            side: "right",
            gridcolor: "#323232",
            zerolinecolor: "#555555",
            color: "#e5e5e5"
        }
    } satisfies Partial<plotly.Layout>), [])

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Non-Hohmann Transfer"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Non-Hohmann Transfer",
                    content:
                        `Compute the family of non-Hohmann interplanetary transfers as a function of hyperbolic excess
                        velocity. The result is plotted as the transfer time and true anomaly versus v_infinity.`
                }
            }>

            {/* INPUT */}

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4 items-end">

                <InputField
                    name="departurePlanet"
                    label="Departure Planet"
                    type="select"
                    value={formIn.departurePlanet}
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
                    name="arrivalPlanet"
                    label="Arrival Planet"
                    type="select"
                    value={formIn.arrivalPlanet}
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
                    type="number"
                    name="numPoints"
                    label="Sample Points"
                    symbol="N"
                    value={String(formIn.numPoints)}
                    onChange={handleChange}
                    min={10}
                    max={1000}
                />

                { errors.planets && <ErrorText text={errors.planets} /> }

            </Form.Root>

            {/* PLOT */}

            <Plot
                data={data}
                layout={layout}
                config={config}
                style={{ width: "100%", height: "500px" }}
            />

        </DialogRUI>
    )
}
