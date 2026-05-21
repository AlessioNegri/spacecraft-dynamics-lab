import * as react from "react"
import * as iconify from "@iconify/react"
import * as Themes from "@radix-ui/themes"

import utility from "@renderer/common/utility"

/** @function SettingsPage */
export default function SettingsPage()
{
    // --- USE STATE ---

    const [srvConnected, setSrvConnected] = react.useState<boolean>(false)

    const [srvUrl, setSrvUrl] = react.useState<string>("")

    const [srvUrlDraft, setSrvUrlDraft] = react.useState<string>("")

    const [editSrvUrl, setEditSrvUrl] = react.useState<boolean>(false)

    const [dbConnected, setDbConnected] = react.useState<boolean>(false)

    const [dbUrl, setDbUrl] = react.useState<string>("")
    
    const [dbName, setDbName] = react.useState<string>("")

    const [versions] = react.useState<any>(globalThis.electron.process.versions)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        const rmTO = globalThis.window.callback.onTcpOpened((opened: boolean) => setSrvConnected(opened))

        const rmTU = globalThis.window.callback.onTcpUrl((url: string) => setSrvUrl(url))

        const rmRI = globalThis.window.callback.onWebSocketInfo((info: WebSocketInfo) =>
        {
            setDbConnected(info.database.connected)

            setDbUrl(info.database.url)

            setDbName(info.database.name)
        })

        return () => { rmTO(); rmTU(); rmRI() }
    }, [])

    // --- RENDERING ---

    return (
        <div className="flex flex-col w-full h-full p-6 space-y-8 text-neutral-200">

            {/* Title */}

            {/* <h1 className="text-2xl font-bold text-orange-300">Settings</h1> */}

            {/* Electron */}

            <section className="space-y-4 border rounded-lg p-2 border-neutral-500 bg-neutral-700/50">

                <div className="flex items-center gap-4">

                    <iconify.Icon icon="skill-icons:electron" height={30} />
                    
                    <h2 className="text-lg font-semibold text-neutral-300">Client</h2>

                    <span className="flex-1"></span>

                </div>

                <Themes.Flex direction={"column"} gap={"2"}>

                    <Themes.Text className="text-neutral-400">
                        Electron Version
                    </Themes.Text>

                    <Themes.TextField.Root value={versions.electron} readOnly>
                        <Themes.TextField.Slot>
                            <iconify.Icon icon="simple-icons:electron" height={20} />
                        </Themes.TextField.Slot>
                    </Themes.TextField.Root>

                </Themes.Flex>

                <Themes.Flex direction={"column"} gap={"2"}>

                    <Themes.Text className="text-neutral-400">
                        Chromium Version
                    </Themes.Text>

                    <Themes.TextField.Root value={versions.chrome} readOnly>
                        <Themes.TextField.Slot>
                            <iconify.Icon icon="devicon-plain:chrome" height={20} />
                        </Themes.TextField.Slot>
                    </Themes.TextField.Root>

                </Themes.Flex>

                <Themes.Flex direction={"column"} gap={"2"}>

                    <Themes.Text className="text-neutral-400">
                        Node Version
                    </Themes.Text>

                    <Themes.TextField.Root value={versions.node} readOnly>
                        <Themes.TextField.Slot>
                            <iconify.Icon icon="mdi:nodejs" height={20} />
                        </Themes.TextField.Slot>
                    </Themes.TextField.Root>

                </Themes.Flex>

            </section>

            {/* FastAPI */}

            <section className="space-y-4 border rounded-lg p-2 border-neutral-500 bg-neutral-700/50">

                <div className="flex items-center gap-4">

                    <iconify.Icon icon="skill-icons:fastapi" height={30} />
                    
                    <h2 className="text-lg font-semibold text-neutral-300">Server</h2>

                    <span className="flex-1"></span>

                    <Themes.Badge
                        color={srvConnected ? "green" : "red"}
                        size={"3"}
                        variant="outline"
                    >
                        {srvConnected ? "Connected" : "Disconnected"}
                    </Themes.Badge>

                </div>

                <Themes.Flex direction={"column"} gap={"2"}>

                    <Themes.Text className="text-neutral-400">
                        FastAPI Web Socket URL
                    </Themes.Text>

                    <Themes.TextField.Root
                        value={editSrvUrl ? srvUrlDraft : srvUrl}
                        onChange={(e) => setSrvUrlDraft(e.target.value)}
                        readOnly={!editSrvUrl}>

                        <Themes.TextField.Slot>
                            <iconify.Icon icon="carbon:url" height={20} className="m-auto" />
                        </Themes.TextField.Slot>

                        <Themes.TextField.Slot>
                            <iconify.Icon
                                icon="mdi:edit"
                                height={20}
                                className={utility.cn(editSrvUrl ? "text-neutral-600" : "text-neutral-300",
                                    "cursor-pointer")}
                                onClick={() => { setEditSrvUrl(true); setSrvUrlDraft(srvUrl) }}
                            />
                        </Themes.TextField.Slot>

                        <Themes.TextField.Slot>
                            <iconify.Icon
                                icon="mdi:check-circle"
                                height={20}
                                className={utility.cn(editSrvUrl ? "text-green-300" : "text-neutral-600",
                                    "cursor-pointer")}
                                onClick={() =>
                                {
                                    setEditSrvUrl(false)

                                    if (srvUrl !== srvUrlDraft)
                                    {
                                        setSrvUrl(srvUrlDraft)

                                        globalThis.window.api.updateTcpUrl(srvUrlDraft)
                                    }
                                }}
                            />
                        </Themes.TextField.Slot>

                        <Themes.TextField.Slot>
                            <iconify.Icon
                                icon="mdi:cancel-circle"
                                height={20}
                                className={utility.cn(editSrvUrl ? "text-red-300" : "text-neutral-600",
                                    "cursor-pointer")}
                                onClick={() => { setEditSrvUrl(false); setSrvUrlDraft(srvUrl) }}
                            />
                        </Themes.TextField.Slot>

                    </Themes.TextField.Root>

                </Themes.Flex>

            </section>

            {/* MongoDB */}

            <section className="space-y-4 border rounded-lg p-2 border-neutral-500 bg-neutral-700/50">

                <div className="flex items-center gap-4">

                    <iconify.Icon icon="skill-icons:mongodb" height={30} />
                    
                    <h2 className="text-lg font-semibold text-neutral-300">Database</h2>

                    <span className="flex-1"></span>

                    <Themes.Badge
                        color={dbConnected ? "green" : "red"}
                        size={"3"}
                        variant="outline"
                    >
                        {dbConnected ? "Connected" : "Disconnected"}
                    </Themes.Badge>

                </div>

                <Themes.Flex direction={"column"} gap={"2"}>

                    <Themes.Text className="text-neutral-400">
                        MongoDB URL
                    </Themes.Text>

                    <Themes.TextField.Root value={dbUrl} readOnly>
                        <Themes.TextField.Slot>
                            <iconify.Icon icon="carbon:url" height={20} className="m-auto" />
                        </Themes.TextField.Slot>
                    </Themes.TextField.Root>

                </Themes.Flex>

                <Themes.Flex direction={"column"} gap={"2"}>

                    <Themes.Text className="text-neutral-400">
                        Database Name
                    </Themes.Text>

                    <Themes.TextField.Root value={dbName} readOnly>
                        <Themes.TextField.Slot>
                            <iconify.Icon icon="mdi:database" height={20} className="m-auto" />
                        </Themes.TextField.Slot>
                    </Themes.TextField.Root>

                </Themes.Flex>

            </section>

            <div className="h-2"></div>

        </div>
    )
}
