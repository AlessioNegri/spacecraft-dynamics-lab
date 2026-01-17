import * as react from "react"
import * as iconify from "@iconify/react"

/** @function StatusBar */
export default function StatusBar(): react.JSX.Element
{
    // --- USE STATE ---

    const [isOpened, setIsOpened] = react.useState<boolean>(false)
    
    const [versions] = react.useState<any>(globalThis.electron.process.versions)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmTO = globalThis.window.callback.onTcpOpened((opened: boolean) => setIsOpened(opened))

        return () => { rmTO() }
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

            <div className="flex items-center gap-3 custom-font">

                <span className={css}>Electron v{versions.electron}</span>

                <span className={css}>Chromium v{versions.chrome}</span>

                <span className={css}>Node v{versions.node}</span>

            </div>

        </div>
    )
}