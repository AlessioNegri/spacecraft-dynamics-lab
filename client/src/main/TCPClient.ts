import * as electron from 'electron'

import Logger from './Logger'
import Singleton from './Singleton'
import MainWindow from './MainWindow'

/** @class TCP client class */
export default class TCPClient extends Singleton
{
    // --- MEMBER ---

    private ws: WebSocket | null = null

    private timer: NodeJS.Timeout | null = null

    private delay = 1000 // ? [ms]

    private readonly maxDelay = 15000 // ? [ms]

    private url = "ws://127.0.0.1:8000/ws"

    private isReconnecting = false;

    private isClosing = false;

    // --- PUBLIC ---

    public constructor()
    {
        super()
    }

    /**
     * @description Update the web socket url and restart the connection
     * 
     * @param url The new web socket url
     */
    public updateUrl(url: string): void
    {
        this.url = url

        this.ws?.close()
    }

    /**
     * @summary Start the web socket
     */
    public start(): void
    {
        this.isClosing = false

        const win: electron.BrowserWindow = MainWindow.GetInstance().window()!

        Logger.info("Connecting to server ...")

        win.webContents.send("tcp:url", this.url)

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
            const json: JSON = JSON.parse(event.data)

            if (json["type"] === "simulation")
            {
                const info: WebSocketSimulation =
                {
                    type: json["type"],
                    source: json["source"],
                    counter: json["counter"],
                    total: json["total"],
                    running: json["running"],
                    data: json["data"]
                }

                win.webContents.send("ws:simulation", info)
            }
            else
            {
                win.webContents.send("ws:info", json)
            }
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

            win.webContents.send("ws:info",
                {
                    type: "info",
                    database:
                    {
                        connected: false,
                        name: "",
                        url: ""
                    }
                })

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