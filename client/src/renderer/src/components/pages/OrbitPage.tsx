import * as react from "react"
import * as cesium from "cesium"
import * as resium from "resium"
import * as iconify from "@iconify/react"

import http from "@renderer/common/http"
import orbit from "@renderer/common/orbit"

import LayersPanel from "../common/LayersPanel"
import TelemetryPanel from "../common/TelemetryPanel"
import Tooltip from "../Tooltip"

/** @function OrbitPage */
export default function OrbitPage()
{
    // --- USE STATE ---

    const [viewerKey, setViewerKey] = react.useState<number>(0)

    // --- RENDERING ---

    return (
        <div className="relative h-full w-full">

            <div className="absolute right-0 bottom-8 z-2">

                <Tooltip title="Reload" side="left">

                    <iconify.Icon
                        icon="mdi:reload"
                        width={29}
                        className="bg-gray-700 border border-gray-600 hover:bg-cyan-700 hover:border hover:border-cyan-300 cursor-pointer"
                        onClick={() => setViewerKey(k => k + 1)} />
                    
                </Tooltip>

            </div>

            <OrbitViewer key={viewerKey} />

        </div>
    )
}

/** @function OrbitViewer */
function OrbitViewer()
{
    // --- HTTP ---

    const getSpacecrafts = async () =>
    {
        try
        {
            const res = await http.api.get<IDbSpacecraftItem[]>("/spacecraft/items")

            const data = res.data.map(item => ({ ...item, visible: true }))

            setItems(data)
        }
        catch (err)
        {
            const message: string | null = http.checkError(import.meta.url, err)
            
            if (message) globalThis.window.api.error(`[${import.meta.url}] ${message}`)
        }
    }

    // --- USE STATE ---

    const [viewerReady, setViewerReady] = react.useState(false)

    const [models, setModels] = react.useState<IGlbModel[]>([])

    const [items, setItems] = react.useState<IDbSpacecraftItem[]>([])

    const [selectedId, setSelectedId] = react.useState<string | null>(null)

    const [creditContainer, setCreditContainer] = react.useState<HTMLDivElement | null>(null)

    const [layoutContainer, setLayoutContainer] = react.useState<HTMLDivElement | null>(null)
    
    const [telemetryContainer, setTelemetryContainer] = react.useState<HTMLDivElement | null>(null)

    // --- USE REF ---

    const viewerRef = react.useRef<resium.CesiumComponentRef<cesium.Viewer>>(null)

    const entityRefs = react.useRef<Map<string, cesium.Entity>>(new Map())

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        // * Retrieve GLB models
        
        fetch("./models/models.json").then(res => res.json()).then(setModels)

        // * Retrieve Spacecraft from DB
        
        getSpacecrafts()
    }, [])

    react.useEffect(() =>
    {
        if (!items.length) return

        const ref = viewerRef.current

        if (!ref) return

        const viewer = ref.cesiumElement

        if (!viewer) return

        //viewer.scene.globe.baseColor = cesium.Color.DARKGRAY

        //viewer.camera.setView({ destination: cesium.Cartesian3.fromDegrees(0, 10_000_000, 20_000_000) })

        const start: cesium.JulianDate  = cesium.JulianDate.now()
        const stop: cesium.JulianDate   = cesium.JulianDate.addSeconds(start, 3600, new cesium.JulianDate())

        clockViewModel.startTime        = start.clone()
        clockViewModel.stopTime         = stop.clone()
        clockViewModel.currentTime      = start.clone()
        clockViewModel.clockRange       = cesium.ClockRange.LOOP_STOP
        clockViewModel.multiplier       = 1 // ? 1 second
        clockViewModel.shouldAnimate    = true

        setViewerReady(true)
    }, [items])

    react.useEffect(() =>
    {
        const viewer = viewerRef.current?.cesiumElement

        if (!viewer) return

        if (selectedId)
        {
            const entity = entityRefs.current.get(selectedId)

            viewer.selectedEntity = entity

            viewer.selectedEntityChanged.raiseEvent(entity)

            viewer.flyTo(entity!, { duration: 5 })

            //viewer.camera.lookAtTransform(cesium.Matrix4.IDENTITY, new cesium.Cartesian3(0, -2000, 800))
        }
        else
        {
            viewer.selectedEntity = undefined
        }
    }, [selectedId])

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

    // * Orbits

    const orbits = react.useMemo(() => items.map(item =>
    {
        return orbit.generateOrbitPositions({ ...item.orbit, sma: item.orbit.sma * 1000 })
    }), [items])

    const satellitePaths = react.useMemo(() =>
    {
        return orbits.map(positions => orbit.buildSampledPosition(positions))
    }, [orbits])

    // --- RENDERING ---

    const toggleVisibility = (id: string) =>
    {
        setItems(prev => prev.map(sc => sc._id === id ? { ...sc, visible: !sc.visible } : sc))
    }

    return (
        <div className="h-full w-full relative">

            {/* Hide default Cesium credit */}

            <div ref={setCreditContainer} style={{ display: "none" }} id="credit-container" />

            {/* Layers panel */}

            <div ref={setLayoutContainer}>

                <LayersPanel
                    spacecrafts={items}
                    selectedId={selectedId}
                    onToggle={toggleVisibility}
                    onTrack={(id: string) => setSelectedId(id)}
                    onStop={() => setSelectedId(null)} />
            
            </div>

            {/* Telemetry panel */}

            <div ref={setTelemetryContainer}>

                <TelemetryPanel
                    selectedId={selectedId}
                    entityRefs={entityRefs}
                    viewerRef={viewerRef}
                    />

            </div>

        {
            creditContainer && layoutContainer && telemetryContainer && (

            <resium.Viewer
                ref={viewerRef}
                creditDisplay={undefined}
                timeline={false}
                animation={false}
                baseLayerPicker={true}
                geocoder={true}
                sceneModePicker={true}
                navigationHelpButton={true}
                homeButton={true}
                imageryProviderViewModels={viewModels}
                terrain={undefined} // ? Disable terrain to avoid CSP issues
                creditContainer={document.getElementById("credit-container") ?? undefined}
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
                            show={items[index].visible}
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
                                    ref={el => { if (el) entityRefs.current.set(items[index]._id!, el.cesiumElement!) }}
                                    position={path}
                                    show={items[index].visible}
                                    point={new cesium.PointGraphics(
                                        {
                                            pixelSize: items[index].style.width * 2,
                                            color: cesium.Color.fromCssColorString(items[index].style.color)
                                        })}
                                    onClick={() => setSelectedId(items[index]._id!)}
                                    />
                            )
                        }
                        else
                        {
                            return (
                                <resium.Entity
                                    key={items[index]._id + "_sat"}
                                    ref={el => { if (el) entityRefs.current.set(items[index]._id!, el.cesiumElement!) }}
                                    position={path}
                                    //path={new cesium.PathGraphics({ width: 2, material: cesium.Color.YELLOW.withAlpha(0.5) })}
                                    show={items[index].visible}
                                    model={new cesium.ModelGraphics(
                                        {
                                            uri: `./models/${items[index].model}.glb`,
                                            scale: 1, // ? Tweak as needed
                                            minimumPixelSize: models.find(m => m.name === items[index].model)?.minimumPixelSize ?? 1, // ? Keeps it visible when far
                                            maximumScale: models.find(m => m.name === items[index].model)?.maximumScale ?? 1 // ? Avoids insane scaling when close
                                        })}
                                    onClick={() => setSelectedId(items[index]._id!)}
                                    />
                            )
                        }                    
                    }
                )}

            </resium.Viewer>)
        }
            
        </div>
    )
}