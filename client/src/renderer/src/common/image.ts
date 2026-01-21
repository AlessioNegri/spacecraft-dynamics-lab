/**
 * @description Convert a base64 image i a File object
 * 
 * @param base64 Base64 image
 * @param filename Name of the file
 * @param mimeType Extension of the file
 * @returns File object
 */
export default function base64ToFile(base64: string, filename: string, mimeType: string): File
{
    const byteString = atob(base64)

    const arrayBuffer = new ArrayBuffer(byteString.length)

    const intArray = new Uint8Array(arrayBuffer)

    for (let i = 0; i < byteString.length; i++)
    {
        intArray[i] = byteString.codePointAt(i)!
    }

    return new File([intArray], filename, { type: mimeType })
}