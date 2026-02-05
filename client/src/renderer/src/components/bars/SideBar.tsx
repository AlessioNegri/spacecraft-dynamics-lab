import * as react from "react"
import * as iconify from "@iconify/react"

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

    // --- GENERIC ---

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
            id: "interplanetary",
            label: "Interplanetary",
            icon: "game-icons:orbital"
        }
    ]

    // --- RENDERING ---

    const css: string = "flex items-center justify-center w-16 h-16 rounded hover:bg-stone-600 cursor-pointer"

    return (
        <div
            className={`${show ? "w-18" : "w-0 hidden"}
            h-full bg-stone-900 text-white flex flex-col items-center select-none`}>

            {/* Top */}

            <div className="flex flex-col flex-1">

            {
                items.map((item: ISideBarItem) => (
                    <button
                        key={item.id}
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

                        {/* Tooltip */}

                        <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2! whitespace-nowrap
                                        px-4 py-1 rounded bg-stone-600 text-white text-sm z-10
                                        opacity-0 group-hover:opacity-100 pointer-events-none transition">

                            {item.label}

                        </div>

                    </button>
                ))
            }

            </div>

            {/* Bottom */}

            <div className="flex flex-col gap-4 mt-auto">

                <button
                    onClick={() => props.setActivePage("settings")}
                    className={`${css} relative transition group
                                    ${(props.activePage === "settings") ? "bg-orange-300/25" : ""}`}>
                    
                    {/* Icon */}

                    <iconify.Icon
                        icon={"mdi:settings"}
                        width={32}
                        className="text-orange-300" />

                    {/* Tooltip */}

                    <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2! whitespace-nowrap
                                    px-4 py-1 rounded bg-stone-600 text-white text-sm z-10
                                    opacity-0 group-hover:opacity-100 pointer-events-none transition">

                        Settings

                    </div>

                </button>

            </div>

        </div>
    )
}