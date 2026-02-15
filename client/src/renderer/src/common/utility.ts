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

const utility =
{
    initArray
}

export default utility