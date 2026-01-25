/// <reference types="vite/client" />

interface IMenuItem
{
    checkable?: boolean
    checked?: boolean
    label?: string
    shortcut?: string
    separator?: boolean
    action?: () => void
}

interface IMenu
{
    label: string
    items: IMenuItem[]
}

interface ISideBarItem
{
    id: string
    label: string
    icon: string
}

interface IDbOrbit
{
    sma: number
    ecc: number
    inc: number
    raan: number
    aop: number
    tan: number
}

interface IDbStyle
{
    width: number
    color: string
}

interface IDbSpacecraftItem
{
    _id?: string
    name: string
    mass: number
    orbit: IDbOrbit
    style: IDbStyle
    image: string | null
    model: string
}

interface ISpacecraftForm
{
    _id?: string
    name: string
    mass: number
    orbit:
    {
        sma: number
        ecc: number
        inc: number
        raan: number
        aop: number
        tan: number
    }
    style:
    {
        width: number
        color: string
    }
    image: File | null
    model: string
}

interface IGlbModel
{
    name: string,
    scale: number,
    minimumPixelSize: number,
    maximumScale: number
}