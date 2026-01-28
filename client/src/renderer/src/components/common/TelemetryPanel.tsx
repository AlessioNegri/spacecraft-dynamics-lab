import * as react from "react"
import * as cesium from "cesium"
import * as resium from "resium"

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

                speed = cesium.Cartesian3.magnitude(diff)
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
            <div className="absolute bottom-2 left-2 bg-stone-800/90 backdrop-blur p-4 rounded shadow-lg w-96 z-2">

                <div className="font-semibold text-base pb-2 mb-2 border-b-2">Telemetry</div>
                
                <div className="text-sm text-gray-500 mt-2">No spacecraft selected</div>
                
            </div>
        )
    }

    return (
        <div className="absolute bottom-2 left-2 bg-stone-800/90 backdrop-blur p-4 rounded shadow-lg w-96 z-2">
            
            <div className="font-semibold text-base pb-2 mb-2 border-b-2">Telemetry</div>

            <div className="text-sm grid grid-cols-2 space-y-2">

                <strong>Latitude</strong>
                
                <p>{telemetry.lat.toFixed(4)}°</p>

                <strong>Longitude</strong>
                
                <p>{telemetry.lon.toFixed(4)}°</p>

                <strong>Altitude</strong>
                
                <p>{telemetry.alt.toFixed(2)} km</p>

                <strong>Speed</strong>
                
                <p>{telemetry.speed.toFixed(2)} m/s</p>

                <strong>Time</strong>
                
                <p>{telemetry.time.toLocaleTimeString()}</p>

            </div>
            
        </div>
    )
}