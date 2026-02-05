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
            minimizeApp     : () => void
            maximizeApp     : () => void
            closeApp        : () => void
            triggerSideBar  : () => void
            triggerConsole  : () => void
            debug           : (message: string) => void
            info            : (message: string) => void
            warning         : (message: string) => void
            error           : (message: string) => void
        },
        callback:
        {
            onWindowMaximized   : (callback: (maximized: boolean) => void) => () => void
            onTriggerSideBar    : (callback: () => void) => () => void
            onTriggerConsole    : (callback: () => void) => () => void
            onLog               : (callback: (entry: LogEntry) => void) => () => void
            onTcpOpened         : (callback: (opened: boolean) => void) => () => void
            onReceivedInfo      : (callback: (info: WebSocketInfo) => void) => () => void
        }
    }
}