import * as react from "react"

import TopPanel from "./relative_motion/TopPanel"
import BottomPanel from "./relative_motion/BottomPanel"

/** @function RelativeMotionPage */
export default function RelativeMotionPage(): react.JSX.Element
{
    // --- USE STATE ---

    const [solutions, setSolutions] = react.useState<IRelativeMotionFormOutput>({
        linearizedSolution: [],
        clohessyWiltshireSolution: [],
        twoImpulsiveManeuver: [],
        twoImpulsiveManeuverCost: 0
    })

    // --- RENDERING ---
    
    return (
        <div className="w-full h-full flex flex-col">

            <TopPanel onSolutionsChange={setSolutions} />

            <BottomPanel solutions={solutions} />

        </div>
    )
}
