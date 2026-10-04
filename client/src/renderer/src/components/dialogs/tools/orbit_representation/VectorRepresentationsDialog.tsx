import * as react from "react"
import * as Form from "@radix-ui/react-form"
import * as themes from "@radix-ui/themes"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

const defaultIn: IVectorRepresentationsFormInput =
{
    orbitalElements:
    {
        sam: 0,
        sma: 0,
        ecc: 0,
        inc: 60,
        raan: 270,
        aop: 45,
        ta: 230
    },
    flightPathAngle: 0,
    positionMagnitude: 8000,
    velocityMagnitude: 7.5
}

const defaultOut: IVectorRepresentationsFormOutput =
{
    positionIJK: { x: 0, y: 0, z: 0 },
    positionPQW: { x: 0, y: 0, z: 0 },
    positionNTW: { x: 0, y: 0, z: 0 },
    positionRSW: { x: 0, y: 0, z: 0 },
    velocityIJK: { x: 0, y: 0, z: 0 },
    velocityPQW: { x: 0, y: 0, z: 0 },
    velocityNTW: { x: 0, y: 0, z: 0 },
    velocityRSW: { x: 0, y: 0, z: 0 }
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function VectorRepresentationsDialog */
export default function VectorRepresentationsDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IVectorRepresentationsFormInput>(defaultIn)

    const [formOut, setFormOut] = react.useState<IVectorRepresentationsFormOutput>(defaultOut)

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>): void =>
    {
        const { name, value } = e.target

        if (name.startsWith("orbitalElements."))
        {
            const element = name.split(".")[1] as keyof IOrbitalElements

            setFormIn(prev => ({ ...prev, orbitalElements: { ...prev.orbitalElements, [element]: Number(value) } }))

            return
        }

        setFormIn(prev => ({ ...prev, [name]: Number(value) }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            const response: any = await http.api.put("/tools/vector-representations", formIn)

            setFormOut(response.data)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- RENDERING ---

    const renderVector = (label: string, vector: IVector3D, unit: string): react.JSX.Element =>
    (
        <div className="flex flex-col gap-3">

            <span className="text-center uppercase font-semibold">{label}</span>

            <OutputField
                label="X"
                symbol="x"
                unit={unit}
                value={vector.x}
            />

            <OutputField
                label="Y"
                symbol="y"
                unit={unit}
                value={vector.y}
            />

            <OutputField
                label="Z"
                symbol="z"
                unit={unit}
                value={vector.z}
            />

        </div>
    )

    return (
        <DialogRUI
            title="Vector Representations"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup=
            {{
                title: "Vector Representations",
                content: `Calculate position and velocity vectors in the Equatorial Coordinate System (IJK), Perifocal
                Coordinate System (PQW), Satellite Coordinate System (NTW), and Satellite Coordinate System (RSW)
                reference frames.`
            }}
        >

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
            >

                <div className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">
                    
                    <InputField
                        name="orbitalElements.inc"
                        label="Inclination"
                        symbol="i"
                        unit="deg"
                        type="number"
                        value={formIn.orbitalElements.inc}
                        onChange={handleChange}
                    />

                    <InputField
                        name="orbitalElements.raan"
                        label="Right Ascension of Ascending Node"
                        symbol="\Omega"
                        unit="deg"
                        type="number"
                        value={formIn.orbitalElements.raan}
                        onChange={handleChange}
                    />

                    <InputField
                        name="orbitalElements.aop"
                        label="Argument of Periapsis"
                        symbol="\omega"
                        unit="deg"
                        type="number"
                        value={formIn.orbitalElements.aop}
                        onChange={handleChange}
                    />

                    <InputField
                        name="orbitalElements.ta"
                        label="True Anomaly"
                        symbol="\theta"
                        unit="deg"
                        type="number"
                        value={formIn.orbitalElements.ta}
                        onChange={handleChange}
                    />

                    <InputField
                        name="flightPathAngle"
                        label="Flight Path Angle"
                        symbol="\gamma"
                        unit="deg"
                        type="number"
                        value={formIn.flightPathAngle}
                        onChange={handleChange}
                    />

                    <InputField
                        name="positionMagnitude"
                        label="Position Magnitude"
                        symbol="r"
                        unit="km"
                        type="number"
                        value={formIn.positionMagnitude}
                        onChange={handleChange}
                    />

                    <InputField
                        name="velocityMagnitude"
                        label="Velocity Magnitude"
                        symbol="v"
                        unit="km/s"
                        type="number"
                        value={formIn.velocityMagnitude}
                        onChange={handleChange}
                    />

                </div>

                <themes.Tabs.Root
                    defaultValue="position"
                    className="w-full"
                >

                    <themes.Tabs.List>
                        <themes.Tabs.Trigger value="position">Position</themes.Tabs.Trigger>
                        <themes.Tabs.Trigger value="velocity">Velocity</themes.Tabs.Trigger>
                    </themes.Tabs.List>

                    <themes.Box pt="4">

                        <themes.Tabs.Content
                            value="position"
                            className="grid grid-cols-2 gap-4"
                        >
                            {renderVector("Equatorial Coordinate System (IJK)", formOut.positionIJK, "km")}
                            {renderVector("Perifocal Coordinate System (PQW)", formOut.positionPQW, "km")}
                            {renderVector("Satellite Coordinate System (NTW)", formOut.positionNTW, "km")}
                            {renderVector("Satellite Coordinate System (RSW)", formOut.positionRSW, "km")}
                        </themes.Tabs.Content>

                        <themes.Tabs.Content
                            value="velocity"
                            className="grid grid-cols-2 gap-4"
                        >
                            {renderVector("Equatorial Coordinate System (IJK)", formOut.velocityIJK, "km/s")}
                            {renderVector("Perifocal Coordinate System (PQW)", formOut.velocityPQW, "km/s")}
                            {renderVector("Satellite Coordinate System (NTW)", formOut.velocityNTW, "km/s")}
                            {renderVector("Satellite Coordinate System (RSW)", formOut.velocityRSW, "km/s")}
                        </themes.Tabs.Content>

                    </themes.Box>

                </themes.Tabs.Root>

            </Form.Root>
            
        </DialogRUI>
    )
}
