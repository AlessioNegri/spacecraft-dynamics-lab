import * as react from "react"

/** @function LogStore */
export default function LogStore(): [LogEntry[], react.Dispatch<react.SetStateAction<LogEntry[]>>]
{
    // --- USE STATE ---

    const [logs, setLogs] = react.useState<LogEntry[]>([])

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmL = globalThis.window.callback.onLog((entry: LogEntry) => setLogs((prev) => [...prev, entry]))

        return () => { rmL() }
    }, [])

    return [logs, setLogs]
}