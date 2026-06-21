import * as electron from 'electron'
import * as path from 'node:path'
import * as utils from '@electron-toolkit/utils'

import icon from '../../resources/SpacecraftDynamicsLab.ico?asset'

import Singleton from './Singleton'
import TCPClient from './TCPClient'
import Logger from './Logger'
import SplashWindow from './SplashWindow'

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
        // * Show splash immediately

        SplashWindow.GetInstance().create()

        // * Init window

        this.win = new electron.BrowserWindow(
        {
            width: 900,
            height: 670,
            show: false,
            autoHideMenuBar: true,
            frame: false,
            titleBarStyle: 'hidden', // ? For macOs
            title: "Spacecraft Dynamics Lab",
            icon: icon,
            transparent: true,
            webPreferences:
            {
                preload: path.join(__dirname, '../preload/index.js'),
                sandbox: false,
                webgl: true,
                experimentalFeatures: true,
                devTools: utils.is.dev
            }
        })

        this.win.on('ready-to-show', () =>
        {
            this.win?.show()

            // * Close splash once main window is visible

            SplashWindow.GetInstance().close()
        })

        this.win.webContents.setWindowOpenHandler((details: Electron.HandlerDetails) =>
        {
            electron.shell.openExternal(details.url)

            return { action: 'deny' }
        })

        this.win.webContents.setUserAgent("SpacecraftDynamicsLab")

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

        if (utils.is.dev)
        {
            this.win.webContents.openDevTools()
        }

        this.win.webContents.on("did-finish-load", () => 
        {
            // * Disclaimer

            Logger.warning("SpacecraftDynamicsLab Developer Disclaimer")
            Logger.warning(`This software is provided for educational and research use.
                It must NOT be used for real spacecraft operations, mission planning, navigation, control, or any
                safety-critical tasks.`)
            Logger.warning(`All results must be independently verified using certified engineering tools and
                validated mission analysis procedures.`)

            // * Start TCP client for web socket once the UI finished rendering

            TCPClient.GetInstance().start()
        })
    }
}
