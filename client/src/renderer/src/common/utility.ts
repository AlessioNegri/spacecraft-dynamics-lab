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

/**
 * @description Create an array of numbers with given limits
 * 
 * @param start Start
 * @param stop Stop
 * @param points Number of points
 * @returns Array of numbers
 */
function linspace(start: number, stop: number, points: number): number[]
{
    if (points <= 1) return [start]

    const step: number = (stop - start) / (points - 1)

    return Array.from({ length: points }, (_, index) => start + step * index)
}

const utility =
{
    initArray,
    cn,
    linspace
}

export default utility