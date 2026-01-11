import * as react from "react";
import * as iconify from "@iconify/react";
import mdi from "@iconify-json/mdi/icons.json"

interface Item
{
    id: string,
    label: string,
    icon:
    {
        body: string
    }
}

export function Sidebar(): react.JSX.Element
{
    const [active, setActive] = react.useState("spacecraft")

    const items: Item[] =
    [
        {
            id: "spacecraft",
            label: "Spacecraft",
            icon: mdi.icons["space-station"]
        },
        {
            id: "spacecraft2",
            label: "Spacecraft2",
            icon: mdi.icons["space-station"]
        }
    ]

    return (
        <div
            className="
            w-18
            h-full
            bg-stone-900
            text-white
            flex
            flex-col
            items-center
            py-2
            select-none">

            {/* Top */}

            <div className="flex flex-col gap-4 flex-1">

                {
                    items.map((item: Item) => (
                        <button
                            key={item.id}
                            title={item.label}
                            onClick={() => setActive(item.id)}
                            className={`
                            relative
                            flex
                            items-center
                            justify-center
                            w-16
                            h-16
                            rounded
                            hover:bg-stone-600
                            transition
                            cursor-pointer`}>
                            
                            {
                                (active === item.id) && (
                                <div
                                    className="
                                    absolute
                                    left-0
                                    top-0
                                    bottom-0
                                    w-1
                                    bg-orange-300
                                    rounded"/>)
                            }

                            <iconify.Icon
                                icon={item.icon}
                                width={24}
                                height={24}
                                color={`${(active === item.id) ? "oklch(83.7% 0.128 66.29)" : "oklch(70.7% 0.022 261.325)"}`}
                                className="iconify" />

                        </button>
                    ))}

            </div>

            {/* Bottom */}

            <div className="flex flex-col gap-4 mt-auto">

                <button
                    title="Exit"
                    className="
                    flex
                    items-center
                    justify-center
                    w-16
                    h-16
                    rounded
                    hover:bg-stone-600
                    cursor-pointer">
                    
                    <iconify.Icon
                        icon={mdi.icons["exit-to-app"]}
                        width={24}
                        height={24}
                        color={"oklch(83.7% 0.128 66.29)"}
                        className="iconify" />

                </button>
            </div>

        </div>
    );
}