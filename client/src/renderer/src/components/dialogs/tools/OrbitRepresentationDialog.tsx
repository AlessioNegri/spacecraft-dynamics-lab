import * as react from "react"

import http from "@renderer/common/http"

import Dialog from "../Dialog"
import FormButton from "../FormButton"
import FormSection from "../FormSection"
import FormInput from "../FormInput"
import FormSelect from "../FormSelect"

const defaultKeplerianIn: IKeplerianFormIn =
{
    attractor: "earth",
    semiMajorAxis: 8350,
    eccentricity: 0.1976,
    inclination: 60,
    rightAscensionOfAscendingNode: 270,
    argumentOfPeriapsis: 45,
    trueAnomaly: 230,
    deltaTime: 45 * 60
}

type FormIn = IKeplerianFormIn

const defaultGeocentricEquatorialOut: IGeocentricEquatorialFormOut =
{
    positionX: 0,
    positionY: 0,
    positionZ: 0,
    velocityX: 0,
    velocityY: 0,
    velocityZ: 0
}

const defaultGroundTrackOut: IGroundTrackFormOut =
{
    rightAscensionOfAscendingNodeVariation: 0,
    argumentOfPeriapsisVariation: 0,
    rightAscension: 0,
    declination: 0
}

type FormOut = 
                
                
                IGeocentricEquatorialFormOut |
                IGroundTrackFormOut

interface OrbitRepresentationDialogProps
{
    onClose: () => void
    onOk: () => void
}

/** @function DeleteSpacecraftDialog */
export default function OrbitRepresentationDialog(props: Readonly<OrbitRepresentationDialogProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [converter, setConverter] = react.useState<string>("1")

    const [formIn, setFormIn] = react.useState<FormIn>(defaultKeplerianIn)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    const [formOut, setFormOut] = react.useState<FormOut>(defaultGeocentricEquatorialOut)

    const [axiosError, setAxiosError] = react.useState<string>("")

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        setConverter("4")
        setFormIn(defaultKeplerianIn)
        setFormOut(defaultGeocentricEquatorialOut)
    }, [])

    // --- HANDLE ---

    const validAngle = (angle: number) => { return angle >= 0 && angle <= 360 }

    const validateKeplerian = () : Record<string, string> =>
    {
        const newErrors: Record<string, string> = {}

        const form: IKeplerianFormIn = formIn as IKeplerianFormIn

        if (!String(form.semiMajorAxis).trim())                 newErrors.semiMajorAxis = "Semi-Major Axis is required"
        if (!String(form.eccentricity).trim())                  newErrors.eccentricity = "Eccentricity is required"
        if (!String(form.inclination).trim())                   newErrors.inclination = "Inclination is required"
        if (!String(form.rightAscensionOfAscendingNode).trim()) newErrors.rightAscensionOfAscendingNode = "Right Ascension of Ascending Node is required"
        if (!String(form.argumentOfPeriapsis).trim())           newErrors.argumentOfPeriapsis = "Argument of Periapsis is required"
        if (!String(form.trueAnomaly).trim())                   newErrors.trueAnomaly = "True Anomaly is required"

        if (Number(form.semiMajorAxis) === 0)   newErrors.sma = "Semi-Major Axis must be different from 0"
        if (Number(form.eccentricity) < 0)      newErrors.ecc = "Eccentricity must be a non negative number"
        
        if (!validAngle(form.inclination))                      newErrors.inc   = "Inclination must be in rage [0°, 360°]"
        if (!validAngle(form.rightAscensionOfAscendingNode))    newErrors.raan  = "Right Ascension Ascending Node must be in rage [0°, 360°]"
        if (!validAngle(form.argumentOfPeriapsis))              newErrors.aop   = "Argument Periapsis must be in rage [0°, 360°]"
        if (!validAngle(form.trueAnomaly))                      newErrors.tan   = "True Anomaly must be in rage [0°, 360°]"

        if (converter === "5")
        {
            if (!String(form.deltaTime).trim()) newErrors.deltaTime = "Time delta is required"

            if (Number(form.deltaTime) <= 0) newErrors.deltaTime = "Time delta must be a positive number"
        }

        return newErrors
    }

    const validate = (): boolean =>
    {
        let newErrors: Record<string, string> = {}

        if (["4", "5"].includes(converter))
        {
            newErrors = validateKeplerian()
        }

        setErrors(newErrors)

        return Object.keys(newErrors).length === 0
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    {
        const { name, value } = e.target

        setFormIn({ ...formIn, [name]: value })
    }

    const prepareKeplerianData = () : FormData =>
    {
        const form: IKeplerianFormIn = formIn as IKeplerianFormIn

        const data = new FormData()

        data.append("attractor", form.attractor)
        data.append("semiMajorAxis", String(form.semiMajorAxis))
        data.append("eccentricity", String(form.eccentricity))
        data.append("inclination", String(form.inclination))
        data.append("rightAscensionOfAscendingNode", String(form.rightAscensionOfAscendingNode))
        data.append("argumentOfPeriapsis", String(form.argumentOfPeriapsis))
        data.append("trueAnomaly", String(form.trueAnomaly))

        if (converter === "5")
        {
            data.append("deltaTime", String(form.deltaTime))
        }

        return data
    }

    const convertPerifocalToGeocentricEquatorial = async (data: FormData) =>
    {
        let response: any = await http.api.put(`/tools/convert-perifocal-to-geocentric-equatorial`, data)

        const result: IGeocentricEquatorialFormOut =
        {
            positionX: response.data["positionX"],
            positionY: response.data["positionY"],
            positionZ: response.data["positionZ"],
            velocityX: response.data["velocityX"],
            velocityY: response.data["velocityY"],
            velocityZ: response.data["velocityZ"]
        }

        setFormOut(result)
    }

    const propagateGroundTrack = async (data: FormData) =>
    {
        let response: any = await http.api.put(`/tools/propagate-ground-track`, data)

        const result: IGroundTrackFormOut =
        {
            rightAscensionOfAscendingNodeVariation: response.data["rightAscensionOfAscendingNodeVariation"],
            argumentOfPeriapsisVariation: response.data["argumentOfPeriapsisVariation"],
            rightAscension: response.data["rightAscension"],
            declination: response.data["declination"]
        }

        setFormOut(result)
    }

    const handleConvert = async (e: React.FormEvent) =>
    {
        e.preventDefault()

        setAxiosError("")

        if (!validate()) return

        let data = new FormData()

        if (["4", "5"].includes(converter))
        {
            data = prepareKeplerianData()
        }

        try
        {
            if (converter === "4")
            {
                await convertPerifocalToGeocentricEquatorial(data)
            }
            else if (converter === "5")
            {
                await propagateGroundTrack(data)
            }
        }
        catch (err)
        {
            const message: string | null = http.checkError(import.meta.url, err)

            if (message) setAxiosError(message)
        }
    }

    // --- RENDERING ---

    return (
        <Dialog title="Orbit Representation" onClose={() => { props.onClose() }} >

            <FormSelect
                label="Converter"
                name="converter"
                value={converter}
                setValue={(e: React.ChangeEvent<HTMLSelectElement>) =>
                {
                    setConverter(e.target.value)

                    if (["4", "5"].includes(e.target.value)) setFormIn(defaultKeplerianIn)

                    if (e.target.value === "4") setFormOut(defaultGeocentricEquatorialOut)
                    else if (e.target.value === "5") setFormOut(defaultGroundTrackOut)
                }}
                options={
                    [
                        { name: "Perifocal → Geocentric Equatorial", value: "4" },
                        { name: "Ground Track Propagation", value: "5" }
                    ]}
            />

            <form
                id="conversion-form"
                onSubmit={handleConvert}
                className="mx-auto p-6 bg-neutral-800 text-neutral-100 rounded-lg shadow-lg space-y-6 overflow-auto
                            max-h-[80vh] custom-scrollbar">

                {/* Specific input data */}

                {
                    ["4", "5"].includes(converter) &&
                    <KeplerianFormIn
                        converter={converter}
                        params={formIn as IKeplerianFormIn}
                        errors={errors}
                        handleChange={handleChange}
                    />
                }

                <p className="border-b-2 border-neutral-300"></p>

                {/* Specific output data */}

                { converter === "4" && <GeocentricEquatorialFormOut params={formOut as IGeocentricEquatorialFormOut} /> }

                { converter === "5" && <GroundTrackFormOut params={formOut as IGroundTrackFormOut} /> }

            </form>

            <div className="flex justify-center">
            
                <FormButton text="Convert" color="blue" type="submit" form="conversion-form" />

            </div>

            {
                axiosError && <p className="text-red-400 text-sm select-text">{axiosError}</p>
            }

        </Dialog>
    )
}

// --- IN ---

interface KeplerianFormInProps
{
    converter: string
    params: IKeplerianFormIn
    errors: Record<string, string>
    handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
}

/** @function KeplerianFormIn */
function KeplerianFormIn(props: Readonly<KeplerianFormInProps>): react.JSX.Element
{
    return (
        <>
            <FormSelect
                label="Attractor"
                name="attractor"
                value={props.params.attractor}
                setValue={props.handleChange}
                options={
                    [
                        { name: "Mercury", value: "mercury" },
                        { name: "Venus", value: "venus" },
                        { name: "Earth", value: "earth" },
                        { name: "Mars", value: "mars" },
                        { name: "Jupiter", value: "jupiter" },
                        { name: "Saturn", value: "saturn" },
                        { name: "Uranus", value: "uranus" },
                        { name: "Neptune", value: "neptune" }
                    ]}
            />

            <FormSection title="Keplerian" className="grid grid-cols-3 space-x-4 mt-4">

                <FormInput
                    label="Semi-Major Axis [ km ]"
                    type="number"
                    name="semiMajorAxis"
                    value={props.params.semiMajorAxis}
                    error={props.errors.semiMajorAxis}
                    setValue={props.handleChange}
                />

                <FormInput
                    label="Eccentricity"
                    type="number"
                    name="eccentricity"
                    value={props.params.eccentricity}
                    error={props.errors.eccentricity}
                    setValue={props.handleChange}
                />

                <FormInput
                    label="Inclination [ deg ]"
                    type="number"
                    name="inclination"
                    value={props.params.inclination}
                    error={props.errors.inclination}
                    setValue={props.handleChange}
                />

                <FormInput
                    label="RAAN [ deg ]"
                    type="number"
                    name="rightAscensionOfAscendingNode"
                    value={props.params.rightAscensionOfAscendingNode}
                    error={props.errors.rightAscensionOfAscendingNode}
                    setValue={props.handleChange}
                />

                <FormInput
                    label="Argument of Periapsis [ deg ]"
                    type="number"
                    name="argumentOfPeriapsis"
                    value={props.params.argumentOfPeriapsis}
                    error={props.errors.argumentOfPeriapsis}
                    setValue={props.handleChange}
                />

                <FormInput
                    label="True Anomaly [ deg ]"
                    type="number"
                    name="trueAnomaly"
                    value={props.params.trueAnomaly}
                    error={props.errors.trueAnomaly}
                    setValue={props.handleChange}
                />

                {
                    props.converter === "5" && (
                        <FormInput
                            label="Time Delta [ s ]"
                            type="number"
                            name="deltaTime"
                            value={props.params.deltaTime}
                            error={props.errors.deltaTime}
                            setValue={props.handleChange}
                        />
                    )
                }

            </FormSection>

        </>
    )
}

// --- OUT ---

interface GeocentricEquatorialFormOutProps
{
    params: IGeocentricEquatorialFormOut
}

/** @function GeocentricEquatorialFormOut */
function GeocentricEquatorialFormOut(props: Readonly<GeocentricEquatorialFormOutProps>): react.JSX.Element
{
    return (
        <FormSection title="Geocentric Equatorial" className="grid grid-cols-3 space-x-4 space-y-4">

            <FormInput
                label="Position X [ km ]"
                type="number"
                readonly={true}
                value={props.params.positionX}
            />

            <FormInput
                label="Position Y [ km ]"
                type="number"
                readonly={true}
                value={props.params.positionY}
            />

            <FormInput
                label="Position Z [ km ]"
                type="number"
                readonly={true}
                value={props.params.positionZ}
            />

            <FormInput
                label="Velocity X [ km / s ]"
                type="number"
                readonly={true}
                value={props.params.velocityX}
            />

            <FormInput
                label="Velocity Y [ km / s ]"
                type="number"
                readonly={true}
                value={props.params.velocityY}
            />

            <FormInput
                label="Velocity Z [ km / s ]"
                type="number"
                readonly={true}
                value={props.params.velocityZ}
            />

            <span></span>

        </FormSection>
    )
}

interface GroundTrackFormOutProps
{
    params: IGroundTrackFormOut
}

/** @function GroundTrackFormOut */
function GroundTrackFormOut(props: Readonly<GroundTrackFormOutProps>): react.JSX.Element
{
    return (
        <FormSection title="Ground Track Propagation" className="grid grid-cols-2 space-x-4 space-y-4">

            <FormInput
                label="RAAN Variation [ deg / day ]"
                type="number"
                readonly={true}
                value={props.params.rightAscensionOfAscendingNodeVariation}
            />

            <FormInput
                label="Argument of Periapsis Variation [ deg / day ]"
                type="number"
                readonly={true}
                value={props.params.argumentOfPeriapsisVariation}
            />

            <FormInput
                label="Right Ascension [ deg ]"
                type="number"
                readonly={true}
                value={props.params.rightAscension}
            />

            <FormInput
                label="Declination [ deg ]"
                type="number"
                readonly={true}
                value={props.params.declination}
            />

            <span></span>

        </FormSection>
    )
}