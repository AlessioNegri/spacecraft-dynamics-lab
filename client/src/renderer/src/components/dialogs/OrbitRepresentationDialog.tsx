import * as react from "react"

import http from "@renderer/common/http"

import Dialog from "./Dialog"
import FormButton from "./FormButton"
import FormSection from "./FormSection"
import FormInput from "./FormInput"
import FormSelect from "./FormSelect"

const defaultCartesianIn: ICartesianFormIn =
{
    attractor: "earth",
    positionX: 8000,
    positionY: 0,
    positionZ: 6000,
    velocityX: 0,
    velocityY: 7,
    velocityZ: 0
}

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

type FormIn = ICartesianFormIn | IKeplerianFormIn

const defaultOrbitParametersOut: IOrbitParametersFormOut =
{
    conicType: "",
    specificAngularMomentum: 0,
    specificMechanicalEnergy: 0,
    eccentricity: 0,
    orbitalPeriod: 0,
    apoapsisRadius: 0,
    periapsisRadius: 0,
    semiMajorAxis: 0,
    semiMinorAxis: 0,
    escapeVelocity: 0,
    infiniteTrueAnomaly: 0,
    hyperbolaAsymptoteAngle: 0,
    turnAngle: 0,
    aimingRadius: 0,
    hyperbolicExcessSpeed: 0,
    characteristicEnergy: 0,
    rightAscension: 0,
    declination: 0
}

const defaultKeplerianOut: IKeplerianFormOut =
{
    specificAngularMomentum: 0,
    semiMajorAxis: 0,
    eccentricity: 0,
    inclination: 0,
    rightAscensionOfAscendingNode: 0,
    argumentOfPeriapsis: 0,
    trueAnomaly: 0
}

const defaultPerifocalOut: IPerifocalFormOut =
{
    positionX: 0,
    positionY: 0,
    velocityX: 0,
    velocityY: 0
}

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

type FormOut = IOrbitParametersFormOut |
                IKeplerianFormOut |
                IPerifocalFormOut |
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

    const [formIn, setFormIn] = react.useState<FormIn>(defaultCartesianIn)

    const [errors, setErrors] = react.useState<Record<string, string>>({})

    const [formOut, setFormOut] = react.useState<FormOut>(defaultOrbitParametersOut)

    const [axiosError, setAxiosError] = react.useState<string>("")

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        setConverter("1")
        setFormIn(defaultCartesianIn)
        setFormOut(defaultOrbitParametersOut)
    }, [])

    // --- HANDLE ---

    const validAngle = (angle: number) => { return angle >= 0 && angle <= 360 }

    const validateCartesian = () : Record<string, string> =>
    {
        const newErrors: Record<string, string> = {}

        const form: ICartesianFormIn = formIn as ICartesianFormIn

        if (!String(form.positionX).trim()) newErrors.positionX = "Position X is required"
        if (!String(form.positionY).trim()) newErrors.positionY = "Position Y is required"
        if (!String(form.positionZ).trim()) newErrors.positionZ = "Position Z is required"

        if (!String(form.velocityX).trim()) newErrors.velocityX = "Velocity X is required"
        if (!String(form.velocityY).trim()) newErrors.velocityY = "Velocity Y is required"
        if (!String(form.velocityZ).trim()) newErrors.velocityZ = "Velocity Z is required"

        if (form.positionX == 0 && form.positionY == 0 && form.positionZ == 0)
        {
            newErrors.positionX = newErrors.positionY = newErrors.positionZ = "Position cannot be 0"
        }

        if (form.velocityX == 0 && form.velocityY == 0 && form.velocityZ == 0)
        {
            newErrors.velocityX = newErrors.velocityY = newErrors.velocityZ = "Velocity cannot be 0"
        }

        return newErrors
    }

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

    const validate = () =>
    {
        let newErrors: Record<string, string> = {}

        if (["1", "2", "3"].includes(converter))
        {
            newErrors = validateCartesian()
        }
        else if (["4", "5"].includes(converter))
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

    const prepareCartesianData = () : FormData =>
    {
        const form: ICartesianFormIn = formIn as ICartesianFormIn

        const data = new FormData()

        data.append("attractor", form.attractor)
        data.append("positionX", String(form.positionX))
        data.append("positionY", String(form.positionY))
        data.append("positionZ", String(form.positionZ))
        data.append("velocityX", String(form.velocityX))
        data.append("velocityY", String(form.velocityY))
        data.append("velocityZ", String(form.velocityZ))

        return data
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

    const convertCartesianToOrbitParameters = async (data: FormData) =>
    {
        let response: any = await http.api.put(`/tools/convert-cartesian-to-orbit-parameters`, data)

        const result: IOrbitParametersFormOut =
        {
            conicType:                  response.data["conicType"],
            specificAngularMomentum:    response.data["specificAngularMomentum"],
            specificMechanicalEnergy:   response.data["specificMechanicalEnergy"],
            eccentricity:               response.data["eccentricity"],
            orbitalPeriod:              response.data["orbitalPeriod"],
            apoapsisRadius:             response.data["apoapsisRadius"],
            periapsisRadius:            response.data["periapsisRadius"],
            semiMajorAxis:              response.data["semiMajorAxis"],
            semiMinorAxis:              response.data["semiMinorAxis"],
            escapeVelocity:             response.data["escapeVelocity"],
            infiniteTrueAnomaly:        response.data["infiniteTrueAnomaly"],
            hyperbolaAsymptoteAngle:    response.data["hyperbolaAsymptoteAngle"],
            turnAngle:                  response.data["turnAngle"],
            aimingRadius:               response.data["aimingRadius"],
            hyperbolicExcessSpeed:      response.data["hyperbolicExcessSpeed"],
            characteristicEnergy:       response.data["characteristicEnergy"],
            rightAscension:             response.data["rightAscension"],
            declination:                response.data["declination"]
        }

        setFormOut(result)
    }

    const convertCartesianToKeplerian = async (data: FormData) =>
    {
        let response: any = await http.api.put(`/tools/convert-cartesian-to-keplerian`, data)

        const result: IKeplerianFormOut =
        {
            specificAngularMomentum:        response.data["specificAngularMomentum"],
            semiMajorAxis:                  response.data["semiMajorAxis"],
            eccentricity:                   response.data["eccentricity"],
            inclination:                    response.data["inclination"],
            rightAscensionOfAscendingNode:  response.data["rightAscensionOfAscendingNode"],
            argumentOfPeriapsis:            response.data["argumentOfPeriapsis"],
            trueAnomaly:                    response.data["trueAnomaly"]
        }

        setFormOut(result)
    }

    const convertCartesianToPerifocal = async (data: FormData) =>
    {
        let response: any = await http.api.put(`/tools/convert-cartesian-to-perifocal`, data)

        const result: IPerifocalFormOut =
        {
            positionX: response.data["positionX"],
            positionY: response.data["positionY"],
            velocityX: response.data["velocityX"],
            velocityY: response.data["velocityY"]
        }

        setFormOut(result)
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

        if (["1", "2", "3"].includes(converter))
        {
            data = prepareCartesianData()
        }
        else if (["4", "5"].includes(converter))
        {
            data = prepareKeplerianData()
        }

        try
        {
            if (converter === "1")
            {
                await convertCartesianToOrbitParameters(data)
            }
            else if (converter === "2")
            {
                await convertCartesianToKeplerian(data)
            }
            else if (converter === "3")
            {
                await convertCartesianToPerifocal(data)
            }
            else if (converter === "4")
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

                    if (["1", "2", "3"].includes(e.target.value)) setFormIn(defaultCartesianIn)
                    else if (["4", "5"].includes(e.target.value)) setFormIn(defaultKeplerianIn)

                    if (e.target.value === "1") setFormOut(defaultOrbitParametersOut)
                    else if (e.target.value === "2") setFormOut(defaultKeplerianOut)
                    else if (e.target.value === "3") setFormOut(defaultPerifocalOut)
                    else if (e.target.value === "4") setFormOut(defaultGeocentricEquatorialOut)
                    else if (e.target.value === "5") setFormOut(defaultGroundTrackOut)
                }}
                options={
                    [
                        { name: "Cartesian → Orbit Parameters", value: "1" },
                        { name: "Cartesian → Keplerian", value: "2" },
                        { name: "Cartesian → Perifocal", value: "3" },
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
                    ["1", "2", "3"].includes(converter) &&
                    <CartesianFormIn
                        params={formIn as ICartesianFormIn}
                        errors={errors}
                        handleChange={handleChange}
                    />
                }

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

                { converter === "1" && <OrbitParametersOut params={formOut as IOrbitParametersFormOut} /> }

                { converter === "2" && <KeplerianFormOut params={formOut as IKeplerianFormOut} /> }

                { converter === "3" && <PerifocalFormOut params={formOut as IPerifocalFormOut} /> }

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

interface CartesianFormInProps
{
    params: ICartesianFormIn
    errors: Record<string, string>
    handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
}

/** @function CartesianFormIn */
function CartesianFormIn(props: Readonly<CartesianFormInProps>): react.JSX.Element
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

            <FormSection title="Position Vector" className="grid grid-cols-3 space-x-4 mt-4">

                <FormInput
                    label="Position X"
                    type="number"
                    name="positionX"
                    value={ props.params.positionX}
                    error={props.errors.positionX}
                    setValue={props.handleChange}
                />

                <FormInput
                    label="Position Y"
                    type="number"
                    name="positionY"
                    value={props.params.positionY}
                    error={props.errors.positionY}
                    setValue={props.handleChange}
                />

                <FormInput
                    label="Position Z"
                    type="number"
                    name="positionZ"
                    value={props.params.positionZ}
                    error={props.errors.positionZ}
                    setValue={props.handleChange}
                />

            </FormSection>

            <FormSection title="Velocity Vector" className="grid grid-cols-3 space-x-4">

                <FormInput
                    label="Velocity X"
                    type="number"
                    name="velocityX"
                    value={props.params.velocityX}
                    error={props.errors.velocityX}
                    setValue={props.handleChange}
                />

                <FormInput
                    label="Velocity Y"
                    type="number"
                    name="velocityY"
                    value={props.params.velocityY}
                    error={props.errors.velocityY}
                    setValue={props.handleChange}
                />

                <FormInput
                    label="Velocity Z"
                    type="number"
                    name="velocityZ"
                    value={props.params.velocityZ}
                    error={props.errors.velocityZ}
                    setValue={props.handleChange}
                />

            </FormSection>

        </>
    )
}

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

interface OrbitParametersOutProps
{
    params: IOrbitParametersFormOut
}

/** @function OrbitParametersOut */
function OrbitParametersOut(props: Readonly<OrbitParametersOutProps>): react.JSX.Element
{
    return (
        <FormSection title="Orbit Parameters" className="grid grid-cols-2 space-x-4 space-y-4">

            <FormInput
                label="Conic Type"
                type="text"
                readonly={true}
                value={props.params.conicType}
            />

            <FormInput
                label="Specific Angular Momentum [ km^2 / s ]"
                type="number"
                readonly={true}
                value={props.params.specificAngularMomentum}
            />

            <FormInput
                label="Specific Mechanical Energy [ km^2 / s^2 ]"
                type="number"
                readonly={true}
                value={props.params.specificMechanicalEnergy}
            />

            <FormInput
                label="Eccentricity"
                type="number"
                readonly={true}
                value={props.params.eccentricity}
            />

            <FormInput
                label="Orbital Period [ s ]"
                type="number"
                readonly={true}
                value={props.params.orbitalPeriod}
            />

            <FormInput
                label="Apoapsis Radius [ km ]"
                type="number"
                readonly={true}
                value={props.params.apoapsisRadius}
            />

            <FormInput
                label="Periapsis Radius [ km ]"
                type="number"
                readonly={true}
                value={props.params.periapsisRadius}
            />

            <FormInput
                label="Semi-Major Axis [ km ]"
                type="number"
                readonly={true}
                value={props.params.semiMajorAxis}
            />

            <FormInput
                label="Semi-Minor Axis [ km ]"
                type="number"
                readonly={true}
                value={props.params.semiMinorAxis}
            />

            <FormInput
                label="Escape Velocity [ km / s ]"
                type="number"
                readonly={true}
                disable={props.params.eccentricity < 1}
                value={props.params.escapeVelocity}
            />

            <FormInput
                label="Infinite True Anomaly [ rad ]"
                type="number"
                readonly={true}
                disable={props.params.eccentricity <= 1}
                value={props.params.infiniteTrueAnomaly}
            />

            <FormInput
                label="Hyperbola Asymptote Angle [ deg ]"
                type="number"
                readonly={true}
                disable={props.params.eccentricity <= 1}
                value={props.params.hyperbolaAsymptoteAngle}
            />

            <FormInput
                label="Turn Angle [ deg ]"
                type="number"
                readonly={true}
                disable={props.params.eccentricity <= 1}
                value={props.params.turnAngle}
            />

            <FormInput
                label="Aiming Radius [ km ]"
                type="number"
                readonly={true}
                disable={props.params.eccentricity <= 1}
                value={props.params.aimingRadius}
            />

            <FormInput
                label="Hyperbolic Excess Speed [ km / s ]"
                type="number"
                readonly={true}
                disable={props.params.eccentricity <= 1}
                value={props.params.hyperbolicExcessSpeed}
            />

            <FormInput
                label="Characteristic Energy [ km^2 / s^2 ]"
                type="number"
                readonly={true}
                disable={props.params.eccentricity <= 1}
                value={props.params.characteristicEnergy}
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

interface KeplerianFormOutProps
{
    params: IKeplerianFormOut
}

/** @function KeplerianFormOut */
function KeplerianFormOut(props: Readonly<KeplerianFormOutProps>): react.JSX.Element
{
    return (
        <FormSection title="Keplerian" className="grid grid-cols-2 space-x-4 space-y-4">

            <FormInput
                label="Specific Angular Momentum [ km^2 / s ]"
                type="number"
                readonly={true}
                value={props.params.specificAngularMomentum}
            />

            <FormInput
                label="Semi-Major Axis [ km ]"
                type="number"
                readonly={true}
                value={props.params.semiMajorAxis}
            />

            <FormInput
                label="Eccentricity"
                type="number"
                readonly={true}
                value={props.params.eccentricity}
            />

            <FormInput
                label="Inclination [ deg ]"
                type="number"
                readonly={true}
                value={props.params.inclination}
            />

            <FormInput
                label="Right Ascension of Ascending Node [ deg ]"
                type="number"
                readonly={true}
                value={props.params.rightAscensionOfAscendingNode}
            />

            <FormInput
                label="Argument of Periapsis [ deg ]"
                type="number"
                readonly={true}
                value={props.params.argumentOfPeriapsis}
            />

            <FormInput
                label="True Anomaly [ deg ]"
                type="number"
                readonly={true}
                value={props.params.trueAnomaly}
            />

            <span></span>

        </FormSection>
    )
}

interface PerifocalFormOutProps
{
    params: IPerifocalFormOut
}

/** @function PerifocalFormOut */
function PerifocalFormOut(props: Readonly<PerifocalFormOutProps>): react.JSX.Element
{
    return (
        <FormSection title="Perifocal" className="grid grid-cols-2 space-x-4 space-y-4">

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

            <span></span>
        
        </FormSection>
    )
}

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