import "react"

declare module "react"
{
    namespace JSX
    {
        interface IntrinsicElements
        {
            "model-viewer": React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> &
            {
                src?: string;
                alt?: string;
                "camera-controls"?: boolean;
                "auto-rotate"?: boolean;
                "shadow-intensity"?: string | number;
                "exposure"?: string | number;
                "environment-image"?: string;
                "poster"?: string;
                "loading"?: string;
                "disable-zoom"?: boolean;
                "interaction-prompt"?: string;
                "ar"?: boolean;
                "ar-modes"?: string;
                "camera-orbit"?: string;
                "field-of-view"?: string;
            }
        }
    }
}
