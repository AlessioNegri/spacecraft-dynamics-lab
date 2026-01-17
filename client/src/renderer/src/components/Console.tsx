import * as react from "react"
import * as iconify from "@iconify/react"

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
                        p-2 bg-stone-800 font-mono text-sm overflow-auto border-2 border-stone-400 select-text
                        custom-scrollbar relative`}>

            <iconify.Icon
                icon={"mdi:cancel"}
                width={32}
                className="absolute top-2 right-2 cursor-pointer hover:text-orange-300"
                onClick={() => logStore[1]([])} />
        
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
    )
}