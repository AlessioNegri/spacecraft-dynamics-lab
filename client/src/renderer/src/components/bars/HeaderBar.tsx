import * as react from "react"

interface HeaderBarProps
{
    title: string
}

/** @function HeaderBar */
export default function HeaderBar(props: Readonly<HeaderBarProps>): react.JSX.Element
{
    // --- USE STATE ---
    
    const [time, setTime] = react.useState<string>("")

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const update = () =>
        {
            const now: Date = new Date()

            const date: string = now.toLocaleDateString("it-IT")

            const time: string = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })

            setTime(`${date} ${time}`)
        }

        update()

        const interval = setInterval(update, 1000)

        return () => clearInterval(interval)
    }, [])

    // --- RENDERING ---

    return (
        <div className="flex items-center justify-between px-6 py-3 border-b border-neutral-700 bg-neutral-800">

                <h1 className="text-xl font-semibold capitalize">{props.title}</h1>

                <div
                    className="w-80 px-2 py-1 bg-neutral-950 text-green-300 rounded-lg shadow-md flex items-start 
                                justify-start text-xl tracking-widest"
                    style={{ fontFamily: "Orbitron" }} >
                
                    {time}

                </div>


            </div>
    )
}