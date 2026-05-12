import * as react from "react"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

function makeTrace(x: string[], y: number[], name: string, color: string, width: number): plotly.Data
{
    const start = new Date(x[0]).getTime();

    const xHours = x.map(t => (new Date(t).getTime() - start) / 3600000);

    const line: plotly.Data =
    {
        x: xHours,
        y: y,
        type: "scatter",
        mode: "lines",
        line: { color: color, width: width },
        name: name,
        text: x,
        hovertemplate: "Time : %{text}<br>Value: %{y}<extra></extra>"
    }

    return line
}

/** @function RightPanel */
export default function RightPanel(): react.JSX.Element
{
    // --- USE STATE ---

    const [specificAngularMomentum, setSpecificAngularMomentum] = react.useState<plotly.Data[]>()
    
    const [semiMajorAxis, setSemiMajorAxis] = react.useState<plotly.Data[]>()

    const [eccentricity, setEccentricity] = react.useState<plotly.Data[]>()

    const [inclination, setInclination] = react.useState<plotly.Data[]>()

    const [raan, setRaan] = react.useState<plotly.Data[]>()

    const [argPeriapsis, setArgPeriapsis] = react.useState<plotly.Data[]>()

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmRI = globalThis.window.callback.onReceivedInfo((info: WebSocketInfo) =>
        {
            if (info.source === "orbital-perturbations" && info.data?.["sam"] != undefined)
            {
                const sam: plotly.Data = makeTrace(info.data["times"], info.data["sam"], "Linearized", "#00ccff", 3)

                setSpecificAngularMomentum([sam])

                const sma: plotly.Data = makeTrace(info.data["times"], info.data["sma"], "Linearized", "#00ccff", 3)

                setSemiMajorAxis([sma])

                const ecc: plotly.Data = makeTrace(info.data["times"], info.data["ecc"], "Linearized", "#00ccff", 3)

                setEccentricity([ecc])

                const inc: plotly.Data = makeTrace(info.data["times"], info.data["inc"], "Linearized", "#00ccff", 3)

                setInclination([inc])

                const raan: plotly.Data = makeTrace(info.data["times"], info.data["raan"], "Linearized", "#00ccff", 3)

                setRaan([raan])

                const aop: plotly.Data = makeTrace(info.data["times"], info.data["aop"], "Linearized", "#00ccff", 3)

                setArgPeriapsis([aop])
            }
            else if (info.source === "orbital-perturbations" && info.data == undefined)
            {
                setSpecificAngularMomentum(undefined)
                setSemiMajorAxis(undefined)
                setEccentricity(undefined)
                setInclination(undefined)
                setRaan(undefined)
                setArgPeriapsis(undefined)
            }
        })

        return () => { rmRI() }
    }, [])

    // --- PLOTLY ---

    const layout: any = //plotly.Layout
    {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 50, r: 50, t: 50, b: 50 },
        title:
        {
            text: "Semi-Major Axis",
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
                text: "Time [h]",
                font:
                {
                    color: "#FFFFFF",
                    size: 16,
                    family: "Lucida Console"
                }
            },
            type: "linear",
            tickformat: ".1f",
            showgrid: true,
            gridcolor: "#ccc",
            gridwidth: 1,
            constrain: "range"
        },
        yaxis:
        {
            title:
            {
                text: "Semi-Major Axis [km]",
                font:
                {
                    color: "#FFFFFF",
                    size: 16,
                    family: "Lucida Console"
                }
            },
            // type: "linear",
            // tickformat: ".2f",
            // constrain: "range"
        }
    }

    const config: any = //plotly.Config
    {
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }

    let layoutSpecificAngularMomentum = structuredClone(layout)

    layoutSpecificAngularMomentum.title.text = "Specific Angular Momentum"
    layoutSpecificAngularMomentum.yaxis.title.text = "h [km^2/s]"

    let layoutSemiMajorAxis = structuredClone(layout)

    layoutSemiMajorAxis.title.text = "Semi-Major Axis"
    layoutSemiMajorAxis.yaxis.title.text = "a [km]"

    let layoutEccentricity = structuredClone(layout)

    layoutEccentricity.title.text = "Eccentricity"
    layoutEccentricity.yaxis.title.text = "e"

    let layoutInclination = structuredClone(layout)

    layoutInclination.title.text = "Inclination"
    layoutInclination.yaxis.title.text = "i [deg]"

    let layoutRaan = structuredClone(layout)

    layoutRaan.title.text = "RAAN"
    layoutRaan.yaxis.title.text = "Ω [deg]"

    let layoutArgPeriapsis = structuredClone(layout)

    layoutArgPeriapsis.title.text = "Argument of Periapsis"
    layoutArgPeriapsis.yaxis.title.text = "ω [deg]"

    // --- RENDERING ---

    return (
        <div className="w-full h-full rounded-lg shadow-inner p-2 grid grid-cols-2 grid-rows-3 gap-0">

            <Plot
                data={specificAngularMomentum ?? []}
                layout={layoutSpecificAngularMomentum}
                style={{ width: "100%", height: "100%" }}
                config={config}
            />

            <Plot
                data={semiMajorAxis ?? []}
                layout={layoutSemiMajorAxis}
                style={{ width: "100%", height: "100%" }}
                config={config}
            />

            <Plot
                data={eccentricity ?? []}
                layout={layoutEccentricity}
                style={{ width: "100%", height: "100%" }}
                config={config}
            />

            <Plot
                data={inclination ?? []}
                layout={layoutInclination}
                style={{ width: "100%", height: "100%" }}
                config={config}
            />

            <Plot
                data={raan ?? []}
                layout={layoutRaan}
                style={{ width: "100%", height: "100%" }}
                config={config}
            />

            <Plot
                data={argPeriapsis ?? []}
                layout={layoutArgPeriapsis}
                style={{ width: "100%", height: "100%" }}
                config={config}
            />

        </div>
    )
}
