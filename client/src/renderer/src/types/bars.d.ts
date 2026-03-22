interface IMenuItem
{
    checkable?: boolean
    checked?: boolean
    label?: string
    shortcut?: string
    separator?: boolean
    children?: IMenuItem[]
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