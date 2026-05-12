import * as react from "react"

import LeftPanel from "./orbital_perturbations/LeftPanel"
import RightPanel from "./orbital_perturbations/RightPanel"

/** @function OrbitalPerturbationsPage */
export default function OrbitalPerturbationsPage(): react.JSX.Element
{
    // --- USE STATE ---

    const [hideLeftBar, setHideLeftBar] = react.useState<boolean>(false)

    // --- RENDERING ---
    
    return (
            <div className="flex flex-col h-full w-full bg-neutral-800 text-neutral-100">
    
                <div className="flex flex-1 overflow-hidden">
    
                    <div className={`${hideLeftBar ? "w-18" : "w-80"} border-r border-neutral-700 p-4 overflow-y-auto`}>
    
                        <LeftPanel onHide={(hide: boolean) => setHideLeftBar(hide)} />
    
                    </div>
    
                    <div className="flex-1 p-4 overflow-auto flex items-center justify-center">
                        
                        <RightPanel />

                    </div>
    
                </div>
            </div>
        )
}
