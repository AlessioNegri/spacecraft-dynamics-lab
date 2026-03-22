import * as react from "react"
import * as form from "@radix-ui/react-form"

import http from "@renderer/common/http"
import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

interface IFormIn
{
    latitude: number
    elevation: number
    localSiderealTime: number[]
    rightAscension: number[]
    declination: number[]
    time: number[]
}

interface IFormOut
{
    position: IVector3D
    velocity: IVector3D
    oe: IOrbitalElements
}

const defaultIn: IFormIn =
{
    latitude: 40,
    elevation: 1,
    localSiderealTime: [44.506, 45, 45.499],
    rightAscension: [43.537, 54.42, 64.318],
    declination: [-8.7833, -12.074, -15.105],
    time: [0, 118.1, 237.58]
}

const defaultOut: IFormOut =
{
    position: { x: 0, y: 0, z: 0 },
    velocity: { x: 0, y: 0, z: 0 },
    oe: { sam: 0, sma: 0, ecc: 0, inc: 0, raan: 0, aop: 0, ta: 0 }
}

interface GaussMethodDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function GaussMethodDialog */
export default function GaussMethodDialog(props: Readonly<GaussMethodDialogProps>): react.JSX.Element
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

        const [ group, index ] = name.split(".")

        console.log(name, value, group, index)

        if (["localSiderealTime", "rightAscension", "declination", "time"].includes(group))
        {
            setFormIn({ ...formIn, [group]: formIn[group].map((v: number, i: number) =>
            {
                console.warn(i, v, index, value)
                return (i === Number(index)) ? Number(value) : v
            })})

            return
        }

        setFormIn({ ...formIn, [name]: value})
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.put(`/tools/predict-gauss-method`, formIn)

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
            title="Predict From Gauss Method"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Gauss Method",
                    content:
                        `Given the direction cosine vectors and the observer's position vectors at 3 times (for which 
                        the altitude and latitude are known), compute the orbital elements.`
                }
            }>

            {/* INPUT */}

            <form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

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
                    value={formIn.elevation}
                    onChange={handleChange}
                />

                <span></span>

                <span className="text-center uppercase font-semibold">Observation 1</span>

                <span className="text-center uppercase font-semibold">Observation 2</span>

                <span className="text-center uppercase font-semibold">Observation 3</span>

                <div className="grid grid-rows-3 gap-4 border-2 border-neutral-700 rounded p-2">

                    <InputField
                        name="time.0"
                        label="Time"
                        unit="S"
                        value={formIn.time[0]}
                        onChange={handleChange}
                    />

                    <InputField
                        name="rightAscension.0"
                        label="Right Ascension"
                        unit="DEG"
                        value={formIn.rightAscension[0]}
                        onChange={handleChange}
                    />
                    
                    <InputField
                        name="declination.0"
                        label="Declination"
                        unit="DEG"
                        value={formIn.declination[0]}
                        onChange={handleChange}
                    />

                    <InputField
                        name="localSiderealTime.0"
                        label="Local Sidereal Time"
                        unit="DEG"
                        value={formIn.localSiderealTime[0]}
                        onChange={handleChange}
                    />

                </div>

                <div className="grid grid-rows-3 gap-4 border-2 border-neutral-700 rounded p-2">

                    <InputField
                        name="time.1"
                        label="Time"
                        unit="S"
                        value={formIn.time[1]}
                        onChange={handleChange}
                    />

                    <InputField
                        name="rightAscension.1"
                        label="Right Ascension"
                        unit="DEG"
                        value={formIn.rightAscension[1]}
                        onChange={handleChange}
                    />

                    <InputField
                        name="declination.1"
                        label="Declination"
                        unit="DEG"
                        value={formIn.declination[1]}
                        onChange={handleChange}
                    />

                    <InputField
                        name="localSiderealTime.1"
                        label="Local Sidereal Time"
                        unit="DEG"
                        value={formIn.localSiderealTime[1]}
                        onChange={handleChange}
                    />

                </div>

                <div className="grid grid-rows-3 gap-4 border-2 border-neutral-700 rounded p-2">

                    <InputField
                        name="time.2"
                        label="Time"
                        unit="S"
                        value={formIn.time[2]}
                        onChange={handleChange}
                    />

                    <InputField
                        name="rightAscension.2"
                        label="Right Ascension"
                        unit="DEG"
                        value={formIn.rightAscension[2]}
                        onChange={handleChange}
                    />

                    <InputField
                        name="declination.2"
                        label="Declination"
                        unit="DEG"
                        value={formIn.declination[2]}
                        onChange={handleChange}
                    />

                    <InputField
                        name="localSiderealTime.2"
                        label="Local Sidereal Time"
                        unit="DEG"
                        value={formIn.localSiderealTime[2]}
                        onChange={handleChange}
                    />

                </div>

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
