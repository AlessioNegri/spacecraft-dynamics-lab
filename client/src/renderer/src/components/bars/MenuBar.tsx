import * as react from "react"
import * as menubar from "@radix-ui/react-menubar"
import * as iconify from "@iconify/react"

import AboutDialog from "../dialogs/AboutDialog"

import CartesianOrbitParametersDialog from "../dialogs/tools/orbit_representation/CartesianOrbitParametersDialog"
import CartesianKeplerianDialog from "../dialogs/tools/orbit_representation/CartesianKeplerianDialog"
import CartesianPerifocalDialog from "../dialogs/tools/orbit_representation/CartesianPerifocalDialog"
import KeplerianCartesianDialog from "../dialogs/tools/orbit_representation/KeplerianCartesianDialog"
import GroundTrackPropagationDialog from "../dialogs/tools/orbit_representation/GroundTrackPropagationDialog"

import GibbsMethodDialog from "../dialogs/tools/orbit_determination/GibbsMethodDialog"
import JulianDayDialog from "../dialogs/tools/orbit_determination/JulianDayDialog"
import TopocentricFrameDialog from "../dialogs/tools/orbit_determination/TopocentricFrameDialog"
import AngleRangeDialog from "../dialogs/tools/orbit_determination/AngleRangeDialog"
import GaussMethodDialog from "../dialogs/tools/orbit_determination/GaussMethod"

import Shortcut from "../Shortcut"

import logo from "../../assets/SDL.png"

const DIALOGS =
{
    aboutDialog: AboutDialog,

    cartesianOrbitParametersDialog: CartesianOrbitParametersDialog,
    cartesianKeplerianDialog: CartesianKeplerianDialog,
    cartesianPerifocalDialog: CartesianPerifocalDialog,
    keplerianCartesianDialog: KeplerianCartesianDialog,
    groundTrackPropagationDialog: GroundTrackPropagationDialog,

    gibbsMethodDialog: GibbsMethodDialog,
    julianDayDialog: JulianDayDialog,
    topocentricFrameDialog: TopocentricFrameDialog,
    angleRangeDialog: AngleRangeDialog,
    gaussMethodDialog: GaussMethodDialog
} as const

/** @function MenuBar */
export default function MenuBar(): react.JSX.Element
{
    // --- SHORTCUT ---
    
    Shortcut("Ctrl+A", () => setOpenDialog("aboutDialog"))
    
    // --- USE STATE ---

    const [isMaximized, setIsMaximized] = react.useState<boolean>(true)

    const [showSideBar, setShowSideBar] = react.useState<boolean>(true)

    const [showConsole, setShowConsole] = react.useState<boolean>(true)

    const [openDialog, setOpenDialog] = react.useState<keyof typeof DIALOGS | null>(null)

    const ActiveDialog = openDialog ? DIALOGS[openDialog] : null

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmWM = globalThis.window.callback.onWindowMaximized((maximized: boolean) => setIsMaximized(maximized))

        const rmTSB = globalThis.window.callback.onTriggerSideBar(() => { setShowSideBar(prev => { return !prev }) })

        const rmTC = globalThis.window.callback.onTriggerConsole(() => { setShowConsole(prev => { return !prev }) })

        return () => { rmWM(); rmTSB(); rmTC() }
    }, [])

    // --- GENERIC ---

    const file: IMenuItem[] =
    [
        { label: "Sep-1", separator: true },
        { label: "Exit", shortcut: "Ctrl+E", action: () => globalThis.window.api.closeApp() }
    ]

    const view: IMenuItem[] =
    [
        { checkable: true, checked: showSideBar, label: "Side Bar", shortcut: "Ctrl+B", action: () => globalThis.window.api.triggerSideBar() },
        { checkable: true, checked: showConsole, label: "Console", shortcut: "Ctrl+ò", action: () => globalThis.window.api.triggerConsole() }
    ]

    const tools: IMenuItem[] =
    [
        {
            label: "Orbit Representation",
            children:
            [
                { label: "Cartesian → Orbit Parameters", action: () => setOpenDialog("cartesianOrbitParametersDialog") },
                { label: "Cartesian → Keplerian", action: () => setOpenDialog("cartesianKeplerianDialog") },
                { label: "Cartesian → Perifocal", action: () => setOpenDialog("cartesianPerifocalDialog") },
                { label: "Keplerian → Cartesian", action: () => setOpenDialog("keplerianCartesianDialog") },
                { label: "Ground Track Propagation", action: () => setOpenDialog("groundTrackPropagationDialog") }
            ]
        },
        {
            label: "Orbit Determination",
            children:
            [
                { label: "Gibbs Method", action: () => setOpenDialog("gibbsMethodDialog") },
                { label: "Julian Day", action: () => setOpenDialog("julianDayDialog") },
                { label: "Topocentric Frame", action: () => setOpenDialog("topocentricFrameDialog") },
                { label: "Angle Range", action: () => setOpenDialog("angleRangeDialog") },
                { label: "Gauss Method", action: () => setOpenDialog("gaussMethodDialog") }
            ]
        }
    ]

    const help: IMenuItem[] =
    [
        { label: "About", shortcut: "Ctrl+A", action: () => setOpenDialog("aboutDialog") }
    ]

    // --- RENDERING ---

    return (
        <div className="w-full h-10 bg-neutral-900 text-white flex items-center ps-2 select-none draggable">
            
            <menubar.Root className="w-full flex gap-1 items-center justify-between">

                <div className="flex gap-1 items-center no-drag">

                    <div className="w-8 flex justify-center">

                        {/* <iconify.Icon
                            icon={"streamline-ultimate:space-rocket-earth"}
                            width={20}
                            className="text-orange-300"
                        /> */}

                        <img
                        src={logo}
                        alt="Spacecraft Dynamics Lab Logo"
                        className="h-auto rounded-3xl"
                    />

                    </div>

                    <Menu label="File" items={file} />

                    <Menu label="View" items={view} />

                    <Menu label="Tools" items={tools} />

                    <Menu label="Help" items={help} />

                </div>
                
                <p className="text-center">Spacecraft Dynamics Lab</p>

                <div className="flex gap-1 items-center no-drag">

                    {/* MINIMIZE */}

                    <button
                        type="button"
                        className="h-10 w-10 hover:bg-neutral-700 flex justify-center items-center"
                        onClick={() => globalThis.window.api.minimizeApp()}>

                        <iconify.Icon
                            icon={"mdi:minimize"}
                            width={20}
                            className="text-stone-400"
                        />

                    </button>

                    {/* MAXIMIZE */}

                    <button
                        type="button"
                        className="h-10 w-10 hover:bg-neutral-700 flex justify-center items-center"
                        onClick={() => globalThis.window.api.maximizeApp()}>

                        <iconify.Icon
                            icon={isMaximized ? "mdi:window-restore" : "mdi:maximize"}
                            width={16}
                            className="text-stone-400"
                        />
                            
                    </button>

                    {/* CLOSE */}

                    <button
                        type="button"
                        className="h-10 w-10 hover:bg-red-800 flex justify-center items-center"
                        onClick={() => globalThis.window.api.closeApp()}>

                        <iconify.Icon
                            icon={"mdi:close"}
                            width={20}
                            className="text-stone-400"
                        />

                    </button>

                </div>

            </menubar.Root>

            {
                ActiveDialog &&
                <ActiveDialog
                    opened={openDialog != null}
                    setOpened={(opened: boolean) => opened ? setOpenDialog(prev => prev) : setOpenDialog(null)}
                />
            }

        </div>
    )
}

/**
 * @function Menu
 * 
 * @param menu Menu params
 * @returns JSX
 */
function Menu(menu: Readonly<IMenu>): react.JSX.Element
{
    return (
        <menubar.Menu>

            <menubar.Trigger
                className="text-base px-2 z-110 rounded cursor-autotext-neutral-500
                            hover:bg-neutral-500 hover:text-neutral-400
                            data-[state=open]:bg-neutral-700 text-neutral-400">
                
                {menu.label}

            </menubar.Trigger>

            <menubar.Portal>
                
                <menubar.Content
                    align="start"
                    className="min-w-80 border rounded shadow-lg p-1 z-2
                                bg-neutral-600 text-white border-neutral-950">

                {
                    menu.items.map((item: IMenuItem) =>
                        <MenuItem key={(item.label ?? '') + (item.checked ?? '')} item={item} />
                )}

                </menubar.Content>

            </menubar.Portal>

        </menubar.Menu>
    )
}

interface MenuItemProps
{
    item: IMenuItem
}

/** @function MenuItem */
function MenuItem(props: Readonly<MenuItemProps>): react.JSX.Element
{
    if (props.item.separator)
    {
        return <menubar.Separator className="h-px bg-neutral-950 my-1"/>
    }

    if (props.item.children)
    {
        return (
            <menubar.Sub>

                <menubar.SubTrigger
                    className="px-2 py-1.5 text-base flex justify-between items-center cursor-pointer rounded
                               hover:bg-neutral-500 hover:text-white"
                >
                    <div className="w-2"></div>

                    <span className="flex-1 ps-4">{props.item.label}</span>

                    <iconify.Icon icon="mdi:chevron-right" width={16} />

                </menubar.SubTrigger>

                <menubar.Portal>

                    <menubar.SubContent
                        sideOffset={5}
                        className="min-w-60 border rounded shadow-lg p-1 bg-neutral-600 text-white border-neutral-950"
                    >

                        {
                            props.item.children.map((item: IMenuItem) =>
                                <MenuItem key={(item.label ?? '') + (item.checked ?? '')} item={item} />)
                        }

                    </menubar.SubContent>

                </menubar.Portal>

            </menubar.Sub>
        )
    }

    return (
        <menubar.Item
            onClick={props.item.action}
            className="px-2 py-1.5 text-base flex justify-start items-center cursor-pointer rounded
                        hover:bg-neutral-500 hover:text-white">

            <div className="w-2">
            
            {
                props.item.checkable && props.item.checked && <iconify.Icon icon={"mdi:check"} width={16} />
            }

            </div>

            <span className="flex-1 ps-4">{props.item.label}</span>

            {
                props.item.shortcut && <span className="text-base text-white/50">{props.item.shortcut}</span>
            }

        </menubar.Item>
    )
}