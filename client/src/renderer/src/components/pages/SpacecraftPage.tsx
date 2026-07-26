import * as react from "react"
import * as iconify from "@iconify/react"
import * as katex from "react-katex"
import * as Themes from "@radix-ui/themes"

import "@google/model-viewer"

import http from "@renderer/common/http"
import utility from "@renderer/common/utility"

// import GlbViewer from "@renderer/components/common/GlbViewer"
import SpacecraftDialog from "@renderer/components/dialogs/spacecraft/SpacecraftDialog"
import DeleteSpacecraftDialog from "@renderer/components/dialogs/spacecraft/DeleteSpacecraftDialog"

/** @function SpacecraftPage */
export default function SpacecraftPage(): react.JSX.Element
{
    // --- HTTP ---

    const getItems = async () =>
    {
        try
        {
            const res = await http.api.get<IDbSpacecraftItem[]>("/spacecraft/items")

            setItems(res.data)

            if (res.data.length > 0) setSelected(res.data[0])
        }
        catch (err)
        {
            const message: string | null = http.checkError(import.meta.url, err)
            
            if (message) globalThis.window.api.error(`[${import.meta.url}] ${message}`)
        }
    }

    // --- USE STATE ---

    const [openAddEdit, setOpenAddEdit] = react.useState<boolean>(false)

    const [openDelete, setOpenDelete] = react.useState<boolean>(false)

    const [edit, setEdit] = react.useState<boolean>(false)

    const [models, setModels] = react.useState<IGlbModel[]>([])

    const [items, setItems] = react.useState<IDbSpacecraftItem[]>([])

    const [selected, setSelected] = react.useState<IDbSpacecraftItem | null>(null)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        // * Retrieve GLB models

        fetch("./models/models.json").then(res => res.json()).then(setModels)

        // * Retrieve spacecraft items
        
        getItems()
    }, [])

    // --- RENDERING ---

    return (
        <div className="flex w-full h-full relative bg-neutral-800">
            
            {/* List */}
            
            <div className="w-1/6 bg-orange-300/5 text-white overflow-y-auto border-r border-neutral-700 p-2
                            custom-scrollbar">

                <h1 className="text-center border-neutral-400 border-b-2 mb-2 pb-2 uppercase font-bold">
                    Spacecraft List
                </h1>
                
            {
                items.map((item: IDbSpacecraftItem) => (
                    <button
                        key={item._id}
                        onClick={() => setSelected(item)}
                        className={utility.cn(
                            "w-full text-left px-4 py-2 hover:bg-neutral-600 transition rounded cursor-pointer",
                            "transition-colors duration-500",
                            selected?._id === item._id ? "bg-orange-300/25 text-orange-300 font-bold" : "")
                            }
                    >

                        {item.name}

                    </button>
                ))
            }

            </div>

            {/* Details */}

            <div className="w-5/6 p-6 overflow-y-auto overflow-x-auto custom-scrollbar mt-15 mb-4">

            {
                selected
                ?
                <SpacecraftDetails item={selected} models={models} />
                :
                <div className="text-neutral-400 text-4xl">Add a spacecraft</div>
            }

            </div>

            {/* Actions */}

            <div className="absolute top-2 left-1/2 -translate-x-1/2 flex gap-2">

                <Themes.Button
                    color="green"
                    variant="outline"
                    onClick={() => { setOpenAddEdit(true); setEdit(false) }}
                >
                    <iconify.Icon icon="mdi:add" height={20} />
                    Add SC
                </Themes.Button>

            {
                selected &&
                (
                    <react.Fragment>

                        <Themes.Button
                            color="blue"
                            variant="outline"
                            onClick={() => { setOpenAddEdit(true); setEdit(true) }}
                        >
                            <iconify.Icon icon="mdi:edit" height={20} />
                            Edit SC
                        </Themes.Button>

                        <Themes.Button
                            color="red"
                            variant="outline"
                            onClick={() => { setOpenDelete(true) }}
                        >
                            <iconify.Icon icon="mdi:remove" height={20} />
                            Delete SC
                        </Themes.Button>

                    </react.Fragment>
                )
            }

            </div>

            {/* Dialogs */}

            {
                openAddEdit &&
                <SpacecraftDialog
                    item={selected}
                    edit={edit}
                    opened={openAddEdit}
                    setOpened={(opened: boolean) => setOpenAddEdit(opened)}
                    onOk={() => { getItems() }}
                />
            }

            {
                openDelete &&
                <DeleteSpacecraftDialog
                    id={selected!._id!}
                    name={selected!.name}
                    opened={openDelete}
                    setOpened={(opened: boolean) => setOpenDelete(opened)}
                    onOk={() => { getItems() }}
                />
            }

        </div>
    )
}

interface SectionItem
{
    name: string
    value: number | string
    unit: string
}

/**
 * @description Fill details of the selected spacecraft
 * 
 * @param item Selected spacecraft
 * @param models Available 3D models
 * @returns JSX
 */
function SpacecraftDetails({ item }: Readonly<{ item: IDbSpacecraftItem, models: IGlbModel[] }>): react.JSX.Element
{
    const ballisticMassItems: SectionItem[] =
    [
        { name: "Mass", value: item.mass, unit: "kg" }
    ]

    const orbitItems: SectionItem[] =
    [
        { name: "Semi-Major Axis", value: item.orbit.sma, unit: "km" },
        { name: "Eccentricity", value: item.orbit.ecc, unit: "" },
        { name: "Inclination", value: item.orbit.inc, unit: "deg" },
        { name: "Right Ascension of Ascending Node", value: item.orbit.raan, unit: "deg" },
        { name: "Argument of Periapsis", value: item.orbit.aop, unit: "deg" },
        { name: "True Anomaly", value: item.orbit.tan, unit: "deg" }
    ]

    const styleItems: SectionItem[] =
    [
        { name: "Width", value: item.style.width, unit: "px" },
        { name: "Color", value: item.style.color, unit: "" }
    ]

    return (
        <div className="text-neutral-300 space-y-8 w-full">

            {/* <h1 className="text-3xl font-bold text-orange-300 border-b-2 mb-2">{item.name}</h1> */}

            <div className="flex gap-4">

                <div className="w-1/2 flex flex-col gap-4 min-w-150">

                    <Section title="Ballistic / Mass" items={ballisticMassItems} />

                    <Section title="Orbit" items={orbitItems} />

                    <Section title="Style" items={styleItems} />

                    {/* Image */}

                    {
                        item.image
                        ?
                        <img
                            src={item.image ? `data:image/png;base64,${item.image}` : undefined}
                            alt={item.name}
                            className="m-auto w-150 h-75 rounded border-2 border-neutral-400"
                        />
                        :
                        <div className="border-neutral-600 border-2 rounded w-full flex items-center justify-center text-gray-500">
                            Image preview not available
                        </div>
                    }

                </div>

                {/* 3D Model */}

                {
                    item.model
                    ?
                    <div className="w-1/2">

                        {/* <GlbViewer
                            model={item.model}
                            scale={models.find(m => m.name === item.model)?.scale ?? 1}
                        /> */}

                        <div className="border-neutral-400 border-2 rounded w-full h-full bg-neutral-500">

                            <model-viewer
                                src={`./models/${item.model}.glb`}
                                alt="GLB model"
                                camera-controls
                                auto-rotate
                                shadow-intensity="5"
                                environment-image="neutral"
                                camera-orbit="0deg 65deg 10m"
                                field-of-view="35deg"
                                style={{ width: "100%", height: "100%" }}
                            />

                        </div>

                    </div>
                    :
                    <div className="border-neutral-600 border-2 rounded w-1/2 flex items-center justify-center text-center text-gray-500">
                        Model preview not available
                    </div>
                }

            </div>

        </div>
    )
}

interface SectionProps
{
    title: string
    items: SectionItem[]
}

/** @function Section */
function Section(props: Readonly<SectionProps>): react.JSX.Element
{
    const isColor = (value: string): boolean =>
    {
        const s: CSSStyleDeclaration = new Option().style

        s.color = value

        return s.color !== ''
    }

    return (
        <section className="space-y-2">

            <h2 className="text-2xl font-semibold text-center text-orange-300">{props.title}</h2>

            <div className="bg-neutral-700/40 p-4 rounded-lg shadow-inner text-neutral-100">

                <div className="grid grid-cols-[auto_1fr_auto] auto-cols-fr gap-10 items-center">

                {
                    props.items.map((item: SectionItem) => 
                        <react.Fragment key={item.name}>
                        
                            <span className="font-semibold text-left">{item.name}</span>
        
                        {
                            isColor(String(item.value))
                            ?
                            <div className="h-6 rounded" style={{ backgroundColor: String(item.value) }}/>
                            :
                            <span
                                className="text-left border-b border-neutral-600 p-1 text-neutral-300"
                                style={{ fontFamily: "Oxanium" }}
                            >
                                {item.value}
                            </span>
                        }

                            <span className="text-right text-orange-300 font-semibold">
                                <katex.InlineMath math={String.raw`{${item.unit}}`} />
                            </span>

                        </react.Fragment>
                    )
                    
                }

                </div>

            </div>

        </section>
    )
}
