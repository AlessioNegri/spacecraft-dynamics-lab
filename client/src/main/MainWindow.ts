// ? Main Window for electron

import * as electron from 'electron'
import * as path from 'node:path'
import * as utils from '@electron-toolkit/utils'

import icon from '../../resources/icon.jpg?asset'

/** @class Main window class */
class MainWindow
{
    // * Members

    private static instance: MainWindow

    private win: electron.BrowserWindow | null = null

    // * Public Functions

    /**
     * @summary Retieve the singleton
     * 
     * @returns Main window
     */
    public static GetInstance(): MainWindow
    {
        if (!MainWindow.instance)
        {
            MainWindow.instance = new MainWindow()
        }

        return MainWindow.instance
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
                ...(process.platform === 'linux' ? { icon } : {}),
                webPreferences:
                {
                    preload: path.join(__dirname, '../preload/index.js'),
                    sandbox: false
                }
            })

        this.win.on('ready-to-show', () => { this.win?.show() })

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

        // * Create menu

        this.createMenu()

        this.win.maximize()
    }

    // * Private Functions

    private constructor() {}

    /**
     * @summary Create the menu of the app
     */
    private createMenu(): void
    {
        const template: Electron.MenuItemConstructorOptions[] =
            [
                {
                    label: 'File',
                    submenu:
                    [
                        { type: 'separator' },
                        { label: 'Exit', role: 'quit' }
                    ]
                },
                {
                    label: "Help",
                    submenu:
                    [
                        {
                            label: "Learn More",
                            click: () =>
                                {
                                    require("electron").shell.openExternal("https://electronjs.org")
                                }
                        }
                    ]
                }
            ]
    
        const menu = electron.Menu.buildFromTemplate(template)
        
        electron.Menu.setApplicationMenu(menu)
    }
}

export { MainWindow }