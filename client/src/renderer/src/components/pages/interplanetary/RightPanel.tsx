import * as react from "react"
import * as iconify from "@iconify/react"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"
import { InlineMath } from "react-katex"

import http from "@renderer/common/http"

import Tooltip from "@renderer/components/Tooltip"
import InputField from "../../dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface IFormIn
{
    departureBody: string
    flybyBody: string
    arrivalBody: string
    launchDate: string
    flybyDate: string
    arrivalDate: string
    departureHeight: number
    arrivalPeriapsisHeight: number
    arrivalOrbitalPeriod: number
}

interface IFormOut
{
    departureDeltaV: number
    arrivalDeltaV: number
}

const defaultIn: IFormIn =
{
    departureBody: "",
    flybyBody: "",
    arrivalBody: "",
    launchDate: "",
    flybyDate: "",
    arrivalDate: "",
    departureHeight: 180,
    arrivalPeriapsisHeight: 300,
    arrivalOrbitalPeriod: 48
}

const defaultOut: IFormOut =
{
    departureDeltaV: 0,
    arrivalDeltaV: 0
}

interface Props
{
    departureBody: string
    flybyBody: string
    arrivalBody: string
    info: ISelectionInfo | null
    onHide: (hide: boolean) => void
}

/** @function InterplanetaryRightBar */
export default function InterplanetaryRightBar(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [hide, setHide] = react.useState<boolean>(false)

    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)
            
    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    // --- USE EFFECT ---

    react.useEffect(() => { props.onHide(hide) }, [hide])

    react.useEffect(() => { setFormIn(prev => ({ ...prev, departureBody: props.departureBody.toLowerCase() })) }, [props.departureBody])

    react.useEffect(() => { setFormIn(prev => ({ ...prev, flybyBody: props.flybyBody?.toLowerCase() })) }, [props.flybyBody])

    react.useEffect(() => { setFormIn(prev => ({ ...prev, arrivalBody: props.arrivalBody.toLowerCase() })) }, [props.arrivalBody])

    react.useEffect(() =>
    {
        if (!props.info) return

        const updated: IFormIn =
        {
            ...formIn,
            launchDate: props.info.launchDate,
            flybyDate: props.info.flybyDate || "",
            arrivalDate: props.info.arrivalDate
        }

        setFormIn(updated)
        
        request(updated)
    }, [props.info])

    // --- HANDLE ---

    const request = async (data: IFormIn) =>
    {
        try
        {
            let response: any = await http.api.post(`/interplanetary/optimal-transfer`, data)

            const result: IFormOut = response.data
            
            setFormOut(result)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setFormIn({ ...formIn, [name]: value})
    }

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
                    {/* Bodies */}
                    
                    <div className="flex space-x-4 col-span-full justify-center items-center">
                    
                        <iconify.Icon
                            icon="game-icons:solar-system"
                            width={32}
                        />
    
                        <span className="font-bold">BODIES</span>
    
                    </div>

                    <div className="flex flex-col gap-2">

                        <Field title="Departure" value={props.departureBody} />

                        { props.flybyBody && <Field title="Flyby" value={props.flybyBody} /> }

                        <Field title="Arrival" value={props.arrivalBody} />

                    </div>

                    {/* Dates */}

                    <div className="flex space-x-4 col-span-full justify-center items-center">
                                    
                        <iconify.Icon
                            icon="clarity:date-solid"
                            width={32}
                        />
    
                        <span className="font-bold">DATES</span>
    
                    </div>

                    <div className="flex flex-col gap-2">

                        <Field title="Launch" value={props.info.launchDate} />

                        { props.info.flybyDate && <Field title="Flyby" value={props.info.flybyDate} /> }

                        <Field title="Arrival" value={props.info.arrivalDate} />

                    {
                        props.info.tof1Days &&
                        <>
                        
                            <Field title="TOF 1" value={props.info.tof1Days.toFixed(0) + " days"} />

                            {/* <Field title="" value={Number(props.info.tof1Days / 365).toFixed(0) + " years"} /> */}

                            {/* <Field title="" value={Number(props.info.tof1Days * 24).toFixed(0) + " hours"} /> */}

                        </>
                    }

                    {
                        props.info.tof2Days &&
                        <>
                        
                            <Field title="TOF 2" value={props.info.tof2Days.toFixed(0) + " days"} />

                            {/* <Field title="" value={Number(props.info.tof2Days / 365).toFixed(0) + " years"} /> */}

                            {/* <Field title="" value={Number(props.info.tof2Days * 24).toFixed(0) + " hours"} /> */}

                        </>
                    }

                        <Field title="TOF" value={props.info.tofDays.toFixed(0) + " days"} />

                        {/* <Field title="" value={Number(props.info.tofDays / 365).toFixed(0) + " years"} /> */}

                        {/* <Field title="" value={Number(props.info.tofDays * 24).toFixed(0) + " hours"} /> */}
                    
                    </div>

                    {/* Delta-V */}

                    <div className="flex space-x-4 justify-center items-center">
                    
                        <iconify.Icon
                            icon="game-icons:rocket-thruster"
                            width={32}
                        />

                        <span className="font-bold">ΔV BREAKDOWN</span>

                    </div>

                    <div className="flex flex-col gap-2">

                        <Field
                            title={<InlineMath math="\Delta v_1 = v_{\infty}^-" />}
                            value={props.info.dv1.toFixed(3) + " km/s"}
                        />

                        {
                            props.info.dvGA &&
                            <Field
                                title={<InlineMath math="\Delta v_{GA}" />}
                                value={props.info.dvGA.toFixed(3) + " km/s"}
                            />
                        }

                        <Field
                            title={<InlineMath math="\Delta v_2 = v_{\infty}^+" />}
                            value={props.info.dv2.toFixed(3) + " km/s"}
                        />

                        <Field
                            title={<InlineMath math="\Delta v_{TOT}" />}
                            value={props.info.dv.toFixed(3) + " km/s"}
                        />

                    </div>

                    {/* Orbits */}

                    <div className="flex space-x-4 justify-center items-center">
                    
                        <iconify.Icon
                            icon="game-icons:orbit"
                            width={32}
                        />

                        <span className="font-bold">ORBITS</span>

                    </div>

                    <div className="flex flex-col gap-2">

                        <Form.Root className="w-full flex-col space-y-4" onSubmit={(e) => e.preventDefault()}>

                            <InputField
                                type="number"
                                name="departureHeight"
                                label="Departure Parking Orbit Altitude"
                                symbol="H_D"
                                unit="km"
                                value={formIn.departureHeight}
                                onChange={handleChange}
                                min={1}
                            />

                            <InputField
                                type="number"
                                name="arrivalPeriapsisHeight"
                                label="Arrival Periapsis Orbit Altitude"
                                symbol="H_p"
                                unit="km"
                                value={formIn.arrivalPeriapsisHeight}
                                onChange={handleChange}
                                min={1}
                            />

                            <InputField
                                type="number"
                                name="arrivalOrbitalPeriod"
                                label="Arrival Orbital Period"
                                symbol="T_A"
                                unit="hours"
                                value={formIn.arrivalOrbitalPeriod}
                                onChange={handleChange}
                                min={1}
                            />

                        </Form.Root>

                        <Form.Root className="w-full flex-col space-y-4 border-t-2 mt-4 pt-4">

                            <OutputField
                                label="Departure Delta Velocity"
                                symbol="\Delta v"
                                unit="km / s"
                                value={formOut.departureDeltaV}
                            />

                            <OutputField
                                label="Arrival Delta Velocity"
                                symbol="\Delta v"
                                unit="km / s"
                                value={formOut.arrivalDeltaV}
                            />

                            <OutputField
                                label="Total Delta Velocity"
                                symbol="\Delta v"
                                unit="km / s"
                                value={formOut.departureDeltaV + formOut.arrivalDeltaV}
                            />

                        </Form.Root>
                        
                    </div>

                    <div className="flex justify-center">
                    
                        <Themes.Button color="green" variant="outline" onClick={() => request(formIn)}>
                            Calculate
                        </Themes.Button>

                    </div>

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
    title: react.ReactNode
    value: react.ReactNode
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
