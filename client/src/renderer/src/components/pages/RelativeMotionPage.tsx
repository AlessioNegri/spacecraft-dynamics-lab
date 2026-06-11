import * as react from "react"

import * as utility from "@renderer/common/utility"

import LeftPanel from "@renderer/components/pages/relative_motion/LeftPanel"
import CentralPanel from "@renderer/components/pages/relative_motion/CentralPanel"
import RightPanel from "@renderer/components/pages/relative_motion/RightPanel"

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

    const [hideLeftBar, setHideLeftBar] = react.useState<boolean>(false)

    const [hideRightBar, setHideRightBar] = react.useState<boolean>(false)

    // --- RENDERING ---
    
    return (
        <div className="flex flex-col h-full w-full bg-neutral-800 text-neutral-100">
        
            <div className="flex flex-1 overflow-hidden">

                <div className={utility.cn(hideLeftBar ? "w-18" : "w-90",
                    "border-r border-neutral-700 p-4 overflow-y-auto bg-orange-300/5")}>

                    <LeftPanel onHide={(hide: boolean) => setHideLeftBar(hide)} onSolutionsChange={setSolutions} />

                </div>

                <div className="flex-1 p-4 overflow-auto flex items-center justify-center">
            
                    <CentralPanel solutions={solutions} />

                </div>

                <div className={utility.cn(hideRightBar ? "w-18" : "w-80",
                    "border-l border-neutral-700 p-4 overflow-y-auto bg-cyan-300/5")}>

                    <RightPanel solutions={solutions} onHide={(hide: boolean) => setHideRightBar(hide)} />

                </div>

            </div>

        </div>
    )
}
