import * as react from "react"
import * as iconify from "@iconify/react"

import Tooltip from "../Tooltip"
import FormSection from "../dialogs/FormSection"

interface InterplanetaryRightBarProps
{
    info: ISelectionInfo | null
    onHide: (hide: boolean) => void
}

/** @function InterplanetaryRightBar */
export default function InterplanetaryRightBar(props: Readonly<InterplanetaryRightBarProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [hide, setHide] = react.useState<boolean>(false)

    // --- USE EFFECT ---

    react.useEffect(() => { props.onHide(hide) }, [hide])

    // --- RENDERING ---

    return (
        <div className="w-full h-full p-4 overflow-y-auto space-y-6 relative">

            <Tooltip title={hide ? "Show" : "Hide"} side="top">
            
                <iconify.Icon
                    icon={hide ? "tabler:layout-sidebar-right" : "tabler:layout-sidebar-right-filled"}
                    width={20}
                    className="absolute top-2 right-2 cursor-pointer hover:text-orange-300"
                    onClick={() => setHide(prev => !prev)}
                />

            </Tooltip>

        {
            !hide && (<>

            {/* Title */}

            <h2 className="text-lg font-semibold text-neutral-200">Transfer Details</h2>

            {
                !props.info &&
                <div className="text-neutral-500 text-sm">
                    Select a point on the pork‑chop plot to view transfer details.
                </div>
            }

            {
                props.info &&
                <>
                    {/* Dates */}

                    <FormSection title="Dates">

                        <Field title="Launch" value={props.info.launchDate} />

                        { props.info.flybyDate && <Field title="Flyby" value={props.info.flybyDate} /> }

                        <Field title="Arrival" value={props.info.arrivalDate} />

                    {
                        props.info.tof1Days &&
                        <>
                        
                            <Field title="TOF 1" value={String(props.info.tof1Days) + " days"} />

                            <Field title="" value={Number(props.info.tof1Days / 365).toFixed(0) + " years"} />

                            <Field title="" value={Number(props.info.tof1Days * 24).toFixed(0) + " hours"} />

                        </>
                    }

                    {
                        props.info.tof2Days &&
                        <>
                        
                            <Field title="TOF 2" value={String(props.info.tof2Days) + " days"} />

                            <Field title="" value={Number(props.info.tof2Days / 365).toFixed(0) + " years"} />

                            <Field title="" value={Number(props.info.tof2Days * 24).toFixed(0) + " hours"} />

                        </>
                    }

                        <Field title="TOF" value={String(props.info.tofDays) + " days"} />

                        <Field title="" value={Number(props.info.tofDays / 365).toFixed(0) + " years"} />

                        <Field title="" value={Number(props.info.tofDays * 24).toFixed(0) + " hours"} />
                    
                    </FormSection>

                    {/* Delta-V */}

                    <FormSection title="Δv Breakdown">

                        <Field title="Departure Δv" value={props.info.dv1.toFixed(3) + " km/s"} />

                        { props.info.dvGA && <Field title="Gravity Assist Δv" value={props.info.dvGA.toFixed(3) + " km/s"} /> }

                        <Field title="Arrival Δv" value={props.info.dv2.toFixed(3) + " km/s"} />

                        <Field title="Total Δv" value={props.info.dv.toFixed(3) + " km/s"} />

                    </FormSection>

                    {/* Lambert Vectors */}
                    {/* <section>
                        <h3 className="text-sm font-semibold text-neutral-300 mb-2">
                            Lambert Solution
                        </h3>

                        <div className="text-xs text-neutral-400 space-y-2">
                            <div>
                                <div className="text-neutral-500 mb-1">v₁ (km/s)</div>
                                <pre className="bg-neutral-800 p-2 rounded text-neutral-300">
                                    
                                </pre>
                            </div>

                            <div>
                                <div className="text-neutral-500 mb-1">v₂ (km/s)</div>
                                <pre className="bg-neutral-800 p-2 rounded text-neutral-300">
                                    
                                </pre>
                            </div>
                        </div>
                    </section> */}

                    {/* Export */}
                    {/* <button
                        className="w-full py-2 bg-neutral-800 hover:bg-neutral-700 rounded text-sm text-neutral-200 border border-neutral-700"
                        onClick={() => console.log("Export transfer")}
                    >
                        Export Transfer
                    </button> */}
                </>
            }
            </>)
        }
        </div>
    )
}

interface FieldProps
{
    title: string
    value: string
}

/** @function Field */
function Field(props: Readonly<FieldProps>): react.JSX.Element
{
    return (
        <div className="flex justify-between text-sm">

            <span className="text-neutral-400">{props.title}</span>

            <span className="text-neutral-200">{props.value}</span>

        </div>
    )
}