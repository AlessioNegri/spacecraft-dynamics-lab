import * as react from "react"
import * as Form from "@radix-ui/react-form"
import * as Themes from "@radix-ui/themes"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

export default function JulianDayDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [timestampIn, setTimestampIn] = react.useState<string>("2004-05-12T14:45:30")

    const [timestampOut, setTimestampOut] = react.useState<string>("")
    
    const [julianDayOut, setJulianDayOut] = react.useState<number>(0)

    const [julianDayIn, setJulianDayIn] = react.useState<number>(2_453_138.115)

    const [longitudeIn, setLongitudeIn] = react.useState<number>(139.8)

    const [localSiderealTimeOut, setLocalSiderealTimeOut] = react.useState<number>(0)

    // --- HANDLE ---

    const handleSubmitT2JD = async (e: react.MouseEvent<HTMLButtonElement | HTMLSelectElement>): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            let data = { timestamp: timestampIn, longitude: longitudeIn }

            let response: any = await http.api.put(`/tools/convert-timestamp-to-julian-day`, data)
            
            setJulianDayOut(response.data.julianDay)
            setLocalSiderealTimeOut(response.data.localSiderealTime)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    const handleSubmitJD2T = async (e: react.MouseEvent<HTMLButtonElement | HTMLSelectElement>): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            let response: any = await http.api.put(`/tools/convert-julian-day-to-timestamp`, julianDayIn)
            
            setTimestampOut(response.data)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    // --- RENDERING ---

    return (
        <DialogRUI
            title="Julian Day"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            popup={
                {
                    title: "Julian Day",
                    content:
                        `Converters between UTC timestamp and Julian Day.`
                }
            }>

            {/* TS -> JD */}

            <Form.Root className="w-full flex justify-between items-center space-x-4 border-b pb-4 mb-4">

                <div className="flex flex-col space-y-4">

                    <InputField
                        name="timestamp"
                        label="Timestamp"
                        symbol="t"
                        type="datetime-local"
                        value={timestampIn}
                        onChange={(e: react.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setTimestampIn(e.target.value)}
                    />

                    <InputField
                        type="number"
                        name="longitude"
                        label="Longitude"
                        symbol="\lambda"
                        unit="deg"
                        value={longitudeIn}
                        min={-360}
                        max={360}
                        onChange={(e: react.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setLongitudeIn(Number(e.target.value))}
                    />

                </div>

                <Themes.Button variant="outline" color="orange" onClick={handleSubmitT2JD}>
                    Convert
                </Themes.Button>

                <div className="flex flex-col space-y-4">

                    <OutputField
                        name="julian-day"
                        label="Julian Day"
                        symbol="JD"
                        value={julianDayOut}
                    />

                    <OutputField
                        name="local-sidereal-time"
                        label="Local Sidereal Time"
                        symbol="\theta"
                        unit="deg"
                        value={localSiderealTimeOut}
                    />

                </div>

            </Form.Root>

            {/* JS -> TS */}

            <Form.Root className="w-full flex justify-between items-end space-x-4 pb-4 mb-4">

                <InputField
                    name="julian-day"
                    label="Julian Day"
                    symbol="JD"
                    value={julianDayIn}
                    onChange={(e: react.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setJulianDayIn(Number(e.target.value))}
                />

                <Themes.Button variant="outline" color="orange" onClick={handleSubmitJD2T}>
                    Convert
                </Themes.Button>

                <OutputField
                    name="timestamp"
                    label="Timestamp"
                    symbol="t"
                    type="datetime-local"
                    value={timestampOut}
                />

            </Form.Root>

        </DialogRUI>
    )
}
