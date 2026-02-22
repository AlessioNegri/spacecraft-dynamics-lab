import * as react from "react"
import * as menubar from "@radix-ui/react-menubar"
import * as iconify from "@iconify/react"

import AboutDialog from "../dialogs/AboutDialog"
import CartesianToOrbitParametersDialog from "../dialogs/CartesianToOrbitParametersDialog"
import Shortcut from "../Shortcut"

import logo from "../../assets/SDL.png"

/** @function MenuBar */
export default function MenuBar(): react.JSX.Element
{
    // --- SHORTCUT ---
    
    Shortcut("Ctrl+A", () => setOpenAboutDialog(true))
    
    // --- USE STATE ---

    const [isMaximized, setIsMaximized] = react.useState<boolean>(true)

    const [showSideBar, setShowSideBar] = react.useState<boolean>(true)

    const [showConsole, setShowConsole] = react.useState<boolean>(true)

    const [openAboutDialog, setOpenAboutDialog] = react.useState<boolean>(false)

    const [openC2OPDialog, setOpenC2OPDialog] = react.useState<boolean>(false)

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
        { separator: true },
        { label: "Exit", shortcut: "Ctrl+E", action: () => globalThis.window.api.closeApp() }
    ]

    const view: IMenuItem[] =
    [
        { checkable: true, checked: showSideBar, label: "Side Bar", shortcut: "Ctrl+B", action: () => globalThis.window.api.triggerSideBar() },
        { checkable: true, checked: showConsole, label: "Console", shortcut: "Ctrl+ò", action: () => globalThis.window.api.triggerConsole() }
    ]

    const tools: IMenuItem[] =
    [
        { label: "Cartesian → Orbit Parameters", action: () => setOpenC2OPDialog(true) }
    ]

    const help: IMenuItem[] =
    [
        { label: "About", shortcut: "Ctrl+A", action: () => setOpenAboutDialog(true) }
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
                openAboutDialog &&
                <AboutDialog onClose={() => { setOpenAboutDialog(false) }} onOk={() => { setOpenAboutDialog(false) }} />
            }

            {
                openC2OPDialog && 
                <CartesianToOrbitParametersDialog
                    onClose={() => { setOpenC2OPDialog(false) }}
                    onOk={() => {}}
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
                className="text-base px-2 rounded cursor-autotext-neutral-500
                            hover:bg-neutral-500 hover:text-neutral-400
                            data-[state=open]:bg-neutral-700 text-neutral-400">
                
                {menu.label}

            </menubar.Trigger>

            <menubar.Portal>
                
                <menubar.Content
                    align="start"
                    className="min-w-80 border rounded shadow-lg py-1 z-2
                                bg-neutral-600 text-white border-neutral-950">

                {
                    menu.items.map((item: IMenuItem) =>
                    
                    item.separator

                    ?
                    
                    <menubar.Separator key={item.label} className="h-px bg-neutral-950 my-1"/>
                    
                    :
                    
                    <menubar.Item
                        key={(item.label ?? '') + (item.checked ?? '')}
                        onClick={item.action}
                        className="px-5 py-1.5 text-base flex justify-start items-center cursor-pointer
                                    hover:bg-neutral-500 hover:text-white">

                        <div className="w-6">
                        
                        {
                            item.checkable && item.checked && <iconify.Icon icon={"mdi:check"} width={20} />
                        }

                        </div>

                        <span className="flex-1 ps-4">{item.label}</span>

                        {
                            item.shortcut && <span className="text-base text-white/50">{item.shortcut}</span>
                        }

                    </menubar.Item>
                    
                )}

                </menubar.Content>

            </menubar.Portal>

        </menubar.Menu>
    )
}