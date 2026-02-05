import * as react from "react"
import * as iconify from "@iconify/react"

/** @function StatusBar */
export default function StatusBar(): react.JSX.Element
{
    // --- USE STATE ---

    const [isOpened, setIsOpened] = react.useState<boolean>(false)
    
    const [versions] = react.useState<any>(globalThis.electron.process.versions)

    const [source, setSource] = react.useState<string>("")

    const [progress, setProgress] = react.useState<number>(0)
    
    const [total, setTotal] = react.useState<number>(0)

    const [percentage, setPercentage] = react.useState<number>(0)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmTO = globalThis.window.callback.onTcpOpened((opened: boolean) => setIsOpened(opened))

        const rmRI = globalThis.window.callback.onReceivedInfo((info: WebSocketInfo) =>
        {
            if (info.counter === info.total)
            {
                setSource(`Simulation completed [${info.source}]`)
            }
            else
            {
                setSource(`Simulation in progress [${info.source}]`)
            }
            
            setProgress(info.counter)
            setTotal(info.total)
            setPercentage(info.total > 0 ? Number(Number((info.counter / info.total) * 100).toFixed(0)) : 0)
        })

        return () => { rmTO(); rmRI() }
    }, [])

    // --- RENDERING ---

    const css: string = "hover:bg-stone-700 px-1 py-0.5 rounded cursor-default"

    return (
        <div className="w-full h-6 bg-stone-950 text-white text-xs flex items-center justify-between px-2 select-none">

            <div className="flex items-center gap-1 custom-font">

                <span className={css}>Server</span>

                <iconify.Icon
                    icon={isOpened ? "mdi:server" : "mdi:server-off"}
                    className={`${isOpened ? "text-green-300" : "text-red-300"}`} />

            </div>

            <div className="flex items-center gap-3 custom-font text-nowrap">

                <p>{source}</p>

                <div className="w-64 bg-neutral-800 rounded h-3 overflow-hidden">
                    
                    <div
                        className={`h-full transition-all duration-150
                                    ${(percentage === 100) ? 'bg-green-300' : 'bg-orange-300'}`}
                        style={{ width: `${percentage}%` }}
                    />

                </div>

                <div className="text-sm text-neutral-300 w-10 text-right">{percentage} %</div>

                {/* <span className={css}>Electron v{versions.electron}</span>

                <span className={css}>Chromium v{versions.chrome}</span>

                <span className={css}>Node v{versions.node}</span> */}

            </div>

        </div>
    )
}