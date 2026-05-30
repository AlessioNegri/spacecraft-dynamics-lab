import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"
import ErrorText from "@renderer/components/dialogs/ErrorText"

interface IFormIn
{
    position: IVector3D
    localSiderealTime: number
    latitude: number
    elevation: number
}

interface IFormOut
{
    positionGeocentricEquatorial: IVector3D // ? Geocentric Equatorial Observer
    positionTopocentricEquatorial: IVector3D // ? Topocentric Equatorial
    positionTopocentricHorizon: IVector3D // ? Topocentric Horizon
    azimuth: number // ? Azimuth
    elevation: number // ? Elevation
    rightAscension: number // ? Right Ascension
    declination: number // ? Declination
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
    positionGeocentricEquatorial: { x: 0, y: 0, z: 0 },
    positionTopocentricEquatorial: { x: 0, y: 0, z: 0 },
    positionTopocentricHorizon: { x: 0, y: 0, z: 0 },
    azimuth: 0,
    elevation: 0,
    rightAscension: 0,
    declination: 0
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function TopocentricFrameDialog */
export default function TopocentricFrameDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---
    
    const [formIn, setFormIn] = react.useState<IFormIn>(defaultIn)
        
    const [formOut, setFormOut] = react.useState<IFormOut>(defaultOut)
    
    const [errors, setErrors] = react.useState<Record<string, string>>({})

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
            http.checkError(import.meta.url, err)
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

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

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
                    name="elevation"
                    label="Elevation Above Sea Level"
                    symbol="H"
                    unit="km"
                    value={formIn.elevation}
                    min={0}
                    onChange={handleChange}
                />

                <span className="col-span-3 text-center uppercase font-semibold">
                    Geocentric Equatorial Position Vector
                </span>

                <InputField
                    name="position.x"
                    symbol="r_x"
                    unit="km"
                    value={formIn.position.x}
                    onChange={handleChange}
                />

                <InputField
                    name="position.y"
                    symbol="r_y"
                    unit="km"
                    value={formIn.position.y}
                    onChange={handleChange}
                />

                <InputField
                    name="position.z"
                    symbol="r_z"
                    unit="km"
                    value={formIn.position.z}
                    onChange={handleChange}
                />

                { errors.position && <ErrorText text={errors.position} /> }
                
            </Form.Root>

            {/* OUTPUT */}

            <Form.Root className="grid grid-cols-3 gap-4 mb-4">

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">
                        Geocentric Equatorial Observer Position Vector
                    </span>

                    <OutputField
                        symbol="r_x"
                        unit="km"
                        value={formOut.positionGeocentricEquatorial.x}
                    />
                
                    <OutputField
                        symbol="r_y"
                        unit="km"
                        value={formOut.positionGeocentricEquatorial.y}
                    />

                    <OutputField
                        symbol="r_z"
                        unit="km"
                        value={formOut.positionGeocentricEquatorial.z}
                    />

                </div>

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">
                        Topocentric Equatorial Position Vector
                    </span>

                    <OutputField
                        symbol="r_x"
                        unit="km"
                        value={formOut.positionTopocentricEquatorial.x}
                    />

                    <OutputField
                        symbol="r_y"
                        unit="km"
                        value={formOut.positionTopocentricEquatorial.y}
                    />

                    <OutputField
                        symbol="r_z"
                        unit="km"
                        value={formOut.positionTopocentricEquatorial.z}
                    />

                </div>

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">
                        Topocentric Horizon Position Vector
                    </span>

                    <OutputField
                        symbol="r_x"
                        unit="km"
                        value={formOut.positionTopocentricHorizon.x}
                    />

                    <OutputField
                        symbol="r_y"
                        unit="km"
                        value={formOut.positionTopocentricHorizon.y}
                    />

                    <OutputField
                        symbol="r_z"
                        unit="km"
                        value={formOut.positionTopocentricHorizon.z}
                    />

                </div>

                <span className="col-span-3 text-center uppercase font-semibold">
                    Orientation
                </span>

                <div className="col-span-full grid grid-cols-4 gap-4">

                    <OutputField
                        symbol="A"
                        label="Azimuth"
                        unit="deg"
                        value={formOut.azimuth}
                    />

                    <OutputField
                        symbol="a"
                        label="Elevation"
                        unit="deg"
                        value={formOut.elevation}
                    />

                    <OutputField
                        symbol="\alpha"
                        label="Right Ascension"
                        unit="deg"
                        value={formOut.rightAscension}
                    />

                    <OutputField
                        symbol="\delta"
                        label="Declination"
                        unit="deg"
                        value={formOut.declination}
                    />

                </div>

            </Form.Root>

        </DialogRUI>
    )
}
