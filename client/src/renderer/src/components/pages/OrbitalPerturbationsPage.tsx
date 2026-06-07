import * as react from "react"

import * as utility from "@renderer/common/utility"

import LeftPanel from "@renderer/components/pages/orbital_perturbations/LeftPanel"
import RightPanel from "@renderer/components/pages/orbital_perturbations/RightPanel"

/** @function OrbitalPerturbationsPage */
export default function OrbitalPerturbationsPage(): react.JSX.Element
{
    // --- USE STATE ---

    const [hideLeftBar, setHideLeftBar] = react.useState<boolean>(false)

    // --- RENDERING ---
    
    return (
        <div className="flex flex-col h-full w-full bg-neutral-800 text-neutral-100">

            <div className="flex flex-1 overflow-hidden">

                <div className={utility.cn(hideLeftBar ? "w-18" : "w-90",
                    "border-r border-neutral-700 p-4 overflow-y-auto bg-orange-300/5")}>

                    <LeftPanel onHide={(hide: boolean) => setHideLeftBar(hide)} />

                </div>

                <div className="flex-1 p-4 overflow-auto flex items-center justify-center">
                    
                    <RightPanel />

                </div>

            </div>
            
        </div>
        )
}
