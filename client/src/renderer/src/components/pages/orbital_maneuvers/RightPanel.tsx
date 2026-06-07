import * as react from "react"
import * as iconify from "@iconify/react"
import * as Form from "@radix-ui/react-form"

import Tooltip from "@renderer/components/Tooltip"
import OutputField from "@renderer/components/dialogs/OutputField"

interface Props
{
    result?: IOrbitalManeuverFormOutput | null
    onHide: (hide: boolean) => void
}

/** @function RightPanel */
export default function RightPanel(props: Readonly<Props>): react.JSX.Element
{
    const [hide, setHide] = react.useState<boolean>(false)

    react.useEffect(() => { props.onHide(hide) }, [hide])

    return (
        <div className={`w-full h-full p-4 overflow-y-auto custom-scrollbar space-y-6 relative`}>

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

                    <div className="flex space-x-4 col-span-full justify-center items-center">
                    
                        <iconify.Icon
                            icon="game-icons:orbit"
                            width={32}
                        />

                        <span className="font-bold">NEW ORBIT</span>

                    </div>

                    <OutputField
                        label="Semimajor Axis"
                        symbol="a"
                        unit="km"
                        value={props.result?.orbitalElements.sma ?? 0}
                        tooltip
                    />

                    <OutputField
                        label="Eccentricity"
                        symbol="e"
                        unit=""
                        value={props.result?.orbitalElements.ecc ?? 0}
                        tooltip
                    />

                    <OutputField
                        label="Inclination"
                        symbol="i"
                        unit="deg"
                        value={props.result?.orbitalElements.inc ?? 0}
                        tooltip
                    />

                    <OutputField
                        label="Right Ascension of Ascending Node"
                        symbol="\Omega"
                        unit="deg"
                        value={props.result?.orbitalElements.raan ?? 0}
                        tooltip
                    />

                    <OutputField
                        label="Argument of Periapsis"
                        symbol="\omega"
                        unit="deg"
                        value={props.result?.orbitalElements.aop ?? 0}
                        tooltip
                    />

                    <OutputField
                        label="True Anomaly"
                        symbol="\theta"
                        unit="deg"
                        value={props.result?.orbitalElements.ta ?? 0}
                        tooltip
                    />

                    <div className="flex space-x-4 col-span-full justify-center items-center">
                    
                        <iconify.Icon
                            icon="iconoir:coins"
                            width={32}
                        />

                        <span className="font-bold">COST</span>

                    </div>

                    <OutputField
                        label="Delta Velocity"
                        symbol="\Delta v"
                        unit="km / s"
                        value={props.result?.maneuver.dv ?? 0}
                        tooltip
                    />

                    <OutputField
                        label="Delta Time"
                        symbol="\Delta t"
                        unit="hours"
                        value={props.result?.maneuver.dt ?? 0}
                        tooltip
                    />

                    <OutputField
                        label="Delta Mass"
                        symbol="\Delta m"
                        unit="kg"
                        value={props.result?.maneuver.dm ?? 0}
                        tooltip
                    />

                    <OutputField
                        label="Burn Time"
                        symbol="t_{burn}"
                        unit="s"
                        value={props.result?.maneuver.burnTime ?? 0}
                        tooltip
                    />

                </Form.Root>
            }

        </div>
    )
}
