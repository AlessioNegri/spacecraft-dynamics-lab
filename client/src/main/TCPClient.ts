// ? TCP client based on Web Socket

import chalk from 'chalk'

/** @class TCP client class */
class TCPClient
{
    // * Members

    private static instance: TCPClient

    private ws: WebSocket | null = null

    // * Public Functions

    /**
     * @summary Retieve the singleton
     * 
     * @returns TCP server
     */
    public static GetInstance(): TCPClient
    {
        if (!TCPClient.instance)
        {
            TCPClient.instance = new TCPClient()
        }

        return TCPClient.instance
    }

    /**
     * @summary Start the web socket
     */
    public start(): void
    {
        this.ws = new WebSocket("ws://127.0.0.1:8000/ws")

        this.ws.onopen = (_: Event) =>
            {
                console.log(chalk.green("Web Socket opened"))
            }
        
        this.ws.onmessage = (event: MessageEvent<any>) =>
            {
                const now = new Date().toISOString();
    
                console.log(now, "Received:", event.data)
            }

        this.ws.onerror = (event: Event) =>
            {
                const err = event as ErrorEvent;

                console.log(chalk.red("Web Socket error:", err.message))
            }

        this.ws.onclose = (_: Event) =>
            {
                console.log(chalk.green("Web Socket closed"))
            }
    }

    /**
     * @summary Stop the web socket
     */
    public stop(): void
    {
        this.ws?.close()
    }

    // * Private Functions

    private constructor() {}
}

export { TCPClient }