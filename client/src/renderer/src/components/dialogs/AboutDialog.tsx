import * as react from "react"

import DialogRUI from "./DialogRUI"

import logo from "../../assets/SDL.png"

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function AboutDialog */
export default function AboutDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [versions] = react.useState<any>(globalThis.electron.process.versions)

    // --- RENDERING ---

    return (
        <DialogRUI
            title="About SDL - Spacecraft Dynamics Lab"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}>

            <div className="flex flex-col custom-font p-4 space-y-6">

                <div className="flex justify-between pb-4 border-b border-neutral-700">

                    <img
                        src={logo}
                        alt="Spacecraft Dynamics Lab Logo"
                        className="w-32 h-auto rounded-3xl"
                    />

                    <div className="flex flex-col items-center justify-center text-right">

                        <span className="text-orange-300 font-bold text-lg">Spacecraft Dynamics Lab</span>

                        <span className="text-neutral-300 font-bold">v1.0.0 - Jan 01 2026</span>

                    </div>


                </div>

                <div className="grid grid-cols-2 gap-y-2 font-mono text-base">

                    <span className="text-neutral-300">Electron</span>

                    <span className="text-neutral-400">v{versions.electron}</span>

                    <span className="text-neutral-300">Chromium</span>

                    <span className="text-neutral-400">v{versions.chrome}</span>

                    <span className="text-neutral-300">Node</span>

                    <span className="text-neutral-400">v{versions.node}</span>

                </div>

            </div>

        </DialogRUI>
    )
}
