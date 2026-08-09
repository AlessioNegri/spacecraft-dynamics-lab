import * as react from "react"
import * as themes from "@radix-ui/themes"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"

interface IAtmosphereData
{
    altitude: number[]
    temperature_reference: number[]
    temperature_consistent: number[]
    pressure_reference: number[]
    pressure_consistent: number[]
    density_reference: number[]
    density_consistent: number[]
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function AtmosphereModelDialog */
export default function AtmosphereModelDialog(props: Readonly<Props>): react.JSX.Element
{
    const makeTrace = (x: number[], y: number[], name: string, color: string): plotly.Data => ({
        x,
        y,
        type: "scatter",
        mode: "lines",
        name,
        line: { color, width: 2 }
    })

    // --- USE STATE ---

    const [data, setData] = react.useState<IAtmosphereData | null>(null)

    const [loading, setLoading] = react.useState<boolean>(false)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (!props.opened) return

        const loadData = async () =>
        {
            setLoading(true)

            try
            {
                const response: any = await http.api.put("/models/atmosphere")

                setData(response.data)
            }
            catch (err)
            {
                http.checkError(import.meta.url, err)
            }
            finally
            {
                setLoading(false)
            }
        }

        loadData()
    }, [props.opened])

    // --- USE CALLBACK ---

    const layout = react.useCallback((xTitle: string): any => ({
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 50, r: 50, t: 50, b: 50 },
        xaxis: { title: { text: xTitle, standoff: 10 }, gridcolor: "#444", automargin: true },
        yaxis: { title: { text: "Altitude [km]" }, gridcolor: "#444" },
        legend: { bgcolor: "rgba(0,0,0,0.2)", x: 1.02, y: 1 }
    }), [])

    // --- USE MEMO ---

    const config = react.useMemo(() => ( //plotly.Config
    {
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }), [])

    const temperatureTraces: plotly.Data[] = react.useMemo(() =>
    {
        if (!data) return []

        return [
            makeTrace(data.temperature_reference, data.altitude, "Reference", "#ff8c42"),
            makeTrace(data.temperature_consistent, data.altitude, "Consistent", "#facc15")
        ]
    }, [data])

    const pressureTraces: plotly.Data[] = react.useMemo(() =>
    {
        if (!data) return []

        return [
            makeTrace(data.pressure_reference, data.altitude, "Reference", "#38bdf8"),
            makeTrace(data.pressure_consistent, data.altitude, "Consistent", "#818cf8")
        ]
    }, [data])

    const densityTraces: plotly.Data[] = react.useMemo(() =>
    {
        if (!data) return []

        return [
            makeTrace(data.density_reference, data.altitude, "Reference", "#34d399"),
            makeTrace(data.density_consistent, data.altitude, "Consistent", "#fb7185")
        ]
    }, [data])

    const temperatureLayout = react.useMemo(() => layout("Temperature [K]"), [layout])

    const pressureLayout = react.useMemo(() => layout("Pressure [kPa]"), [layout])

    const densityLayout = react.useMemo(() => layout("Density [kg/m³]"), [layout])

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Atmosphere Model"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            popup={
            {
                title: "Atmosphere Model",
                content:
                `Trend of temperature, pressure, and density with altitude using the U.S. Standard Atmosphere
                1976 model, including a thermodynamically consistent density estimate.`
            }}
        >

            <div className="flex flex-col gap-4 justify-center items-center">

                {
                    loading &&
                    <p className="text-center text-orange-300">Loading atmosphere data…</p>
                }

                {
                    !loading && !data &&
                    <p className="text-center text-neutral-400">No data available.</p>
                }

                {
                    !loading && data &&
                        
                    <themes.Tabs.Root defaultValue="temperature" className="w-full">

                        <themes.Tabs.List>

                            <themes.Tabs.Trigger value="temperature">Temperature</themes.Tabs.Trigger>

                            <themes.Tabs.Trigger value="pressure">Pressure</themes.Tabs.Trigger>

                            <themes.Tabs.Trigger value="pensity">Density</themes.Tabs.Trigger>

                        </themes.Tabs.List>

                        <themes.Box pt="3">

                            <themes.Tabs.Content value="temperature">
                                
                                <Plot
                                    data={temperatureTraces}
                                    layout={temperatureLayout}
                                    config={config}
                                    style={{ width: "100%", height: "500px" }}
                                />
                                
                            </themes.Tabs.Content>

                            <themes.Tabs.Content value="pressure">
                                
                                <Plot
                                    data={pressureTraces}
                                    layout={pressureLayout}
                                    config={config}
                                    style={{ width: "100%", height: "500px" }}
                                />

                            </themes.Tabs.Content>

                            <themes.Tabs.Content value="pensity">
                                
                                <Plot
                                    data={densityTraces}
                                    layout={densityLayout}
                                    config={config}
                                    style={{ width: "100%", height: "500px" }}
                                />

                            </themes.Tabs.Content>

                        </themes.Box>

                    </themes.Tabs.Root>
                }

            </div>

        </DialogRUI>
    )
}
