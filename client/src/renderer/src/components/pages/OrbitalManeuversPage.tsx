import * as react from "react"

import * as utility from "@renderer/common/utility"

import LeftPanel from "@renderer/components/pages/orbital_maneuvers/LeftPanel"
import CentralPanel from "@renderer/components/pages/orbital_maneuvers/CentralPanel"
import RightPanel from "@renderer/components/pages/orbital_maneuvers/RightPanel"

/** @function OrbitalManeuversPage */
export default function OrbitalManeuversPage(): react.JSX.Element
{
    // --- USE STATE ---

    const [orbits, setOrbits] = react.useState<IOrbits>({initial: [], transfer: [], final: []})

    const [maneuverResult, setManeuverResult] = react.useState<IOrbitalManeuverFormOutput | null>(null)

    const [hideLeftBar, setHideLeftBar] = react.useState<boolean>(false)

    const [hideRightBar, setHideRightBar] = react.useState<boolean>(false)

    // --- RENDERING ---
    
    return (
        <div className="flex flex-col h-full w-full bg-neutral-800 text-neutral-100">
        
            <div className="flex flex-1 overflow-hidden">

                <div className={utility.cn(hideLeftBar ? "w-18" : "w-90",
                    "border-r border-neutral-700 p-4 overflow-y-auto bg-orange-300/5")}>

                    <LeftPanel
                        onHide={(hide: boolean) => setHideLeftBar(hide)}
                        onOrbitsChange={setOrbits}
                        onResultChange={setManeuverResult}
                    />

                </div>

                <div className="flex-1 p-4 overflow-auto flex items-center justify-center">
            
                    <CentralPanel orbits={orbits} />

                </div>

                <div className={utility.cn(hideRightBar ? "w-18" : "w-80",
                    "border-l border-neutral-700 p-4 overflow-y-auto bg-cyan-300/5")}>

                    <RightPanel result={maneuverResult} onHide={(hide: boolean) => setHideRightBar(hide)} />

                </div>

            </div>

        </div>
    )
}
