import * as react from "react"
import * as form from "@radix-ui/react-form"

import http from "@renderer/common/http"
import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

interface IFormIn
{
    slantRange: number
    azimuth: number
    elevationA: number
    rangeRate: number
    azimuthRate: number
    elevationARate: number
    localSiderealTime: number
    latitude: number
    elevationH: number
}

interface IFormOut
{
    position: IVector3D
    velocity: IVector3D
    oe: IOrbitalElements
}

const defaultIn: IFormIn =
{
    slantRange: 2551,
    azimuth: 90,
    elevationA: 30,
    rangeRate: 0,
    azimuthRate: 0.113,
    elevationARate: 0.05651,
    localSiderealTime: 300,
    latitude: 60,
    elevationH: 0
}

const defaultOut: IFormOut =
{
    position: { x: 0, y: 0, z: 0 },
    velocity: { x: 0, y: 0, z: 0 },
    oe: { sam: 0, sma: 0, ecc: 0, inc: 0, raan: 0, aop: 0, ta: 0 }
}

interface AngleRangeDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function AngleRangeDialog */
export default function AngleRangeDialog(props: Readonly<AngleRangeDialogProps>): react.JSX.Element
{
    // --- USE STATE ---
        
    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)
        
    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    const [_, setAxiosError] = react.useState<string>("")

    // --- USE REF ---
    
    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setFormIn({ ...formIn, [name]: value})
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.put(`/tools/predict-angle-range`, formIn)

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
            title="Predict From Angle Range"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Angle Range",
                    content:
                        `Given the range, azimuth, angular elevation together with their rates relative to an
                        earth-based tracking station (for which the altitude, latitude, and local sidereal times are
                        known), calculate the state vectors in the geocentric equatorial frame.`
                }
            }>

            {/* INPUT */}

            <form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <InputField
                    name="slantRange"
                    label="Slant Range"
                    unit="KM"
                    value={formIn.slantRange}
                    onChange={handleChange}
                />

                <InputField
                    name="azimuth"
                    label="Azimuth"
                    unit="DEG"
                    value={formIn.azimuth}
                    onChange={handleChange}
                />

                <InputField
                    name="elevationA"
                    label="Elevation"
                    unit="DEG"
                    value={formIn.elevationA}
                    onChange={handleChange}
                />

                <InputField
                    name="rangeRate"
                    label="Range Rate"
                    unit="KM / S"
                    value={formIn.rangeRate}
                    onChange={handleChange}
                />

                <InputField
                    name="azimuthRate"
                    label="Azimuth Rate"
                    unit="DEG / S"
                    value={formIn.azimuthRate}
                    onChange={handleChange}
                />

                <InputField
                    name="elevationARate"
                    label="Elevation Rate"
                    unit="DEG / S"
                    value={formIn.elevationARate}
                    onChange={handleChange}
                />

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
                    name="elevationH"
                    label="Elevation Above Sea Level"
                    unit="KM"
                    value={formIn.elevationH}
                    onChange={handleChange}
                />

            </form.Root>

            {/* OUTPUT */}

            <form.Root className="grid grid-cols-3 gap-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Position Vector</span>

                <OutputField name="position.x" label="X" unit="KM" value={formOut.position.x} />

                <OutputField name="position.y" label="Y" unit="KM" value={formOut.position.y} />

                <OutputField name="position.z" label="Z" unit="KM" value={formOut.position.z} />

                <span className="col-span-3 text-center uppercase font-semibold">Velocity Vector</span>

                <OutputField name="velocity.x" label="X" unit="KM / S" value={formOut.velocity.x} />

                <OutputField name="velocity.y" label="Y" unit="KM / S" value={formOut.velocity.y} />

                <OutputField name="velocity.z" label="Z" unit="KM / S" value={formOut.velocity.z} />

                <span className="col-span-3 text-center uppercase font-semibold">Orbital Elements</span>

                <OutputField name="sma" label="Semi-Major Axis" unit="KM" value={formOut.oe.sma} />

                <OutputField name="ecc" label="Eccentricity" value={formOut.oe.ecc} />

                <OutputField name="inc" label="Inclination" unit="DEG" value={formOut.oe.inc} />

                <OutputField name="raan" label="RAAN" unit="DEG" value={formOut.oe.raan} />

                <OutputField name="aop" label="Argument Periapsis" unit="DEG" value={formOut.oe.aop} />

                <OutputField name="ta" label="True Anomaly" unit="DEG" value={formOut.oe.ta} />

            </form.Root>

        </DialogRUI>
    )
}
