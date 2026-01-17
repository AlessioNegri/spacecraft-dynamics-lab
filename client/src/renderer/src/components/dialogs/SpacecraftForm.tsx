import * as react from "react";
import axios, { AxiosRequestConfig } from 'axios'

export default function SpacecraftForm()
{
    const [form, setForm] = react.useState(
    {
        name: "",
        mass: "",
        orbitalElements:
        {
            semiMajorAxis: "",
            eccentricity: "",
            inclination: "",
            rightAscensionAscendingNode: "",
            argumentPeriapsis: "",
            trueAnomaly: ""
        },
        image: null as File | null,
    });

    const [errors, setErrors] = react.useState<Record<string, string>>({});
    
    const [preview, setPreview] = react.useState<string | null>(null);

    const validate = () =>
    {
        const newErrors: Record<string, string> = {};

        if (!form.name.trim()) newErrors.name = "Name is required";

        if (!form.mass || Number(form.mass) <= 0) newErrors.mass = "Mass must be a positive number";

        const orbitalElements = form.orbitalElements;

        if (!orbitalElements.semiMajorAxis) newErrors.semiMajorAxis = "Semi-major axis required";
        if (!orbitalElements.eccentricity)  newErrors.eccentricity = "Eccentricity required";
        if (!orbitalElements.inclination)   newErrors.inclination = "Inclination required";
        if (!orbitalElements.rightAscensionAscendingNode) newErrors.rightAscensionAscendingNode = "Right Ascension Ascending Node required";
        if (!orbitalElements.argumentPeriapsis)  newErrors.argumentPeriapsis = "Argument Periapsis required";
        if (!orbitalElements.trueAnomaly)   newErrors.trueAnomaly = "True Anomaly required";

        setErrors(newErrors);

        return Object.keys(newErrors).length === 0;
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    {
        const { name, value, files } = e.target;

        if (name === "image" && files)
        {
            const file = files[0];

            setForm({ ...form, image: file });

            const url = URL.createObjectURL(file);

            setPreview(url);

            return;

        }

        if (name in form.orbitalElements)
        {
            setForm({ ...form, orbitalElements: { ...form.orbitalElements, [name]: value } });

            return;
        }

        setForm({ ...form, [name]: value });
    };

    const handleSubmit = async (e: React.FormEvent) =>
    {
        e.preventDefault();

        if (!validate()) return;

        const data = new FormData();

        data.append("name", form.name);
        data.append("mass", form.mass);
        data.append("a", form.orbitalElements.semiMajorAxis);
        data.append("e", form.orbitalElements.eccentricity);
        data.append("i", form.orbitalElements.inclination);
        data.append("OMEGA", form.orbitalElements.rightAscensionAscendingNode);
        data.append("omega", form.orbitalElements.argumentPeriapsis);
        data.append("theta", form.orbitalElements.trueAnomaly);

        if (form.image) data.append("image", form.image);

        let config: AxiosRequestConfig<any> = { headers: { 'Content-Type': 'multipart/form-data' } };

        try {
            const response = await axios.post("http://127.0.0.1:8000/spacecraft/insert", data, config)

            console.log("Upload success:", response.data);
        }
        catch (err)
        {
            console.error("Upload failed:", err)
        }
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="mx-auto p-6 bg-stone-800 text-gray-100 rounded-lg shadow-lg space-y-6">

            {/* Name */}
            <div>
                <label  className="block mb-1 font-medium">Name</label>
                <input
                    type="text"
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    className="w-full px-3 py-2 rounded bg-stone-700 border border-gray-700 focus:border-orange-500 focus:outline-none"
                    placeholder="e.g. Voyager 1"
                />
                {errors.name && <p className="text-red-400 text-sm">{errors.name}</p>}
            </div>

            {/* Mass */}
            <div>
                <label className="block mb-1 font-medium">Mass (kg)</label>
                <input
                    type="number"
                    name="mass"
                    value={form.mass}
                    onChange={handleChange}
                    className="w-full px-3 py-2 rounded bg-stone-700 border border-gray-700 focus:border-orange-500 focus:outline-none"
                    placeholder="e.g. 825"
                />
                {errors.mass && <p className="text-red-400 text-sm">{errors.mass}</p>}
            </div>

            {/* Orbital Elements */}
            <div className="space-y-3">

                <h3 className="text-lg font-semibold">Orbital Elements</h3>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block mb-1">Semi-major axis (km)</label>
                        <input
                            type="number"
                            name="semiMajorAxis"
                            value={form.orbitalElements.semiMajorAxis}
                            onChange={handleChange}
                            className="w-full px-3 py-2 rounded bg-gray-800 border border-gray-700 focus:border-blue-500"
                        />
                        {errors.semiMajorAxis && <p className="text-red-400 text-sm">{errors.semiMajorAxis}</p>}
                    </div>

                    <div>
                        <label className="block mb-1">Eccentricity</label>
                        <input
                            type="number"
                            step="0.0001"
                            name="eccentricity"
                            value={form.orbitalElements.eccentricity}
                            onChange={handleChange}
                            className="w-full px-3 py-2 rounded bg-gray-800 border border-gray-700 focus:border-blue-500"
                        />
                        {errors.eccentricity && <p className="text-red-400 text-sm">{errors.eccentricity}</p>}
                    </div>

                    <div>
                        <label className="block mb-1">Inclination (°)</label>
                        <input
                            type="number"
                            name="inclination"
                            value={form.orbitalElements.inclination}
                            onChange={handleChange}
                            className="w-full px-3 py-2 rounded bg-gray-800 border border-gray-700 focus:border-blue-500"
                        />
                        {errors.inclination && <p className="text-red-400 text-sm">{errors.inclination}</p>}
                    </div>

                    <div>
                        <label className="block mb-1">RAAN (°)</label>
                        <input
                            type="number"
                            name="rightAscensionAscendingNode"
                            value={form.orbitalElements.rightAscensionAscendingNode}
                            onChange={handleChange}
                            className="w-full px-3 py-2 rounded bg-gray-800 border border-gray-700 focus:border-blue-500"
                        />
                        {errors.rightAscensionAscendingNode && <p className="text-red-400 text-sm">{errors.rightAscensionAscendingNode}</p>}
                    </div>

                    <div>
                        <label className="block mb-1">Argument of Periapsis (°)</label>
                        <input
                            type="number"
                            name="argumentPeriapsis"
                            value={form.orbitalElements.argumentPeriapsis}
                            onChange={handleChange}
                            className="w-full px-3 py-2 rounded bg-gray-800 border border-gray-700 focus:border-blue-500"
                        />
                        {errors.argumentPeriapsis && <p className="text-red-400 text-sm">{errors.argumentPeriapsis}</p>}
                    </div>

                    <div>
                        <label className="block mb-1">True Anomaly (°)</label>
                        <input
                            type="number"
                            name="trueAnomaly"
                            value={form.orbitalElements.trueAnomaly}
                            onChange={handleChange}
                            className="w-full px-3 py-2 rounded bg-gray-800 border border-gray-700 focus:border-blue-500"
                        />
                        {errors.trueAnomaly && <p className="text-red-400 text-sm">{errors.trueAnomaly}</p>}
                    </div>
                </div>
            </div>

            {/* Image */}
            <div>
                <label className="block mb-1 font-medium">Image</label>
                <input
                    type="file"
                    name="image"
                    accept="image/*"
                    onChange={handleChange}
                    className="w-full text-gray-300"
                />

                {/* Preview */}
                {preview && (
                <div className="mt-3">
                    <img
                    src={preview}
                    alt="Preview"
                    className="w-40 h-40 object-cover rounded border border-gray-700"
                    />
                </div>
                )}

            </div>

            {/* Submit */}
            <button
                type="submit"
                className="w-full py-2 bg-blue-600 hover:bg-blue-700 rounded text-white font-semibold transition"
            >
                Save
            </button>
        </form>
    );
}