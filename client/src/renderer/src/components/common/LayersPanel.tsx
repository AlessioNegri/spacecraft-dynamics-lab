import * as react from "react"
import * as iconify from "@iconify/react"

import Tooltip from "../Tooltip"

interface LayersPanelProps
{
    spacecrafts: IDbSpacecraftItem[]
    selectedId: string | null
    onToggle: (id: string) => void
    onTrack: (id: string) => void
    onStop: () => void
}

/** @function LayersPanel */
export default function LayersPanel(props: Readonly<LayersPanelProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [open, setOpen] = react.useState<boolean>(true)

    // --- HANDLERS ---

    const handleShowAll = (e: react.MouseEvent<SVGSVGElement, MouseEvent>) =>
    {
        e.stopPropagation()

        props.spacecrafts.forEach(spacecraft => { if (!spacecraft.visible) props.onToggle(spacecraft._id!) })
    }

    const handleHideAll = (e: react.MouseEvent<SVGSVGElement, MouseEvent>) =>
    {
        e.stopPropagation()

        props.spacecrafts.forEach(spacecraft => { if (spacecraft.visible) props.onToggle(spacecraft._id!) })
    }

    // --- RENDERING ---

    return (
        <div className="absolute top-2 left-2 w-96 bg-neutral-800/90 backdrop-blur border-2 border-neutral-400
                        rounded-lg shadow-lg p-3 z-2">

            <button
                className="w-full pb-2 mb-2 border-b-2 flex items-center justify-between gap-2 cursor-pointer"
                onClick={() => setOpen(o => !o)}>

                <div className="font-semibold text-base">Spacecraft List</div>

                <div className="flex-1"></div>

                <Tooltip title="Show All" side="bottom">
                
                    <iconify.Icon
                        icon="mdi:show"
                        width={24}
                        className="cursor-pointer hover:text-orange-300"
                        onClick={handleShowAll}
                    />

                </Tooltip>

                <Tooltip title="Hide All" side="bottom">
                    
                    <iconify.Icon
                        icon="mdi:hide"
                        width={24}
                        className="cursor-pointer hover:text-orange-300"
                        onClick={handleHideAll}
                    />

                </Tooltip>

                <Tooltip title="Remove Tracking" side="bottom">

                    <iconify.Icon
                        icon="mdi:camera-off"
                        width={24}
                        className="cursor-pointer hover:text-orange-300"
                        onClick={(e: react.MouseEvent<SVGSVGElement, MouseEvent>) =>
                        {
                            e.stopPropagation()
                            
                            props.onStop()
                        }}
                    />

                </Tooltip>


            </button>

        {
            open &&
            <div className="flex flex-col gap-2 max-h-64 pt-2 overflow-auto custom-scrollbar">

                {
                    props.spacecrafts.map((spacecraft: IDbSpacecraftItem) => (
                    <button
                        key={spacecraft._id}
                        className={`flex items-center justify-start gap-2 p-1 cursor-pointer
                                    hover:bg-neutral-600 hover:rounded mr-2
                                    ${(spacecraft._id === props.selectedId) ? 'bg-neutral-500 rounded' : ''}`}
                        onClick={() => props.onToggle(spacecraft._id!)}>

                        <iconify.Icon
                            icon={`${spacecraft.visible ? "mdi:show" : "mdi:hide"}`}
                            width={24}
                            className={`${spacecraft.visible ? "text-green-300" : "text-red-300"}`}
                        />

                        <div className="w-3 h-3 rounded border" style={{ backgroundColor: spacecraft.style.color }} />

                        <span className="text-sm w-64 text-left">{spacecraft.name}</span>

                        <Tooltip title="Track" side="left">

                            <iconify.Icon
                                icon="mdi:camera"
                                width={24}
                                className={`cursor-pointer hover:text-orange-300
                                            ${(spacecraft._id === props.selectedId) ? 'text-green-300' : ''}`}
                                onClick={(e: react.MouseEvent<SVGSVGElement, MouseEvent>) =>
                                {
                                    e.stopPropagation()
                                    
                                    props.onTrack(spacecraft._id!)
                                }}
                            />

                        </Tooltip>

                    </button>
                ))}

            </div>
        }
            
        </div>
    )
}