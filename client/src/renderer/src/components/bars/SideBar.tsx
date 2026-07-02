import * as react from "react"
import * as iconify from "@iconify/react"

import utility from "@renderer/common/utility"

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
        id: "relative-motion",
        label: "Relative Motion",
        icon: "mdi:proximity-sensor"
    },
    {
        id: "interplanetary",
        label: "Interplanetary",
        icon: "game-icons:orbital"
    },
    {
        id: "orbital-perturbations",
        label: "Orbital Perturbations",
        icon: "game-icons:perpendicular-rings"
    },
    {
        id: "circular-restricted-three-body-problem",
        label: "Circular Restricted Three-Body Problem",
        icon: "mingcute:three-circles-fill"
    }
]

interface Props
{
    activePage: string
    setActivePage: (id: string) => void
}

/** @function Sidebar */
export default function Sidebar(props: Readonly<Props>): react.JSX.Element
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

    return (
        <div
            className={utility.cn(show ? "w-18" : "w-0 hidden",
                "h-full bg-neutral-900 text-white flex flex-col items-center select-none")}
            >

            {/* Top */}

            <div className="flex flex-col flex-1">

            {
                items.map((item: ISideBarItem, index: number) =>
                    <Item
                        key={item.id}
                        index={index}
                        item={item}
                        visible={show}
                        activePage={props.activePage}
                        setActivePage={props.setActivePage}
                    />
                )
            }

            </div>

            {/* Bottom */}

            <div className="flex flex-col mt-auto">

                <Item
                    index={0}
                    item={{ id: "settings", label: "Settings", icon: "mdi:settings-outline" }}
                    visible={show}
                    activePage={props.activePage}
                    setActivePage={props.setActivePage}
                />

            </div>

        </div>
    )
}

interface ItemProps
{
    index: number
    item: ISideBarItem
    visible: boolean
    activePage: string
    setActivePage: (id: string) => void
}

/** @function Item */
function Item({ index, item, visible, activePage, setActivePage }: Readonly<ItemProps>): react.JSX.Element
{
    const css: string = "flex items-center justify-center w-16 h-16 rounded hover:bg-neutral-600 cursor-pointer"

    const isActive = activePage === item.id

    return (
        <div className={utility.cn(index ? "z-100" : "", visible ? "" : "hidden")}>

            <Tooltip title={item.label} side="right">

                <button
                    onClick={() => setActivePage(item.id)}
                    className={utility.cn(css,
                        isActive ? "bg-orange-300/25" : "",
                        "relative transition-all duration-500 group")}
                >

                    {/* Vertical Bar */}

                    <div
                        className={utility.cn("absolute left-0 top-0 bottom-0 w-1 bg-orange-300 rounded",
                            "transition-all duration-500",
                            isActive ? "bg-orange-300 scale-y-100" : "bg-transparent scale-y-0")}
                    />

                    {/* Icon */}

                    <iconify.Icon
                        icon={item.icon}
                        width={32}
                        className={utility.cn("transition-all duration-1000",
                            isActive ? "text-orange-300 drop-shadow-[0_0_6px_rgba(255,165,0,0.5)]"
                                : "text-orange-100 hover:text-orange-300")}
                    />

                </button>

            </Tooltip>

        </div>
    )
}