import Versions from './components/Versions'
import electronLogo from './assets/electron.svg'
import React from 'react'


import { MenuBar } from './components/MenuBar'
import { StatusBar } from './components/StatusBar'
import { Sidebar } from './components/SideBar'

import { SpacecraftPage } from './components/pages/SpacecraftPage'

function App(): React.JSX.Element {
    const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')

    // const handleStart = async () => {
    //     let config: AxiosRequestConfig<any> = { headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' } };

    //     try {
    //         await axios.get("http://127.0.0.1:8000/start", config)
    //     } catch (err) {
    //         console.error(err)
    //     }
    // }

    // const handleEnd = async () => {
    //     let config: AxiosRequestConfig<any> = { headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' } };

    //     try {
    //         await axios.get("http://127.0.0.1:8000/end", config)
    //     } catch (err) {
    //         console.error(err)
    //     }
    // }


    return (
        <div className='flex flex-col w-full h-full'>

            <MenuBar />

            <div className='flex-1 overflow-auto flex flex-row'>

                <Sidebar/>

                <div className='flex-1 overflow-auto'>

                    <SpacecraftPage/>

                </div>

            </div>

            {/* <img alt="logo" className="logo" src={electronLogo} />
            <div className="creator">Powered by electron-vite</div>

            <div className='flex gap-4'>
                <button onClick={handleStart}>Start</button>
                <button onClick={handleEnd}>End</button>
            </div>

            <div className="text">
                Build an Electron app with <span className="react">React</span>
                &nbsp;and <span className="ts">TypeScript</span>
            </div>
            <p className="tip">
                Please try pressing <code>F12</code> to open the devTool
            </p>
            <div className="actions">
                <div className="action">
                    <a href="https://electron-vite.org/" target="_blank" rel="noreferrer">
                        Documentation
                    </a>
                </div>
                <div className="action">
                    <a target="_blank" rel="noreferrer" onClick={ipcHandle}>
                        Send IPC
                    </a>
                </div>
            </div> */}

            <StatusBar/>
        </div>
    )
}

export default App
