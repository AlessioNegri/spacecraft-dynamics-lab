import * as react from "react"
import * as iconify from "@iconify/react"
import * as Toast from "@radix-ui/react-toast"
import * as Themes from "@radix-ui/themes"

import utility from "@renderer/common/utility"

/** @function StatusBar */
export default function StatusBar(): react.JSX.Element
{
    // --- USE STATE ---

    const [serverConnected, setServerConnected] = react.useState<boolean>(false)

    const [info, setInfo] = react.useState<WebSocketInfo | null>(null)

    const [sim, setSim] = react.useState<WebSocketSimulation | null>(null)

    const [notification, setNotification] = react.useState<boolean>(false)
    
    const [eventDate, setEventDate] = react.useState<string>("")

    const [online, setOnline] = react.useState<boolean>(false)

    // --- USE REF ---

    const timerRef = react.useRef<number>(0)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmAO = globalThis.window.callback.onAppOnline((online: boolean) => setOnline(online))

        const rmTO = globalThis.window.callback.onTcpOpened((opened: boolean) => setServerConnected(opened))

        const rmWSI = globalThis.window.callback.onWebSocketInfo((info: WebSocketInfo) =>
        {
            setInfo(info)
        })

        const rmWSS = globalThis.window.callback.onWebSocketSimulation((sim: WebSocketSimulation) =>
        {
            setSim(sim)

            if (sim.counter === sim.total && sim.counter != 0)
            {
                setNotification(false)

                globalThis.window.clearTimeout(timerRef.current)

                timerRef.current = globalThis.window.setTimeout(() => setNotification(true), 100);
            }
        })

        return () => { rmAO(); rmTO(); rmWSI(); rmWSS(); clearTimeout(timerRef.current) }
    }, [])

    react.useEffect(() =>
    {
        if (!notification) return

        const now: Date = new Date()

        const date: string = now.toLocaleDateString("it-IT")

        const time: string = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })

        setEventDate(`${date} ${time}`)

    }, [notification])

    // --- RENDERING ---

    const value: number = (sim && sim.total > 0) ? Math.min(100, Math.round((sim.counter / sim.total) * 100)) : 0

    const status: string = (sim && value !== 100) ? `Simulation [${sim.source}]` : ""

    const toastTitle: string = sim ? `Simulation [${sim.source}]` : ""

    const databaseConnected: boolean = info ? info.database.connected : false

    const css: string = "hover:bg-neutral-700 px-1 py-0.5 rounded cursor-default text-xs"

    let progressColor: string = ""

    if (value < 25)
    {
        progressColor = "bg-red-300"
    }
    else if (value < 50)
    {
        progressColor = "bg-orange-300"
    }
    else if (value < 75)
    {
        progressColor = "bg-yellow-300"
    }
    else if (value < 100)
    {
        progressColor = "bg-lime-300"
    }
    else
    {
        progressColor = "bg-green-300"
    }

    return (
        <div className="w-full h-8 bg-neutral-900 text-white flex items-center justify-between px-2 gap-4">

            

            {/* Status */}

            <div className="flex items-center gap-1 custom-font">

                <span className={css}>Server</span>

                <iconify.Icon
                    icon="simple-icons:fastapi"
                    className={utility.cn(serverConnected ? "text-green-300" : "text-red-300")} />

                <span className={css}>Database</span>

                <iconify.Icon
                    icon="simple-icons:mongodb"
                    className={utility.cn(databaseConnected ? "text-green-300" : "text-red-300")} />

                <span className={css}>Internet</span>

                <iconify.Icon
                    icon="mdi:internet"
                    className={utility.cn(online ? "text-green-300" : "text-red-300")} />

            </div>

            {/* Progress Bar */}

            <div className="flex items-center gap-3 custom-font text-nowrap">

                <p className="text-xs">{status}</p>

                {
                    value > 0 && value < 100 &&
                    <iconify.Icon icon="ion:hourglass-outline" className="text-cyan-300 animate-pulse" />
                }

                {
                    value === 100 &&
                    <iconify.Icon icon="mdi:done-outline" className="text-green-300" />
                }

                <div className="w-50 bg-neutral-700 rounded h-3 overflow-hidden relative">
                    
                    <div
                        className={utility.cn("h-full transition-[width] duration-300 ease-out", progressColor)}
                        style={{ width: `${value}%` }}
                    />

                    {
                        value > 0 && value < 100 &&
                        <div
                            className={utility.cn("absolute inset-0",
                                "bg-linear-to-r from-transparent via-white/20 to-transparent animate-shimmer")}
                        />
                    }

                </div>

                <div className="text-neutral-300 w-10 text-right text-xs">{value} %</div>

            </div>

            {/* Toast */}

            <div className="absolute">

                <Toast.Provider swipeDirection="right">

                    <Toast.Root
                        className={utility.cn(
                            "grid grid-cols-[auto_max-content] [grid-template-areas:'title_action'_'description_action']",
                            "items-center gap-x-4 rounded-md bg-neutral-950 p-4")}
                        open={notification}
                        onOpenChange={setNotification}
                    >

                        <Toast.Title className="[grid-area:title] mb-4 text-sm font-medium">
                            {toastTitle} Completed
                        </Toast.Title>

                        <Toast.Description asChild>
                            <p className="[grid-area:description] text-xs">{eventDate}</p>
                        </Toast.Description>
                        
                        <Toast.Action className="[grid-area:action]" asChild altText="Close">
                            <Themes.Button color="red" variant="outline">
                                Close
                            </Themes.Button>
                        </Toast.Action>

                    </Toast.Root>

                    <Toast.Viewport
                        className="fixed bottom-10 right-4 z-1000 flex w-120 max-w-[100vw] flex-col gap-2.5"
                    />

                </Toast.Provider>
                
            </div>

        </div>
    )
}