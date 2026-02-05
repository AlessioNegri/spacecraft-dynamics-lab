import * as react from "react"

import InterplanetaryLeftBar from "../common/InterplanetaryLeftBar"
import InterplanetaryMainPlot from "../common/InterplanetaryMainPlot"
import { InterplanetaryRightBar } from "../common/InterplanetaryRightBar"

/** @function InterplanetaryPage */
export default function InterplanetaryPage()
{
    // --- USE STATE ---

    const [dvGrid, setDvGrid] = react.useState<number[][] | null>(null)

    const [dv1Grid, setDv1Grid] = react.useState<number[][] | null>(null)

    const [dv2Grid, setDv2Grid] = react.useState<number[][] | null>(null)

    const [tofGrid, setTofGrid] = react.useState<number[][] | null>(null)

    const [launchDates, setLaunchDates] = react.useState<string[] | null>(null)

    const [arrivalDates, setArrivalDates] = react.useState<string[] | null>(null)

    const [selected, setSelected] = react.useState<ISelectionInfo | null>(null)

    const [time, setTime] = react.useState<string>("")

    // --- USE EFFECT ---
    
    react.useEffect(() =>
    {
        const rmRI = globalThis.window.callback.onReceivedInfo((info: WebSocketInfo) =>
        {
            if (info.source === "interplanetary" && info.data != undefined)
            {
                setDvGrid(info.data["dv"])
                setDv1Grid(info.data["dv_1"])
                setDv2Grid(info.data["dv_2"])
                setTofGrid(info.data["tof"])
                setLaunchDates(info.data["launch_dates"])
                setArrivalDates(info.data["arrival_dates"])
            }
        })

        return () => { rmRI() }
    }, [])

    react.useEffect(() =>
    {
        const update = () =>
        {
            const now: Date = new Date()

            const date: string = now.toLocaleDateString("it-IT")

            const time: string = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })

            setTime(`${date} ${time}`)
        }

        update()

        const interval = setInterval(update, 1000)

        return () => clearInterval(interval)
    }, [])

    // --- RENDERING ---

    return (
        <div className="flex flex-col h-full w-full bg-neutral-900 text-neutral-100">

            {/* Header */}

            <div className="flex items-center justify-between px-6 py-3 border-b border-neutral-700 bg-neutral-800">

                <h1 className="text-xl font-semibold">Interplanetary Analysis</h1>

                <div
                    className="w-70 p-1 bg-neutral-950 text-green-300 rounded-lg shadow-md flex items-center 
                                justify-center text-xl font-mono tracking-widest">
                
                    {time}

                </div>


            </div>

            <div className="flex flex-1 overflow-hidden">

                <div className="w-80 border-r border-neutral-700 p-4 overflow-y-auto">

                    <InterplanetaryLeftBar />

                </div>

                <div className="flex-1 p-4 overflow-auto flex items-center justify-center">
                    
                    <InterplanetaryMainPlot
                        dvGrid={dvGrid}
                        dv1Grid={dv1Grid}
                        dv2Grid={dv2Grid}
                        tofGrid={tofGrid}
                        launchDates={launchDates}
                        arrivalDates={arrivalDates}
                        onSelect={setSelected}
                    />

                </div>

                <div className="w-80 border-l border-neutral-700 p-4 overflow-y-auto">

                    <InterplanetaryRightBar info={selected} />

                </div>

            </div>
        </div>
    )
}