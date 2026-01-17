import * as react from "react"

/** @function Shortcut */
export default function Shortcut(keys: string, callback: () => void): void
{
    // --- GENERIC ---

    /**
     * @description Call the callback on matching keyboard sequence
     * 
     * @param e Keyboard event
     */
    function handler(e: KeyboardEvent): void
    {
        const parts: string[] = []

        if (e.ctrlKey)  parts.push("CTRL")
        if (e.shiftKey) parts.push("SHIFT")
        if (e.altKey)   parts.push("ALT")

        parts.push(e.key.toUpperCase())

        const combo: string = parts.join("+")

        if (combo === keys.toUpperCase())
        {
            e.preventDefault()

            callback()
        }
    }

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        globalThis.window.addEventListener("keydown", handler)

        return () => globalThis.window.removeEventListener("keydown", handler)
    }, [keys, callback])
}