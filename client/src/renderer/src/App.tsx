import * as react from 'react'
import * as themes from "@radix-ui/themes"
import * as tooltip from "@radix-ui/react-tooltip"

import "katex/dist/katex.min.css"

import Shortcut from "./components/Shortcut"
import MenuBar from './components/bars/MenuBar'
import StatusBar from './components/bars/StatusBar'
import Sidebar from './components/bars/SideBar'
import RightPanel from './components/RightPanel'

/** @function App */
export default function App(): react.JSX.Element
{
    // --- USE STATE ---

    const [activePage, setActivePage] = react.useState<string>("spacecraft")

    // --- SHORTCUT ---

    Shortcut("Ctrl+E", () => globalThis.window.api.closeApp())
    Shortcut("Ctrl+B", () => globalThis.window.api.triggerSideBar())
    Shortcut("Ctrl+ò", () => globalThis.window.api.triggerConsole())

    // --- RENDERING ---
    
    return (
        <themes.Theme appearance="dark" accentColor="orange" grayColor="slate" className="w-full h-full flex flex-col">

            <tooltip.Provider>

                <div className='flex flex-col w-full h-full bg-neutral-800'>

                    <MenuBar />

                    <div className='flex-1 overflow-auto custom-scrollbar flex flex-row'>

                        <Sidebar activePage={activePage} setActivePage={setActivePage} />

                        <RightPanel activePage={activePage} />

                    </div>

                    <StatusBar />

                </div>

            </tooltip.Provider>
            
        </themes.Theme>
    )
}