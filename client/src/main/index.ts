import { app, BrowserWindow } from 'electron'
import * as utils from '@electron-toolkit/utils'

import { MainWindow } from './MainWindow'
import { TCPClient } from './TCPClient'

// * This method will be called when Electron has finished
// * initialization and is ready to create browser windows.
// * Some APIs can only be used after this event occurs.

app.whenReady().then(() =>
{
    // * Set app user model id for windows

    utils.electronApp.setAppUserModelId('com.alessio-negri')

    // * Default open or close DevTools by F12 in development
    // * and ignore CommandOrControl + R in production.
    // * see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils

    app.on('browser-window-created', (_, window) =>
    {
        utils.optimizer.watchWindowShortcuts(window)
    })

    app.on('activate', () =>
    {
        // * On macOS it's common to re-create a window in the app when the
        // * dock icon is clicked and there are no other windows open.

        if (BrowserWindow.getAllWindows().length === 0) MainWindow.GetInstance().createWindow()
    })

    // * Quit when all windows are closed, except on macOS. There, it's common
    // * for applications and their menu bar to stay active until the user quits
    // * explicitly with Cmd + Q.
    app.on('window-all-closed', () =>
    {
        if (process.platform !== 'darwin')
        {
            TCPClient.GetInstance().stop()

            app.quit()
        }
    })

    // * Setup

    MainWindow.GetInstance().createWindow()

    TCPClient.GetInstance().start()
})