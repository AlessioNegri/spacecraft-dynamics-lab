import * as react from "react"
import * as iconify from "@iconify/react"

import api from "@renderer/common/api"
import checkError from "@renderer/common/error"

import Tooltip from "../Tooltip"
import SpacecraftDialog from "../dialogs/SpacecraftDialog"
import DeleteSpacecraftDialog from "../dialogs/DeleteSpacecraftDialog"

/** @function SpacecraftPage */
export default function SpacecraftPage(): react.JSX.Element
{
    // --- USE STATE ---

    const [open, setOpen] = react.useState<boolean>(false)

    const [openDelete, setOpenDelete] = react.useState<boolean>(false)

    const [edit, setEdit] = react.useState<boolean>(false)

    const [items, setItems] = react.useState<IDbSpacecraftItem[]>([])

    const [selected, setSelected] = react.useState<IDbSpacecraftItem | null>(null)

    // --- USE EFFECT ---

    const getItems = async () =>
    {
        try
        {
            const res = await api.get<IDbSpacecraftItem[]>("/spacecraft/items")

            setItems(res.data)

            if (res.data.length > 0) setSelected(res.data[0])
        }
        catch (err)
        {
            const message: string | null = checkError(import.meta.url, err)
            
            if (message) globalThis.window.api.error(`[${import.meta.url}] ${message}`)
        }
    }

    react.useEffect(() => { getItems() }, [])

    // --- RENDERING ---

    return (
        <div className="flex w-full h-full relative">
            
            {/* List */}
            
            <div className="w-64 bg-stone-800 text-white overflow-y-auto border-4 border-stone-600 p-2 rounded">

                <h1 className="text-center border-b-2 mb-2 uppercase">Spacecraft List</h1>
                
            {
                items.map((item: IDbSpacecraftItem) => (
                    <button
                        key={item._id}
                        onClick={() => setSelected(item)}
                        className={`w-full text-left px-4 py-2 hover:bg-stone-600 transition rounded cursor-pointer
                            ${selected?._id === item._id ? "bg-orange-300/25" : ""}`}>

                        {item.name}

                    </button>
                ))
            }

            </div>

            {/* Details */}

            <div className="flex-1 p-6 overflow-auto">

            {
                selected
                ?
                <SpacecraftDetails item={selected} />
                :
                <div className="text-stone-400">Add a spacecraft</div>
            }

            </div>

            {/* Open dialog */}

            <div className="absolute top-2 right-4 flex">

                <Tooltip title="Add Spacecraft" side="bottom">

                    <iconify.Icon
                        icon={"mdi:add-box"}
                        width={40}
                        onClick={() => { setOpen(true); setEdit(false) }}
                        className="text-green-300 hover:text-white cursor-pointer" />

                </Tooltip>

            {
                selected &&
                (
                    <>

                        <Tooltip title="Edit Spacecraft" side="bottom">
                            
                            <iconify.Icon
                                icon={"mdi:edit-box"}
                                width={40}
                                onClick={() => { setOpen(true); setEdit(true) }}
                                className="text-blue-300 hover:text-white cursor-pointer" />

                        </Tooltip>

                        <Tooltip title="Delete Spacecraft" side="bottom">

                            <iconify.Icon
                                icon={"mdi:cancel-box"}
                                width={40}
                                onClick={() => setOpenDelete(true)}
                                className="text-red-300 hover:text-white cursor-pointer" />

                        </Tooltip>

                    </>
                )
            }

            </div>

            {/* Dialogs */}

            {
                open &&
                <SpacecraftDialog
                    item={selected}
                    edit={edit}
                    onClose={() => { setOpen(false) }}
                    onOk={() => { getItems() }} />
            }

            {
                openDelete &&
                <DeleteSpacecraftDialog
                    id={selected!._id!}
                    name={selected!.name}
                    onClose={() => { setOpenDelete(false) }}
                    onOk={() => { getItems() }} />
            }

        </div>
    )
}

/**
 * @description Fill details of the selected spacecraft
 * 
 * @param item Selected spacecraft
 * @returns JSX
 */
function SpacecraftDetails({ item }: Readonly<{ item: IDbSpacecraftItem }>): react.JSX.Element
{
    return (
        <div className="text-stone-300 space-y-4">

            {/* Name */}

            <h1 className="text-3xl font-bold text-orange-300 border-b-2 mb-2">{item.name}</h1>

            {/* General */}

            <h2 className="text-2xl text-center">General</h2>

            <p><strong className="font-bold">Mass:</strong> {item.mass} kg</p>

            <div className="border-b-2 border-stone-300"></div>

            {/* Orbit */}

            <h2 className="text-2xl text-center">Orbit</h2>

            <div className="grid grid-cols-2 gap-4 text-stone-300">

                <div><strong>Semi-Major Axis:</strong> {item.orbit.sma} km</div>
                <div><strong>Eccentricity:</strong> {item.orbit.ecc}</div>
                <div><strong>Inclination:</strong> {item.orbit.inc}°</div>
                <div><strong>Right Ascension Ascending Node:</strong> {item.orbit.raan}°</div>
                <div><strong>Argument Periapsis:</strong> {item.orbit.aop}°</div>
                <div><strong>True Anomaly:</strong> {item.orbit.tan}°</div>

            </div>

            <div className="border-b-2 border-stone-300"></div>

            {/* Image */}

            {item.image && (
                <img
                    src={item.image ? `data:image/png;base64,${item.image}` : undefined}
                    alt={item.name}
                    className="w-64 h-auto rounded border border-stone-700"
                />
            )}
        </div>
    )
}