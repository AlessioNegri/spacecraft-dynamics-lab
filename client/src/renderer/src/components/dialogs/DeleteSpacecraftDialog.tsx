import * as react from "react"

import api from "@renderer/common/api"
import checkError from "@renderer/common/error"

import Dialog from "./Dialog"

interface DeleteSpacecraftDialogProps
{
    id: string
    name: string
    onClose: () => void
    onOk: () => void
}

/** @function DeleteSpacecraftDialog */
export default function DeleteSpacecraftDialog(props: Readonly<DeleteSpacecraftDialogProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [axiosError, setAxiosError] = react.useState<string>("")

    // --- GENERIC ---

    const handleDelete = async () =>
    {
        try
        {
            let response: any = await api.delete(`/spacecraft/${props.id}`)

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
        <Dialog title={`Delete Spacecraft`} onClose={() => { props.onClose() }} >

            <p className="mb-4">
                {`Do you want to delete spacecraft`} <strong className="text-orange-300">{props.name}</strong>?
            </p>

            <button
                onClick={handleDelete}
                className="px-3 py-1 rounded cursor-pointer
                            bg-red-700 hover:bg-red-800 border border-red-900 text-white">

                Delete

            </button>

            {
                axiosError && <p className="text-red-400 text-sm">{axiosError}</p>
            }

        </Dialog>
    )
}