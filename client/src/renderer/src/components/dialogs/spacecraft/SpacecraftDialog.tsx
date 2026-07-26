import * as react from "react"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import GlbViewer from "@renderer/components/common/GlbViewer"
import ErrorText from "@renderer/components/dialogs/ErrorText"

import InputField from "@renderer/components/dialogs/InputField"

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
    description: "",
    scale: 1,
    minimumPixelSize: 1,
    maximumScale: 1
}

/**
 * @description Retrieve the size of the GLB model
 * 
 * @param url GLB model URL
 * @returns GLB model size
 */
async function getGlbFileSize(url: string): Promise<number>
{
    if (url !== "")
    {
        return globalThis.window.api.getFileSize(url)
    }

    return 0
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
    
    const [preview, setPreview] = react.useState<string | null>(null)

    const [models, setModels] = react.useState<IGlbModel[]>([])

    const [groups, setGroups] = react.useState<Array<{ caption: string; options: Array<{ label: string; value: string | number }> }>>([])
    
    const [selectedModel, setSelectedModel] = react.useState<IGlbModel>(defaultModel)

    const [selectedModelSize, setSelectedModelSize] = react.useState<number>(0)

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

            // * Group models by first letter

            const grouped: Record<string, Array<{ label: string; value: string }>> =
            models.reduce((acc, model) =>
            {
                const letter: string = model.description[0].toUpperCase()

                if (!acc[letter]) acc[letter] = []

                acc[letter].push({ label: model.description, value: model.name })

                return acc
            }, {} as Record<string, Array<{ label: string; value: string }>>);

            // * Convert to your Select groups format

            const groups = Object.entries(grouped).map(([letter, items]) => (
            {
                caption: letter,
                options: items
            }))

            setGroups(groups)
        })
    }, [])

    react.useEffect(() =>
    {
        if (props.edit)
        {
            setSelectedModel(models.find(m => m.name === props.item!.model) || defaultModel)
        }
    }, [props.edit, models])

    react.useEffect(() =>
    {
        if (!selectedModel) return

        async function loadSize()
        {
            setSelectedModelSize(await getGlbFileSize(selectedModel.name))
        }

        loadSize()

    }, [selectedModel])

    // --- FORM ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        if (e.target instanceof HTMLInputElement && e.target.type === "file")
        {
            const { name, files } = e.target

            if (name === "image" && files)
            {
                console.log(files)
                setForm({ ...form, image: files[0] })

                setPreview(URL.createObjectURL(files[0]))
            }
        }
        else
        {
            const { name, value } = e.target

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
    }

    const handleSubmit = async (e: React.FormEvent) =>
    {
        e.preventDefault()

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

                <InputField
                    label="Name"
                    type="text"
                    name="name"
                    value={form.name}
                    placeholder="e.g. Voyager 1"
                    showSides={false}
                    onChange={handleChange}
                />

                <h3 className="text-lg font-semibold my-4">Ballistic / Mass</h3>

                <InputField
                    label="Mass"
                    type="number"
                    name="mass"
                    symbol="m"
                    unit="kg"
                    value={form.mass}
                    min={0}
                    onChange={handleChange}
                />

                <h3 className="text-lg font-semibold my-4">Orbit</h3>

                <div className="grid grid-cols-2 gap-4">

                    <InputField
                        label="Semimajor Axis"
                        type="text"
                        name="sma"
                        symbol="a"
                        unit="km"
                        value={String(form.orbit.sma)}
                        pattern="^(?!0$).*"
                        onChange={handleChange}
                    />

                    <InputField
                        label="Eccentricity"
                        type="number"
                        name="ecc"
                        symbol="e"
                        value={form.orbit.ecc}
                        min={0}
                        onChange={handleChange}
                    />

                    <InputField
                        label="Inclination"
                        type="number"
                        name="inc"
                        symbol="i"
                        unit="deg"
                        value={form.orbit.inc}
                        min={0}
                        max={180}
                        onChange={handleChange}
                    />

                    <InputField
                        label="Right Ascension of Ascending Node"
                        type="number"
                        name="raan"
                        symbol="\Omega"
                        unit="deg"
                        value={form.orbit.raan}
                        min={-360}
                        max={360}
                        onChange={handleChange}
                    />

                    <InputField
                        label="Argument of Periapsis"
                        type="number"
                        name="aop"
                        symbol="\omega"
                        unit="deg"
                        value={form.orbit.aop}
                        min={-360}
                        max={360}
                        onChange={handleChange}
                    />

                    <InputField
                        label="True Anomaly (deg)"
                        type="number"
                        name="tan"
                        symbol="\theta"
                        unit="deg"
                        value={form.orbit.tan}
                        min={-360}
                        max={360}
                        onChange={handleChange}
                    />

                </div>

                <h3 className="text-lg font-semibold my-4">Style</h3>

                <div className="grid grid-cols-2 gap-4">

                    <InputField
                        label="Line Width"
                        type="number"
                        name="width"
                        unit="px"
                        value={form.style.width}
                        min={1}
                        onChange={handleChange}
                    />

                    <InputField
                        label="Line Color"
                        type="color"
                        name="color"
                        value={form.style.color}
                        onChange={handleChange}
                    />

                </div>

                <h3 className="text-lg font-semibold my-4">Media</h3>

                <InputField
                    label={`Image - ${((form.image?.size ?? 0) / 1024).toFixed(0)} KB`}
                    type="file"
                    name="image"
                    value={""}
                    onChange={handleChange}
                />

            {
                preview &&
                (
                    <div className="mt-3 border-neutral-400 border-2 rounded flex items-center justify-center">

                        <img src={preview} alt="Preview" className="object-cover" />

                    </div>
                )
            }

            <div className="flex items-end gap-4">

                <InputField
                    className="flex-1"
                    name="model"
                    label="Model"
                    type="select"
                    value={selectedModel.name}
                    onSelectChange={(value: string) =>
                    {
                        const model: IGlbModel | undefined = models.find(m => m.name === value)
                        
                        setSelectedModel(model ?? defaultModel)
                    }}
                    groups={groups}
                />

                <Themes.Badge color="grass" size="3" style={{ fontFamily: "Oxanium" }}>
                    {(selectedModelSize / 1024).toFixed(2) + " KB"}
                </Themes.Badge>

            </div>

            <div className="flex w-full h-64">
                
                <GlbViewer model={selectedModel.name} scale={selectedModel.scale} />
                
            </div>

            { axiosError && <ErrorText text={axiosError} /> }

            </Form.Root>
        
        </DialogRUI>
    )
}
