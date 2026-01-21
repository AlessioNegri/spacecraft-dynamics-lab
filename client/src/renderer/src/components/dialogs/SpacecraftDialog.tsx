import * as react from "react"

import api from "@renderer/common/api"
import checkError from "@renderer/common/error"

import Dialog from "./Dialog"
import FormInput from "./FormInput"

const defaultSpacecraft: ISpacecraftForm =
{
    _id: undefined,
    name: "",
    mass: 0,
    orbit:
    {
        sma: 0,
        ecc: 0,
        inc: 0,
        raan: 0,
        aop: 0,
        tan: 0
    },
    image: null
}

interface SpacecraftDialogProps
{
    item: IDbSpacecraftItem | null
    edit: boolean // ? True => edit dialog - False => add dialog
    onClose: () => void
    onOk: () => void
}

/** @function SpacecraftDialog */
export default function SpacecraftDialog(props: Readonly<SpacecraftDialogProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [form, setForm] = react.useState<ISpacecraftForm>(defaultSpacecraft)

    const [errors, setErrors] = react.useState<Record<string, string>>({})
    
    const [preview, setPreview] = react.useState<string | null>(null)

    const [axiosError, setAxiosError] = react.useState<string>("")

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (props.edit)
        {
            const spacecraft: ISpacecraftForm =
            {
                _id: props.item!._id,
                name: props.item!.name,
                mass: Number(props.item!.mass),
                orbit:
                {
                    sma: Number(props.item!.orbit.sma),
                    ecc: Number(props.item!.orbit.ecc),
                    inc: Number(props.item!.orbit.inc),
                    raan: Number(props.item!.orbit.raan),
                    aop: Number(props.item!.orbit.aop),
                    tan: Number(props.item!.orbit.tan)
                },
                image: null
            }

            setForm(spacecraft)
        }
        else
        {
            setForm(defaultSpacecraft)
        }
    }, [])

    // --- FORM ---

    const validAngle = (angle: number) => { return angle >= 0 && angle <= 360 }

    const validate = () =>
    {
        const newErrors: Record<string, string> = {}

        if (!form.name.trim()) newErrors.name = "Name is required"

        if (Number(form.mass) <= 0)         newErrors.mass  = "Mass must be a positive number"
        if (Number(form.orbit.sma) === 0)   newErrors.sma   = "Semi-Major Axis must be different from 0"
        if (Number(form.orbit.ecc) < 0)     newErrors.ecc   = "Eccentricity must be a non negative number"
        
        if (!validAngle(form.orbit.inc))    newErrors.inc   = "Inclination must be in rage [0°, 360°]"
        if (!validAngle(form.orbit.raan))   newErrors.raan  = "Right Ascension Ascending Node must be in rage [0°, 360°]"
        if (!validAngle(form.orbit.aop))    newErrors.aop   = "Argument Periapsis must be in rage [0°, 360°]"
        if (!validAngle(form.orbit.tan))    newErrors.tan   = "True Anomaly must be in rage [0°, 360°]"

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    {
        const { name, value, files } = e.target

        if (name === "image" && files)
        {
            setForm({ ...form, image: files[0] })

            setPreview(URL.createObjectURL(files[0]))

            return
        }

        if (name in form.orbit)
        {
            setForm({ ...form, orbit: { ...form.orbit, [name]: value } })

            return
        }

        setForm({ ...form, [name]: value })
    }

    const handleSubmit = async (e: React.FormEvent) =>
    {
        e.preventDefault()

        if (!validate()) return

        const data = new FormData()

        data.append("name", form.name)
        data.append("mass", String(form.mass))

        data.append("orbit", JSON.stringify(
        {
            sma: form.orbit.sma,
            ecc: form.orbit.ecc,
            inc: form.orbit.inc,
            raan: form.orbit.raan,
            aop: form.orbit.aop,
            tan: form.orbit.tan
        }))

        if (form.image) data.append("image", form.image)

        try
        {
            let response: any

            if (props.edit)
            {
                response = await api.post(`/spacecraft/update/${form._id!}`, data)
            }
            else
            {
                response = await api.post("/spacecraft/insert", data)
            }

            globalThis.window.api.info(`[${import.meta.url}] ${JSON.stringify(response.data)}`)

            props.onOk()
            props.onClose()
        }
        catch (err)
        {
            const message: string | null = checkError(import.meta.url, err)

            if (message) setAxiosError(message)
        }
    }

    // --- RENDERING ---

    return (
        <Dialog title={`${props.edit ? "Edit" : "Add"} Spacecraft`} onClose={() => { props.onClose() }} >

            <form
                onSubmit={handleSubmit}
                className="mx-auto p-6 bg-stone-800 text-gray-100 rounded-lg shadow-lg space-y-6">

                <FormInput
                    label="Name"
                    type="text"
                    name="name"
                    value={form.name}
                    error={errors.name}
                    placeholder="e.g. Voyager 1"
                    setValue={handleChange} />

                <FormInput
                    label="Mass (kg)"
                    type="number"
                    name="mass"
                    value={form.mass}
                    error={errors.mass}
                    placeholder="e.g. 825"
                    setValue={handleChange} />
                
                <div className="space-y-3">

                    <h3 className="text-lg font-semibold">Orbital Elements</h3>

                    <div className="grid grid-cols-2 gap-4">

                        <FormInput
                            label="Semi-Major Axis (km)"
                            type="number"
                            name="sma"
                            value={form.orbit.sma}
                            error={errors.sma}
                            setValue={handleChange} />

                        <FormInput
                            label="Eccentricity"
                            type="number"
                            name="ecc"
                            value={form.orbit.ecc}
                            error={errors.ecc}
                            setValue={handleChange} />

                        <FormInput
                            label="Inclination (°)"
                            type="number"
                            name="inc"
                            value={form.orbit.inc}
                            error={errors.inc}
                            setValue={handleChange} />

                        <FormInput
                            label="Right Ascension Ascending Node (°)"
                            type="number"
                            name="raan"
                            value={form.orbit.raan}
                            error={errors.raan}
                            setValue={handleChange} />

                        <FormInput
                            label="Argument Periapsis (°)"
                            type="number"
                            name="aop"
                            value={form.orbit.aop}
                            error={errors.aop}
                            setValue={handleChange} />

                        <FormInput
                            label="True Anomaly (°)"
                            type="number"
                            name="tan"
                            value={form.orbit.tan}
                            error={errors.tan}
                            setValue={handleChange} />

                    </div>

                </div>

                <FormInput
                    label="Image"
                    type="file"
                    name="image"
                    value={form.image}
                    setValue={handleChange} />

            {
                preview &&
                (
                    <div className="mt-3">

                        <img src={preview} alt="Preview" className="w-40 h-40 object-cover" />

                    </div>
                )
            }

                <button
                    type="submit"
                    className="w-full py-2 bg-blue-800 hover:bg-blue-700 rounded font-semibold transition">

                    Save

                </button>

            {
                axiosError && <p className="text-red-400 text-sm">{axiosError}</p>
            }

            </form>

        </Dialog>
    )
}