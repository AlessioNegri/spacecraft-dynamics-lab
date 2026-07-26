import * as react from "react"
import * as iconify from "@iconify/react"
import * as Themes from "@radix-ui/themes"

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

                    <Row left="Author" right="Alessio Negri" />

                    <Row left="Version" right="v0.2.0" />

                    <Row left="Release" right="2026.XX.XX" />

                    <Row left="License" right="MIT License" />

                    <div className="flex justify-between">
                        <span className="text-neutral-400">Source Code</span>
                        
                        <Themes.Link
                            href="https://github.com/AlessioNegri/spacecraft-dynamics-lab"
                            target="_blank"
                            className="text-orange-300 hover:text-orange-400"
                        >
                            GitHub Repository →
                        </Themes.Link>
                    </div>

                    <span className="text-neutral-400">Stack</span>

                    <div className="pt-4 space-y-3 pb-2 border-b border-neutral-500">

                        <div className="flex flex-row gap-2 text-neutral-300 text-sm">

                            <Technology name="astropy" icon="simple-icons:astro" color="text-orange-300" />

                            <Technology name="numpy" icon="simple-icons:numpy" color="text-cyan-300" />

                            <Technology name="scipy" icon="simple-icons:scipy" color="text-blue-300" />

                            <Technology name="typing" icon="simple-icons:typst" color="text-pink-300" />

                        </div>

                    </div>

                    <div className="space-y-3 pb-2 border-b border-neutral-500">

                        <div className="flex flex-row gap-2 text-neutral-300 text-sm mt-4">

                            <Technology name="FastAPI" icon="simple-icons:fastapi" color="text-emerald-300" />

                            <Technology name="MongoDB" icon="simple-icons:mongodb" color="text-green-300" />

                            <Technology name="WebSocket" icon="simple-icons:socket" color="text-yellow-300" />

                        </div>
                        
                    </div>

                    <div className="space-y-3">

                        <div className="flex flex-row gap-2 text-neutral-300 text-sm mt-4">


                            <Technology name="Electron" icon="simple-icons:electron" color="text-blue-300" />

                            <Technology name="React" icon="simple-icons:react" color="text-sky-300" />

                            <Technology name="TailwindCSS" icon="simple-icons:tailwindcss" color="text-cyan-300" />

                            <Technology name="RadixUI" icon="simple-icons:radixui" color="text-violet-300" />

                            <Technology name="Plotly" icon="simple-icons:plotly" color="text-red-300" />

                        </div>

                        <div className="flex flex-row gap-2 text-neutral-300 text-sm mt-4">

                            <Technology name="CesiumJS" icon="simple-icons:cesium" color="text-emerald-300" />

                        </div>
                        
                    </div>

                </div>

                {/* Copyright */}

                <div className="border-neutral-700 text-center text-neutral-500 text-sm">
                    © 2026 Spacecraft Dynamics Lab — Licensed under MIT.
                </div>

            </div>

        </DialogRUI>
    )
}

/** @function Row */
function Row({ left, right } : Readonly<{ left: string, right: string }>): react.JSX.Element
{
    return (
        <div className="flex justify-between">
            <span className="text-neutral-400">{left}</span>
            <span className="font-semibold">{right}</span>
        </div>
    )
}

/** @function Technology */
function Technology({ name, icon, color } : Readonly<{ name: string, icon: string, color: string }>): react.JSX.Element
{
    return (
        <div className="flex items-center space-x-3 bg-neutral-700 rounded p-2">

            <iconify.Icon icon={icon} width={22} className={color} />

            <span>{name}</span>

        </div>
    )
}
