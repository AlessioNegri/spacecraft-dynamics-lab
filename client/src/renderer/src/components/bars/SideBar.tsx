import * as react from "react"
import * as iconify from "@iconify/react"

import Tooltip from "../Tooltip"

const items: ISideBarItem[] =
[
    {
        id: "spacecraft",
        label: "Spacecraft",
        icon: "mdi:space-station"
    },
    {
        id: "orbit",
        label: "Orbit",
        icon: "mdi:orbit"
    },
    {
        id: "orbital-maneuvers",
        label:"Orbital Maneuvers",
        icon: "game-icons:rocket"
    },
    {
        id: "interplanetary",
        label: "Interplanetary",
        icon: "game-icons:orbital"
    }
]

interface SideBarProps
{
    activePage: string
    setActivePage: (id: string) => void
}

/** @function Sidebar */
export default function Sidebar(props: Readonly<SideBarProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [show, setShow] = react.useState<boolean>(true)

    // --- USE EFFECT ---
    
    react.useEffect(() =>
    {
        const rmTSB = globalThis.window.callback.onTriggerSideBar(() => { setShow(prev => { return !prev }) })

        return () => { rmTSB() }
    }, [])
    
    // --- RENDERING ---

    const css: string = "flex items-center justify-center w-16 h-16 rounded hover:bg-neutral-600 cursor-pointer"

    return (
        <div
            className={`${show ? "w-18" : "w-0 hidden"}
                        h-full bg-neutral-900 text-white flex flex-col items-center select-none`}>

            {/* Top */}

            <div className="flex flex-col flex-1">

            {
                items.map((item: ISideBarItem, index: number) => (
                    <div className={index ? 'z-100' : ''} key={item.id}>
                        <Tooltip title={item.label} side="right">
                        
                            <button
                                onClick={() => props.setActivePage(item.id)}
                                className={`${css} relative transition group
                                            ${(props.activePage === item.id) ? "bg-orange-300/25" : ""}`}>
                                
                                {/* Vertical Bar */}
                                
                            {
                                (props.activePage === item.id) && (
                                <div className="absolute left-0 top-0 bottom-0 w-1 bg-orange-300 rounded"/>)
                            }

                                {/* Icon */}

                                <iconify.Icon
                                    icon={item.icon}
                                    width={32}
                                    className={`${(props.activePage === item.id) ?
                                                "text-orange-300" : "text-orange-100 hover:text-orange-300"}`} />

                            </button>

                        </Tooltip>
                    </div>
                ))
            }

            </div>

            {/* Bottom */}

            <div className="flex flex-col gap-4 mt-auto z-100">

                <Tooltip title="Settings" side="right">

                    <button
                        onClick={() => props.setActivePage("settings")}
                        className={`${css} relative transition group
                                        ${(props.activePage === "settings") ? "bg-orange-300/25" : ""}`}>
                        
                        <iconify.Icon
                            icon={"mdi:settings"}
                            width={32}
                            className="text-orange-300"
                        />

                    </button>

                </Tooltip>

            </div>

        </div>
    )
}