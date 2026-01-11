import * as Menubar from "@radix-ui/react-menubar";
import * as react from "react";

export function MenuBar()
{
    return (
        <div
            className="
            w-full
            h-12
            bg-stone-950
            text-white
            flex
            items-center
            px-2
            select-none">
            
            <Menubar.Root className="flex gap-1">

                <Menu
                    label="File"
                    items={
                        [
                            { separator: true },
                            { label: "Exit" },
                        ]}
                    />

                <Menu
                    label="View"
                    items={
                        [
                            { label: "Reload" },
                            { label: "Toggle DevTools" },
                            { separator: true },
                            { label: "Toggle Fullscreen" },
                        ]}
                    />

                <Menu
                    label="Help"
                    items={
                        [
                            { label: "Learn More" },
                        ]}
                    />

            </Menubar.Root>

        </div>
    );
}

function Menu({ label, items }: Readonly<{ label: string, items: any[]}>)
{
    return (
        <Menubar.Menu>

            <Menubar.Trigger
                className="
                text-lg
                px-2
                rounded
                text-stone-500
                hover:bg-stone-500
                hover:text-stone-400
                data-[state=open]:bg-stone-700
                cursor-pointer">

                {label}

            </Menubar.Trigger>

            <Menubar.Portal>
                
                <Menubar.Content
                    align="start"
                    className="
                    min-w-45
                    bg-stone-600
                    text-white
                    border
                    border-black
                    rounded
                    shadow-lg
                    py-1"
                >

                    {
                        items.map(
                            (
                                item: { separator: boolean; label: string, shortcut: boolean },
                                i: react.Key
                            ) =>
                        item.separator
                        ?
                        (
                            <Menubar.Separator
                                key={i}
                                className="h-px bg-stone-950 my-1"/>
                        )
                        :
                        (
                            <Menubar.Item
                                key={i}
                                className="
                                px-10
                                py-1.5
                                text-base
                                flex
                                justify-between
                                hover:bg-stone-500
                                hover:text-white
                                cursor-pointer"
                            >

                                <span className="font-bold">{item.label}</span>

                                {
                                    item.shortcut &&
                                    (
                                        <span className="text-xs text-white">
                                            {item.shortcut}
                                        </span>
                                    )
                                }

                            </Menubar.Item>
                        )
                    )}

                </Menubar.Content>

            </Menubar.Portal>

        </Menubar.Menu>
    );
}