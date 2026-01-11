import * as react from "react";

export function StatusBar()
{
    const [versions] = react.useState(globalThis.electron.process.versions)

    const css: string = "hover:bg-stone-700 px-1 py-0.5 rounded cursor-default"

    return (
        <div
            className="
            w-full
            h-6
            bg-stone-950
            text-white
            text-xs
            flex
            items-center
            justify-between
            px-2
            select-none">

            <div className="flex items-center gap-3 custom-font">

                <span className={css}>Server Connected</span>

            </div>

            <div className="flex items-center gap-3 custom-font">

                <span className={css}>Electron v{versions.electron}</span>

                <span className={css}>Chromium v{versions.chrome}</span>

                <span className={css}>Node v{versions.node}</span>

            </div>

        </div>
    );
}