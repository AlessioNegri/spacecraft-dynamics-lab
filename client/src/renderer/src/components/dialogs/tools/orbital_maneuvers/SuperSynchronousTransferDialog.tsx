import * as react from "react"
import * as Form from "@radix-ui/react-form"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"

const defaultIn: ISuperSynchronousTransferFormInput =
{
    sstoPeriapsisRadius: 6563.1,
    samples: 200
}

const defaultOut: ISuperSynchronousTransferOut =
{
    series: []
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function SuperSynchronousTransferDialog */
export default function SuperSynchronousTransferDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<ISuperSynchronousTransferFormInput>(defaultIn)

    const [formOut, setFormOut] = react.useState<ISuperSynchronousTransferOut>(defaultOut)

    const [loading, setLoading] = react.useState<boolean>(false)

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- USE MEMO ---

    const traces: plotly.Data[] = react.useMemo(() =>
    {
        const colors: string[] = ["#ff8a65", "#facc15", "#38bdf8", "#34d399", "#c084fc", "#f472b6"]

        return formOut.series.map((series: ISuperSynchronousTransferSeries, index: number) => ({
            x: series.x,
            y: series.y,
            type: "scatter",
            mode: "lines",
            name: series.label,
            line: { color: colors[index % colors.length], width: 2.5 }
        }))
    }, [formOut.series])

    const layout: any = react.useMemo(() => ({
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5e5e5" },
        margin: { l: 60, r: 20, t: 40, b: 60 },
        xaxis:
        {
            title: { text: "SSTO apoapsis / GEO radius", standoff: 10 },
            gridcolor: "#444",
            zeroline: false,
            tickfont: { color: "#e5e5e5" }
        },
        yaxis:
        {
            title: { text: "dV₂ + dV₃ [km/s]", standoff: 10 },
            gridcolor: "#444",
            zeroline: false,
            tickfont: { color: "#e5e5e5" }
        },
        legend: { bgcolor: "rgba(0,0,0,0.15)", x: 1.02, y: 1 }
    }), [])

    const config: any = react.useMemo(() => ({
        responsive: true,
        displaylogo: false,
        scrollZoom: true
    }), [])

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
            setLoading(true)

            const response: any = await http.api.put("/orbital-maneuvers/tools/super-synchronous-transfer", formIn)

            setFormOut(response.data)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
        finally
        {
            setLoading(false)
        }
    }

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Super-Synchronous Transfer"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
            {
                title: "Super-Synchronous Transfer",
                content:
                    `Parametric super-synchronous transfer study: each curve corresponds to a different SSTO inclination
                    value (representing the launch site latitudes) and plots dV₂ + dV₃ against the normalized SSTO
                    apoapsis radius.
                    The total delta-v of the satellite for a LEO -> SSTO -> ITO -> GEO transfer as a function of
                    relative SSTO apogee distance and for different inclination changes at the second kick-burn (SSTO
                    apogee) and vanishing inclination change at the first and third kick-burn.`
            }}
        >

            <Form.Root ref={formRef} onSubmit={handleSubmit} className="space-y-4">

                <div className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                    <InputField
                        name="sstoPeriapsisRadius"
                        label="SSTO Periapsis Radius"
                        symbol="r_{p,SSTO}"
                        unit="km"
                        type="number"
                        value={formIn.sstoPeriapsisRadius}
                        onChange={handleChange}
                    />

                    <InputField
                        name="samples"
                        label="Samples"
                        symbol="N"
                        unit=""
                        type="number"
                        value={formIn.samples}
                        onChange={handleChange}
                    />

                </div>

                {
                    !loading && formOut.series.length === 0 &&

                    <p className="text-center text-neutral-400">
                        No data available yet. Set the SSTO configuration and press Compute.
                    </p>
                }

                {
                    loading &&
                    <p className="text-center text-orange-300">Computing SSTO family ...</p>
                }

                {
                    !loading && formOut.series.length > 0 &&

                    <Plot
                        data={traces}
                        layout={layout}
                        config={config}
                        style={{ width: "100%", height: "500px" }}
                    />
                }

            </Form.Root>

        </DialogRUI>
    )
}
