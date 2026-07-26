import * as react from "react"
import * as Themes from "@radix-ui/themes"

import DialogRUI from "./DialogRUI"

import omes from "@renderer/assets/references/orbital-mechanics-for-engineering-students.png"
import sfd from "@renderer/assets/references/space-flight-dynamics.png"
// import iar from "@renderer/assets/references/introduction-to-astrodynamic-reentry.png"

interface Reference {
    title: string
    authors: string
    year: number
    publisher: string
    series: string
    isbn: string
    cover: string
    link: string
}

const references: Reference[] =
[
    {
        title: "Orbital Mechanics for Engineering Students",
        authors: "Howard D. Curtis",
        year: 2013,
        publisher: "Elsevier Science",
        series: "Aerospace Engineering",
        isbn: "978-0080977485",
        cover: omes,
        // link: "https://www.google.it/books/edition/Orbital_Mechanics_for_Engineering_Studen/2U9Z8k0TlTYC?hl=it&gbpv=0"
        link: "https://www.elsevier.com/books/orbital-mechanics-for-engineering-students/curtis/9780080977478"
    },
    {
        title: "Space Flight Dynamics",
        authors: "Craig A. Kluever",
        year: 2018,
        publisher: "Wiley",
        series: "Aerospace",
        isbn: "978-1119157823",
        cover: sfd,
        // link: "https://www.google.it/books/edition/Space_Flight_Dynamics/Cp1PDwAAQBAJ?hl=it&gbpv=0"
        link: "https://www.wiley.com/en-us/Space+Flight+Dynamics-p-9781119157823"
    },
    // {
    //     title: "Introduction To Astrodynamic Reentry",
    //     authors: "Kerry D. Hicks",
    //     year: 2009,
    //     publisher: "Books Express Publishing",
    //     series: "",
    //     isbn: "978-1782662433",
    //     cover: iar,
    //     link: "https://www.google.it/books/edition/Introduction_to_Astrodynamic_Reentry/9_5qmQEACAAJ?hl=it"
    // }
]

interface Props {
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function ReferencesDialog */
export default function ReferencesDialog(props: Readonly<Props>): react.JSX.Element
{
    return (
        <DialogRUI
            title="References"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}>

            <Themes.Flex direction="column" gap="4">
                {
                    references.map(ref =>
                        <Themes.Flex
                            key={ref.title}
                            gap="4"
                            align="center"
                            justify="between"
                            direction="row"
                            className="bg-neutral-700/50 rounded p-4 select-text transition-colors hover:bg-neutral-600/50"
                        >

                            <img
                                src={ref.cover}
                                alt={ref.title}
                                className="h-40 object-cover rounded shadow transition-transform duration-300 hover:scale-115 hover:rotate-1"
                                
                            />

                            <Themes.Flex direction="column" align="end">

                                <Themes.Text size="4" weight="bold" className="pb-2">
                                    {ref.title}
                                </Themes.Text>

                                <Themes.Text size="3" className="text-neutral-300">
                                    {ref.authors} — {ref.year}
                                </Themes.Text>

                                <Themes.Text size="3" className="text-neutral-400">
                                    {ref.publisher}
                                </Themes.Text>

                                <Themes.Text size="3" className="text-neutral-500">
                                    Series: {ref.series}
                                </Themes.Text>

                                <Themes.Text size="3" className="text-neutral-500">
                                    ISBN: {ref.isbn}
                                </Themes.Text>

                                <Themes.Link
                                    href={ref.link}
                                    target="_blank"
                                    className="text-orange-300 hover:text-orange-400 mt-2"
                                >
                                    View Book →
                                </Themes.Link>

                            </Themes.Flex>

                        </Themes.Flex>
                    )}

            </Themes.Flex>

        </DialogRUI>
    )
}
