import * as react from 'react'

/** @function useManeuverState */
export default function useManeuverState<T>(initial: T, onChange: (data: T) => void)
{
    // --- USE STATE ---

    const [data, setData] = react.useState<T>(initial)

    // --- USE EFFECT ---

    react.useEffect(() => { onChange(data) }, [])

    // --- HANDLE ---

    const handleChange = (e: react.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        const updated = { ...data, [name]: value } as T

        setData(updated)

        onChange(updated)
    }

    return { data, handleChange }
}
