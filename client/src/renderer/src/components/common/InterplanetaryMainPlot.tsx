import Plot from "react-plotly.js"
import * as plotly from "plotly.js"

interface InterplanetaryMainPlotProps
{
    dvGrid: number[][] | null
    dv1Grid: number[][] | null
    dv2Grid: number[][] | null
    tofGrid: number[][] | null
    launchDates: string[] | null
    arrivalDates: string[] | null
    onSelect: (info: ISelectionInfo) => void
}

/** @function InterplanetaryMainPlot */
export default function InterplanetaryMainPlot(props: Readonly<InterplanetaryMainPlotProps>)
{
    const dvHeatmap: plotly.Data =
    {
        x: props.launchDates,
        y: props.arrivalDates,
        z: props.dvGrid,
        name: "Total Δv",
        type: "contour",
        colorscale: "Viridis",
        reversescale: false,
        contours:
        {
            coloring: "heatmap",
            showlabels: true
        },
        colorbar:
        {
            title: "Δv (km/s)",
            titleside: "right",
            x: -0.15
        },
    }

    const dv1Isolines: plotly.Data =
    {
        x: props.launchDates,
        y: props.arrivalDates,
        z: props.dv1Grid,
        name: "ΔV₁",
        hoverinfo: "skip",
        type: "contour",
        showscale: false,
        line:
        {
            color: "red",
            width: 1
        },
        contours:
        {
            coloring: "none",
            showlines: true,
            showlabels: true,
            labelfont:
            {
                color: "red",
                size: 10
            }
        }
    }

    const tofIsolines: plotly.Data =
    {
        x: props.launchDates,
        y: props.arrivalDates,
        z: props.tofGrid,
        name: "TOF",
        hoverinfo: "skip",
        type: "contour",
        showscale: false,
        line:
        {
            color: "white",
            width: 1
        },
        contours:
        {
            coloring: "none",
            showlines: true,
            showlabels: true,
            labelfont:
            {
                color: "white",
                size: 10
            }
        }
    }

    const layout: plotly.Layout =
    {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 80, r: 80, t: 50, b: 50 },
        title:
        {
            text: "Pork Chop Plot",
            font:
            {
                color: "#FFFFFF",
                size: 20,
                family: "Lucida Console"
            }
        },
        xaxis:
        {
            title:
            {
                text: "Launch Date",
                font:
                {
                    color: "#FFFFFF",
                    size: 16,
                    family: "Lucida Console"
                }
            },
            type: "date",
            tickformat: "%Y-%m-%d",
            showgrid: true,
            gridcolor: "#ccc",
            gridwidth: 1
        },
        yaxis:
        {
            title:
            {
                text: "Arrival Date",
                font:
                {
                    color: "#FFFFFF",
                    size: 16,
                    family: "Lucida Console"
                }
            },
            type: "date",
            tickformat: "%Y-%m-%d"
        }
    }

    const config: plotly.Config =
    {
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }

    const handleClick = (e: plotly.PlotMouseEvent) =>
    {
        if (!e.points || e.points.length === 0) return

        const p = e.points[0]

        props.onSelect(
        {
            launchDate: p.x as string,
            arrivalDate: p.y as string,
            dv: p.z as number,
            dv1: props.dv1Grid![p.pointIndex[0]][p.pointIndex[1]],
            dv2: props.dv2Grid![p.pointIndex[0]][p.pointIndex[1]],
            tofDays: props.tofGrid![p.pointIndex[0]][p.pointIndex[1]]
        })
    }

    return (
        <div className="w-full h-full bg-neutral-900 rounded-lg shadow-inner p-2 flex">

        {
            !props.dvGrid &&
                <div className="w-full h-full flex items-center justify-center text-neutral-500">
                    Run the analysis to generate the pork‑chop plot
                </div>
        }

        {
            props.dvGrid && (
            <div className="flex-1">

                <Plot
                    data={[dvHeatmap, tofIsolines, dv1Isolines]}
                    layout={layout}
                    style={{ width: "100%", height: "100%" }}
                    config={config}
                    onClick={handleClick}
                />

            </div>
        )}

        {
            props.dvGrid && <PorkChopLegend/>
        }

        </div>
    )
}

/** @function PorkChopLegend */
export function PorkChopLegend()
{
    return (
        <div className="text-sm text-neutral-300 space-y-3 mt-4 w-64 shrink-0">

            <h3 className="text-base font-semibold text-neutral-200">
                Legend
            </h3>

            <div className="grid grid-cols-2 space-y-4">

                <div className="w-4 h-4 bg-linear-to-r from-blue-900 via-green-500 to-yellow-300 rounded-sm" />

                <span>Δv Heatmap (km/s)</span>

                <div className="w-6 h-0.5 bg-white" />

                <span>TOF Isolines (days)</span>

                <div className="w-6 h-0.5 bg-red-500" />

                <span>Δv₁ Isolines (km/s)</span>
                
            </div>

            <p className="text-neutral-400 text-xs leading-relaxed">
                The heatmap shows the total Δv required for the transfer.
                White lines indicate equal time-of-flight (TOF).
                Red lines indicate equal departure Δv (Δv₁), useful for
                identifying C3-limited launch windows.
            </p>

        </div>
    )
}