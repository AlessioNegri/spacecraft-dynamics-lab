import * as react from "react"
import * as Form from "@radix-ui/react-form"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"
import utility from "@renderer/common/utility"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"

interface IFormIn
{
    body1: string
    body2: string
}

interface IFormOut
{
    inertialAngularVelocity: number
    dimensionlessMassRatio1: number
    dimensionlessMassRatio2: number
    gravitationalParameter1: number
    gravitationalParameter2: number
    bodyPosition1: number
    bodyPosition2: number
    lagrangianPoint1: number[]
    lagrangianPoint2: number[]
    lagrangianPoint3: number[]
    lagrangianPoint4: number[]
    lagrangianPoint5: number[]
}

const defaultIn: IFormIn =
{
    body1: "earth",
    body2: "moon"
}

const defaultOut: IFormOut =
{
    inertialAngularVelocity: 0,
    dimensionlessMassRatio1: 0,
    dimensionlessMassRatio2: 0,
    gravitationalParameter1: 0,
    gravitationalParameter2: 0,
    bodyPosition1: 0,
    bodyPosition2: 0,
    lagrangianPoint1: [0, 0, 0],
    lagrangianPoint2: [0, 0, 0],
    lagrangianPoint3: [0, 0, 0],
    lagrangianPoint4: [0, 0, 0],
    lagrangianPoint5: [0, 0, 0]
}

/**
 * @description Compute the Jacobi constant at the given Lagrange point
 * 
 * @param x Adimensional Lagrange point position x
 * @param y Adimensional Lagrange point position y
 * @param x1 Adimensional primary body position x
 * @param x2 Adimensional secondary body position x
 * @param mu Adimensional secondary body gravitational constant
 * @returns Jacobi constant
 */
function computeJacobiAtPoint(x: number, y: number, x1: number, x2: number, mu: number): number
{
    const r1: number = Math.hypot(x - x1, y)
    const r2: number = Math.hypot(x - x2, y)
    
    const C: number = (x ** 2 + y ** 2) + (2 * (1 - mu)) / r1 + (2 * mu) / r2

    return C
}

/**
 * @description Compute the Jacobi constant for all Lagrange points
 * 
 * @param formOut Form data
 * @returns Jacobi constants
 */
function computeJacobiConstants(formOut: IFormOut): { C1: number, C2: number, C3: number, C4: number, C5: number }
{
    // ! Use the dimensionless version for easier choice of Jacobi constant

    const x1: number = formOut.bodyPosition1
    const x2: number = formOut.bodyPosition2
    const mu1: number = formOut.gravitationalParameter1
    const mu2: number = formOut.gravitationalParameter2
    const L1: number[] = formOut.lagrangianPoint1
    const L2: number[] = formOut.lagrangianPoint2
    const L3: number[] = formOut.lagrangianPoint3
    const L4: number[] = formOut.lagrangianPoint4
    const L5: number[] = formOut.lagrangianPoint5
    
    const D: number = Math.abs(x2 - x1) // ? Bodies distance

    const mu: number = mu2 / (mu1 + mu2) // ? Adimensional gravitational constant

    const C1 = computeJacobiAtPoint(L1[0] / D, L1[1] / D, x1 / D, x2 / D, mu)
    const C2 = computeJacobiAtPoint(L2[0] / D, L2[1] / D, x1 / D, x2 / D, mu)
    const C3 = computeJacobiAtPoint(L3[0] / D, L3[1] / D, x1 / D, x2 / D, mu)
    const C4 = computeJacobiAtPoint(L4[0] / D, L4[1] / D, x1 / D, x2 / D, mu)
    const C5 = computeJacobiAtPoint(L5[0] / D, L5[1] / D, x1 / D, x2 / D, mu)
    
    return { C1, C2, C3, C4, C5 }
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function ZeroVelocityCurvesDialog */
export default function ZeroVelocityCurvesDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [jacobiConstant, setJacobiConstant] = react.useState<number>(0)

    const [jacobiConstantMin, setJacobiConstantMin] = react.useState<number>(0)

    const [jacobiConstantMax, setJacobiConstantMax] = react.useState<number>(0)
    
    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (formIn.body1 === "sun")
        {
            setFormIn(prev => ({ ...prev, body2: "earth" }))
        }
        else if (formIn.body1 === "earth")
        {
            setFormIn(prev => ({ ...prev, body2: "moon" }))
        }
    }, [formIn.body1])

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            const response: any = await http.api.put(`/circular-restricted-three-body-problem/orbit-parameters`, formIn)

            const { C1, C2, C3, C4, C5 } = computeJacobiConstants(response.data)

            const minC: number = Math.min(C1, C2, C3, C4, C5) * 0.99
            const maxC: number = Math.max(C1, C2, C3, C4, C5) * 1.01

            setJacobiConstant((minC + maxC) * 0.5)
            setJacobiConstantMin(minC)
            setJacobiConstantMax(maxC)

            setFormOut(response.data)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- RENDERING ---

    const plotData: plotly.Data[] = react.useMemo<plotly.Data[]>(() =>
    {
        if (!formOut.bodyPosition1 || !formOut.bodyPosition2) return []

        // ! Use the dimensionless version for easier choice of Jacobi constant

        const C: number = jacobiConstant

        const x1: number = formOut.bodyPosition1
        const x2: number = formOut.bodyPosition2
        const mu1: number = formOut.gravitationalParameter1
        const mu2: number = formOut.gravitationalParameter2
        const L2: number[] = formOut.lagrangianPoint2
        const L3: number[] = formOut.lagrangianPoint3
        const L4: number[] = formOut.lagrangianPoint4
        const L5: number[] = formOut.lagrangianPoint5
        
        const D: number = Math.abs(x2 - x1) // ? Bodies distance

        const mu: number = mu2 / (mu1 + mu2) // ? Adimensional gravitational constant
        
        const size: number = 220 // ? Grid size

        const xValues: number[] = utility.linspace(L3[0] / D * 1.5, L2[0] / D * 1.5, size)
        const yValues: number[] = utility.linspace(L5[1] / D * 2, L4[1] / D * 2, size)
        
        const zValues = yValues.map(y =>
            xValues.map(x =>
            {
                const r1: number = Math.hypot(x - x1 / D, y) // ? First body distance
                const r2: number = Math.hypot(x - x2 / D, y) // ? Second body distance
                
                const vSquared: number = (x ** 2 + y ** 2) + (2 * (1 - mu)) / r1 + (2 * mu) / r2 - C

                return vSquared
            })
        )

        const contourTrace: plotly.Data =
        {
            x: xValues,
            y: yValues,
            z: zValues,
            type: "contour",
            showscale: false,
            showlegend: true,
            contours:
            {
                showlabels: false,
                start: 0,
                end: 0,
                size: 1
            },
            line:
            {
                color: "#00FF00",
                width: 2
            },
            colorscale: [[0, "rgba(255,255,255,0)"], [1, "rgba(0,255,0,0.25)"]],
            hoverinfo: "skip",
            name: "ZVC"
        }

        const forbiddenTrace: plotly.Data =
        {
            x: xValues,
            y: yValues,
            z: zValues.map(row => row.map((v: number) => v < 0 ? 1 : 0)),
            type: "contour",
            showscale: false,
            showlegend: true,
            contours:
            {
                showlabels: false,
                start: 0,
                end: 0,
                size: 1
            },
            colorscale: [[0, "rgba(255,255,255,0)"], [1, "rgba(255,0,0,0.25)"]],
            hoverinfo: "skip",
            name: "Forbidden Region"
        }

        const body1Trace: plotly.Data =
        {
            x: [x1 / D],
            y: [0],
            type: "scatter",
            mode: "markers",
            marker: { color: "#38bdf8", size: 14 },
            name: formIn.body1.toUpperCase()
        }

        const body2Trace: plotly.Data =
        {
            x: [x2 / D],
            y: [0],
            type: "scatter",
            mode: "markers",
            marker: { color: "#fb7185", size: 14 },
            name: formIn.body2.toUpperCase()
        }

        const lagrangePoints: number[][] =
            [
                formOut.lagrangianPoint1,
                formOut.lagrangianPoint2,
                formOut.lagrangianPoint3,
                formOut.lagrangianPoint4,
                formOut.lagrangianPoint5
            ]
        
        const lagrangeTrace: plotly.Data =
        {
            x: lagrangePoints.map(point => point[0] / D),
            y: lagrangePoints.map(point => point[1] / D),
            type: "scatter",
            mode: "text+markers",
            marker: { color: "#fde68a", size: 8 },
            name: "Lagrange points",
            text: ["L1", "L2", "L3", "L4", "L5"].map(l => `<b>${l}</b>`),
            textposition: "top center",
            textfont:
            {
                size: 14,
                color: "#fde68a",
                family: "Lucida Console",
            }
        }

        return [forbiddenTrace, contourTrace, body1Trace, body2Trace, lagrangeTrace]
    }, [formOut, jacobiConstant])

    const layout: any = react.useMemo(() => (
    {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 50, r: 50, t: 50, b: 50 },
        xaxis:
        {
            title: { text: "x" },
            zeroline: false
        },
        yaxis:
        {
            title: { text: "y" },
            zeroline: false
        },
        showlegend: true
    }), [jacobiConstant])

    const config: any =
    {
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }

    return (
        <DialogRUI
            title="Zero Velocity Curves"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={{
                title: "Zero Velocity Curves",
                content: `Use the CR3BP orbit parameters from the selected primaries to compute the zero-velocity
                    manifold and visualize the forbidden regions as the Jacobi constant varies.`
            }}
        >

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-2 gap-4 border-b pb-4 mb-4"
            >
                
                <InputField
                    name="body1"
                    label="Primary Body"
                    type="select"
                    value={formIn.body1}
                    onChange={handleChange}
                    options={
                        [
                            { label: "Sun", value: "sun" },
                            { label: "Earth", value: "earth" }
                        ]}
                />

                <InputField
                    name="body2"
                    label="Secondary Body"
                    type="select"
                    value={formIn.body2}
                    onChange={handleChange}
                    options={
                        formIn.body1 === "sun"
                            ? [
                                { label: "Mercury", value: "mercury" },
                                { label: "Venus", value: "venus" },
                                { label: "Earth", value: "earth" },
                                { label: "Mars", value: "mars" },
                                { label: "Jupiter", value: "jupiter" },
                                { label: "Saturn", value: "saturn" },
                                { label: "Uranus", value: "uranus" },
                                { label: "Neptune", value: "neptune" }
                            ]
                            : [
                                { label: "Moon", value: "moon" }
                            ]}
                />

                <InputField
                    className="col-span-full"
                    type="range"
                    name="jacobiConstant"
                    label="Jacobi Constant"
                    symbol="C"
                    value={jacobiConstant}
                    onChange={(e) => setJacobiConstant(Number(e.target.value))}
                    min={jacobiConstantMin}
                    max={jacobiConstantMax}
                    step={0.001}
                />

            </Form.Root>

            <div className="border rounded-xl overflow-hidden">
                <Plot
                    className="w-full"
                    data={plotData}
                    layout={layout}
                    config={config}
                    style={{ width: "100%", height: "500px" }}
                />
            </div>
            
        </DialogRUI>
    )
}
