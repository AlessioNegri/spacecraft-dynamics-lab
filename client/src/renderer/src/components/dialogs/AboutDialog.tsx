import * as react from "react"

import DialogRUI from "./DialogRUI"

import logo from "../../assets/SpacecraftDynamicsLab.png"

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function AboutDialog */
export default function AboutDialog(props: Readonly<Props>): react.JSX.Element
{
    return (
        <DialogRUI
            title="About SDL - Spacecraft Dynamics Lab"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}>

            <div className="flex flex-col custom-font p-6 space-y-8 text-neutral-200">

                {/* Logo */}

                <div className="flex justify-center items-center space-x-6">
                    <img
                        src={logo}
                        alt="Spacecraft Dynamics Lab Logo"
                        className="w-[70%] h-auto rounded shadow-lg"
                    />
                </div>

                {/* Metadata */}

                <div className="border border-neutral-700 rounded p-4 space-y-2 bg-neutral-900/40">

                    <div className="flex justify-between">
                        <span className="text-neutral-400">Author</span>
                        <span className="font-semibold">Alessio Negri</span>
                    </div>

                    <div className="flex justify-between">
                        <span className="text-neutral-400">Version</span>
                        <span className="font-semibold">v0.1.0</span>
                    </div>

                    <div className="flex justify-between">
                        <span className="text-neutral-400">Release</span>
                        <span className="font-semibold">2026.06.21</span>
                    </div>

                    <div className="flex justify-between">
                        <span className="text-neutral-400">License</span>
                        <span className="font-semibold">MIT License</span>
                    </div>

                    <div className="flex justify-between">
                        <span className="text-neutral-400">Source Code</span>
                        <a
                            href="https://github.com/AlessioNegri/spacecraft-dynamics-lab"
                            target="_blank"
                            rel="noreferrer"
                            className="text-orange-400 hover:underline"
                        >
                            GitHub Repository
                        </a>
                    </div>
                </div>

                {/* Copyright */}

                <div className="border-neutral-700 text-center text-neutral-500 text-sm">
                    © 2026 Spacecraft Dynamics Lab — All rights reserved.
                </div>

            </div>

            {/* <div className="flex flex-col custom-font p-4 space-y-6">

                <div className="flex justify-between border-neutral-700">

                    <img
                        src={logo}
                        alt="Spacecraft Dynamics Lab Logo"
                        className="w-96 h-auto rounded"
                    />

                    <div className="flex flex-col gap-4 items-center justify-center text-right">

                        <span className="text-orange-300 font-bold text-lg">Spacecraft Dynamics Lab</span>

                        <span className="text-neutral-300 font-bold">v0.1.0 - Jun 21 2026</span>

                        <span className="text-neutral-400 text-sm">Developed by Alessio Negri</span>

                    </div>

                </div>

            </div> */}

        </DialogRUI>
    )
}
