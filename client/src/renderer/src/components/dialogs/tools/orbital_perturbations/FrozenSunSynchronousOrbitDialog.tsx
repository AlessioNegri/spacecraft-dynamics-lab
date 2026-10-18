import * as react from "react"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"

interface IFrozenSunSynchronousOrbitData
{
    semimajorAxis: number[]
    sunSynchronousEccentricity: (number | null)[]
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function FrozenSunSynchronousOrbitDialog */
export default function FrozenSunSynchronousOrbitDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [data, setData] = react.useState<IFrozenSunSynchronousOrbitData | null>(null)

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
                const response = await http.api.put<IFrozenSunSynchronousOrbitData>(
                    "/orbital-perturbations/frozen-sun-synchronous-orbit"
                )

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

        const sunSynchronousTrace: plotly.Data =
        {
            x: data.semimajorAxis,
            y: data.sunSynchronousEccentricity,
            type: "scatter",
            mode: "lines",
            line: { color: "#fb7185", width: 3 },
            name: "Sun-synchronous eccentricity",
            hovertemplate: "a: %{x:.3f} Rₑ<br>e_f_sso: %{y:.6f}<extra></extra>"
        }

        return [sunSynchronousTrace]
    }, [data])

    const layout: Partial<plotly.Layout> = react.useMemo(() => ({
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 70, r: 25, t: 20, b: 60 },
        xaxis: { title: { text: "Semimajor Axis / Earth Radius" }, gridcolor: "#444", automargin: true },
        yaxis: { title: { text: "Sun-Synchronous Eccentricity e_f_sso" }, gridcolor: "#444", automargin: true },
        showlegend: false
    }), [])

    const config: Partial<plotly.Config> = react.useMemo(() => ({
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }), [])

    return (
        <DialogRUI
            title="Frozen Sun-Synchronous Orbit"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}
            popup={{
                title: "Sun-Synchronous Eccentricity Trend",
                content: `Sun-synchronous eccentricity as a function of semimajor axis, normalized by Earth's radius.`
            }}
        >

            {
                loading &&
                <p className="text-center text-orange-300">Loading sun-synchronous trend...</p>
            }

            {
                !loading && !data &&
                <p className="text-center text-neutral-400">No trend data available.</p>
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
