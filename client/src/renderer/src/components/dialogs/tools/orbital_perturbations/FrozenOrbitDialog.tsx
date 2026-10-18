import * as react from "react"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"

interface IFrozenOrbitData
{
    inclination: number[]
    semimajorAxis: number[]
    firstOrderEccentricity: (number | null)[][]
    eccentricity: (number | null)[][]
    type1Inclination: number
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function FrozenOrbitDialog */
export default function FrozenOrbitDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---
    
    const [data, setData] = react.useState<IFrozenOrbitData | null>(null)

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
                const response = await http.api.put<IFrozenOrbitData>("/orbital-perturbations/frozen-orbit-type-2")

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

        const contours =
        {
            coloring: "fill" as const,
            showlabels: true,
            start: 0,
            end: 0.01,
            size: 0.0001,
            labelfont: { size: 10, color: "#e5e7eb" }
        }

        const colorbar = (title: string) => (
        {
            tick0: 0,
            dtick: 5,
            x: -0.15,
            title: { text: title }
        })

        const firstOrderTrace: plotly.Data =
        {
            x: data.inclination,
            y: data.semimajorAxis,
            z: data.firstOrderEccentricity,
            type: "contour",
            colorscale: "Cividis",
            ncontours: 50,
            contours,
            colorbar: colorbar("Frozen eccentricity 1st order"),
            line: { color: "#38bdf8", width: 1 },
            showscale: false,
            showlegend: true,
            name: "First-order eccentricity",
            hovertemplate: "i: %{x:.1f}°<br>a: %{y:.0f} km<br>e: %{z:.5f}<extra>First order</extra>"
        }

        const correctedTrace: plotly.Data =
        {
            x: data.inclination,
            y: data.semimajorAxis,
            z: data.eccentricity,
            type: "contour",
            colorscale: "Cividis",
            ncontours: 50,
            contours,
            colorbar: colorbar("Frozen eccentricity higher order"),
            line: { color: "#fb923c", width: 2 },
            showscale: false,
            showlegend: true,
            name: "Corrected eccentricity",
            hovertemplate: "i: %{x:.1f}°<br>a: %{y:.0f} km<br>e: %{z:.5f}<extra>Corrected</extra>"
        }

        const type1Trace1: plotly.Data =
        {
            x: [data.type1Inclination, data.type1Inclination],
            y: [data.semimajorAxis[0], data.semimajorAxis.at(-1)!],
            type: "scatter",
            mode: "lines",
            line: { color: "#15facc", width: 2, dash: "dash" },
            name: "Type I critical inclination (63.43°)",
            hovertemplate: "Type I: %{x:.3f}°<extra></extra>"
        }

        const type1Trace2: plotly.Data =
        {
            x: [180 - data.type1Inclination, 180 - data.type1Inclination],
            y: [data.semimajorAxis[0], data.semimajorAxis.at(-1)!],
            type: "scatter",
            mode: "lines",
            line: { color: "#15facc", width: 2, dash: "dash" },
            name: "Type I critical inclination (116.57°)",
            hovertemplate: "Type I: %{x:.3f}°<extra></extra>"
        }

        return [firstOrderTrace, correctedTrace, type1Trace1, type1Trace2]
    }, [data])

    const layout: Partial<plotly.Layout> = react.useMemo(() => (
    {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 65, r: 25, t: 20, b: 60 },
        xaxis: { title: { text: "Inclination [deg]" }, range: [0, 180], gridcolor: "#444", automargin: true },
        yaxis: { title: { text: "Semimajor Axis / Earth Radius" }, gridcolor: "#444", automargin: true },
        showlegend: true,
        legend: { orientation: "h", y: -0.2 }
    }), [])

    const config: Partial<plotly.Config> = react.useMemo(() => (
    {
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }), [])

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Frozen Orbit"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}
            popup={{
                title: "Frozen Orbits",
                content:
                    `Type-II frozen-orbit eccentricity contours versus semimajor axis and inclination, with the type-I
                    critical inclination.`
            }}
        >
            {
                loading &&
                <p className="text-center text-orange-300">Loading frozen-orbit contours...</p>
            }

            {
                !loading && !data &&
                <p className="text-center text-neutral-400">No contour data available.</p>
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
