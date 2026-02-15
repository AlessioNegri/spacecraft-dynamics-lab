import * as react from "react"
import * as iconify from "@iconify/react"

import http from "@renderer/common/http"

import Tooltip from "../Tooltip"
import SpacecraftDialog from "../dialogs/SpacecraftDialog"
import DeleteSpacecraftDialog from "../dialogs/DeleteSpacecraftDialog"
import GlbViewer from "../common/GlbViewer"

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
            
            <div className="w-64 bg-neutral-800 text-white overflow-y-auto border-r border-neutral-700 p-2
                            overflow-auto custom-scrollbar">

                <h1 className="text-center border-b-2 mb-2 uppercase">Spacecraft List</h1>
                
            {
                items.map((item: IDbSpacecraftItem) => (
                    <button
                        key={item._id}
                        onClick={() => setSelected(item)}
                        className={`w-full text-left px-4 py-2 hover:bg-neutral-600 transition rounded cursor-pointer
                            ${selected?._id === item._id ? "bg-orange-300/25 text-orange-300 font-bold" : ""}`}>

                        {item.name}

                    </button>
                ))
            }

            </div>

            {/* Details */}

            <div className="flex-1 p-6 overflow-auto custom-scrollbar flex justify-center mt-15 mb-4">

            {
                selected
                ?
                <SpacecraftDetails item={selected} models={models} />
                :
                <div className="text-neutral-400 text-4xl">Add a spacecraft</div>
            }

            </div>

            {/* Actions */}

            <div className="absolute top-2 right-4 flex">

                <Tooltip title="Add Spacecraft" side="bottom">

                    <iconify.Icon
                        icon={"mdi:add-box"}
                        width={40}
                        onClick={() => { setOpenAddEdit(true); setEdit(false) }}
                        className="text-green-300 hover:text-white cursor-pointer"
                    />

                </Tooltip>

            {
                selected &&
                (
                    <>

                        <Tooltip title="Edit Spacecraft" side="bottom">
                            
                            <iconify.Icon
                                icon={"mdi:edit-box"}
                                width={40}
                                onClick={() => { setOpenAddEdit(true); setEdit(true) }}
                                className="text-blue-300 hover:text-white cursor-pointer"
                            />

                        </Tooltip>

                        <Tooltip title="Delete Spacecraft" side="bottom">

                            <iconify.Icon
                                icon={"mdi:cancel-box"}
                                width={40}
                                onClick={() => setOpenDelete(true)}
                                className="text-red-300 hover:text-white cursor-pointer"
                            />

                        </Tooltip>

                    </>
                )
            }

            </div>

            {/* Dialogs */}

            {
                openAddEdit &&
                <SpacecraftDialog
                    item={selected}
                    edit={edit}
                    onClose={() => { setOpenAddEdit(false) }}
                    onOk={() => { getItems() }}
                />
            }

            {
                openDelete &&
                <DeleteSpacecraftDialog
                    id={selected!._id!}
                    name={selected!.name}
                    onClose={() => { setOpenDelete(false) }}
                    onOk={() => { getItems() }}
                />
            }

        </div>
    )
}

/**
 * @description Fill details of the selected spacecraft
 * 
 * @param item Selected spacecraft
 * @param models Available 3D models
 * @returns JSX
 */
function SpacecraftDetails({ item, models }: Readonly<{ item: IDbSpacecraftItem, models: IGlbModel[] }>): react.JSX.Element
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
        { name: "Right Ascension Ascending Node", value: item.orbit.raan, unit: "deg" },
        { name: "Argument Periapsis", value: item.orbit.aop, unit: "deg" },
        { name: "True Anomaly", value: item.orbit.tan, unit: "deg" }
    ]

    const styleItems: SectionItem[] =
    [
        { name: "Width", value: item.style.width, unit: "px" },
        { name: "Color", value: item.style.color, unit: "" }
    ]

    return (
        <div className="text-neutral-300 space-y-8">

            {/* <h1 className="text-3xl font-bold text-orange-300 border-b-2 mb-2">{item.name}</h1> */}

            <Section title="Ballistic / Mass" items={ballisticMassItems} />

            <Section title="Orbit" items={orbitItems} />

            <Section title="Style" items={styleItems} />

            <div className="flex gap-4 h-75 text-gray-500">

                {/* Image */}

                {
                    item.image
                    ?
                    <img
                        src={item.image ? `data:image/png;base64,${item.image}` : undefined}
                        alt={item.name}
                        className="w-1/2 rounded border-2 border-neutral-400"
                    />
                    :
                    <div className="border-neutral-600 border-2 rounded w-1/2 flex items-center justify-center">
                        Image preview not available
                    </div>
                }

                {/* 3D Model */}

                {
                    item.model
                    ?
                    <div className="w-1/2">

                        <GlbViewer
                            model={item.model}
                            scale={models.find(m => m.name === item.model)?.scale ?? 1} />

                    </div>
                    :
                    <div className="border-neutral-600 border-4 rounded w-1/2 flex items-center justify-center">
                        Model preview not available
                    </div>
                }

            </div>

        </div>
    )
}

interface SectionItem
{
    name: string
    value: number | string
    unit: string
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
        const s = new Option().style

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
                        <>
                        
                            <span className="font-semibold text-left">{item.name}</span>
        
                        {
                            isColor(String(item.value))
                            ?
                            <div className="h-6 rounded" style={{ backgroundColor: String(item.value) }}/>
                            :
                            <span className="text-left border-b border-neutral-600 p-1">{item.value}</span>
                        }

                            <span className="text-right text-orange-300 font-semibold">{item.unit}</span>

                        </>
                    )
                    
                }

                </div>

            </div>

        </section>
    )
}