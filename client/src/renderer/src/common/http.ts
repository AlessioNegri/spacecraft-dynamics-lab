import axios from "axios"

const api = axios.create(
{
    baseURL: "http://127.0.0.1:8000",
    timeout: 10000
})

/**
 * @description Check the error type, returning either the FastAPI error or null for standard error (printed on console)
 * 
 * @param file File name
 * @param error Error
 * @returns FastAPI error or generic error
 */
function checkError(file: string, error: any): string | null
{
    if (axios.isAxiosError(error))
    {
        // * Generic Axios message

        let message: string = error.message + ": "

        // * FastAPI JSONResponse

        if (error.response)
        {
            if (Array.isArray(error.response.data.detail))
            {
                const details: string[] = []

                for (const item of error.response.data.detail)
                {
                    details.push(item.msg + " -> " + item.loc.join('.'))
                }

                message += details.join(' - ')
            }
            else if (error.response.data.error)
            {
                message += error.response.data.error
            }
            else
            {
                message += error.response.data.detail
            }
        }

        globalThis.window.api.error(`[${file}] ${message}`)

        return message
    }
    else
    {
        let message: string = ""

        if      (error instanceof Error)    message = error.message
        else if (typeof error === "string") message = error
        else                                message = JSON.stringify(error)

        globalThis.window.api.error(`[${file}] ${message}`)
    }

    return null
}

const http =
{
    api,
    checkError
}

export default http

// { headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' } }
// { headers: { 'Content-Type': 'multipart/form-data' } }