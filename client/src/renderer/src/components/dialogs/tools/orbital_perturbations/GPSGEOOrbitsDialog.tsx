import * as react from "react"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"

interface IGPSOrbitData
{
    longitudeAscendingNode: number[]
    driftHarmonics32: number[]
    driftHarmonics3244: number[]
    driftHarmonics324452: number[]
    geoDriftHarmonics22: number[]
    geoDriftHarmonics2231: number[]
    geoDriftHarmonics223133: number[]
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function GPSGEOOrbitDialog */
export default function GPSGEOOrbitDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [data, setData] = react.useState<IGPSOrbitData | null>(null)

    const [loading, setLoading] = react.useState<boolean>(false)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (!props.opened) return

        let active = true

        const loadData = async () =>
        {
            setLoading(true)

            try
            {
                const response = await http.api.put<IGPSOrbitData>("/orbital-perturbations/gps-orbit")

                if (active) setData(response.data)
            }
            catch (err)
            {
                http.checkError(import.meta.url, err)
            }
            finally
            {
                if (active) setLoading(false)
            }
        }

        void loadData()

        return () => { active = false }
    }, [props.opened])

    // --- PLOTLY ---

    const plotData: plotly.Data[] = react.useMemo(() =>
    {
        if (!data) return []

        return [
            {
                x: data.longitudeAscendingNode,
                y: data.driftHarmonics32,
                type: "scatter",
                mode: "lines",
                line: { color: "#38bdf8", width: 2 },
                name: "GPS: 3:2",
                hovertemplate: "Longitude: %{x:.0f}°<br>Drift: %{y:.3e} rad/year²<extra>GPS 3:2</extra>"
            },
            {
                x: data.longitudeAscendingNode,
                y: data.driftHarmonics3244,
                type: "scatter",
                mode: "lines",
                line: { color: "#facc15", width: 2 },
                name: "GPS: 3:2 + 4:4",
                hovertemplate: "Longitude: %{x:.0f}°<br>Drift: %{y:.3e} rad/year²<extra>GPS 3:2 + 4:4</extra>"
            },
            {
                x: data.longitudeAscendingNode,
                y: data.driftHarmonics324452,
                type: "scatter",
                mode: "lines",
                line: { color: "#fb7185", width: 2 },
                name: "GPS: 3:2 + 4:4 + 5:2",
                hovertemplate: "Longitude: %{x:.0f}°<br>Drift: %{y:.3e} rad/year²<extra>GPS all harmonics</extra>"
            },
            {
                x: data.longitudeAscendingNode,
                y: data.geoDriftHarmonics22,
                type: "scatter",
                mode: "lines",
                line: { color: "#a78bfa", width: 2, dash: "dash" },
                name: "GEO: 2:2",
                hovertemplate: "Longitude: %{x:.0f}°<br>Drift: %{y:.3e} rad/year²<extra>GEO 2:2</extra>"
            },
            {
                x: data.longitudeAscendingNode,
                y: data.geoDriftHarmonics2231,
                type: "scatter",
                mode: "lines",
                line: { color: "#4ade80", width: 2, dash: "dash" },
                name: "GEO: 2:2 + 3:1",
                hovertemplate: "Longitude: %{x:.0f}°<br>Drift: %{y:.3e} rad/year²<extra>GEO 2:2 + 3:1</extra>"
            },
            {
                x: data.longitudeAscendingNode,
                y: data.geoDriftHarmonics223133,
                type: "scatter",
                mode: "lines",
                line: { color: "#f97316", width: 2, dash: "dash" },
                name: "GEO: 2:2 + 3:1 + 3:3",
                hovertemplate: "Longitude: %{x:.0f}°<br>Drift: %{y:.3e} rad/year²<extra>GEO all harmonics</extra>"
            }
        ]
    }, [data])

    const layout: Partial<plotly.Layout> = react.useMemo(() => ({
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 80, r: 25, t: 20, b: 60 },
        xaxis: { title: { text: "Longitude of Ascending Node [deg]" }, range: [0, 360], dtick: 45, gridcolor: "#444", automargin: true },
        yaxis: { title: { text: "Longitudinal Drift Rate [rad/year²]" }, exponentformat: "e", gridcolor: "#444", automargin: true },
        showlegend: true,
        legend: { orientation: "h", y: -0.2 }
    }), [])

    const config: Partial<plotly.Config> = react.useMemo(() => ({
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }), [])

    // --- RENDERING ---

    return (
        <DialogRUI
            title="GPS and GEO Longitudinal Drift"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}
            popup={{
                title: "GPS and GEO Longitudinal Drift",
                content:
                    `Longitudinal drift rate versus longitude of ascending node for GPS and GEO orbits, with
                    successive gravity harmonics enabled.`
            }}
        >
            {
                loading &&
                <p className="text-center text-orange-300">Loading GPS and GEO drift curves...</p>
            }

            {
                !loading && !data &&
                <p className="text-center text-neutral-400">No GPS and GEO drift data available.</p>
            }

            {
                data &&
                <div className="w-full overflow-hidden rounded border border-neutral-700">
                    <Plot
                        className="w-full"
                        data={plotData}
                        layout={layout}
                        config={config}
                        style={{ width: "100%", height: "min(65vh, 600px)" }}
                    />
                </div>
            }
            
        </DialogRUI>
    )
}
