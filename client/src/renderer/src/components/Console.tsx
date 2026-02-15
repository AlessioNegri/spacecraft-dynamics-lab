import * as react from "react"
import * as iconify from "@iconify/react"

import Tooltip from "./Tooltip"
import LogStore from "./LogStore"

/** @function Console */
export default function Console(): react.JSX.Element
{
    const logStore = LogStore()

    // --- USE STATE ---

    const [show, setShow] = react.useState<boolean>(true)

    // --- USE REF ---

    const logRef = react.useRef<HTMLDivElement>(null)

    // --- USE EFFECT ---
        
    react.useEffect(() =>
    {
        const rmTC = globalThis.window.callback.onTriggerConsole(() => { setShow(prev => { return !prev }) })

        return () => { rmTC() }
    }, [])

    react.useEffect(() => { if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight }, [logStore[0]])

    // --- RENDERING ---

    const color = { debug: "text-neutral-300", info: "text-blue-300", warning: "text-yellow-300", error: "text-red-400" }

    return (
        <div className={`${show ? 'flex-1' : 'h-0 hidden'}
                        p-2 bg-neutral-800 font-mono text-sm border-2 border-neutral-400 select-text relative`}>

            <Tooltip title="Clear Console" side="left">

                <iconify.Icon
                    icon={"mdi:cancel"}
                    width={32}
                    className="absolute top-2 right-6 cursor-pointer hover:text-orange-300"
                    onClick={() => logStore[1]([])}
                />

            </Tooltip>
        
            <div ref={logRef} className="overflow-auto custom-scrollbar h-full">

            {
                logStore[0].map((log: LogEntry, i: react.Key) => (
                    <div key={i} className={`${color[log.level]} break-all`}>

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