// Ensure `global` exists for libraries that expect a Node-like global variable (e.g. plotly)
//(globalThis as any).global = (globalThis as any).global || globalThis

(globalThis as any).CESIUM_BASE_URL = new URL('./cesium/', globalThis.location.href).toString()

import './assets/main.css'

//import * as react from 'react'
import * as client from 'react-dom/client'

import App from './App'

//client.createRoot(document.getElementById('root')!).render(<react.StrictMode><App/></react.StrictMode>)
client.createRoot(document.getElementById('root')!).render(<App/>)