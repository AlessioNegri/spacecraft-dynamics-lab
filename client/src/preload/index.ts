import * as electron from 'electron'
import * as preload from '@electron-toolkit/preload'

// * Custom APIs for renderer

const api =
{
    minimizeApp     : () => electron.ipcRenderer.send('app:minimize'),
    maximizeApp     : () => electron.ipcRenderer.send('app:maximize'),
    closeApp        : () => electron.ipcRenderer.send('app:close'),
    triggerSideBar  : () => electron.ipcRenderer.send('app:trigger-side-bar'),
    triggerConsole  : () => electron.ipcRenderer.send('app:trigger-console'),
    debug           : (message: string) => electron.ipcRenderer.send('log:message', 'debug', message),
    info            : (message: string) => electron.ipcRenderer.send('log:message', 'info', message),
    warning         : (message: string) => electron.ipcRenderer.send('log:message', 'warning', message),
    error           : (message: string) => electron.ipcRenderer.send('log:message', 'error', message),
    updateTcpUrl    : (url: string) => electron.ipcRenderer.send('tcp:update-url', url),
    getFileSize     : (filename: string) => electron.ipcRenderer.invoke('utils:get-file-size', filename),
}

// * Custom Callbacks for renderer

const callback =
{
    onWindowMaximized: (callback: (maximized: boolean) => void): (() => void) =>
    {
        const listener = (_: Electron.IpcRendererEvent, maximized: boolean) => callback(maximized)

        electron.ipcRenderer.on('window:isMaximized', listener)

        return () => electron.ipcRenderer.removeListener('window:isMaximized', listener)
    },
    onTriggerSideBar: (callback: () => void): (() => void) =>
    {
        const listener = (_: Electron.IpcRendererEvent) => callback()

        electron.ipcRenderer.on('window:triggerSideBar', listener)

        return () => electron.ipcRenderer.removeListener('window:triggerSideBar', listener)
    },
    onTriggerConsole: (callback: () => void): (() => void) =>
    {
        const listener = (_: Electron.IpcRendererEvent) => callback()

        electron.ipcRenderer.on('window:triggerConsole', listener)

        return () => electron.ipcRenderer.removeListener('window:triggerConsole', listener)
    },
    onLog: (callback: (entry: LogEntry) => void): (() => void) =>
    {
        const listener = (_event: Electron.IpcRendererEvent, entry: LogEntry) => callback(entry)

        electron.ipcRenderer.on('log:append', listener)

        return () => electron.ipcRenderer.removeListener('log:append', listener)
    },
    onAppOnline: (callback: (online: boolean) => void): (() => void) =>
    {
        const listener = (_event: Electron.IpcRendererEvent, online: boolean) => callback(online)

        electron.ipcRenderer.on('app:online', listener)

        return () => electron.ipcRenderer.removeListener('app:online', listener)
    },
    onTcpOpened: (callback: (opened: boolean) => void): (() => void) =>
    {
        const listener = (_event: Electron.IpcRendererEvent, opened: boolean) => callback(opened)

        electron.ipcRenderer.on('tcp:opened', listener)

        return () => electron.ipcRenderer.removeListener('tcp:opened', listener)
    },
    onTcpUrl: (callback: (url: string) => void): (() => void) =>
    {
        const listener = (_event: Electron.IpcRendererEvent, url: string) => callback(url)

        electron.ipcRenderer.on('tcp:url', listener)

        return () => electron.ipcRenderer.removeListener('tcp:url', listener)
    },
    onWebSocketInfo: (callback: (info: WebSocketInfo) => void): (() => void) =>
    {
        const listener = (_event: Electron.IpcRendererEvent, info: WebSocketInfo) => callback(info)

        electron.ipcRenderer.on('ws:info', listener)

        return () => electron.ipcRenderer.removeListener('ws:info', listener)
    },
    onWebSocketSimulation: (callback: (sim: WebSocketSimulation) => void): (() => void) =>
    {
        const listener = (_event: Electron.IpcRendererEvent, sim: WebSocketSimulation) => callback(sim)

        electron.ipcRenderer.on('ws:simulation', listener)

        return () => electron.ipcRenderer.removeListener('ws:simulation', listener)
    }
}

// * Use `contextBridge` APIs to expose Electron APIs to renderer only if context isolation is enabled, otherwise
// * just add to the DOM global

if (process.contextIsolated)
{
    try
    {
        electron.contextBridge.exposeInMainWorld('electron', preload.electronAPI)
        electron.contextBridge.exposeInMainWorld('api', api)
        electron.contextBridge.exposeInMainWorld('callback', callback)
    }
    catch (error)
    {
        console.error(error)
    }
}
else
{
    // @ts-ignore (define in dts)
    globalThis.window.electron = electronAPI

    // @ts-ignore (define in dts)
    globalThis.window.api = api
}