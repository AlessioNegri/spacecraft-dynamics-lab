import * as electron from 'electron'

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

    // ? BE --> FE

    // * window

    win.on("maximize", () => win.webContents.send("window:isMaximized", true))

    win.on("unmaximize", () => win.webContents.send("window:isMaximized", false))
}