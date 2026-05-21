import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * @description Initialize a 2D array
 * 
 * @param size1 Size 1
 * @param size2 Size 2
 * @returns 2D Array
 */
function initArray(size1: number, size2: number) : number[][]
{
    return Array.from({ length: size1 }, () => Array.from({ length: size2 }, () => 0) )
}

/**
 * @description Format className property
 *
 * @param inputs List of props
 * @returns Formatted props
 */
export function cn(...inputs: any[])
{
    return twMerge(clsx(inputs))
}


const utility =
{
    initArray,
    cn
}

export default utility