import * as react from "react"

import utility from "@renderer/common/utility"

import Console from "./Console"
import SpacecraftPage from "./pages/SpacecraftPage"
import OrbitPage from "./pages/OrbitPage"
import OrbitalManeuversPage from "./pages/OrbitalManeuversPage"
import RelativeMotionPage from "./pages/RelativeMotionPage"
import InterplanetaryPage from "./pages/InterplanetaryPage"
import OrbitalPerturbationsPage from "./pages/OrbitalPerturbationsPage"
import SettingsPage from "./pages/SettingsPage"

interface RightPanelProps
{
    activePage: string
}

/** @function RightPanel */
export default function RightPanel(props: Readonly<RightPanelProps>): react.JSX.Element
{
    // --- USE STATE ---
    
    const [consoleHeight, setConsoleHeight] = react.useState(180)

    const [consoleShow, setConsoleShow] = react.useState<boolean>(true)

    // --- USE REF ---
    
    const dragging = react.useRef<boolean>(false)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        globalThis.window.addEventListener("mousemove", onMouseMove)
        globalThis.window.addEventListener("mouseup", onMouseUp)

        const rmTC = globalThis.window.callback.onTriggerConsole(() => { setConsoleShow(prev => { return !prev }) })

        return () =>
        {
            globalThis.window.removeEventListener("mousemove", onMouseMove)
            globalThis.window.removeEventListener("mouseup", onMouseUp)
            
            rmTC()
        }
    }, [])

    // --- GENERIC ---

    const onMouseDown = () => dragging.current = true

    const onMouseUp = () => dragging.current = false

    const onMouseMove = (e: MouseEvent) =>
    {
        if (!dragging.current) return;

        const newHeight = window.innerHeight - e.clientY - 30; // ? 30 = StatusBar height

        setConsoleHeight(Math.max(80, newHeight)); // ? Min height
    }

    // --- RENDERING ---

    return (
        <div className="flex-1 flex flex-col min-h-0">

            {/* Page fills remaining space */}

            <div className="flex-1 min-h-1/4 overflow-auto custom-scrollbar">

                {props.activePage === "spacecraft" && <SpacecraftPage />}
                {props.activePage === "orbit" && <OrbitPage/>}
                {props.activePage === "orbital-maneuvers" && <OrbitalManeuversPage/>}
                {props.activePage === "relative-motion" && <RelativeMotionPage/>}
                {props.activePage === "interplanetary" && <InterplanetaryPage/>}
                {props.activePage === "orbital-perturbations" && <OrbitalPerturbationsPage/>}

                <div className={utility.cn(props.activePage === 'settings' ? 'block' : 'hidden', 'h-full')}>
                    <SettingsPage />
                </div>

                
            </div>

            {/* Resize bar */}

            <button
                onMouseDown={onMouseDown}
                className={`h-2 cursor-row-resize bg-neutral-700 hover:bg-neutral-600 active:bg-neutral-500
                            ${consoleShow ? "" : "hidden"}`}/>

            {/* Console with dynamic height */}
        
            <div
                className={`overflow-auto custom-scrollbar bg-red-300 text-white min-h-1/6 flex
                            ${consoleShow ? "" : "hidden"}`}
                style={{ height: consoleHeight }}>

                <Console />

            </div>

        </div>
    )
}