import * as react from "react"
import * as iconify from "@iconify/react"

import Tooltip from "./Tooltip"
import LogStore from "./Log"

/** @function Console */
export default function Console(): react.JSX.Element
{
    // --- USE STATE ---

    const [show, setShow] = react.useState<boolean>(true)

    // --- USE EFFECT ---
        
    react.useEffect(() =>
    {
        const rmTC = globalThis.window.callback.onTriggerConsole(() => { setShow(prev => { return !prev }) })

        return () => { rmTC() }
    }, [])

    // --- RENDERING ---

    const logStore = LogStore()

    const color = { debug: "text-stone-300", info: "text-blue-300", warning: "text-yellow-300", error: "text-red-400" }

    return (
        <div className={`${show ? 'flex-1' : 'h-0 hidden'}
                        p-2 bg-stone-800 font-mono text-sm border-2 border-stone-400 select-text relative`}>

            <Tooltip title="Clear Console" side="left">

                <iconify.Icon
                    icon={"mdi:cancel"}
                    width={32}
                    className="absolute top-2 right-6 cursor-pointer hover:text-orange-300"
                    onClick={() => logStore[1]([])} />

            </Tooltip>
        
            <div className="overflow-auto custom-scrollbar h-full">

            {
                logStore[0].map((log: LogEntry, i: react.Key) => (
                    <div key={i} className={color[log.level]}>

                        <span className="text-gray-500">{log.timestamp}</span>

                        <span className="uppercase">{" | " + log.level + " | "}</span>

                        <span>{log.message}</span>

                    </div>
                ))
            }

            </div>

        </div>
    )
}