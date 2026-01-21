import axios from "axios"

/**
 * @description Check the error type, returning either the FastAPI error or null for standard error (printed on console)
 * 
 * @param file File name
 * @param error Error
 * @returns FastAPI error or generic error
 */
export default function checkError(file: string, error: any): string | null
{
    if (axios.isAxiosError(error))
    {
        return error.response?.data?.error ||   // * FastAPI JSONResponse
                error.response?.data ||         // * Fallback
                error.message                   // * Generic Axios message
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