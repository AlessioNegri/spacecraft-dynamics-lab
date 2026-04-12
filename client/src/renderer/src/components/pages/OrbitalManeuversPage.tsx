import * as react from "react"

import LeftPanel from "./orbital_maneuvers/LeftPanel"
import RightPanel from "./orbital_maneuvers/RightPanel"

/** @function OrbitalManeuversPage */
export default function OrbitalManeuversPage(): react.JSX.Element
{
    // --- USE STATE ---

    const [orbits, setOrbits] = react.useState<IOrbits>({initial: [], transfer: [], final: []})

    // --- RENDERING ---
    
    return (
        <div className="w-full h-full flex">

            <LeftPanel onOrbitsChange={setOrbits} />

            <RightPanel orbits={orbits} />

        </div>
    )
}
