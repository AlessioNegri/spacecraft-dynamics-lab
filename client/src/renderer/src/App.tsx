import * as react from 'react'
import * as Tooltip from "@radix-ui/react-tooltip"

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
        <Tooltip.Provider>

            <div className='flex flex-col w-full h-full'>

                <MenuBar />

                <div className='flex-1 overflow-auto custom-scrollbar flex flex-row'>

                    <Sidebar activePage={activePage} setActivePage={setActivePage} />

                    <RightPanel activePage={activePage} />

                </div>

                <StatusBar/>

            </div>
            
        </Tooltip.Provider>
    )
}