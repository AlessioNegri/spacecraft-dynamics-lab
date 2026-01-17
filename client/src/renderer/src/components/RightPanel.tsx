import * as react from "react"

import { SpacecraftPage } from "./pages/SpacecraftPage"
import Console from "./Console"

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

            <div className="flex-1 min-h-1/4 overflow-auto">

                {props.activePage === "spacecraft" && <SpacecraftPage />}
                {props.activePage === "orbit" && <div className="bg-red-500 h-full w-full border-8" />}
                {props.activePage === "settings" && <div className="bg-green-500 h-full w-full border-8" />}
                
            </div>

        {
            consoleShow && (
            <>

                {/* Resize bar */}

                <button
                    onMouseDown={onMouseDown}
                    className="h-2 cursor-row-resize bg-stone-700 hover:bg-stone-600 active:bg-stone-500"/>

                {/* Console with dynamic height */}

            
                <div
                    className="overflow-auto custom-scrollbar bg-red-300 text-white min-h-1/4 flex"
                    style={{ height: consoleHeight }}>

                    <Console />

                </div>
                
            </>)
        }

        </div>
    )
}