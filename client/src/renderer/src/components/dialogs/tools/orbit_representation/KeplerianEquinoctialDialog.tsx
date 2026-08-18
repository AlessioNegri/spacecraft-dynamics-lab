import * as react from "react"
import * as Form from "@radix-ui/react-form"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface IFormIn
{
    orbitalElements: IOrbitalElements
}

interface IFormOut
{
    semimajorAxis: number
    eccentricityVectorH: number
    eccentricityVectorK: number
    ascendingNodeVectorP: number
    ascendingNodeVectorQ: number
    periapsisLocation: number
}

const defaultIn: IFormIn =
{
    orbitalElements:
    {
        sam: 0,
        sma: 8350,
        ecc: 0.1976,
        inc: 60,
        raan: 270,
        aop: 45,
        ta: 230
    }
}

const defaultOut: IFormOut =
{
    semimajorAxis: 0,
    eccentricityVectorH: 0,
    eccentricityVectorK: 0,
    ascendingNodeVectorP: 0,
    ascendingNodeVectorQ: 0,
    periapsisLocation: 0
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function KeplerianEquinoctialDialog */
export default function KeplerianEquinoctialDialog(props: Readonly<Props>): react.JSX.Element
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

        if (name.includes("."))
        {
            const [ group, axis ] = name.split(".")

            setFormIn({ ...formIn, [group]: { ...formIn[group], [axis]: value } })

            return
        }

        setFormIn(prev => ({ ...prev, [name]: value }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            const response: any = await http.api.put(`/tools/convert-keplerian-to-equinoctial`, formIn)

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
            title="Keplerian → Equinoctial"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
                {
                    title: "Keplerian → Equinoctial",
                    content:
                        `Convert the Keplerian orbital elements to the standard equinoctial elements.
                        This representation avoids the singularity of classical elements for circular or equatorial orbits.`
                }
            }>

            {/* INPUT */}

            <Form.Root
                ref={formRef}
                onSubmit={handleSubmit}
                className="grid grid-cols-3 gap-4 border-b pb-4 mb-4">

                <span className="col-span-3 text-center uppercase font-semibold">Orbital Elements</span>

                <InputField
                    name="oe.sma"
                    label="Semimajor Axis"
                    symbol="a"
                    unit="km"
                    type="text"
                    value={String(formIn.orbitalElements.sma)}
                    onChange={handleChange}
                    pattern="^(?!0$).*"
                />

                <InputField
                    name="oe.ecc"
                    label="Eccentricity"
                    symbol="e"
                    unit=""
                    value={formIn.orbitalElements.ecc}
                    onChange={handleChange}
                    min={0}
                />

                <InputField
                    type="number"
                    name="oe.inc"
                    label="Inclination"
                    symbol="i"
                    unit="deg"
                    value={formIn.orbitalElements.inc}
                    onChange={handleChange}
                    min={0}
                    max={180}
                />

                <InputField
                    type="number"
                    name="oe.raan"
                    label="Right Ascension of Ascending Node"
                    symbol="\Omega"
                    unit="deg"
                    value={formIn.orbitalElements.raan}
                    onChange={handleChange}
                    min={0}
                    max={360}
                />

                <InputField
                    type="number"
                    name="oe.aop"
                    label="Argument Of Periapsis"
                    symbol="\omega"
                    unit="deg"
                    value={formIn.orbitalElements.aop}
                    onChange={handleChange}
                    min={0}
                    max={360}
                />

                <InputField
                    type="number"
                    name="oe.ta"
                    label="True Anomaly"
                    symbol="\theta"
                    unit="deg"
                    value={formIn.orbitalElements.ta}
                    onChange={handleChange}
                    min={0}
                    max={360}
                />

            </Form.Root>

            {/* OUTPUT */}

            <Form.Root className="grid grid-cols-2 gap-4 mb-4">

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Eccentricity Vector</span>

                    <OutputField
                        symbol="h"
                        value={formOut.eccentricityVectorH}
                    />

                    <OutputField
                        symbol="k"
                        value={formOut.eccentricityVectorK}
                    />

                </div>

                <div className="flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Node Vector</span>

                    <OutputField
                        symbol="p"
                        value={formOut.ascendingNodeVectorP}
                    />

                    <OutputField
                        symbol="q"
                        value={formOut.ascendingNodeVectorQ}
                    />

                </div>

                <div className="col-span-2 flex flex-col gap-4">

                    <span className="text-center uppercase font-semibold">Orbital Parameters</span>

                    <div className="grid grid-cols-2 gap-4">
                        <OutputField
                            label="Semimajor Axis"
                            symbol="a"
                            unit="km"
                            value={formOut.semimajorAxis}
                        />

                        <OutputField
                            label="Location of the periapsis"
                            symbol="l"
                            unit="deg"
                            value={formOut.periapsisLocation}
                        />
                    </div>

                </div>

            </Form.Root>

        </DialogRUI>
    )
}
