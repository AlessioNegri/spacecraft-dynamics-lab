import * as react from 'react'
import axios, { AxiosRequestConfig } from 'axios'
import SpacecraftForm from '../dialogs/SpacecraftForm'
import { Icon } from '@iconify/react'

export function SpacecraftPage(): react.JSX.Element {
    const [name, setName] = react.useState("")
    const [mass, setMass] = react.useState(0)
    const [response, setResponse] = react.useState<string | null>(null)
    const [open, setOpen] = react.useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        let config: AxiosRequestConfig<any> = { headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' } };

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

    return (
        <>
            {/* Button to open dialog */}
            <button
                onClick={() => setOpen(true)}
                className="px-4 py-2 bg-stone-600 hover:bg-stone-700 text-white rounded"
            >
                Add Spacecraft
            </button>

            {/* Overlay */}
            {open && (
                <div className="fixed inset-0 bg-stone-700/60 backdrop-blur-sm flex items-center justify-center z-50">

                    {/* Dialog container */}
                    <div className="bg-stone-800 text-white rounded-lg shadow-xl w-full max-w-2xl p-6 relative animate-fadeIn">

                        {/* Close button */}
                        <Icon icon={"mdi:close-box"} width={30} height={30} className='absolute top-3 right-3 text-gray-400 hover:text-gray-200' onClick={() => setOpen(false)}/>

                        {/* Title */}
                        <h2 className="text-2xl font-semibold mb-4">Add Spacecraft</h2>

                        {/* Form */}
                        <SpacecraftForm />

                    </div>
                </div>
            )}
        </>

        // <div className='flex flex-col h-full w-full bg-stone-800'>

        //     <div className="max-w-sm mx-auto mt-10 space-y-4">
        //         <form onSubmit={handleSubmit} className="space-y-4">
        //             <div>
        //                 <label className="block text-sm font-medium text-gray-700 mb-1">
        //                     Name
        //                 </label>
        //                 <input
        //                     type="text"
        //                     value={name}
        //                     onChange={(e) => setName(e.target.value)}
        //                     className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        //                     placeholder="Enter your name"
        //                 />
        //             </div>

        //             <div>
        //                 <label className="block text-sm font-medium text-gray-700 mb-1">
        //                     Mass
        //                 </label>
        //                 <input
        //                     type="text"
        //                     value={mass}
        //                     onChange={(e) => setMass(Number(e.target.value))}
        //                     className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        //                     placeholder="Enter your mass"
        //                 />
        //             </div>

        //             <button
        //                 type="submit"
        //                 className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
        //             >
        //                 Submit
        //             </button>
        //         </form>

        //         {response && (
        //             <pre className="bg-gray-100 p-3 rounded-md text-sm text-red-950">
        //                 {response}
        //             </pre>
        //         )}
        //     </div>

        // </div>
    )
}