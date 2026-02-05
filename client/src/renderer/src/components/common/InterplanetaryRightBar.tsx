import * as react from "react"

import FormSection from "../dialogs/FormSection"

/** @function InterplanetaryRightBar */
export function InterplanetaryRightBar({ info }: Readonly<{ info: ISelectionInfo | null }>): react.JSX.Element
{
    return (
        <div className="w-full h-full bg-neutral-900 p-4 overflow-y-auto space-y-6">

            {/* Title */}

            <h2 className="text-lg font-semibold text-neutral-200">Transfer Details</h2>

            {
                !info &&
                <div className="text-neutral-500 text-sm">
                    Select a point on the pork‑chop plot to view transfer details.
                </div>
            }

            {
                info &&
                <>
                    {/* Dates */}

                    <FormSection title="Dates">

                        <Field title="Launch" value={info.launchDate} />

                        <Field title="Arrival" value={info.arrivalDate} />

                        <Field title="TOF" value={String(info.tofDays) + " days"} />

                        <Field title="" value={Number(info.tofDays / 365).toFixed(0) + " years"} />

                        <Field title="" value={Number(info.tofDays * 24).toFixed(0) + " hours"} />
                    
                    </FormSection>

                    {/* Delta-V */}

                    <FormSection title="Δv Breakdown">

                        <Field title="Departure Δv" value={info.dv1.toFixed(3) + " km/s"} />

                        <Field title="Arrival Δv" value={info.dv2.toFixed(3) + " km/s"} />

                        <Field title="Total Δv" value={info.dv.toFixed(3) + " km/s"} />

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