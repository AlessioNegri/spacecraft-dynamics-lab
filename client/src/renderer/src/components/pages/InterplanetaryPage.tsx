import * as react from "react"

import utility from "@renderer/common/utility"

import InterplanetaryLeftBar from "../common/InterplanetaryLeftBar"
import InterplanetaryMainPlot from "../common/InterplanetaryMainPlot"
import InterplanetaryRightBar from "../common/InterplanetaryRightBar"

/** @function InterplanetaryPage */
export default function InterplanetaryPage()
{
    // --- USE STATE ---

    const [porkChopData2D, setPorkChopData2D] = react.useState<IPorkChopData2D | null>(null)

    const [porkChopData3D, setPorkChopData3D] = react.useState<IPorkChopData3D | null>(null)

    const [selected, setSelected] = react.useState<ISelectionInfo | null>(null)

    const [departureBody, setDepartureBody] = react.useState<string>("")

    const [flybyBody, setFlybyBody] = react.useState<string>("")

    const [arrivalBody, setArrivalBody] = react.useState<string>("")

    const [hideLeftBar, setHideLeftBar] = react.useState<boolean>(false)

    const [hideRightBar, setHideRightBar] = react.useState<boolean>(false)

    // --- USE EFFECT ---

    const processData2D = (info: WebSocketInfo) =>
    {
        const A: number = info.data["arrivalDates"].length
        const L: number = info.data["launchDates"].length

        const dv: number[][] = utility.initArray(A, L)

        for (let a = 0; a < A; a++)
        {
            for (let l = 0; l < L; l++)
            {
                dv[a][l] = info.data["dv1"][a][l] + info.data["dv2"][a][l]
            }
        }

        const data: IPorkChopData2D =
        {
            launchDates: info.data["launchDates"],
            arrivalDates: info.data["arrivalDates"],
            tofGrid: info.data["tof"],
            dv1Grid: info.data["dv1"],
            dv2Grid: info.data["dv2"],
            dvGrid: dv
        }

        setPorkChopData2D(data)
        setPorkChopData3D(null)
    }

    const processData3D = (info: WebSocketInfo) =>
    {
        const A = info.data["arrivalDates"].length
        const L = info.data["launchDates"].length

        const tof1  : number[][] = utility.initArray(A, L)
        const tof2  : number[][] = utility.initArray(A, L)
        const tof   : number[][] = utility.initArray(A, L)
        const dv1   : number[][] = utility.initArray(A, L)
        const dvGA  : number[][] = utility.initArray(A, L)
        const dv2   : number[][] = utility.initArray(A, L)
        const dv    : number[][] = utility.initArray(A, L)

        for (let a = 0; a < A; a++)
        {
            for (let l = 0; l < L; l++)
            {
                tof1[a][l]  = info.data["tof1"][a][0][l]
                tof2[a][l]  = info.data["tof2"][a][0][l]
                tof[a][l]   = tof1[a][l] + tof2[a][l]
                dv1[a][l]   = info.data["dv1"][a][0][l]
                dvGA[a][l]  = info.data["dvGA"][a][0][l]
                dv2[a][l]   = info.data["dv2"][a][0][l]
                dv[a][l]    = dv1[a][l] + dvGA[a][l] + dv2[a][l]
            }
        }

        const data: IPorkChopData3D =
        {
            launchDates: info.data["launchDates"],
            flybyDates: info.data["flybyDates"],
            arrivalDates: info.data["arrivalDates"],
            tof1Grid: tof1,
            tof2Grid: tof2,
            tofGrid: tof,
            dv1Grid: dv1,
            dvGAGrid: dvGA,
            dv2Grid: dv2,
            dvGrid: dv,
            tof1: info.data["tof1"],
            tof2: info.data["tof2"],
            dv1: info.data["dv1"],
            dvGA: info.data["dvGA"],
            dv2: info.data["dv2"]
        }

        setPorkChopData2D(null)
        setPorkChopData3D(data)
    }
    
    react.useEffect(() =>
    {
        const rmRI = globalThis.window.callback.onReceivedInfo((info: WebSocketInfo) =>
        {
            if (info.source === "interplanetary" && info.data != undefined)
            {
                if (info.data["dvGA"] === undefined)
                {
                    processData2D(info)
                }
                else
                {
                    processData3D(info)
                }
            }
            else if (info.source === "interplanetary" && info.data == undefined)
            {
                if (porkChopData2D !== null) setPorkChopData2D(null)
                if (porkChopData3D !== null) setPorkChopData3D(null)
            }
        })

        return () => { rmRI() }
    }, [])

    // --- RENDERING ---

    return (
        <div className="flex flex-col h-full w-full bg-neutral-800 text-neutral-100">

            <div className="flex flex-1 overflow-hidden">

                <div className={`${hideLeftBar ? "w-18" : "w-80"} border-r border-neutral-700 p-4 overflow-y-auto`}>

                    <InterplanetaryLeftBar
                        onBodies={(departure: string, flyby: string, arrival: string) =>
                        {
                            setDepartureBody(departure)
                            setFlybyBody(flyby)
                            setArrivalBody(arrival)
                        }}
                        onHide={(hide: boolean) => setHideLeftBar(hide)} />

                </div>

                <div className="flex-1 p-4 overflow-auto flex items-center justify-center">
                    
                    <InterplanetaryMainPlot
                        porkChopData2D={porkChopData2D}
                        porkChopData3D={porkChopData3D}
                        onSelect={setSelected}
                    />

                </div>

                <div className={`${hideRightBar ? "w-18" : "w-80"} border-l border-neutral-700 p-4 overflow-y-auto`}>

                    <InterplanetaryRightBar
                        departureBody={departureBody.toLocaleUpperCase()}
                        flybyBody={flybyBody.toLocaleUpperCase()}
                        arrivalBody={arrivalBody.toLocaleUpperCase()}
                        info={selected}
                        onHide={(hide: boolean) => setHideRightBar(hide)}
                    />

                </div>

            </div>
        </div>
    )
}