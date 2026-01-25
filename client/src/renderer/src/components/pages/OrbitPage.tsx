import * as react from "react"
import * as cesium from "cesium"
import * as resium from "resium"

import api from "@renderer/common/api"
import checkError from "@renderer/common/error"
import { generateOrbitPositions } from "@renderer/common/orbit"

/** @function OrbitPage */
export default function OrbitPage()
{
    // --- USE STATE ---

    const [viewerKey, setViewerKey] = react.useState<number>(0)

    // --- RENDERING ---

    return (
        <div className="relative h-full w-full">

            <button
                onClick={() => setViewerKey(k => k + 1)}
                className="absolute left-2 top-2 z-2 bg-stone-600 p-2 rounded hover:bg-stone-400 cursor-pointer" >
                Reload Viewer
            </button>

            <OrbitViewer key={viewerKey} />
        </div>
    )
}

/** @function OrbitViewer */
function OrbitViewer()
{
    // --- USE STATE ---

    const [viewerReady, setViewerReady] = react.useState(false)

    const [models, setModels] = react.useState<IGlbModel[]>([])

    const [items, setItems] = react.useState<IDbSpacecraftItem[]>([])

    // --- USE REF ---

    const viewerRef = react.useRef<resium.CesiumComponentRef<cesium.Viewer>>(null)

    const creditRef = react.useRef<HTMLDivElement>(null)

    // --- USE MEMO ---

    // * Resium / Cesium

    const clockViewModel = react.useMemo(() => new cesium.ClockViewModel(), [])

    const osm = react.useMemo(() =>
        new cesium.UrlTemplateImageryProvider({ url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png" })
    , [])

    const viewModels = react.useMemo(() => [
        new cesium.ProviderViewModel(
        {
            name: "OpenStreetMap",
            iconUrl: cesium.buildModuleUrl("Widgets/Images/ImageryProviders/openStreetMap.png"),
            tooltip: "OSM imagery",
            creationFunction: () => osm
        })
    ], [osm])

    // * Models

    react.useEffect(() =>
    {
        // * Retrieve GLB models
        
        fetch("/models/models.json").then(res => res.json()).then(setModels)
    }, [])

    // * Orbits

    const orbits = react.useMemo(() => items.map(item =>
    {
        return generateOrbitPositions({ ...item.orbit, sma: item.orbit.sma * 1000 })
    }), [items])

    const satellitePaths = react.useMemo(() =>
    {
        return orbits.map(positions => buildSampledPosition(positions))
    }, [orbits])

    // --- HTTP ---

    const getSpacecrafts = async () =>
    {
        try
        {
            const res = await api.get<IDbSpacecraftItem[]>("/spacecraft/items")

            setItems(res.data)
        }
        catch (err)
        {
            const message: string | null = checkError(import.meta.url, err)
            
            if (message) globalThis.window.api.error(`[${import.meta.url}] ${message}`)
        }
    }

    // --- USE EFFECT ---

    react.useEffect(() => { getSpacecrafts() }, [])

    react.useEffect(() =>
    {
        const ref = viewerRef.current

        if (!ref) return

        const viewer = ref.cesiumElement

        if (!viewer) return

        //viewer.scene.globe.baseColor = cesium.Color.DARKGRAY

        //viewer.camera.setView({ destination: cesium.Cartesian3.fromDegrees(0, 0, 20_000_000) })

        const start: cesium.JulianDate  = cesium.JulianDate.now()
        const stop: cesium.JulianDate   = cesium.JulianDate.addSeconds(start, 3600, new cesium.JulianDate())

        clockViewModel.startTime        = start.clone()
        clockViewModel.stopTime         = stop.clone()
        clockViewModel.currentTime      = start.clone()
        clockViewModel.clockRange       = cesium.ClockRange.LOOP_STOP
        clockViewModel.multiplier       = 100
        clockViewModel.shouldAnimate    = true

        setViewerReady(true)
    })

    // --- RENDERING ---

    return (
        <>

            <div ref={creditRef} style={{ display: "none" }} /> {/* Hide default Cesium credit */}

            <resium.Viewer
                ref={viewerRef}
                timeline={false}
                animation={false}
                baseLayerPicker={true}
                geocoder={true}
                sceneModePicker={true}
                navigationHelpButton={true}
                homeButton={true}
                imageryProviderViewModels={viewModels}
                terrain={undefined} // ? Disable terrain to avoid CSP issues
                creditContainer={creditRef.current || undefined}
                shouldAnimate={true}
                clockViewModel={clockViewModel}
                style={{ width: "100%", height: "100%", position: "relative" }}>
                
                {/* Camera */}

                {/* <resium.CameraFlyTo duration={0} destination={cesium.Cartesian3.fromDegrees(-100, 40, 100_000_000)} /> */}

                {
                    viewerReady && orbits.map((positions: cesium.Cartesian3[], index: number) => (

                    <resium.Entity key={items[index]._id}>
                    
                        <resium.PolylineGraphics
                            positions={positions}
                            width={items[index].style.width}
                            material={cesium.Color.fromCssColorString(items[index].style.color)}
                            clampToGround={false}/>

                    </resium.Entity>

                ))}

                {
                    viewerReady && satellitePaths.map((path, index) =>
                    {
                        if (items[index].model === "")
                        {
                            return (
                                <resium.Entity
                                    key={items[index]._id + "_sat"}
                                    position={path}
                                    point={new cesium.PointGraphics(
                                        {
                                            pixelSize: items[index].style.width * 2,
                                            color: cesium.Color.fromCssColorString(items[index].style.color)
                                        })}
                                    />
                            )
                        }
                        else
                        {
                            return (
                                <resium.Entity
                                    key={items[index]._id + "_sat"}
                                    position={path}
                                    //path={new cesium.PathGraphics({ width: 2, material: cesium.Color.YELLOW.withAlpha(0.5) })}
                                    model={new cesium.ModelGraphics(
                                        {
                                            uri: `/models/${items[index].model}.glb`,
                                            scale: 1, // ? Tweak as needed
                                            minimumPixelSize: models.find(m => m.name === items[index].model)?.minimumPixelSize ?? 1, // ? Keeps it visible when far
                                            maximumScale: models.find(m => m.name === items[index].model)?.maximumScale ?? 1 // ? Avoids insane scaling when close
                                        })}
                                    />
                            )
                        }                    
                    }
                )}

            </resium.Viewer>
            
        </>
    )
}

/**
 * @description Build a SampledPositionProperty from an array of Cartesian3 positions for simulating orbits
 * 
 * @param positions Positions array
 * @returns SampledPositionProperty
 */
function buildSampledPosition(positions: cesium.Cartesian3[]): cesium.SampledPositionProperty
{
    const property: cesium.SampledPositionProperty = new cesium.SampledPositionProperty()

    const start: cesium.JulianDate = cesium.JulianDate.now()

    const step = 10 // ? Seconds between samples

    positions.forEach((pos: cesium.Cartesian3, i: number) =>
    {
        const time: cesium.JulianDate = cesium.JulianDate.addSeconds(start, i * step, new cesium.JulianDate())

        property.addSample(time, pos)
    })

    return property
}