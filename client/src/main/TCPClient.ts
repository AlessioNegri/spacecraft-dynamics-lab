import * as electron from 'electron'

import Logger from './Logger'
import Singleton from './Singleton'
import MainWindow from './MainWindow'

/** @class TCP client class */
export default class TCPClient extends Singleton<TCPClient>
{
    // --- MEMBER ---

    private ws: WebSocket | null = null

    private timer: NodeJS.Timeout | null = null

    private delay = 1000 // ? [ms]

    private readonly maxDelay = 15000 // ? [ms]

    private readonly url = "ws://127.0.0.1:8000/ws"

    private isReconnecting = false;

    private isClosing = false;

    // --- PUBLIC ---

    public constructor()
    {
        super()
    }

    /**
     * @summary Start the web socket
     */
    public start(): void
    {
        this.isClosing = false

        const win: electron.BrowserWindow = MainWindow.GetInstance().window()!

        Logger.info("Connecting to server ...")

        this.ws = new WebSocket(this.url)

        this.ws.onopen = (_: Event) =>
        {
            Logger.info("Server connected")

            win.webContents.send("tcp:opened", true)

            this.isReconnecting = false
            this.delay          = 1000
        }
        
        this.ws.onmessage = (event: MessageEvent<any>) =>
        {
            Logger.debug("Received: " + event.data)
        }

        this.ws.onerror = (event: Event) =>
        {
            if (this.isClosing) return

            const err = event as ErrorEvent;

            Logger.error("Server error: " + err.message)

            // * Prevent infinite loops

            if (this.isReconnecting) return

            this.isReconnecting = true

            // * Force close (safe even if CONNECTING)

            try
            {
                this.ws?.close()
            }
            catch
            {}

            this.scheduleReconnect()
        }

        this.ws.onclose = (_: Event) =>
        {
            Logger.warning("Server disconnected")

            win.webContents.send("tcp:opened", false)

            if (!this.isReconnecting)
            {
                this.isReconnecting = true

                this.scheduleReconnect()
            }
        }
    }

    /**
     * @summary Stop the web socket
     */
    public stop(): void
    {
        this.isReconnecting = false
        this.isClosing      = true

        if (this.timer)
        {
            clearTimeout(this.timer)

            this.timer = null
        }

        this.ws?.close()

        this.ws = null
    }

    // --- PRIVATE ---

    private scheduleReconnect(): void
    {
        if (this.timer) return

        Logger.info(`Reconnecting in ${this.delay / 1000}s ...`)

        this.isReconnecting = false

        this.timer = setTimeout(() =>
        {
            this.timer = null;
        
            this.start();

            // * Increase delay (exponential backoff)

            this.delay = Math.min(this.delay * 2, this.maxDelay)

        }, this.delay)
    }
}