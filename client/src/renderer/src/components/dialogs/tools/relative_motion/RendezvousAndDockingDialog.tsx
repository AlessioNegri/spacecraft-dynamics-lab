import * as react from "react"
import * as Form from "@radix-ui/react-form"
import * as themes from "@radix-ui/themes"

import http from "@renderer/common/http"

import DialogRUI from "@renderer/components/dialogs/DialogRUI"
import InputField from "@renderer/components/dialogs/InputField"
import OutputField from "@renderer/components/dialogs/OutputField"

const defaultIn: IRendezvousAndDockingFormInput =
{
    timestamp: "2026-01-01T00:00:00",
    launchSiteLatitude: 28.5,
    launchSiteLongitude: -80.6,
    targetInclination: 28.5,
    targetRaan: 0,
    chaserSemimajorAxis: 6718,
    targetSemimajorAxis: 6728,
    closingDistance: 1,
    closingStrategy: "V_BAR_POS",
    closingTrajectory: "ELLIPTIC",
    cycloidalRevolutions: 1,
    closingInitialVelocity: 0,
    finalApproachDistance: 0.01,
    finalApproachTime: 600,
    finalApproachStrategy: "V_BAR_POS"
}

const defaultOut: IRendezvousAndDockingFormOutput =
{
    launchPhaseAscending: 0,
    launchPhaseDescending: 0,
    phasingAngle: 0,
    phasingDistance: 0,
    homingAngle: 0,
    homingDeltaVelocity: 0,
    closingDeltaVelocity: 0,
    finalApproachDeltaVelocity: 0
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function RendezvousAndDockingDialog */
export default function RendezvousAndDockingDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- USE STATE ---

    const [formIn, setFormIn] = react.useState<IRendezvousAndDockingFormInput>(defaultIn)

    const [formOut, setFormOut] = react.useState<IRendezvousAndDockingFormOutput>(defaultOut)

    // --- USE REF ---

    const formRef = react.useRef<HTMLFormElement>(null)

    // --- HANDLE ---

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>): void =>
    {
        const { name, value } = e.target

        setFormIn(prev =>
        ({
            ...prev,
            [name]: value
        }))
    }

    const handleSubmit = async (e: React.FormEvent): Promise<void> =>
    {
        e.preventDefault()

        try
        {
            const response: any = await http.api.put("/relative-motion/rendezvous-and-docking", formIn)

            setFormOut(response.data)
        }
        catch (err)
        {
            http.checkError(import.meta.url, err)
        }
    }

    return (
        <DialogRUI
            title="Rendezvous and Docking"
            button="Compute"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => formRef.current?.requestSubmit()}
            popup={
            {
                title: "Rendezvous and Docking",
                content:
                    "Compute the launch, phasing, homing, closing, and final approach phases of a rendezvous sequence."
            }}
        >
            <Form.Root ref={formRef} onSubmit={handleSubmit}>

                <themes.Tabs.Root
                    defaultValue="launch"
                    className="w-full"
                >

                    <themes.Tabs.List>

                        <themes.Tabs.Trigger value="launch">Launch</themes.Tabs.Trigger>

                        <themes.Tabs.Trigger value="phasing">Phasing and Homing</themes.Tabs.Trigger>

                        <themes.Tabs.Trigger value="closing">Closing</themes.Tabs.Trigger>
                        
                        <themes.Tabs.Trigger value="final-approach">Final Approach</themes.Tabs.Trigger>

                    </themes.Tabs.List>

                    <themes.Box pt="4">

                        <themes.Tabs.Content value="launch" className="grid grid-cols-3 gap-4">

                            <InputField
                                name="timestamp"
                                label="UTC Timestamp"
                                symbol="t"
                                type="datetime-local"
                                value={formIn.timestamp}
                                onChange={handleChange}
                            />

                            <InputField
                                name="launchSiteLatitude"
                                label="Site Latitude"
                                symbol="\phi"
                                unit="deg"
                                type="number"
                                value={formIn.launchSiteLatitude}
                                onChange={handleChange}
                            />

                            <InputField
                                name="launchSiteLongitude"
                                label="Site Longitude"
                                symbol="\lambda"
                                unit="deg"
                                type="number"
                                value={formIn.launchSiteLongitude}
                                onChange={handleChange}
                            />

                            <InputField
                                name="targetInclination"
                                label="Target Inclination"
                                symbol="i"
                                unit="deg"
                                type="number"
                                value={formIn.targetInclination}
                                onChange={handleChange}
                            />

                            <InputField
                                name="targetRaan"
                                label="Target RAAN"
                                symbol="\Omega"
                                unit="deg"
                                type="number"
                                value={formIn.targetRaan}
                                onChange={handleChange}
                            />

                            <div className="col-span-3 border-t pt-4 mt-2" />

                            <OutputField
                                label="Launch Ascending"
                                symbol="t_+"
                                unit="s"
                                value={formOut.launchPhaseAscending}
                            />

                            <OutputField
                                label="Launch Descending"
                                symbol="t_-"
                                unit="s"
                                value={formOut.launchPhaseDescending}
                            />

                        </themes.Tabs.Content>

                        <themes.Tabs.Content value="phasing" className="grid grid-cols-3 gap-4">

                            <InputField
                                name="chaserSemimajorAxis"
                                label="Chaser Semimajor Axis"
                                symbol="a_C"
                                unit="km"
                                type="number"
                                value={formIn.chaserSemimajorAxis}
                                onChange={handleChange}
                            />

                            <InputField
                                name="targetSemimajorAxis"
                                label="Target Semimajor Axis"
                                symbol="a_T"
                                unit="km"
                                type="number"
                                value={formIn.targetSemimajorAxis}
                                onChange={handleChange}
                            />

                            <div className="col-span-3 border-t pt-4 mt-2" />

                            <OutputField
                                label="Phasing Angle"
                                symbol="\Delta\theta"
                                unit="deg"
                                value={formOut.phasingAngle}
                            />

                            <OutputField
                                label="Phasing Distance"
                                symbol="\Delta x"
                                unit="km"
                                value={formOut.phasingDistance}
                            />

                            <OutputField
                                label="Homing Angle"
                                symbol="\theta_i"
                                unit="deg"
                                value={formOut.homingAngle}
                            />

                            <OutputField
                                label="Homing Delta-V"
                                symbol="\Delta v"
                                unit="m/s"
                                value={formOut.homingDeltaVelocity}
                            />

                        </themes.Tabs.Content>

                        <themes.Tabs.Content value="closing" className="grid grid-cols-3 gap-4">

                            <InputField
                                name="closingDistance"
                                label="Distance"
                                symbol="d"
                                unit="km"
                                type="number"
                                value={formIn.closingDistance}
                                onChange={handleChange}
                            />

                            <InputField
                                name="closingInitialVelocity"
                                label="Initial Relative Velocity"
                                symbol="v_0"
                                unit="km/s"
                                type="number"
                                value={formIn.closingInitialVelocity}
                                onChange={handleChange}
                            />

                            <InputField
                                name="cycloidalRevolutions"
                                label="Cycloidal Revolutions"
                                symbol="N"
                                type="number"
                                value={formIn.cycloidalRevolutions}
                                onChange={handleChange}
                            />

                            <InputField
                                name="closingStrategy"
                                label="Strategy"
                                type="select"
                                value={formIn.closingStrategy}
                                onChange={handleChange}
                                options={[
                                    { label: "R-bar +", value: "R_BAR_POS" },
                                    { label: "R-bar -", value: "R_BAR_NEG" },
                                    { label: "V-bar +", value: "V_BAR_POS" },
                                    { label: "V-bar -", value: "V_BAR_NEG" }
                                ]}
                            />

                            <InputField
                                name="closingTrajectory"
                                label="Trajectory"
                                type="select"
                                value={formIn.closingTrajectory}
                                onChange={handleChange}
                                options={[
                                    { label: "Elliptic", value: "ELLIPTIC" },
                                    { label: "Cycloidal", value: "CYCLOIDAL" }
                                ]}
                            />

                            <div className="col-span-3 border-t pt-4 mt-2" />

                            <OutputField
                                label="Closing Delta-V"
                                symbol="\Delta v"
                                unit="m/s"
                                value={formOut.closingDeltaVelocity}
                            />

                        </themes.Tabs.Content>

                        <themes.Tabs.Content value="final-approach" className="grid grid-cols-3 gap-4">

                            <InputField
                                name="finalApproachDistance"
                                label="Distance"
                                symbol="d"
                                unit="km"
                                type="number"
                                value={formIn.finalApproachDistance}
                                onChange={handleChange}
                            />

                            <InputField
                                name="finalApproachTime"
                                label="Time"
                                symbol="t"
                                unit="s"
                                type="number"
                                value={formIn.finalApproachTime}
                                onChange={handleChange}
                            />

                            <InputField
                                name="finalApproachStrategy"
                                label="Strategy"
                                type="select"
                                value={formIn.finalApproachStrategy}
                                onChange={handleChange}
                                options={[
                                    { label: "R-bar +", value: "R_BAR_POS" },
                                    { label: "R-bar -", value: "R_BAR_NEG" },
                                    { label: "V-bar +", value: "V_BAR_POS" },
                                    { label: "V-bar -", value: "V_BAR_NEG" }
                                ]}
                            />

                            <div className="col-span-3 border-t pt-4 mt-2" />

                            <OutputField
                                label="Final Approach Delta-V"
                                symbol="\Delta v"
                                unit="m/s"
                                value={formOut.finalApproachDeltaVelocity}
                            />

                        </themes.Tabs.Content>

                    </themes.Box>

                </themes.Tabs.Root>
                
            </Form.Root>

        </DialogRUI>
    )
}
