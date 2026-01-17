import * as react from 'react'


import MenuBar from './components/bars/MenuBar'
import StatusBar from './components/bars/StatusBar'
import Sidebar from './components/bars/SideBar'
import RightPanel from './components/RightPanel'
import Shortcut from "./components/Shortcut"

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
        <div className='flex flex-col w-full h-full'>

            <MenuBar />

            <div className='flex-1 overflow-auto flex flex-row'>

                <Sidebar activePage={activePage} setActivePage={setActivePage} />

                <RightPanel activePage={activePage} />

            </div>

            <StatusBar/>

        </div>
    )
}