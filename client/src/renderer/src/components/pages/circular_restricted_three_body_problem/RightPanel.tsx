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
function makeOrbitTrace(x: number[], y: number[], z: number[], name: string, color: string, width: number): plotly.Data
{
    const orbit: plotly.Data =
    {
        x: x,
        y: y,
        z: z,
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
    lagrangePoint?: string
}

/** @function RightPanel */
export default function RightPanel(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---
    
    const [solution, setSolution] = react.useState<plotly.Data[] | null>()

    // --- USE REF ---

    const lagrangePointRef = react.useRef<string | undefined>(props.lagrangePoint)
    
    // --- USE EFFECT ---

    const axisX: plotly.Data =
    {
        x: [0, 100],
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
        y: [0, 100],
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
        z: [0, 100],
        type: "scatter3d",
        mode: "lines",
        line: { color: "#00A0ff", width: 3, dash: "longdashdot" },
        name: "Z",
    }

    react.useEffect(() => { lagrangePointRef.current = props.lagrangePoint }, [props.lagrangePoint])
        
    react.useEffect(() =>
    {
        const rmWSS = globalThis.window.callback.onWebSocketSimulation((sim: WebSocketSimulation) =>
        {
            if (sim.source === "circular-restricted-three-body-problem" &&
                sim.data && typeof sim.data === "object" && Object.keys(sim.data).length > 0)
            {
                const linearized: plotly.Data = makeOrbitTrace(sim.data['position_x'],
                    sim.data['position_y'], sim.data['position_z'], "Linearized", "#00ccff", 10)
                
                const start: plotly.Data = makeMarker({ x: 0, y: 0, z: 0 }, lagrangePointRef.current ?? "", "#00ff00", 10)

                setSolution([axisX, axisY, axisZ, linearized, start])
            }
            else if (sim.source === "circular-restricted-three-body-problem" &&
                (!sim.data || typeof sim.data !== "object" || Object.keys(sim.data).length === 0))
            {
                const start: plotly.Data = makeMarker({ x: 0, y: 0, z: 0 }, "", "#00ff00", 10)

                setSolution([axisX, axisY, axisZ, start])
            }
        })

        const start: plotly.Data = makeMarker({ x: 0, y: 0, z: 0 }, "", "#00ff00", 10)

        setSolution([axisX, axisY, axisZ, start])

        return () => { rmWSS() }
    }, [])

    // --- CONST ---

    const layout: any = //plotly.Layout
    {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 50, r: 50, t: 50, b: 50 },
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
        }
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
                data={solution ?? []}
                layout={layout}
                config={config}
                style={{ width: "100%", height: "100%" }}
            />
            
        </div>
    )
}
