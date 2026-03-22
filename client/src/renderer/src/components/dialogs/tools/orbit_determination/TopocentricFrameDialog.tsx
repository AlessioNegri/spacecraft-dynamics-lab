import * as react from "react"
import * as form from "@radix-ui/react-form"

import http from "@renderer/common/http"
import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

interface IFormIn
{
    position: IVector3D
    localSiderealTime: number
    latitude: number
    elevation: number
}

interface IFormOut
{
    geo: IVector3D // ? Geocentric Equatorial Observer
    te: IVector3D // ? Topocentric Equatorial
    th: IVector3D // ? Topocentric Horizon
    A: number // ? Azimuth
    a: number // ? Elevation
    alpha: number // ? Right Ascension
    delta: number // ? Declination
}

const defaultIn: IFormIn =
{
    position: { x: -5368, y: -1784, z: 3691 },
    localSiderealTime: 186.7,
    latitude: 20,
    elevation: 0
}

const defaultOut: IFormOut =
{
    geo: { x: 0, y: 0, z: 0 },
    te: { x: 0, y: 0, z: 0 },
    th: { x: 0, y: 0, z: 0 },
    A: 0,
    a: 0,
    alpha: 0,
    delta: 0
}

interface TopocentricFrameDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function TopocentricFrameDialog */
export default function TopocentricFrameDialog(props: Readonly<TopocentricFrameDialogProps>): react.JSX.Element
{
    // --- USE STATE ---
    
    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)
        
    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)
    
    const [errors, setErrors] = react.useState<Record<string, string>>({})

    const [_, setAxiosError] = react.useState<string>("")

    // --- USE REF ---
    
    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const validate = () : boolean =>
    {
        const newErrors: Record<string, string> = {}

        if (formIn.position.x == 0 && formIn.position.y == 0 && formIn.position.z == 0)
        {
            newErrors.position = "Position cannot be [0,0,0]"
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        const [ group, axis ] = name.split(".")

        if (group === "position")
        {
            setFormIn({ ...formIn, [group]: { ...formIn[group], [axis]: value } })

            return
        }

        setFormIn({ ...formIn, [name]: value})
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        if (!validate()) return

        try
        {
            let response: any = await http.api.put(`/tools/topocentric-frame`, formIn)

            const result: IFormOut = response.data
            
            setFormOut(result)
        }
        catch (err)
        {
            const message: string | null = http.checkError(import.meta.url, err)

            if (message) setAxiosError(message)
        }
    }

    // --- RENDERING ---
    
    return (
        <DialogRUI
            title="Topocentric Frame"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Topocentric Frame",
                    content:
                        `Given the Geocentric Equatorial Position vector of an earth-based tracking station (for which 
                        the altitude, latitude, and local sidereal times are known), compute the derived position
                        vectors and the orientation in the sky.`
                }
            }>

            {/* INPUT */}

            <form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <InputField
                    name="localSiderealTime"
                    label="Local Sidereal Time"
                    unit="DEG"
                    value={formIn.localSiderealTime}
                    onChange={handleChange}
                />

                <InputField
                    name="latitude"
                    label="Latitude"
                    unit="DEG"
                    value={formIn.latitude}
                    onChange={handleChange}
                />

                <InputField
                    name="elevation"
                    label="Elevation Above Sea Level"
                    unit="KM"
                    value={formIn.elevation}
                    onChange={handleChange}
                />

                <span className="col-span-3 text-center uppercase font-semibold">
                    Geocentric Equatorial Position Vector
                </span>

                <InputField
                    name="position.x"
                    label="X"
                    unit="KM"
                    value={formIn.position.x}
                    onChange={handleChange}
                />

                <InputField
                    name="position.y"
                    label="Y"
                    unit="KM"
                    value={formIn.position.y}
                    onChange={handleChange}
                />

                <InputField
                    name="position.z"
                    label="Z"
                    unit="KM"
                    value={formIn.position.z}
                    onChange={handleChange}
                />

                {
                    errors.position &&
                    <span className="col-span-3 text-center text-sm text-red-400">{errors.position}</span>
                }
                
            </form.Root>

            {/* OUTPUT */}

            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">
                    Geocentric Equatorial Observer Position Vector
                </span>

                <OutputField name="geo.x" label="X" unit="KM" value={formOut.geo.x} />
                
                <OutputField name="geo.y" label="Y" unit="KM" value={formOut.geo.y} />
    
                <OutputField name="geo.z" label="Z" unit="KM" value={formOut.geo.z} />

                <span className="col-span-3 text-center uppercase font-semibold">
                    Topocentric Equatorial Position Vector
                </span>

                <OutputField name="te.x" label="X" unit="KM" value={formOut.te.x} />
                
                <OutputField name="te.y" label="Y" unit="KM" value={formOut.te.y} />
    
                <OutputField name="te.z" label="Z" unit="KM" value={formOut.te.z} />

                <span className="col-span-3 text-center uppercase font-semibold">
                    Topocentric Horizon Position Vector
                </span>

                <OutputField name="th.x" label="X" unit="KM" value={formOut.th.x} />
                
                <OutputField name="th.y" label="Y" unit="KM" value={formOut.th.y} />
    
                <OutputField name="th.z" label="Z" unit="KM" value={formOut.th.z} />

                <span className="col-span-3 text-center uppercase font-semibold">
                    Orientation
                </span>

                <div className="col-span-full grid grid-cols-4 gap-4">

                    <OutputField name="A" label="Azimuth" unit="DEG" value={formOut.A} />

                    <OutputField name="a" label="Elevation" unit="DEG" value={formOut.a} />

                    <OutputField name="alpha" label="Right Ascension" unit="DEG" value={formOut.alpha} />

                    <OutputField name="delta" label="Declination" unit="DEG" value={formOut.delta} />

                </div>

            </form.Root>

        </DialogRUI>
    )
}
