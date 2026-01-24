import * as react from "react"
import * as Menubar from "@radix-ui/react-menubar"
import * as iconify from "@iconify/react"

/** @function MenuBar */
export default function MenuBar(): react.JSX.Element
{
    // --- USE STATE ---

    const [isMaximized, setIsMaximized] = react.useState<boolean>(true)

    const [showSideBar, setShowSideBar] = react.useState<boolean>(true)

    const [showConsole, setShowConsole] = react.useState<boolean>(true)

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

    // --- RENDERING ---

    return (
        <div className="w-full h-10 bg-stone-950 text-white flex items-center ps-2 select-none draggable">
            
            <Menubar.Root className="w-full flex gap-1 items-center justify-between">

                <div className="flex gap-1 items-center no-drag">

                    <div className="w-8 flex justify-center">

                        <iconify.Icon icon={"streamline-ultimate:space-rocket-earth"} width={20} className="text-orange-300" />

                    </div>

                    <Menu label="File" items={file} />

                    <Menu label="View" items={view} />

                </div>
                
                <p className="text-center">Spacecraft Dynamics Lab</p>

                <div className="flex gap-1 items-center no-drag">

                    {/* MINIMIZE */}

                    <button
                        type="button"
                        className="h-10 w-10 hover:bg-stone-600 flex justify-center items-center"
                        onClick={() => globalThis.window.api.minimizeApp()}>

                        <iconify.Icon icon={"mdi:minimize"} width={20} className="text-stone-400" />

                    </button>

                    {/* MAXIMIZE */}

                    <button
                        type="button"
                        className="h-10 w-10 hover:bg-stone-600 flex justify-center items-center"
                        onClick={() => globalThis.window.api.maximizeApp()}>

                        <iconify.Icon icon={isMaximized ? "mdi:window-restore" : "mdi:maximize"} width={16}
                            className="text-stone-400" />
                            
                    </button>

                    {/* CLOSE */}

                    <button
                        type="button"
                        className="h-10 w-10 hover:bg-red-800 flex justify-center items-center"
                        onClick={() => globalThis.window.api.closeApp()}>

                        <iconify.Icon icon={"mdi:close"} width={20} className="text-stone-400" />

                    </button>

                </div>

            </Menubar.Root>

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
                className="text-base px-2 rounded cursor-autotext-stone-500 hover:bg-stone-500 hover:text-stone-400
                            data-[state=open]:bg-stone-700 text-stone-400">
                
                {menu.label}

            </Menubar.Trigger>

            <Menubar.Portal>
                
                <Menubar.Content
                    align="start"
                    className="min-w-80 border rounded shadow-lg py-1 bg-stone-600 text-white border-black">

                {
                    menu.items.map((item: IMenuItem) =>
                    
                    item.separator

                    ?
                    
                    <Menubar.Separator key={item.label} className="h-px bg-stone-950 my-1"/>
                    
                    :
                    
                    <Menubar.Item
                        key={(item.label ?? '') + (item.checked ?? '')}
                        onClick={item.action}
                        className="px-5 py-1.5 text-base flex justify-start items-center cursor-pointer
                        hover:bg-stone-500 hover:text-white">

                        <div className="w-6">
                        
                        {
                            item.checkable && item.checked && <iconify.Icon icon={"mdi:check"} width={20} />
                        }

                        </div>

                        <span className="flex-1 ps-4">{item.label}</span>

                        {
                            item.shortcut && <span className="text-base text-white/50">{item.shortcut}</span>
                        }

                    </Menubar.Item>
                    
                )}

                </Menubar.Content>

            </Menubar.Portal>

        </Menubar.Menu>
    )
}