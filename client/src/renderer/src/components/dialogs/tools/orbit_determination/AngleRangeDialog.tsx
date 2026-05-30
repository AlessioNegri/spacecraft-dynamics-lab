import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

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

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function AngleRangeDialog */
export default function AngleRangeDialog(props: Readonly<Props>): react.JSX.Element
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
            http.checkError(import.meta.url, err)
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

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <InputField
                    type="number"
                    name="slantRange"
                    label="Slant Range"
                    symbol="\rho"
                    unit="km"
                    value={formIn.slantRange}
                    min={0}
                    onChange={handleChange}
                />

                <InputField
                    type="number"
                    name="azimuth"
                    label="Azimuth"
                    symbol="A"
                    unit="deg"
                    value={formIn.azimuth}
                    min={-360}
                    max={360}
                    onChange={handleChange}
                />

                <InputField
                    type="number"
                    name="elevationA"
                    label="Elevation"
                    symbol="a"
                    unit="deg"
                    value={formIn.elevationA}
                    min={-360}
                    max={360}
                    onChange={handleChange}
                />

                <InputField
                    type="number"
                    name="rangeRate"
                    label="Range Rate"
                    symbol="\dot{\rho}"
                    unit="km / s"
                    value={formIn.rangeRate}
                    min={0}
                    onChange={handleChange}
                />

                <InputField
                    type="number"
                    name="azimuthRate"
                    label="Azimuth Rate"
                    symbol="\dot{A}"
                    unit="deg / s"
                    value={formIn.azimuthRate}
                    min={-360}
                    max={360}
                    onChange={handleChange}
                />

                <InputField
                    type="number"
                    name="elevationARate"
                    label="Elevation Rate"
                    symbol="\dot{a}"
                    unit="deg / s"
                    value={formIn.elevationARate}
                    min={-360}
                    max={360}
                    onChange={handleChange}
                />

                <InputField
                    type="number"
                    name="localSiderealTime"
                    label="Local Sidereal Time"
                    symbol="\theta"
                    unit="deg"
                    value={formIn.localSiderealTime}
                    min={-360}
                    max={360}
                    onChange={handleChange}
                />

                <InputField
                    type="number"
                    name="latitude"
                    label="Latitude"
                    symbol="\phi"
                    unit="deg"
                    value={formIn.latitude}
                    min={-360}
                    max={360}
                    onChange={handleChange}
                />

                <InputField
                    type="number"
                    name="elevationH"
                    label="Elevation Above Sea Level"
                    symbol="H"
                    unit="km"
                    value={formIn.elevationH}
                    min={0}
                    onChange={handleChange}
                />

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
