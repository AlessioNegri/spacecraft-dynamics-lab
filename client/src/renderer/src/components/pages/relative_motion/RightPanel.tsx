import * as react from "react"
import * as iconify from "@iconify/react"
import * as Form from "@radix-ui/react-form"


import Tooltip from "@renderer/components/Tooltip"
import OutputField from "@renderer/components/dialogs/OutputField"

interface Props
{
    solutions?: IRelativeMotionFormOutput | null
    onHide: (hide: boolean) => void
}

/** @function RightPanel */
export default function RightPanel(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [hide, setHide] = react.useState<boolean>(false)

    // --- USE EFFECT ---
    
    react.useEffect(() => { props.onHide(hide) }, [hide])

    // --- RENDERING ---
    
    return (
        <div className="w-full h-full p-4 overflow-y-auto custom-scrollbar space-y-6 relative">

            <Tooltip title={hide ? "Show" : "Hide"} side="top">
            
                <iconify.Icon
                    icon={hide ? "tabler:layout-sidebar-right" : "tabler:layout-sidebar-right-filled"}
                    width={20}
                    className="absolute top-2 left-2 cursor-pointer hover:text-cyan-300"
                    onClick={() => setHide(prev => !prev)}
                />

            </Tooltip>

            {
                !hide &&

                <Form.Root className="space-y-6">

                    <div className="flex space-x-4 justify-center items-center">
                                        
                        <iconify.Icon icon="iconoir:coins" width={32} />

                        <span className="font-bold">COST</span>

                    </div>

                    <OutputField
                        label="2-Impulsive Delta Velocity"
                        symbol="\Delta v"
                        unit="m / s"
                        value={props.solutions?.twoImpulsiveManeuverCost ?? 0}
                    />

                </Form.Root>
            }

        </div>
    )
}
