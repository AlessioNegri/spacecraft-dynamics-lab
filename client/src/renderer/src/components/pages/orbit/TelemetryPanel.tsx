import * as react from "react"
import * as cesium from "cesium"
import * as resium from "resium"
import * as iconify from "@iconify/react"
import * as katex from "react-katex"

interface TelemetryData
{
    latitude: number
    longitude: number
    altitude: number
    speed: number
    time: Date
}

interface Props
{
    selectedId: string | null
    entityRefs: react.RefObject<Map<string, cesium.Entity>>
    viewerRef: react.RefObject<resium.CesiumComponentRef<cesium.Viewer> | null>
}

/** @function TelemetryPanel */
export default function TelemetryPanel(props : Readonly<Props>)
{
    // --- USE STATE ---

    const [telemetry, setTelemetry] = react.useState<TelemetryData | null>(null)

    const [open, setOpen] = react.useState<boolean>(true)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (!props.selectedId)
        {
            setTelemetry(null)
            
            return
        }

        const viewer: cesium.Viewer | undefined = props.viewerRef.current?.cesiumElement

        if (!viewer) return

        const entity: cesium.Entity | undefined = props.entityRefs.current.get(props.selectedId)

        if (!entity) return

        const clock: cesium.Clock = viewer.clock

        const update = () =>
        {
            // * Julian date

            const time: cesium.JulianDate = clock.currentTime

            // * Position

            const position: cesium.Cartesian3 | undefined = entity.position?.getValue(time)
            
            if (!position) return

            // * Cartographic

            const carto: cesium.Cartographic = cesium.Ellipsoid.WGS84.cartesianToCartographic(position)

            const latitude: number = cesium.Math.toDegrees(carto.latitude)
            const longitude: number = cesium.Math.toDegrees(carto.longitude)
            const altitude: number = carto.height / 1000 // ? km

            // * Velocity (finite difference)

            const prev: cesium.Cartesian3 | undefined = entity.position?.getValue(cesium.JulianDate.addSeconds(time,
                                                                                                    -1,
                                                                                                    new cesium.JulianDate()))

            let speed: number = 0

            if (prev)
            {
                const diff: cesium.Cartesian3 = cesium.Cartesian3.subtract(position, prev, new cesium.Cartesian3())

                speed = cesium.Cartesian3.magnitude(diff) / 1000 // ? km/s
            }

            setTelemetry({
                latitude: latitude,
                longitude: longitude,
                altitude: altitude,
                speed: speed,
                time: cesium.JulianDate.toDate(time)
            })
        }

        // * Update every frame

        const remove: cesium.Event.RemoveCallback = viewer.scene.postRender.addEventListener(update)

        return () => remove()
    }, [props.selectedId])

    // --- RENDERING ---

    return (
        <div className="absolute bottom-2 left-2 bg-neutral-800/90 backdrop-blur p-4 rounded shadow-lg w-80 z-2
                        border-2 border-neutral-400">

            <button className="w-full cursor-pointer" onClick={() => setOpen(prev => !prev)}>
                <div className="font-semibold text-base pb-2 mb-2 border-b-2">Telemetry</div>
            </button>

            { !telemetry && <div className="text-sm text-gray-500 mt-2">No spacecraft selected</div> }
            
            {
                open && telemetry &&

                <div className="text-sm grid grid-cols-[32px_1fr_1fr_1fr] gap-2 items-center">

                    <iconify.Icon icon="mdi:latitude" width={24} />

                    <span className="font-bold">Latitude</span>
                    
                    <span className="text-right">{telemetry.latitude.toFixed(4)}</span>

                    <div className="text-right"><katex.InlineMath math="\mathbf{deg}" /></div>



                    <iconify.Icon icon="mdi:longitude" width={24} />

                    <span className="font-bold">Longitude</span>
                    
                    <span className="text-right">{telemetry.longitude.toFixed(4)}</span>

                    <div className="text-right"><katex.InlineMath math="\mathbf{deg}" /></div>



                    <iconify.Icon icon="mdi:elevation-rise" width={24} />

                    <span className="font-bold">Altitude</span>
                    
                    <span className="text-right">{telemetry.altitude.toFixed(3)}</span>

                    <div className="text-right"><katex.InlineMath math="\mathbf{km}" /></div>



                    <iconify.Icon icon="mdi:speedometer" width={24} />

                    <span className="font-bold">Speed</span>
                    
                    <span className="text-right">{telemetry.speed.toFixed(3)}</span>

                    <div className="text-right"><katex.InlineMath math="\mathbf{km / s}" /></div>



                    <iconify.Icon icon="mdi:access-time" width={24} />

                    <span className="font-bold">Time</span>
                    
                    <span className="text-right">{telemetry.time.toLocaleTimeString()}</span>

                    <div className="text-right"><katex.InlineMath math="" /></div>

                </div>
            }

        </div>
    )
}
