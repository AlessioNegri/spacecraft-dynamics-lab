import * as react from "react"
import * as Form from "@radix-ui/react-form"

import type { OptionProps } from "@renderer/components/dialogs/FormSelect"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import FormInput from "@renderer/components/dialogs/FormInput"
import FormSelect from "@renderer/components/dialogs/FormSelect"
import GlbViewer from "@renderer/components/common/GlbViewer"
import ErrorText from "@renderer/components/dialogs/ErrorText"

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
    style:
    {
        width: 1,
        color: "#FFFFFF"
    },
    image: null,
    model: ""
}

const defaultModel: IGlbModel =
{
    name: "",
    scale: 1,
    minimumPixelSize: 1,
    maximumScale: 1
}

interface Props
{
    item: IDbSpacecraftItem | null
    edit: boolean // ? True => edit dialog - False => add dialog
    opened: boolean
    setOpened: (opened: boolean) => void
    onOk: () => void
}

/** @function SpacecraftDialog */
export default function SpacecraftDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [form, setForm] = react.useState<ISpacecraftForm>(defaultSpacecraft)

    const [errors, setErrors] = react.useState<Record<string, string>>({})
    
    const [preview, setPreview] = react.useState<string | null>(null)

    const [models, setModels] = react.useState<IGlbModel[]>([])

    const [options, setOptions] = react.useState<OptionProps[]>([])
    
    const [selectedModel, setSelectedModel] = react.useState<IGlbModel>(defaultModel)

    const [axiosError, setAxiosError] = react.useState<string>("")

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

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
                style:
                {
                    width: Number(props.item!.style.width),
                    color: String(props.item!.style.color)
                },
                image: null,
                model: String(props.item!.model)
            }

            setForm(spacecraft)
        }
        else
        {
            setForm(defaultSpacecraft)
        }

        fetch("./models/models.json")
        .then(res => res.json())
        .then((models: IGlbModel[]) =>
        {
            setModels(models)

            const options: OptionProps[] = [ { name: "Choose a model", value: "" },
                                                    ...models.map(m => ({ name: m.name, value: m.name }))]

            setOptions(options)

            if (props.edit) setSelectedModel(models.find(m => m.name === props.item!.model) || defaultModel)
        })
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

        if (Number(form.style.width) < 0)   newErrors.width = "Width must be a positive number"

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

        if (name in form.style)
        {
            setForm({ ...form, style: { ...form.style, [name]: value } })

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

        data.append("style", JSON.stringify(
        {
            width: form.style.width,
            color: form.style.color
        }))

        if (form.image) data.append("image", form.image)
        
        data.append("model", selectedModel.name)

        try
        {
            let response: any

            if (props.edit)
            {
                response = await http.api.post(`/spacecraft/update/${form._id!}`, data)
            }
            else
            {
                response = await http.api.post("/spacecraft/insert", data)
            }

            globalThis.window.api.info(`[${import.meta.url}] ${JSON.stringify(response.data)}`)

            props.onOk()
            
            props.setOpened(false)
        }
        catch (err)
        {
            const message: string | null = http.checkError(import.meta.url, err)

            if (message) setAxiosError(message)
        }
    }

    // --- RENDERING ---

    return (
        <DialogRUI
            title={`${props.edit ? "Edit" : "Add"} Spacecraft`}
            button="Save"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
        >

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="flex flex-col gap-2"
            >

                <FormInput
                    label="Name"
                    type="text"
                    name="name"
                    value={form.name}
                    error={errors.name}
                    placeholder="e.g. Voyager 1"
                    setValue={handleChange}
                />

                <h3 className="text-lg font-semibold">Ballistic / Mass</h3>

                <FormInput
                    label="Mass (kg)"
                    type="number"
                    name="mass"
                    value={form.mass}
                    error={errors.mass}
                    placeholder="e.g. 825"
                    setValue={handleChange}
                />

                <h3 className="text-lg font-semibold">Orbit</h3>

                <div className="grid grid-cols-2 gap-4">

                    <FormInput
                        label="Semimajor Axis (km)"
                        type="number"
                        name="sma"
                        value={form.orbit.sma}
                        error={errors.sma}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="Eccentricity"
                        type="number"
                        name="ecc"
                        value={form.orbit.ecc}
                        error={errors.ecc}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="Inclination (deg)"
                        type="number"
                        name="inc"
                        value={form.orbit.inc}
                        error={errors.inc}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="Right Ascension of Ascending Node (deg)"
                        type="number"
                        name="raan"
                        value={form.orbit.raan}
                        error={errors.raan}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="Argument of Periapsis (deg)"
                        type="number"
                        name="aop"
                        value={form.orbit.aop}
                        error={errors.aop}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="True Anomaly (deg)"
                        type="number"
                        name="tan"
                        value={form.orbit.tan}
                        error={errors.tan}
                        setValue={handleChange}
                    />

                </div>

                <h3 className="text-lg font-semibold">Style</h3>

                <div className="grid grid-cols-2 gap-4">

                    <FormInput
                        label="Line Width (px)"
                        type="number"
                        name="width"
                        value={form.style.width}
                        error={errors.width}
                        setValue={handleChange}
                    />

                    <FormInput
                        label="Line Color"
                        type="color"
                        name="color"
                        value={form.style.color}
                        error={errors.color}
                        setValue={handleChange}
                    />

                </div>

                <FormInput
                    label="Image"
                    type="file"
                    name="image"
                    value={form.image}
                    setValue={handleChange}
                />

            {
                preview &&
                (
                    <div className="mt-3 border-neutral-400 border-2 rounded flex items-center justify-center">

                        <img src={preview} alt="Preview" className="object-cover" />

                    </div>
                )
            }


            <FormSelect
                label="Model"
                name="model"
                value={selectedModel.name}
                setValue={e => 
                {
                    const name: string = e.target.value

                    const model: IGlbModel | undefined = models.find(m => m.name === name)

                    setSelectedModel(model ?? defaultModel)
                }}
                options={options}
            />

            <div className="flex w-full h-64">
                
                <GlbViewer model={selectedModel.name} scale={selectedModel.scale} />
                
            </div>

            { axiosError && <ErrorText text={axiosError} /> }

            </Form.Root>
        
        </DialogRUI>
    )
}
