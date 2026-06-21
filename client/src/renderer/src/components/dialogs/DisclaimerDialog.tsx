import * as react from "react"

import DialogRUI from "./DialogRUI"

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function DisclaimerDialog */
export default function DisclaimerDialog(props: Readonly<Props>): react.JSX.Element
{
    return (
        <DialogRUI
            title="Disclaimer"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}>

            <div className="flex flex-col custom-font p-4 space-y-4 text-justify text-neutral-300">

                <p>
                    The Spacecraft Dynamics Lab (SDL) software is provided for educational and research
                    purposes only. While every effort has been made to ensure the accuracy of the
                    calculations and information contained herein, SDL is provided "as is" without
                    warranty of any kind, express or implied.
                </p>

                <p>
                    The author disclaims all liability for any direct, indirect, incidental, consequential,
                    or special damages arising from the use of this software, including but not limited to
                    loss of data, loss of profits, or damage to equipment. Users should independently verify
                    results before relying on them for operational, engineering, or safety-critical decisions.
                </p>

                <p>
                    This software is not intended for real spacecraft operations, mission planning,
                    navigation, control, or any activity where inaccurate results could lead to harm or
                    mission failure. It does not replace consultation with qualified engineers, scientists,
                    or regulatory authorities.
                </p>

                <p className="text-sm text-neutral-400">
                    By using this application you acknowledge that you have read and understood
                    this disclaimer.
                </p>

            </div>

        </DialogRUI>
    )
}
