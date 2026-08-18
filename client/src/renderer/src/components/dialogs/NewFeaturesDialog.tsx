import * as react from "react"
import * as Themes from "@radix-ui/themes"
import * as iconify from "@iconify/react"

import DialogRUI from "./DialogRUI"

const newFeatures: string[] =
[
    `Circular Restricted 3-Body Problem page with simulation near a Lagrange point`,
    `Circular Restricted 3-Body Problem Tools menu dialogs for orbit parameters evaluation and Zero Velocity Curves
    representation`,
    `Non-Impulsive maneuvers (Coplanar Circle-to-Circle and Inclination Change) in Orbital Maneuvers page`,
    `Non-Impulsive maneuvers dialog (Coplanar Circle-to-Circle, Inclination Change, and Inclined Circular Orbits) in
    Orbital Maneuvers Tool menu`,
    `References dialog in Help menu`,
    `GitHub Issues dialog in Help menu`,
    `What's New dialog in Help menu`,
    `Added more than 100 spacecraft models`,
    `Atmosphere model`,
    `Ground track visualization with horizon footprint`,
    `Conversion between Keplerian to Equinoctial Orbital Elements`,
    `New output parameters in Cartesian to Orbit Parameters dialog`,
    `New algorithms in astro Orbital Maneuvers`,
    `Super-Synchronous Transfer dialog in Orbital Maneuvers Tool menu`,
]

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function NewFeaturesDialog */
export default function NewFeaturesDialog(props: Readonly<Props>): react.JSX.Element
{
    return (
        <DialogRUI
            title="What's New"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}
        >

            <Themes.Flex direction="column" gap="4">

                {
                    newFeatures.map((feature: string) =>
                    <Themes.Flex
                        key={feature}
                        direction="row"
                        align="center"
                        className="bg-neutral-700/50 rounded p-4 select-text group transition-colors hover:bg-neutral-600/50"
                        gap="2"
                    >

                        <iconify.Icon
                            icon="game-icons:light-bulb"
                            width={30}
                            className="min-w-10
                                transition-all duration-300 ease-out
                                group-hover:text-yellow-300
                                group-hover:animate-[pulse_2.0s_ease-in-out_infinite]
                                group-hover:rotate-12
                                group-hover:drop-shadow-[0_0_6px_rgba(255,255,0,0.7)]
                                group-hover:scale-125
                            "
                        />

                        <Themes.Text size="3" className="text-neutral-300 leading-relaxed">
                            {feature}
                        </Themes.Text>

                    </Themes.Flex>
                )}

            </Themes.Flex>
            
        </DialogRUI>
    )
}
