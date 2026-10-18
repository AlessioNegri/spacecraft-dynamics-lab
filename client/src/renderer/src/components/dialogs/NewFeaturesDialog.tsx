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
    Orbital Maneuvers Tools menu`,
    `References dialog in Help menu`,
    `GitHub Issues dialog in Help menu`,
    `What's New dialog in Help menu`,
    `Added more than 100 spacecraft models`,
    `Atmosphere model`,
    `Ground track visualization with horizon footprint`,
    `Conversion between Keplerian to Equinoctial Orbital Elements`,
    `New output parameters in Cartesian to Orbit Parameters dialog`,
    `New algorithms in astro Orbital Maneuvers`,
    `Super-Synchronous Transfer dialog in Orbital Maneuvers Tools menu`,
    `New algorithms in astro Relative Motion`,
    `Rendezvous and Docking dialog in Relative Motion Tools menu`,
    `Non-approximated Sphere of Influence calculation in Interplanetary Trajectory Tools menu`,
    `Non-Hohmann Transfer dialog in Interplanetary Trajectory Tools menu`,
    `New flyby scheme algorithm in astro Interplanetary Trajectories`,
    `Circular Restricted 3-Body Problem page linearizations around the libration points`,
    `Vector representations dialog, for different reference frames, in Orbit Representation Tools menu`,
    `Instantaneous access area added to ground track visualization`,
    `Herrick-Gibbs method added to Orbit Determination Tools menu`,
    `New algorithms in astro Orbital Perturbations`,
    `Frozen Orbit & Frozen Sun Synchronous Orbit dialogs in Orbital Perturbations Tools menu`,
    `CIRA72 model added to astro Orbital Perturbations`,
    `Commensurate Orbits dialog in Orbital Perturbations Tools menu`,
    `GPS and GEO Longitudinal Drift dialog in Orbital Perturbations Tools menu`,
    `Drag Orbit Times dialog in Orbital Perturbations Tools menu`,
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
