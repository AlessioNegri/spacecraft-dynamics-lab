import * as react from "react"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

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
    solutions: IRelativeMotionFormOutput
}

/** @function BottomPanel */
export default function BottomPanel(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [solutions, setSolutions] = react.useState<plotly.Data[]>()

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (props.solutions === null) return

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

        const linearized: plotly.Data = makeOrbitTrace(props.solutions.linearizedSolution, "Linearized", "#00ccff", 10)

        const clohessyWiltshire: plotly.Data = makeOrbitTrace(props.solutions.clohessyWiltshireSolution,
            "Clohessy Wiltshire", "#ff00ff", 10)

        const twoImpulsiveManeuver: plotly.Data = makeOrbitTrace(props.solutions.twoImpulsiveManeuver,
            "2-Impulsive Maneuver", "#F0F0F0", 10)

        const start: plotly.Data = makeMarker(props.solutions.twoImpulsiveManeuver[0], "Start", "#00ff00", 10)

        const finish: plotly.Data = makeMarker(props.solutions.twoImpulsiveManeuver[-1], "Finish", "#ffff00", 10)

        setSolutions([axisX, axisY, axisZ, linearized, clohessyWiltshire, twoImpulsiveManeuver, start, finish])
    }, [props.solutions])

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
            text: "Relative Motion and 2-Imulsive Maneuver",
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
        }
    }

    // --- RENDERING ---

    return (
        <div className="w-full h-[50%] flex flex-col space-y-4 p-4 overflow-auto custom-scrollbar">

            <Plot
                data={solutions ?? []}
                layout={layout}
                style={{ width: "100%", height: "100%" }}
            />
            
        </div>
    )
}
