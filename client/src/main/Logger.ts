import * as electron from 'electron'

import MainWindow from './MainWindow'

/**
 * @description Calculate current timestamp
 * 
 * @returns Formatted timestamp
 */
function currentTimestamp(): string
{
    return new Date().toISOString().replace("T", " ").slice(0, 19)
}

/**
 * @description Send an INFO message to the UI
 * 
 * @param message Message
 */
function debug(message: string)
{
    const win: electron.BrowserWindow = MainWindow.GetInstance().window()!

    win.webContents.send("log:append",
    {
        level: "debug",
        message: message,
        timestamp: currentTimestamp()
    });
}

/**
 * @description Send an INFO message to the UI
 * 
 * @param message Message
 */
function info(message: string)
{
    const win: electron.BrowserWindow = MainWindow.GetInstance().window()!

    win.webContents.send("log:append",
    {
        level: "info",
        message: message,
        timestamp: currentTimestamp()
    });
}

/**
 * @description Send a WARNING message to the UI
 * 
 * @param message Message
 */
function warning(message: string)
{
    const win: electron.BrowserWindow = MainWindow.GetInstance().window()!

    win.webContents.send("log:append",
    {
        level: "warning",
        message: message,
        timestamp: currentTimestamp()
    });
}

/**
 * @description Send an ERROR message to the UI
 * 
 * @param message Message
 */
function error(message: string)
{
    const win: electron.BrowserWindow = MainWindow.GetInstance().window()!

    win.webContents.send("log:append",
    {
        level: "error",
        message: message,
        timestamp: currentTimestamp()
    });
}

const Logger = { debug, info, warning, error }

export default Logger