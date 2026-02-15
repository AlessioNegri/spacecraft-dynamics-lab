import * as electron from 'electron'
import * as path from 'node:path'
import * as utils from '@electron-toolkit/utils'

import icon from '../../resources/icon.ico?asset'

import Singleton from './Singleton'
import TCPClient from './TCPClient'

/** @class Main window class */
export default class MainWindow extends Singleton
{
    // --- MEMBER ---

    private win: electron.BrowserWindow | null = null

    // --- PUBLIC ---

    public constructor()
    {
        super()
    }

    /**
     * @summary Retrieve the underlying window object
     * 
     * @returns Browser window
     */
    public window(): electron.BrowserWindow | null
    {
        return this.win
    }

    /**
     * @summary Create the electron main window
     */
    public createWindow(): void
    {
        // * Init window

        this.win = new electron.BrowserWindow(
        {
            width: 900,
            height: 670,
            show: false,
            autoHideMenuBar: true,
            frame: false,
            titleBarStyle: 'hidden', // ? For macOs
            icon: icon,
            webPreferences:
            {
                preload: path.join(__dirname, '../preload/index.js'),
                sandbox: false,
                webgl: true,
                experimentalFeatures: true,
                devTools: true
            }
        })

        this.win.on('ready-to-show', () =>
        {
            this.win?.show()
        })

        this.win.webContents.setWindowOpenHandler((details: Electron.HandlerDetails) =>
        {
            electron.shell.openExternal(details.url)

            return { action: 'deny' }
        })

        // * HMR for renderer base on electron-vite cli.
        // * Load the remote URL for development or the local html file for production.

        if (utils.is.dev && process.env['ELECTRON_RENDERER_URL'])
        {
            this.win.loadURL(process.env['ELECTRON_RENDERER_URL'])
        }
        else
        {
            this.win.loadFile(path.join(__dirname, '../renderer/index.html'))
        }

        // * Configuration

        this.win.setMenuBarVisibility(false);

        this.win.maximize()

        this.win.webContents.openDevTools()

        this.win.webContents.on("did-finish-load", () => 
        {
            // * Start TCP client for web socket once the UI finished rendering

            TCPClient.GetInstance().start()
        })
    }
}