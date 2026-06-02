import * as react from "react"
import * as iconify from "@iconify/react"
import * as Menubar from "@radix-ui/react-menubar"

import utility from "@renderer/common/utility"

import logo from "../../assets/SDL.png"

import Shortcut from "../Shortcut"

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

import LvlhKinematicsDialog from "../dialogs/tools/relative_motion/LvlhKinematicsDialog"
import GeocentricEquatorialKinematicsDialog from "../dialogs/tools/relative_motion/GeocentricEquatorialKinematicsDialog"

import SynodicPeriodDialog from "../dialogs/tools/interplanetary_trajectory/SynodicPeriodDialog"
import SphereOfInfluenceDialog from "../dialogs/tools/interplanetary_trajectory/SphereOfInfluenceDialog"
import TransferDialog from "../dialogs/tools/interplanetary_trajectory/TransferDialog"
import NodalRegressionDialog from "../dialogs/tools/orbital_perturbations/NodalRegressionDialog"
import ApsidalRotationDialog from "../dialogs/tools/orbital_perturbations/ApsidalRotationDialog"
import SunSynchronousDialog from "../dialogs/tools/orbital_perturbations/SunSynchronousDialog"

const DIALOGS =
{
    aboutDialog: AboutDialog,

    cartesianOrbitParametersDialog: CartesianOrbitParametersDialog,
    cartesianKeplerianDialog: CartesianKeplerianDialog,
    cartesianPerifocalDialog: CartesianPerifocalDialog,
    keplerianCartesianDialog: KeplerianCartesianDialog,
    groundTrackPropagationDialog: GroundTrackPropagationDialog,
    nodalRegressionDialog: NodalRegressionDialog,
    apsidalRotationDialog: ApsidalRotationDialog,
    sunSynchronousDialog: SunSynchronousDialog,

    gibbsMethodDialog: GibbsMethodDialog,
    julianDayDialog: JulianDayDialog,
    topocentricFrameDialog: TopocentricFrameDialog,
    angleRangeDialog: AngleRangeDialog,
    gaussMethodDialog: GaussMethodDialog,

    lvlhKinematicsDialog: LvlhKinematicsDialog,
    geocentricEquatorialKinematicsDialog: GeocentricEquatorialKinematicsDialog,
    synodicPeriodDialog: SynodicPeriodDialog,
    sphereOfInfluenceDialog: SphereOfInfluenceDialog,
    transferDialog: TransferDialog
} as const

interface Props
{
    activePage: string
}

/** @function MenuBar */
export default function MenuBar(props: Readonly<Props>): react.JSX.Element
{
    // --- SHORTCUT ---
    
    Shortcut("Ctrl+A", () => setOpenDialog("aboutDialog"))
    
    // --- USE STATE ---

    const [isMaximized, setIsMaximized] = react.useState<boolean>(true)

    const [showSideBar, setShowSideBar] = react.useState<boolean>(true)

    const [showConsole, setShowConsole] = react.useState<boolean>(true)

    const [time, setTime] = react.useState<string>("")

    const [openDialog, setOpenDialog] = react.useState<keyof typeof DIALOGS | null>(null)

    const ActiveDialog = openDialog ? DIALOGS[openDialog] : null

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmWM = globalThis.window.callback.onWindowMaximized((maximized: boolean) => setIsMaximized(maximized))

        const rmTSB = globalThis.window.callback.onTriggerSideBar(() => { setShowSideBar(prev => { return !prev }) })

        const rmTC = globalThis.window.callback.onTriggerConsole(() => { setShowConsole(prev => { return !prev }) })

        const update = () =>
        {
            const now: Date = new Date()

            const date: string = now.toLocaleDateString("it-IT")

            const time: string = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })

            setTime(`${date} ${time}`)
        }

        update()

        const interval = setInterval(update, 1000)

        return () => { rmWM(); rmTSB(); rmTC(); clearInterval(interval) }
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
        { checkable: true, checked: showConsole, label: "Console", shortcut: "Ctrl+L", action: () => globalThis.window.api.triggerConsole() }
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
        },
        {
            label: "Orbital Perturbations",
            children:
            [
                { label: "Nodal Regression", action: () => setOpenDialog("nodalRegressionDialog") },
                { label: "Apsidal Rotation", action: () => setOpenDialog("apsidalRotationDialog") },
                { label: "Sun-Synchronous Orbit", action: () => setOpenDialog("sunSynchronousDialog") }
            ]
        },
        {
            label: "Relative Motion",
            children:
            [
                { label: "LVLH Kinematics", action: () => setOpenDialog("lvlhKinematicsDialog") },
                { label: "Geocentric Equatorial Kinematics", action: () => setOpenDialog("geocentricEquatorialKinematicsDialog") }
            ]
        },
        {
            label: "Interplanetary Trajectory",
            children:
            [
                { label: "Synodic Period", action: () => setOpenDialog("synodicPeriodDialog") },
                { label: "Sphere of Influence", action: () => setOpenDialog("sphereOfInfluenceDialog") },
                { label: "Transfer", action: () => setOpenDialog("transferDialog") }
            ]
        }
    ]

    const help: IMenuItem[] =
    [
        { label: "About", shortcut: "Ctrl+A", action: () => setOpenDialog("aboutDialog") }
    ]

    // --- RENDERING ---

    const css: string = "h-10 w-10 flex justify-center items-center transition-colors duration-150"

    return (
        <div className="w-full h-20 bg-neutral-900 text-white flex-col items-center select-none draggable">

            <div className="w-full flex gap-4 items-center justify-start border-b border-neutral-700 ps-2 mb-2">

                <div className="w-8 flex justify-center">

                    <img src={logo} alt="Spacecraft Dynamics Lab Logo" className="h-auto rounded-3xl"/>

                </div>

                <p
                    className="flex-1 text-orange-300 capitalize"
                    style={{ fontFamily: "Oxanium" }}
                >
                    SDL - Spacecraft Dynamics Lab | {props.activePage.replaceAll("-", " ")}
                </p>

                <div className="flex gap-1 items-center no-drag">

                    {/* MINIMIZE */}

                    <button
                        type="button"
                        className={utility.cn(css, "hover:bg-neutral-700")}
                        onClick={() => globalThis.window.api.minimizeApp()}>

                        <iconify.Icon icon={"mdi:minimize"} width={20} className="text-stone-400" />

                    </button>

                    {/* MAXIMIZE */}

                    <button
                        type="button"
                        className={utility.cn(css, "hover:bg-neutral-700")}
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
                        className={utility.cn(css, "hover:bg-red-800")}
                        onClick={() => globalThis.window.api.closeApp()}>

                        <iconify.Icon icon={"mdi:close"} width={20} className="text-stone-400"/>

                    </button>

                </div>

            </div>
            
            <Menubar.Root className="w-full flex gap-1 items-center justify-between px-2">

                <div className="w-full flex gap-1 items-center justify-between no-drag">

                    <Menu label="File" items={file} />

                    <Menu label="View" items={view} />

                    <Menu label="Tools" items={tools} />

                    <Menu label="Help" items={help} />

                    <p className="flex-1"></p>

                    <div
                        className="text-green-300 rounded-lg text-base tracking-widest"
                        style={{ fontFamily: "Oxanium" }}
                    >
                        {time}
                    </div>

                </div>

            </Menubar.Root>

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
        <Menubar.Menu>

            <Menubar.Trigger
                className="text-base px-2 z-110 rounded cursor-auto
                            hover:bg-neutral-500 hover:text-neutral-400
                            data-[state=open]:bg-neutral-700 text-neutral-400">
                
                {menu.label}

            </Menubar.Trigger>

            <Menubar.Portal>
                
                <Menubar.Content
                    align="start"
                    className="min-w-80 border rounded shadow-lg p-1 z-2
                                bg-neutral-600 text-white border-neutral-950">

                {
                    menu.items.map((item: IMenuItem) =>
                        <MenuItem key={(item.label ?? '') + (item.checked ?? '')} item={item} />
                )}

                </Menubar.Content>

            </Menubar.Portal>

        </Menubar.Menu>
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
        return <Menubar.Separator className="h-px bg-orange-300 my-1"/>
    }

    if (props.item.children)
    {
        return (
            <Menubar.Sub>

                <Menubar.SubTrigger
                    className="px-2 py-1.5 text-base flex justify-between items-center cursor-pointer rounded
                        hover:bg-neutral-500 hover:text-white"
                >
                    <div className="w-4 flex justify-center"></div>

                    <span className="flex-1 ps-4">{props.item.label}</span>

                    <iconify.Icon icon="mdi:chevron-right" width={16} className="text-orange-300"/>

                </Menubar.SubTrigger>

                <Menubar.Portal>

                    <Menubar.SubContent
                        sideOffset={5}
                        alignOffset={-4}
                        className="min-w-60 rounded shadow-lg p-1 bg-neutral-600 text-white
                            border border-neutral-950"
                    >

                        {
                            props.item.children.map((item: IMenuItem) =>
                                <MenuItem key={(item.label ?? '') + (item.checked ?? '')} item={item} />)
                        }

                    </Menubar.SubContent>

                </Menubar.Portal>

            </Menubar.Sub>
        )
    }

    return (
        <Menubar.Item
            onClick={props.item.action}
            className="px-2 py-1.5 text-base flex justify-start items-center cursor-pointer rounded
                hover:bg-neutral-500 hover:text-white">

            <div className="w-4 flex justify-center">
            
            {
                props.item.checkable && props.item.checked &&
                <iconify.Icon icon={"mdi:check-outline"} width={16} className="text-orange-300" />
            }

            </div>

            <span className="flex-1 ps-4">{props.item.label}</span>

            {
                props.item.shortcut &&
                <span className="text-base text-white/50 tracking-wider">{props.item.shortcut}</span>
            }

        </Menubar.Item>
    )
}