import * as react from "react"
import * as Form from "@radix-ui/react-form"
import * as plotly from "plotly.js"
import Plot from "react-plotly.js"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface IFormIn
{
    attractor: string
    oe: IOrbitalElements
    timestamp: string
    duration: number
    samples: number
}

interface IFormOut
{
    draan_dt: number // ? RAAN variation
    daop_dt: number // ? Argument Of Periapsis variation
    alpha: number // ? Right Ascension
    delta: number // ? Declination
    tangentPointAngle: number
    lineOfSightAngle: number
    horizonFootprintArcLengthAttractor: number
    longitude: number[]
    latitude: number[]
    horizonFootprintArcLengthEarth: number[]
}

const defaultIn: IFormIn =
{
    attractor: "earth",
    oe:
    {
        sam: 0,
        sma: 8350,
        ecc: 0.1976,
        inc: 60,
        raan: 270,
        aop: 45,
        ta: 230
    },
    timestamp: '2026-01-01T00:00:00',
    duration: 45 * 60,
    samples: 100
}

const defaultOut: IFormOut =
{
    draan_dt: 0,
    daop_dt: 0,
    alpha: 0,
    delta: 0,
    tangentPointAngle: 0,
    lineOfSightAngle: 0,
    horizonFootprintArcLengthAttractor: 0,
    longitude: [],
    latitude: [],
    horizonFootprintArcLengthEarth: []
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function GroundTrackPropagationDialog */
export default function GroundTrackPropagationDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)

    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [data, setData] = react.useState<plotly.Data[]>([])

    const [showFootprints, setShowFootprints] = react.useState<boolean>(true)

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- USE MEMO ---

    const latAnnotations =
    [
        { x: 0, y: -90, text: "" },
        { x: 0, y: 0, text: "" },
        { x: 0, y: 90, text: "" }
    ].map(a => ({
        ...a,
        xref: "x",
        yref: "y",
        showarrow: false,
        font: { color: "#e5e5e5", size: 12 }
    }))

    const lonAnnotations =
    [
        { x: -180, y: -90, text: "" },
        { x: 0, y: -90, text: "" },
        { x: 180, y: -90, text: "" }
    ].map(a => ({
        ...a,
        xref: "x",
        yref: "y",
        showarrow: false,
        font: { color: "#e5e5e5", size: 12 }
    }))

    const layout: any = react.useMemo(() => (
    {
        autosize: true,
        showlegend: false,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        geo:
        {
            projection: { type: "equirectangular" },
            showland: true,
            landcolor: "#2f4f2f", // "#111827",
            showcountries: true,
            countrycolor: "888", // "#444444",
            showocean: true,
            oceancolor: "#0a2a43", // "#0b1220",
            showlakes: true,
            lakecolor: "#0a1b33",
            showcountriesframe: false,
            showcoastlines: true,
            coastlinecolor: "#555555",
            lataxis: { showgrid: true, gridcolor: "#323232", },
            lonaxis: { showgrid: true, gridcolor: "#323232", }
        },
        margin: { l: 30, r: 30, t: 30, b: 30 },
        title:
        {
            text: "Earth Ground Track",
            font: { color: "#ffffff", size: 18 }
        },
        font: { color: "#e5e5e5" },
        annotations: [ ...latAnnotations, ...lonAnnotations ]
    }), [])

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        if (name.includes("."))
        {
            const [ group, axis ] = name.split(".")
    
            setFormIn({ ...formIn, [group]: { ...formIn[group], [axis]: value } })

            return
        }

        setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.put(`/tools/propagate-ground-track`, formIn)

            const result: IFormOut = response.data
            
            setFormOut(result)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    react.useEffect(() =>
    {
        const trace: plotly.Data =
        {
            lon: formOut.longitude,
            lat: formOut.latitude,
            type: "scattergeo",
            mode: "lines+markers",
            marker: { color: "#ff9900", size: 6 },
            line: { color: "#00ccff", width: 2 },
            name: "Ground Track"
        }

        const footprintTraces: plotly.Data[] = formOut.latitude.map((lat0, i) =>
        {
            const lon0Rad: number = formOut.longitude[i] * Math.PI / 180

            const lat0Rad: number = lat0 * Math.PI / 180

            const arc: number = formOut.horizonFootprintArcLengthEarth[i]

            const angularRadius: number = arc / 6378

            const N: number = 100

            const circleLat: number[] = []
            const circleLon: number[] = []

            let circleLat0: number = 0
            let circleLon0: number = 0

            for (let k = 0; k < N; k++)
            {
                const theta: number = 2 * Math.PI * k / N

                const lat: number = Math.asin(
                    Math.sin(lat0Rad) * Math.cos(angularRadius) +
                    Math.cos(lat0Rad) * Math.sin(angularRadius) * Math.cos(theta)
                )

                const lon: number = lon0Rad + Math.atan2(
                    Math.sin(theta) * Math.sin(angularRadius) * Math.cos(lat0Rad),
                    Math.cos(angularRadius) - Math.sin(lat0Rad) * Math.sin(lat)
                )

                circleLat.push(lat * 180 / Math.PI)
                circleLon.push(lon * 180 / Math.PI)

                if (k === 0)
                {
                    circleLat0 = circleLat[0]
                    circleLon0 = circleLon[0]
                }
            }

            circleLat.push(circleLat0)
            circleLon.push(circleLon0)

            return {
                lon: circleLon,
                lat: circleLat,
                type: "scattergeo",
                mode: "lines",
                line: { color: "rgba(255,255,255,0.3)", width: 1 },
            }
        })

        setData(showFootprints ? [trace, ...footprintTraces] : [trace])
    }, [formOut, showFootprints])

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Ground Track Propagation"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Ground Track Propagation",
                    content:
                        `Given the initial orbital elements of a satellite relative to the Inertial Reference Frame,
                        compute the right ascension and declination relative to the rotating earth after a given time
                        interval. In addition, the horizon footprint is evaluated and also shown in the Earth Ground
                        Track`
                }
            }>

            {/* INPUT */}

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <InputField
                    name="attractor"
                    label="Attractor"
                    type="select"
                    value={formIn.attractor}
                    onChange={handleChange}
                    options={
                        [
                            { label: "Mercury", value: "mercury" },
                            { label: "Venus", value: "venus" },
                            { label: "Earth", value: "earth" },
                            { label: "Mars", value: "mars" },
                            { label: "Jupiter", value: "jupiter" },
                            { label: "Saturn", value: "saturn" },
                            { label: "Uranus", value: "uranus" },
                            { label: "Neptune", value: "neptune" }
                        ]}
                />

                <InputField
                    name="timestamp"
                    label="UTC Timestamp"
                    symbol="t"
                    type="datetime-local"
                    value={formIn.timestamp}
                    onChange={handleChange}
                />

                <InputField
                    name="duration"
                    label="Duration"
                    symbol="t"
                    unit="s"
                    value={formIn.duration}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    name="samples"
                    label="Samples"
                    symbol="\#"
                    unit=""
                    type="number"
                    value={formIn.samples}
                    onChange={handleChange}
                    min={2}
                    max={1000}
                />

                <InputField
                    name="showFootprints"
                    label="Show Horizon Footprints"
                    type="checkbox"
                    value={Number(showFootprints)}
                    onChange={(e) => setShowFootprints((e.target as unknown as { value: boolean }).value)}
                />

                <span className="col-span-full"></span>

                {/* <span className="col-span-3 text-center uppercase font-semibold">Orbital Elements</span> */}

                <InputField
                    name="oe.sma"
                    label="Semimajor Axis"
                    symbol="a"
                    unit="km"
                    type="text"
                    value={String(formIn.oe.sma)}
                    onChange={handleChange}
                    pattern="^(?!0$).*"
                />

                <InputField
                    name="oe.ecc"
                    label="Eccentricity"
                    symbol="e"
                    unit=""
                    value={formIn.oe.ecc}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    type="number"
                    name="oe.inc"
                    label="Inclination"
                    symbol="i"
                    unit="deg"
                    value={formIn.oe.inc}
                    onChange={handleChange}
                    min={0}
                    max={180}
                />

                <InputField
                    type="number"
                    name="oe.raan"
                    label="Right Ascension of Ascending Node"
                    symbol="\Omega"
                    unit="deg"
                    value={formIn.oe.raan}
                    onChange={handleChange}
                    min={0}
                    max={360}
                />

                <InputField
                    type="number"
                    name="oe.aop"
                    label="Argument Of Periapsis"
                    symbol="\omega"
                    unit="deg"
                    value={formIn.oe.aop}
                    onChange={handleChange}
                    min={0}
                    max={360}
                />

                <InputField
                    type="number"
                    name="oe.ta"
                    label="True Anomaly"
                    symbol="\theta"
                    unit="deg"
                    value={formIn.oe.ta}
                    onChange={handleChange}
                    min={0}
                    max={360}
                />

            </Form.Root>

            {/* OUTPUT */}
            
            <Form.Root className="grid grid-cols-2 gap-4 mb-4">
                
                <OutputField
                    label="Right Ascension of Ascending Node Variation"
                    symbol="d\Omega / dt"
                    unit="deg / day"
                    value={formOut.draan_dt}
                />

                <OutputField
                    label="Argument Of Periapsis Variation"
                    symbol="d\omega / dt"
                    unit="deg / day"
                    value={formOut.daop_dt}
                />

                <OutputField
                    label="Right Ascension"
                    symbol="\alpha"
                    unit="deg"
                    value={formOut.alpha}
                />

                <OutputField
                    label="Declination"
                    symbol="\delta"
                    unit="deg"
                    value={formOut.delta}
                />

                <div className="col-span-full flex gap-4">

                    <OutputField
                        label="Tangent point angle"
                        symbol="\beta"
                        unit="deg"
                        value={formOut.tangentPointAngle}
                    />

                    <OutputField
                        label="Line of sight angle"
                        symbol="\delta"
                        unit="deg"
                        value={formOut.lineOfSightAngle}
                    />

                    <OutputField
                        label="Horizon footprint arc length"
                        symbol="C_f"
                        unit="km"
                        value={formOut.horizonFootprintArcLengthAttractor}
                    />

                </div>

            </Form.Root>

            {/* MAP PLOT */}

            <Plot
                data={data}
                layout={layout}
                config={{ responsive: true, displaylogo: false, scrollZoom: true, staticPlot: false }}
                style={{ width: "100%", height: "400px" }}
            />

        </DialogRUI>
    )
}