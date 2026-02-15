import * as react from "react"

import http from "@renderer/common/http"

import Dialog from "./Dialog"
import FormButton from "./FormButton"

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

    // --- HANDLE ---

    const handleDelete = async () =>
    {
        try
        {
            let response: any = await http.api.delete(`/spacecraft/${props.id}`)

            globalThis.window.api.info(`[${import.meta.url}] ${JSON.stringify(response.data)}`)

            props.onOk()
            props.onClose()
        }
        catch (err)
        {
            const message: string | null = http.checkError(import.meta.url, err)

            if (message) setAxiosError(message)
        }
    }

    // --- RENDERING ---

    return (
        <Dialog title={`Delete Spacecraft`} onClose={() => { props.onClose() }} >

            <p className="mb-4">
                {`Do you want to delete spacecraft`} <strong className="text-orange-300">{props.name}</strong>?
            </p>

            <div className="flex justify-center">
            
                <FormButton text="Delete" color="red" onClick={handleDelete} />

            </div>

            {
                axiosError && <p className="text-red-400 text-sm">{axiosError}</p>
            }

        </Dialog>
    )
}