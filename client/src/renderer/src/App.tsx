import Versions from './components/Versions'
import electronLogo from './assets/electron.svg'
import React from 'react'
import axios, { AxiosRequestConfig } from 'axios'

function App(): React.JSX.Element {
  const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')

  const [name, setName] = React.useState("")
  const [mass, setMass] = React.useState(0)
  const [response, setResponse] = React.useState<string | null>(null)


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    let config : AxiosRequestConfig<any> = { headers : { 'Content-Type': 'application/json', 'Accept': 'application/json' } };

    try {
      const res = await axios.post("http://127.0.0.1:8000/spacecraft/insert", {
        name: name,
        mass: mass
      }, config)

      setResponse(JSON.stringify(res.data, null, 2))
    } catch (err) {
      console.error(err)
      setResponse("Error contacting backend")
    }
  }

  const handleStart = async () =>
  {
    let config : AxiosRequestConfig<any> = { headers : { 'Content-Type': 'application/json', 'Accept': 'application/json' } };

    try {
      await axios.get("http://127.0.0.1:8000/start", config)
    } catch (err) {
      console.error(err)
    }
  }

  const handleEnd = async () =>
  {
    let config : AxiosRequestConfig<any> = { headers : { 'Content-Type': 'application/json', 'Accept': 'application/json' } };

    try {
      await axios.get("http://127.0.0.1:8000/end", config)
    } catch (err) {
      console.error(err)
    }
  }


  return (
    <>
      <img alt="logo" className="logo" src={electronLogo} />
      <div className="creator">Powered by electron-vite</div>

      <div className="max-w-sm mx-auto mt-10 space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Mass
          </label>
          <input
            type="text"
            value={mass}
            onChange={(e) => setMass(Number(e.target.value))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your mass"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
        >
          Submit
        </button>
      </form>

      {response && (
        <pre className="bg-gray-100 p-3 rounded-md text-sm text-red-950">
          {response}
        </pre>
      )}
    </div>

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
      </div>
      <Versions></Versions>
    </>
  )
}

export default App
