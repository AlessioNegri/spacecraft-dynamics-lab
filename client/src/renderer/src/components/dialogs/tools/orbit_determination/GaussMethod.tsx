import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

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

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function GaussMethodDialog */
export default function GaussMethodDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---
        
    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)
        
    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        const [ group, index ] = name.split(".")

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
            http.checkError(import.meta.url, err)
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

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <InputField
                    type="number"
                    name="latitude"
                    label="Latitude"
                    symbol="\phi"
                    unit="deg"
                    value={formIn.latitude}
                    min={-90}
                    max={90}
                    onChange={handleChange}
                />

                <InputField
                    type="number"
                    name="elevationH"
                    label="Elevation Above Sea Level"
                    symbol="H"
                    unit="km"
                    value={formIn.elevation}
                    min={0}
                    onChange={handleChange}
                />

                <span></span>

                <span className="text-center uppercase font-semibold">Observation 1</span>

                <span className="text-center uppercase font-semibold">Observation 2</span>

                <span className="text-center uppercase font-semibold">Observation 3</span>

                <div className="grid grid-rows-3 gap-4 border-2 border-neutral-700 rounded p-2">

                    <InputField
                        type="number"
                        name="time.0"
                        label="Time"
                        symbol="t"
                        unit="s"
                        value={formIn.time[0]}
                        min={0}
                        onChange={handleChange}
                    />

                    <InputField
                        type="number"
                        name="rightAscension.0"
                        label="Right Ascension"
                        symbol="\alpha"
                        unit="deg"
                        value={formIn.rightAscension[0]}
                        min={-360}
                        max={360}
                        onChange={handleChange}
                    />
                    
                    <InputField
                        type="number"
                        name="declination.0"
                        label="Declination"
                        symbol="\delta"
                        unit="deg"
                        value={formIn.declination[0]}
                        min={-90}
                        max={90}
                        onChange={handleChange}
                    />

                    <InputField
                        type="number"
                        name="localSiderealTime.0"
                        label="Local Sidereal Time"
                        symbol="\theta"
                        unit="deg"
                        value={formIn.localSiderealTime[0]}
                        min={-360}
                        max={360}
                        onChange={handleChange}
                    />

                </div>

                <div className="grid grid-rows-3 gap-4 border-2 border-neutral-700 rounded p-2">

                    <InputField
                        type="number"
                        name="time.1"
                        label="Time"
                        symbol="t"
                        unit="s"
                        value={formIn.time[1]}
                        min={0}
                        onChange={handleChange}
                    />

                    <InputField
                        type="number"
                        name="rightAscension.1"
                        label="Right Ascension"
                        symbol="\alpha"
                        unit="deg"
                        value={formIn.rightAscension[1]}
                        min={-360}
                        max={360}
                        onChange={handleChange}
                    />

                    <InputField
                        type="number"
                        name="declination.1"
                        label="Declination"
                        symbol="\delta"
                        unit="deg"
                        value={formIn.declination[1]}
                        min={-90}
                        max={90}
                        onChange={handleChange}
                    />

                    <InputField
                        type="number"
                        name="localSiderealTime.1"
                        label="Local Sidereal Time"
                        symbol="\theta"
                        unit="deg"
                        value={formIn.localSiderealTime[1]}
                        min={-360}
                        max={360}
                        onChange={handleChange}
                    />

                </div>

                <div className="grid grid-rows-3 gap-4 border-2 border-neutral-700 rounded p-2">

                    <InputField
                        type="number"
                        name="time.2"
                        label="Time"
                        symbol="t"
                        unit="s"
                        value={formIn.time[2]}
                        min={0}
                        onChange={handleChange}
                    />

                    <InputField
                        type="number"
                        name="rightAscension.2"
                        label="Right Ascension"
                        symbol="\alpha"
                        unit="deg"
                        value={formIn.rightAscension[2]}
                        min={-360}
                        max={360}
                        onChange={handleChange}
                    />

                    <InputField
                        type="number"
                        name="declination.2"
                        label="Declination"
                        symbol="\delta"
                        unit="deg"
                        value={formIn.declination[2]}
                        min={-90}
                        max={90}
                        onChange={handleChange}
                    />

                    <InputField
                        type="number"
                        name="localSiderealTime.2"
                        label="Local Sidereal Time"
                        symbol="\theta"
                        unit="deg"
                        value={formIn.localSiderealTime[2]}
                        min={-360}
                        max={360}
                        onChange={handleChange}
                    />

                </div>

            </Form.Root>

            {/* OUTPUT */}

            <Form.Root className="grid grid-cols-2 gap-4 mb-4">

                <div className="flex flex-col gap-4">
                
                    <span className="text-center uppercase font-semibold">Position Vector</span>

                    <OutputField
                        symbol="r_x"
                        unit="km"
                        value={formOut.position.x}
                    />

                    <OutputField
                        symbol="r_y"
                        unit="km"
                        value={formOut.position.y}
                    />

                    <OutputField
                        symbol="r_z"
                        unit="km"
                        value={formOut.position.z}
                    />

                </div>

                <div className="flex flex-col gap-4">
                
                    <span className="text-center uppercase font-semibold">Velocity Vector</span>

                    <OutputField
                        symbol="v_x"
                        unit="km / s"
                        value={formOut.velocity.x}
                    />

                    <OutputField
                        symbol="v_y"
                        unit="km / s"
                        value={formOut.velocity.y}
                    />

                    <OutputField
                        symbol="v_z"
                        unit="km / s"
                        value={formOut.velocity.z}
                    />

                </div>

                <div className="col-span-full grid grid-cols-3 gap-4">
                
                    <span className="col-span-3 text-center uppercase font-semibold">Orbital Elements</span>

                    <OutputField
                        label="Semimajor Axis"
                        symbol="a"
                        unit="km"
                        value={formOut.oe.sma}
                    />

                    <OutputField
                        label="Eccentricity"
                        symbol="e"
                        value={formOut.oe.ecc}
                    />

                    <OutputField
                        label="Inclination"
                        symbol="i"
                        unit="deg"
                        value={formOut.oe.inc}
                    />

                    <OutputField
                        label="Right Ascension Of Ascending Node"
                        symbol="\Omega"
                        unit="deg"
                        value={formOut.oe.raan}
                    />

                    <OutputField
                        label="Argument Of Periapsis"
                        symbol="\omega"
                        unit="deg"
                        value={formOut.oe.aop}
                    />

                    <OutputField
                        label="True Anomaly"
                        symbol="\theta"
                        unit="deg"
                        value={formOut.oe.ta}
                    />

                </div>

            </Form.Root>

        </DialogRUI>
    )
}
