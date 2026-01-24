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

interface IDbSpacecraftItem
{
    _id?: string
    name: string
    mass: number
    orbit: IDbOrbit
    image: string | null
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
    image: File | null
}