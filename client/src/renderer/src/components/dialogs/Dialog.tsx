import * as react from "react"
import * as iconify from "@iconify/react"

interface DialogProps
{
    children: react.ReactNode
    title: string
    onClose: () => void
}

/** @function Dialog */
export default function Dialog(props: Readonly<DialogProps>): react.JSX.Element
{
    return (
        <div className="fixed inset-0 bg-stone-700/60 backdrop-blur-sm flex items-center justify-center z-50">
                
            {/* Dialog container */}

            <div className="bg-stone-800 text-white rounded-lg shadow-xl w-full max-w-2xl p-6 relative animate-fadeIn">

                {/* Close button */}

                <iconify.Icon
                    icon={"mdi:close-box"}
                    width={30}
                    onClick={() => props.onClose()}
                    className="absolute top-3 right-3 text-gray-400 hover:text-gray-200 cursor-pointer"/>

                {/* Title */}

                <h2 className="text-2xl font-semibold mb-4">{props.title}</h2>

                {/* Children */}

                {props.children}

            </div>

        </div>
    )
}