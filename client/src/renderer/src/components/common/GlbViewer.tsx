import * as react from "react"
import * as drei from "@react-three/drei"
import * as fiber from "@react-three/fiber"

interface GlbViewerProps
{
    model: string
    scale?: number
    cameraPos?: [number, number, number]
}

/** @function GlbViewer */
export default function GlbViewer({model, scale = 1.5, cameraPos = [0, 0, 1]}: Readonly<GlbViewerProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [centerKey, setCenterKey] = react.useState<number>(0)

    // --- USE REF ---

    const resetRef = react.useRef<() => void>(() => {})

    // --- RENDERING ---

    if (!model)
    {
        return (
        <div className="border-stone-600 border-4 rounded w-full flex items-center justify-center h-full text-gray-500">
            Select a model to preview
        </div>
        )
    }

    return (
        <div className="border-stone-600 border-4 rounded w-full h-full">

            <fiber.Canvas
                // camera={{ position: cameraPos, fov: 45 }}
                onDoubleClick={() => resetRef.current()}
                style={{ width: "100%", height: "100%" }}>

                <ambientLight intensity={0.6} />

                <directionalLight position={[5, 5, 5]} intensity={1} />

                <CameraController initialPos={[4, 4, 4]} onDoubleClick={resetRef} />

                {/* Recompute centering when model changes OR when double-click resets */}

                <drei.Center key={model + "-" + centerKey}>

                    <Model url={`/models/${model}.glb`} scale={scale} />

                </drei.Center>

            </fiber.Canvas>

        </div>
    )
}

/**
 * @description GLB model creation
 * 
 * @param url GLB model URL
 * @param scale Model scale
 * @returns JSX.Element
 */
function Model({ url, scale = 1 } : Readonly<{ url: string; scale?: number }>): react.JSX.Element
{
    const gltf = drei.useGLTF(url)

    return <drei.Clone object={gltf.scene} scale={scale} /> // ? Create a dedicated scene with Clone
}

/**
 * @description Camera controller with double-click reset
 * 
 * @param initialPos Initial camera position
 * @param onDoubleClick Ref to expose double-click reset function 
 * @returns 
 */
function CameraController({ initialPos, onDoubleClick }): react.JSX.Element
{
    const { reset, controlsRef } = resetCamera(initialPos)

    // * Expose reset to parent

    react.useEffect(() => { onDoubleClick.current = reset }, [reset, onDoubleClick])

    return <drei.OrbitControls ref={controlsRef} makeDefault />
}

interface ResetCameraReturn
{
    reset: () => void
    controlsRef: react.RefObject<any>
}

/**
 * @description Camera reset hook
 * 
 * @param initialPos Initial camera position
 * @returns 
 */
function resetCamera(initialPos: [number, number, number] = [4, 4, 4]): ResetCameraReturn
{
    const { camera } = fiber.useThree()

    const controlsRef = react.useRef<any>(null)

    const reset = react.useCallback(() =>
    {
        //camera.position.set(...initialPos)
        camera.lookAt(0, 0, 1)

        if (controlsRef.current)
        {
            controlsRef.current.target.set(0, 0, 1)
            controlsRef.current.update()
        }
    }, [camera, initialPos])

    return { reset, controlsRef }
}