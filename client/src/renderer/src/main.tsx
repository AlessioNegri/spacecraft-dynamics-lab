import './assets/main.css'

import * as react from 'react'
import * as client from 'react-dom/client'

import App from './App'

client.createRoot(document.getElementById('root')!).render(<react.StrictMode><App/></react.StrictMode>)