import * as react from "react"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"

interface ICommensurateOrbitData
{
    altitude: number[]
    repeatCycle: number[]
    orbitalRevolutions: number[]
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function CommensurateOrbitDialog */
export default function CommensurateOrbitDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [data, setData] = react.useState<ICommensurateOrbitData | null>(null)

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
                const response = await http.api.put<ICommensurateOrbitData>("/orbital-perturbations/commensurate-orbits")
                
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

        const points: plotly.Data =
        {
            x: data.altitude,
            y: data.repeatCycle,
            text: data.orbitalRevolutions.map(String),
            type: "scatter",
            mode: "text+markers",
            marker: { color: "#f8fafc", size: 7 },
            textposition: "top center",
            textfont: { color: "#f8fafc", size: 10 },
            name: "Commensurate orbits",
            hovertemplate: "Altitude: %{x:.0f} km<br>Repeat cycle: %{y} days<br>k: %{text}<extra></extra>"
        }

        return [points]
    }, [data])

    const layout: Partial<plotly.Layout> = react.useMemo(() => ({
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 65, r: 25, t: 20, b: 60 },
        xaxis: {
            title: { text: "Approx. Altitude [km]" },
            range: [550, 1300],
            dtick: 50,
            gridcolor: "#666",
            automargin: true
        },
        yaxis: {
            title: { text: "Repeat Cycle [days]" },
            range: [0, 11],
            dtick: 1,
            gridcolor: "#666",
            automargin: true
        },
        showlegend: false
    }), [])

    const config: Partial<plotly.Config> = react.useMemo(() => ({
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }), [])

    return (
        <DialogRUI
            title="Commensurate Orbits"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}
            popup={{
                title: "Commensurate Orbits",
                content:
                    `Approximate orbit altitude and repeat cycle for the orbital revolutions values in the reference
                    chart.`
            }}
        >
            {
                loading &&
                <p className="text-center text-orange-300">Loading commensurate orbit points...</p>
            }

            {
                !loading && !data &&
                <p className="text-center text-neutral-400">No orbit points available.</p>
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
