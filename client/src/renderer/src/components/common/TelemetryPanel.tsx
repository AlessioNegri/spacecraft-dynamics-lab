import * as react from "react"
import * as cesium from "cesium"
import * as resium from "resium"
import * as iconify from "@iconify/react"

interface TelemetryData
{
    lat: number
    lon: number
    alt: number
    speed: number
    time: Date
}

interface TelemetryPanelProps
{
    selectedId: string | null
    entityRefs: react.RefObject<Map<string, cesium.Entity>>
    viewerRef: react.RefObject<resium.CesiumComponentRef<cesium.Viewer> | null>
}

/** @function TelemetryPanel */
export default function TelemetryPanel(props : Readonly<TelemetryPanelProps>)
{
    // --- USE STATE ---

    const [telemetry, setTelemetry] = react.useState<TelemetryData | null>(null)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (!props.selectedId) { setTelemetry(null); return }

        const viewer = props.viewerRef.current?.cesiumElement

        if (!viewer) return

        const entity = props.entityRefs.current.get(props.selectedId)

        if (!entity) return

        const clock = viewer.clock

        const update = () =>
        {
            const time = clock.currentTime

            // * Position

            const pos: cesium.Cartesian3 | undefined = entity.position?.getValue(time)
            
            if (!pos) return

            // * Cartographic

            const carto: cesium.Cartographic = cesium.Ellipsoid.WGS84.cartesianToCartographic(pos)

            const lat: number = cesium.Math.toDegrees(carto.latitude)
            const lon: number = cesium.Math.toDegrees(carto.longitude)
            const alt: number = carto.height / 1000 // ? km

            // * Velocity (finite difference)

            const prev: cesium.Cartesian3 | undefined = entity.position?.getValue(cesium.JulianDate.addSeconds(time,
                                                                                                    -1,
                                                                                                    new cesium.JulianDate()))

            let speed: number = 0

            if (prev)
            {
                const diff: cesium.Cartesian3 = cesium.Cartesian3.subtract(pos, prev, new cesium.Cartesian3())

                speed = cesium.Cartesian3.magnitude(diff) / 1000 // ? km/s
            }

            setTelemetry({ lat: lat, lon: lon, alt: alt, speed: speed, time: cesium.JulianDate.toDate(time) })
        }

        // * Update every frame

        const remove = viewer.scene.postRender.addEventListener(update)

        return () => remove()
    }, [props.selectedId])

    // --- RENDERING ---

    if (!telemetry)
    {
        return (
            <div
                className="absolute bottom-2 left-2 bg-neutral-800/90 backdrop-blur p-4 rounded shadow-lg w-70 z-2
                            border-2 border-neutral-400">

                <div className="font-semibold text-base pb-2 mb-2 border-b-2">Telemetry</div>
                
                <div className="text-sm text-gray-500 mt-2">No spacecraft selected</div>
                
            </div>
        )
    }

    return (
        <div
            className="absolute bottom-2 left-2 bg-neutral-800/90 backdrop-blur p-4 rounded shadow-lg w-70 z-2
                        border-2 border-neutral-400">
            
            <div className="font-semibold text-base pb-2 mb-2 border-b-2">Telemetry</div>

            <div className="text-sm grid grid-cols-[32px_1fr_1fr] space-y-2 items-center">

                <iconify.Icon icon="mdi:latitude" width={24} />

                <span className="font-bold">Latitude</span>
                
                <span>{telemetry.lat.toFixed(4)}°</span>

                <iconify.Icon icon="mdi:longitude" width={24} />

                <span className="font-bold">Longitude</span>
                
                <span>{telemetry.lon.toFixed(4)}°</span>

                <iconify.Icon icon="mdi:elevation-rise" width={24} />

                <span className="font-bold">Altitude</span>
                
                <span>{telemetry.alt.toFixed(3)} km</span>

                <iconify.Icon icon="mdi:speedometer" width={24} />

                <span className="font-bold">Speed</span>
                
                <span>{telemetry.speed.toFixed(3)} km/s</span>

                <iconify.Icon icon="mdi:access-time" width={24} />

                <span className="font-bold">Time</span>
                
                <span>{telemetry.time.toLocaleTimeString()}</span>

                <p></p>

            </div>
            
        </div>
    )
}