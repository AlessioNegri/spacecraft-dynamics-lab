import * as react from "react"
import * as form from "@radix-ui/react-form"
import * as themes from "@radix-ui/themes"

import http from "@renderer/common/http"
import DialogRUI from "../../DialogRUI"
import InputField from "../../InputField"
import OutputField from "../../OutputField"

interface JulianDayDialogProps
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

export default function JulianDayDialog(props: Readonly<JulianDayDialogProps>): react.JSX.Element
{
    // --- USE STATE ---

    const [timestampIn, setTimestampIn] = react.useState<string>("2004-05-12T14:45:30")

    const [timestampOut, setTimestampOut] = react.useState<string>("")
    
    const [julianDayOut, setJulianDayOut] = react.useState<number>(0)

    const [julianDayIn, setJulianDayIn] = react.useState<number>(2_453_138.115)

    const [longitudeIn, setLongitudeIn] = react.useState<number>(139.8)

    const [localSiderealTimeOut, setLocalSiderealTimeOut] = react.useState<number>(0)

    const [_, setAxiosError] = react.useState<string>("")

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
            const message: string | null = http.checkError(import.meta.url, err)

            if (message) setAxiosError(message)
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
            const message: string | null = http.checkError(import.meta.url, err)

            if (message) setAxiosError(message)
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

            <form.Root className="w-full flex justify-between items-center space-x-4 border-b pb-4 mb-4">

                <div className="flex flex-col space-y-4">

                    <InputField
                        name="timestamp"
                        label="Timestamp"
                        type="datetime-local"
                        value={timestampIn}
                        onChange={(e: react.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setTimestampIn(e.target.value)}
                    />

                    <InputField
                        name="longitude"
                        label="Longitude"
                        unit="DEG"
                        value={longitudeIn}
                        onChange={(e: react.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setLongitudeIn(Number(e.target.value))}
                    />

                </div>

                <themes.Button variant="outline" color="orange" onClick={handleSubmitT2JD}>
                    Convert
                </themes.Button>

                <div className="flex flex-col space-y-4">

                    <OutputField name="julian-day" label="Julian Day" value={julianDayOut} />

                    <OutputField name="local-sidereal-time" label="Local Sidereal Time" unit="DEG" value={localSiderealTimeOut} />

                </div>

            </form.Root>

            {/* JS -> TS */}

            <form.Root className="w-full flex justify-between items-end space-x-4 pb-4 mb-4">

                <InputField
                    name="julian-day"
                    label="Julian Day"
                    value={julianDayIn}
                    onChange={(e: react.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setJulianDayIn(Number(e.target.value))}
                />

                <themes.Button variant="outline" color="orange" onClick={handleSubmitJD2T}>
                    Convert
                </themes.Button>

                <OutputField name="timestamp" label="Timestamp" type="datetime-local" value={timestampOut} />

            </form.Root>

        </DialogRUI>
    )
}
