import * as electron from 'electron'
import * as path from 'node:path'

import Singleton from './Singleton'

/** @class SplashWindow */
export default class SplashWindow extends Singleton
{
    // --- MEMBER ---

    private win: electron.BrowserWindow | null = null

    // --- PUBLIC ---

    public constructor()
    {
        super()
    }

    /** Create and show the splash window */
    public create(): void
    {
        if (this.win)
            return

        const splashFile = path.join(__dirname, '../renderer/splash.html')

        this.win = new electron.BrowserWindow({
            width: 1024,
            height: 700,
            frame: false,
            transparent: false,
            resizable: false,
            movable: false,
            alwaysOnTop: true,
            skipTaskbar: true,
            show: false,
            center: true,
            webPreferences:
            {
                sandbox: false
            }
        })

        this.win.loadFile(splashFile)

        this.win.once('ready-to-show', () => this.win?.show())
    }

    /** Close and destroy the splash window */
    public close(): void
    {
        if (!this.win) return

        try
        {
            this.win.close()
        }
        catch (e)
        {
            // ignore
        }

        this.win = null
    }
}
