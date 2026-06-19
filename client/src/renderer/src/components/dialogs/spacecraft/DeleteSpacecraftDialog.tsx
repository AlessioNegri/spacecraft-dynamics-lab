import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import ErrorText from "@renderer/components/dialogs/ErrorText"

interface Props
{
    id: string
    name: string
    opened: boolean
    setOpened: (opened: boolean) => void
    onOk: () => void
}

/** @function DeleteSpacecraftDialog */
export default function DeleteSpacecraftDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [axiosError, setAxiosError] = react.useState<string>("")

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const handleDelete = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.delete(`/spacecraft/${props.id}`)

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
            title="Delete Spacecraft"
            button="Delete"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
        >

            <Form.Root
                ref={formRef}
                onSubmit={handleDelete}
                className="mt-15 flex flex-col items-center justify-center"
            >

                <p className="text-nowrap text-lg">
                    {`Do you want to delete spacecraft`} <strong className="text-orange-300">{props.name}</strong>?
                </p>
            
            { axiosError && <ErrorText text={axiosError} /> }

            </Form.Root>


        </DialogRUI>
    )
}
