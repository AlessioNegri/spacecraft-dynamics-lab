import * as react from "react"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import utility from "@renderer/common/utility"

import FormInput from "../dialogs/FormInput"

interface InterplanetaryMainPlotProps
{
    porkChopData2D: IPorkChopData2D | null
    porkChopData3D: IPorkChopData3D | null
    onSelect: (info: ISelectionInfo) => void
}

/** @function InterplanetaryMainPlot */
export default function InterplanetaryMainPlot(props: Readonly<InterplanetaryMainPlotProps>)
{
    // --- USE STATE ---

    const [data2D, setData2D] = react.useState<plotly.Data[]>()

    const [data3D, setData3D] = react.useState<plotly.Data[]>()

    const [flybyDateIndex, setFlybyDateIndex] = react.useState<number>(0)

    const [flybyDateLength, setFlybyDateLength] = react.useState<number>(0)

    // --- CONST ---

    const layout: any = //plotly.Layout
    {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 80, r: 100, t: 50, b: 50 },
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
            gridwidth: 1,
            constrain: "range"
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
            tickformat: "%Y-%m-%d",
            constrain: "range"
        },
        //transition: { duration: 0 },
        //uirevision: "static"
    }

    const config: any = //plotly.Config
    {
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (props.porkChopData2D === null) return

        const dvHeatmap: plotly.Data =
        {
            x: props.porkChopData2D.launchDates,
            y: props.porkChopData2D.arrivalDates,
            z: props.porkChopData2D.dvGrid,
            name: "ΔV (km/s)",
            type: "contour",
            colorscale: "Cividis",
            reversescale: false,
            line:
            {
                color: "black",
                width: 1
            },
            contours:
            {
                coloring: "heatmap",
                showlabels: true,
                size: 15,
                showlines: true,
                type: "levels",
                labelfont:
                {
                    color: "black",
                    size: 15
                }
            },
            colorbar:
            {
                title:
                {
                    text: "ΔV (km/s)",//"$\\Delta v_{total}$",
                },
                x: -0.15
            }
        }

        const dv1Isolines: plotly.Data =
        {
            x: props.porkChopData2D.launchDates,
            y: props.porkChopData2D.arrivalDates,
            z: props.porkChopData2D.dv1Grid,
            name: "ΔV_1 (km/s)",
            hoverinfo: "skip",
            type: "contour",
            showscale: false,
            line:
            {
                color: "red",
                width: 2
            },
            contours:
            {
                coloring: "none",
                showlines: true,
                showlabels: true,
                labelfont:
                {
                    color: "red",
                    size: 15
                }
            }
        }

        const dv2Isolines: plotly.Data =
        {
            x: props.porkChopData2D.launchDates,
            y: props.porkChopData2D.arrivalDates,
            z: props.porkChopData2D.dv2Grid,
            name: "ΔV_2 (km/s)",
            hoverinfo: "skip",
            type: "contour",
            showscale: false,
            line:
            {
                color: "yellow",
                width: 2
            },
            contours:
            {
                coloring: "none",
                showlines: true,
                showlabels: true,
                labelfont:
                {
                    color: "yellow",
                    size: 15
                }
            }
        }

        const tofIsolines: plotly.Data =
        {
            x: props.porkChopData2D.launchDates,
            y: props.porkChopData2D.arrivalDates,
            z: props.porkChopData2D.tofGrid,
            name: "TOF (days)",
            hoverinfo: "skip",
            type: "contour",
            showscale: false,
            line:
            {
                color: "white",
                width: 2
            },
            contours:
            {
                coloring: "none",
                showlines: true,
                showlabels: true,
                labelfont:
                {
                    color: "white",
                    size: 15
                }
            }
        }
        
        setData2D([dvHeatmap, dv1Isolines, dv2Isolines, tofIsolines])
    }, [props.porkChopData2D])

    react.useEffect(() =>
    {
        if (props.porkChopData3D === null) return

        setFlybyDateLength(props.porkChopData3D.flybyDates.length - 1)

        const dvHeatmap: plotly.Data =
        {
            x: props.porkChopData3D.launchDates,
            y: props.porkChopData3D.arrivalDates,
            z: props.porkChopData3D.dvGrid,
            name: "ΔV (km/s)",
            type: "contour",
            colorscale: "Cividis",
            reversescale: false,
            line:
            {
                color: "black",
                width: 1
            },
            contours:
            {
                coloring: "heatmap",
                showlabels: true,
                size: 15,
                showlines: true,
                type: "levels",
                labelfont:
                {
                    color: "black",
                    size: 15
                }
            },
            colorbar:
            {
                title:
                {
                    text: "Δv (km/s)",
                },
                x: -0.15
            }
        }

        const dv1Isolines: plotly.Data =
        {
            x: props.porkChopData3D.launchDates,
            y: props.porkChopData3D.arrivalDates,
            z: props.porkChopData3D.dv1Grid,
            name: "ΔV_1 (km/s)",
            hoverinfo: "skip",
            type: "contour",
            showscale: false,
            line:
            {
                color: "red",
                width: 2
            },
            contours:
            {
                coloring: "none",
                showlines: true,
                showlabels: true,
                labelfont:
                {
                    color: "red",
                    size: 15
                }
            }
        }

        const dvGAIsolines: plotly.Data =
        {
            x: props.porkChopData3D.launchDates,
            y: props.porkChopData3D.arrivalDates,
            z: props.porkChopData3D.dvGAGrid,
            name: "ΔV_GA (km/s)",
            hoverinfo: "skip",
            type: "contour",
            showscale: false,
            line:
            {
                color: "green",
                width: 2
            },
            contours:
            {
                coloring: "none",
                showlines: true,
                showlabels: true,
                labelfont:
                {
                    color: "green",
                    size: 15
                }
            }
        }

        const dv2Isolines: plotly.Data =
        {
            x: props.porkChopData3D.launchDates,
            y: props.porkChopData3D.arrivalDates,
            z: props.porkChopData3D.dv2Grid,
            name: "ΔV_2 (km/s)",
            hoverinfo: "skip",
            type: "contour",
            showscale: false,
            line:
            {
                color: "yellow",
                width: 2
            },
            contours:
            {
                coloring: "none",
                showlines: true,
                showlabels: true,
                labelfont:
                {
                    color: "yellow",
                    size: 15
                }
            }
        }

        const tofIsolines: plotly.Data =
        {
            x: props.porkChopData3D.launchDates,
            y: props.porkChopData3D.arrivalDates,
            z: props.porkChopData3D.tofGrid,
            name: "TOF (days)",
            hoverinfo: "skip",
            type: "contour",
            showscale: false,
            line:
            {
                color: "white",
                width: 2
            },
            contours:
            {
                coloring: "none",
                showlines: true,
                showlabels: true,
                labelfont:
                {
                    color: "white",
                    size: 15
                }
            }
        }
        
        setData3D([dvHeatmap, dv1Isolines, dvGAIsolines, dv2Isolines, tofIsolines])
    }, [props.porkChopData3D, flybyDateIndex])

    // --- HANDLE ---

    const handleClick2D = (e: plotly.PlotMouseEvent) =>
    {
        if (!e.points || e.points.length === 0) return

        const p = e.points[0]

        props.onSelect(
        {
            launchDate: p.x as string,
            arrivalDate: p.y as string,
            dv: props.porkChopData2D!.dvGrid[p.pointIndex[0]][p.pointIndex[1]],
            dv1: props.porkChopData2D!.dv1Grid[p.pointIndex[0]][p.pointIndex[1]],
            dv2: props.porkChopData2D!.dv2Grid[p.pointIndex[0]][p.pointIndex[1]],
            tofDays: props.porkChopData2D!.tofGrid[p.pointIndex[0]][p.pointIndex[1]]
        })
    }

    const handleClick3D = (e: plotly.PlotMouseEvent) =>
    {
        if (!e.points || e.points.length === 0) return

        const p = e.points[0]

        props.onSelect(
        {
            launchDate: p.x as string,
            flybyDate: props.porkChopData3D!.flybyDates[flybyDateIndex],
            arrivalDate: p.y as string,
            dv: props.porkChopData3D!.dvGrid[p.pointIndex[0]][p.pointIndex[1]],
            dv1: props.porkChopData3D!.dv1Grid[p.pointIndex[0]][p.pointIndex[1]],
            dvGA: props.porkChopData3D!.dvGAGrid[p.pointIndex[0]][p.pointIndex[1]],
            dv2: props.porkChopData3D!.dv2Grid[p.pointIndex[0]][p.pointIndex[1]],
            tof1Days: props.porkChopData3D!.tof1Grid[p.pointIndex[0]][p.pointIndex[1]],
            tof2Days: props.porkChopData3D!.tof2Grid[p.pointIndex[0]][p.pointIndex[1]],
            tofDays: props.porkChopData3D!.tofGrid[p.pointIndex[0]][p.pointIndex[1]]
        })
    }

    const handleLayer = (e: react.ChangeEvent<HTMLInputElement>) =>
    {
        const index: number = Number(e.target.value)

        const A = props.porkChopData3D!.arrivalDates.length
        const L = props.porkChopData3D!.launchDates.length

        const tof1  : number[][] = utility.initArray(A, L)
        const tof2  : number[][] = utility.initArray(A, L)
        const tof   : number[][] = utility.initArray(A, L)
        const dv1   : number[][] = utility.initArray(A, L)
        const dvGA  : number[][] = utility.initArray(A, L)
        const dv2   : number[][] = utility.initArray(A, L)
        const dv    : number[][] = utility.initArray(A, L)

        for (let a = 0; a < A; a++)
        {
            for (let l = 0; l < L; l++)
            {
                tof1[a][l]  = props.porkChopData3D!.tof1[a][index][l]
                tof2[a][l]  = props.porkChopData3D!.tof2[a][index][l]
                tof[a][l]   = tof1[a][l] + tof2[a][l]
                dv1[a][l]   = props.porkChopData3D!.dv1[a][index][l]
                dvGA[a][l]  = props.porkChopData3D!.dvGA[a][index][l]
                dv2[a][l]   = props.porkChopData3D!.dv2[a][index][l]
                dv[a][l]    = dv1[a][l] + dvGA[a][l] + dv2[a][l]
            }
        }

        props.porkChopData3D!.tof1Grid  = tof1
        props.porkChopData3D!.tof2Grid  = tof2
        props.porkChopData3D!.tofGrid   = tof
        props.porkChopData3D!.dv1Grid   = dv1
        props.porkChopData3D!.dvGAGrid  = dvGA
        props.porkChopData3D!.dv2Grid   = dv2
        props.porkChopData3D!.dvGrid    = dv

        setFlybyDateIndex(index)
    }

    // --- RENDERING ---

    return (
        <div className="w-full h-full rounded-lg shadow-inner p-2 flex">

        {
            !props.porkChopData2D && !props.porkChopData3D &&
                <div className="w-full h-full flex items-center justify-center text-neutral-500">
                    Run the analysis to generate the pork‑chop plot
                </div>
        }

        <div className="flex-1 relative">

        {
            props.porkChopData2D && 

            <Plot
                data={data2D ?? []}
                layout={layout}
                style={{ width: "100%", height: "100%" }}
                config={config}
                onClick={handleClick2D}
            />
        }

        {
            props.porkChopData3D &&

            <>

                <div className="absolute left-100 z-2 flex">

                    <FormInput
                        label={`Flyby Date: ${props.porkChopData3D.flybyDates[flybyDateIndex]}`}
                        type="range"
                        name="flybyDate"
                        min={0}
                        max={flybyDateLength}
                        value={flybyDateIndex}
                        setValue={handleLayer}
                    />

                </div>

                <Plot
                    data={data3D ?? []}
                    key={flybyDateIndex}
                    layout={layout}
                    style={{ width: "100%", height: "100%" }}
                    config={config}
                    onClick={handleClick3D}
                />

            </>
        }

        </div>

        {
            //props.porkChopData2D && <PorkChopLegend/>
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