import * as react from "react"
//import * as iconify from "@iconify/react"

import DialogRUI from "./DialogRUI"

import logo from "../../assets/SDL.png"

interface AboutDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function AboutDialog */
export default function AboutDialog(props: Readonly<AboutDialogProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [versions] = react.useState<any>(globalThis.electron.process.versions)

    // --- RENDERING ---

    return (
        <DialogRUI
                    title="About SDL"
                    button="Close"
                    open={props.opened}
                    onClose={() => props.setOpened(false)}
                    onSubmit={() => props.setOpened(false)}>

            <div className="flex-col custom-font p-4 space-y-6">

                <div className="flex justify-between pb-4 border-b border-neutral-700">

                    {/* <iconify.Icon
                        icon={"streamline-ultimate:space-rocket-earth"}
                        width={100}
                        className="text-orange-300"
                    /> */}

                    <img
                        src={logo}
                        alt="Spacecraft Dynamics Lab Logo"
                        className="w-32 h-auto rounded-3xl"
                    />

                    <div className="flex flex-col items-center">

                        <span className="text-orange-300 font-bold">Spacecraft Dynamics Lab</span>

                        <span className="text-orange-300 font-bold">1.0.0</span>
                        
                        <span>Release Date: Jan 01 2026</span>

                    </div>


                </div>

                <div className="flex-row custom-font p-2 space-y-4">

                    <div className="flex justify-between">
                        
                        <span className="text-cyan-400">Electron</span>

                        <span className="text-green-400">v{versions.electron}</span>

                    </div>

                    <div className="flex justify-between">
                        
                        <span className="text-cyan-400">Chromium</span>

                        <span className="text-green-400">v{versions.chrome}</span>

                    </div>

                    <div className="flex justify-between">
                        
                        <span className="text-cyan-400">Node</span>

                        <span className="text-green-400">v{versions.node}</span>

                    </div>

                </div>

            </div>

        </DialogRUI>
    )
}