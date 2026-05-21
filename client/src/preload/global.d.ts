import * as preload from '@electron-toolkit/preload'

export {}

declare global
{
    interface LogEntry
    {
        level: "debug" | "info" | "warn" | "error"
        message: string
        timestamp: string
    }

    interface WebSocketInfo
    {
        type: string = "info"
        database:
        {
            connected: boolean
            name: string
            url: string
        }
    }

    interface WebSocketSimulation
    {
        type: string = "simulation"
        source: string = ""
        counter: number = 0
        total: number = 0
        running: boolean = false
        data: JSON
    }

    interface Window
    {
        electron: preload.ElectronAPI,
        api:
        {
            minimizeApp: () => void
            maximizeApp: () => void
            closeApp: () => void
            triggerSideBar: () => void
            triggerConsole: () => void
            debug: (message: string) => void
            info: (message: string) => void
            warning: (message: string) => void
            error: (message: string) => void
            updateTcpUrl: (url: string) => void
        },
        callback:
        {
            onWindowMaximized : (callback: (maximized: boolean) => void) => () => void
            onTriggerSideBar : (callback: () => void) => () => void
            onTriggerConsole : (callback: () => void) => () => void
            onLog : (callback: (entry: LogEntry) => void) => () => void
            onAppOnline: (callback: (online: boolean) => void) => () => void
            onTcpOpened : (callback: (opened: boolean) => void) => () => void
            onTcpUrl : (callback: (url: string) => void) => () => void
            onWebSocketInfo : (callback: (info: WebSocketInfo) => void) => () => void
            onWebSocketSimulation : (callback: (info: WebSocketSimulation) => void) => () => void
        }
    }
}