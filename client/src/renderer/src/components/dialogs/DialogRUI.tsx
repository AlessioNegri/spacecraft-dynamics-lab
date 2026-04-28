import * as react from "react"
import * as themes from "@radix-ui/themes"
import * as dialog from "@radix-ui/react-dialog"
import * as iconify from "@iconify/react"
import * as popover from "@radix-ui/react-popover"

interface PopupProps
{
    title: string
    content: string
}

interface DialogRUIProps
{
    children: react.ReactNode
    title: string
    button?: string
    open: boolean
    onClose: () => void
    onSubmit?: () => void
    popup?: PopupProps
}

/** @function DialogRUI base class based on Radix UI */
export default function DialogRUI(props: Readonly<DialogRUIProps>): react.JSX.Element
{
    // --- RENDERING ---

    return (
        <dialog.Root open={props.open}>

            <dialog.Portal>

                <dialog.Overlay className="fixed top-10 left-0 right-0 bottom-6 bg-orange-400/10" />

                <themes.Theme appearance="dark" accentColor="orange" grayColor="slate">

                    <dialog.Content
                        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                                    w-[80%] max-w-200 bg-neutral-800 text-white rounded-lg shadow-xl
                                    border-2 border-orange-800/50 p-6 space-y-6"
                    >

                        {/* HEADER */}
                        
                        <div className="flex justify-between items-center border-b border-neutral-700 pb-4">

                            <dialog.Title className="text-xl font-semibold flex-1">{props.title}</dialog.Title>

                            { props.popup && <Popup title={props.popup.title} content={props.popup.content} /> }

                            <iconify.Icon
                                icon="mdi:close-box"
                                width={30}
                                className="text-orange-400/25 hover:text-orange-400/75 hover:cursor-pointer"
                                onClick={props.onClose} />

                        </div>

                        {/* CONTENT */}

                        <div className="overflow-auto custom-scrollbar h-auto min-h-[10vh] max-h-[70vh]
                                        text-neutral-300 pe-4">

                            {props.children}

                        </div>

                        {/* FOOTER */}

                        <div className="flex items-center justify-center border-t border-neutral-700 pt-4">

                        {
                            props.button &&
                            <themes.Button variant="outline" color="orange" onClick={props.onSubmit}>
                                {props.button}
                            </themes.Button>
                        }

                        </div>

                    </dialog.Content>

                </themes.Theme>

            </dialog.Portal>

        </dialog.Root>
    )
}

/** @function Popup */
function Popup(props: Readonly<PopupProps>): react.JSX.Element {
    return (
        <popover.Root>

            <popover.Trigger asChild>

                <iconify.Icon
                    icon="mdi:information-box"
                    width={30}
                    className="text-blue-400/25 hover:text-blue-400/75 hover:cursor-pointer"
                />

            </popover.Trigger>

            <popover.Portal>

                <popover.Content
                    side="bottom"
                    align="end"
                    className="w-100 bg-neutral-900 border border-blue-400/50 rounded-lg p-4 text-justify
                                shadow-[0_0_20px_rgba(0,0,0,0.4)] text-sm text-neutral-200 leading-relaxed select-text"
                >

                    <div className="space-y-2">
                        <p className="font-semibold text-blue-300">{props.title}</p>
                        <p>{props.content}</p>
                    </div>

                    <popover.Arrow className="fill-blue-400/50" />

                </popover.Content>

            </popover.Portal>
            
        </popover.Root>)
}
