import * as react from "react"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import background from "@renderer/assets/space_background.jpg"

/**
 * @description Create a Plotly trace for visualization
 * 
 * @param positions 3D position vector
 * @param name Name of the trace
 * @param color Color of the trace
 * @param width Width of the trace
 * @returns A Plotly data trace
 */
function makeOrbitTrace(positions: IVector3D[], name: string, color: string, width: number): plotly.Data
{
    const orbit: plotly.Data =
    {
        x: positions.map(p => p.x),
        y: positions.map(p => p.y),
        z: positions.map(p => p.z),
        type: "scatter3d",
        mode: "lines",
        line: { color: color, width: width },
        name: name,
    }

    return orbit
}

/**
 * @description Create a Plotly marker for visualization
 * 
 * @param position 3D position vector
 * @param name Name of the marker
 * @param color Color of the marker
 * @param size Size of the marker
 * @returns A Plotly marker
 */
function makeMarker(position: IVector3D | undefined, name: string, color: string, size: number = 10): plotly.Data
{
    const marker: plotly.Data =
    {
        x: [position?.x ?? 0],
        y: [position?.y ?? 0],
        z: [position?.z ?? 0],
        type: "scatter3d",
        mode: "markers",
        marker: { color: color, size: size },
        name: name,
    }

    return marker
}

interface Props
{
    orbits: IOrbits
}

/** @function CentralPanel */
export default function CentralPanel(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [orbits, setOrbits] = react.useState<plotly.Data[]>()

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (props.orbits === null) return

        const axisX: plotly.Data =
        {
            x: [0, 10000],
            y: [0, 0],
            z: [0, 0],
            type: "scatter3d",
            mode: "lines",
            line: { color: "#ff0000", width: 3, dash: "longdashdot" },
            name: "X",
        }

        const axisY: plotly.Data =
        {
            x: [0, 0],
            y: [0, 10000],
            z: [0, 0],
            type: "scatter3d",
            mode: "lines",
            line: { color: "#00ff00", width: 3, dash: "longdashdot" },
            name: "Y",
        }

        const axisZ: plotly.Data =
        {
            x: [0, 0],
            y: [0, 0],
            z: [0, 10000],
            type: "scatter3d",
            mode: "lines",
            line: { color: "#00A0ff", width: 3, dash: "longdashdot" },
            name: "Z",
        }

        const planet: plotly.Data =
        {
            x: [0],
            y: [0],
            z: [0],
            type: "scatter3d",
            mode: "markers",
            marker: { color: "yellow", size: 30 },
            name: "Attractor",
        }

        const initialPosition: plotly.Data = makeMarker(props.orbits.initial[0], "Initial Position", "#00ccff", 10)

        const initialOrbit: plotly.Data = makeOrbitTrace(props.orbits.initial, "Initial Orbit", "#00ccff", 10)

        const transferOrbit: plotly.Data = makeOrbitTrace(props.orbits.transfer, "Transfer Orbit", "#ffffff", 5)

        const finalPosition: plotly.Data = makeMarker(props.orbits.final[0], "Final Position", "#ff00ff", 10)

        const finalOrbit: plotly.Data = makeOrbitTrace(props.orbits.final, "Final Orbit", "#ff00ff", 10)

        setOrbits([axisX, axisY, axisZ, planet, initialOrbit, initialPosition, finalOrbit, finalPosition, transferOrbit])
    }, [props.orbits])

    // --- CONST ---

    const layout: any = //plotly.Layout
    {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 50, r: 50, t: 50, b: 50 },
        title:
        {
            text: "",
            font:
            {
                color: "#FFFFFF",
                size: 20,
                family: "Lucida Console"
            }
        },
        scene:
        {
            aspectmode: "data",
            xaxis:
            {
                visible: false,
                title:
                {
                    text: "X (km)",
                    font:
                    {
                        color: "#FFFFFF",
                        size: 16,
                        family: "Lucida Console"
                    }
                }
            },
            yaxis:
            {
                visible: false,
                title:
                {
                    text: "Y (km)",
                    font:
                    {
                        color: "#FFFFFF",
                        size: 16,
                        family: "Lucida Console"
                    }
                }
            },
            zaxis:
            {
                visible: false,
                title:
                {
                    text: "Z (km)",
                    font:
                    {
                        color: "#FFFFFF",
                        size: 16,
                        family: "Lucida Console"
                    }
                }
            },
        },
        // updatemenus:
        // [
        //     {
        //         type: "buttons",
        //         showactive: false,
        //         buttons: [
        //             {
        //                 label: "Play",
        //                 method: "animate",
        //                 args: [null, { frame: { duration: 30, redraw: false }, fromcurrent: true }],
        //             },
        //             {
        //                 label: "Pause",
        //                 method: "animate",
        //                 args: [[null], { mode: "immediate", frame: { duration: 0 } }],
        //             },
        //         ],
        //     },
        // ]
    }

    const config: any = //plotly.Config
    {
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }

    // --- RENDERING ---

    return (
        <div
            className={`w-full h-full bg-cover bg-center rounded-xl`}
            style={{ backgroundImage: `url(${background})` }}
        >

            <Plot
                data={orbits ?? []}
                layout={layout}
                style={{ width: "100%", height: "100%" }}
                config={config}
            />
            
        </div>
    )
}
