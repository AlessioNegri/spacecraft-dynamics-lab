import * as electron from 'electron'
import * as fs from 'node:fs'
import * as path from 'node:path'

import MainWindow from './MainWindow'
import TCPClient from './TCPClient'

/** @class Inter Protocol Communication class */
export default function IPC(): void
{
    const win: electron.BrowserWindow = MainWindow.GetInstance().window()!

    // ? FE --> BE

    // * app

    electron.ipcMain.on('app:minimize', () =>
    {
        MainWindow.GetInstance().window()?.minimize()
    })
    
    electron.ipcMain.on('app:maximize', () =>
    {
        if (win.isMaximized())
        {
            win.unmaximize()
        }
        else
        {
            win.maximize()
        }
    })
    
    electron.ipcMain.on('app:close', () =>
    {
        electron.app.quit()
    })

    electron.ipcMain.on('app:trigger-side-bar', () =>
    {
        win.webContents.send('window:triggerSideBar')
    })

    electron.ipcMain.on('app:trigger-console', () =>
    {
        win.webContents.send('window:triggerConsole')
    })

    // * log

    electron.ipcMain.on('log:message', (_, level: string, message: string) =>
    {
        const entry =
        {
            level: level,
            message: message,
            timestamp: new Date().toISOString().replace("T", " ").slice(0, 19)
        }

        win.webContents.send('log:append', entry)
    })

    // * tcp

    electron.ipcMain.on('tcp:update-url', (_, url: string) =>
    {
        TCPClient.GetInstance().updateUrl(url)
    })

    // * utils

    electron.ipcMain.handle('utils:get-file-size', (_, filename: string) : number =>
    {
        if (!filename || filename.trim() === "")
        {
            throw new Error("Filename is empty")
        }

        const isDev: boolean = !electron.app.isPackaged

        const filePath: string = isDev
            ? path.join("./src/renderer/public/models", `${filename}.glb`)
            : path.join(process.resourcesPath, "app.asar/out/renderer/models", `${filename}.glb`)

        const stats: fs.Stats = fs.statSync(filePath)

        return stats.size;
    })

    // ? BE --> FE

    // * window

    win.on("maximize", () => win.webContents.send("window:isMaximized", true))

    win.on("unmaximize", () => win.webContents.send("window:isMaximized", false))
}