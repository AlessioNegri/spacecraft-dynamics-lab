/** @class Singleton class */
export default abstract class Singleton<T>
{
    // --- MEMBER ---

    private static _instances = new Map<Function, any>()

    // --- STATIC ---

    /**
     * @description Manage a single istance for a derived class
     * 
     * @param this Derived class object
     * @returns Singleton
     */
    static GetInstance<T>(this: new () => T): T
    {
        let instance = Singleton._instances.get(this)

        if (!instance)
        {
            instance = new this()

            Singleton._instances.set(this, instance)
        }

        return instance;
    }

    // --- PROTECTED ---

    /**
     * @description Constructor
     */
    protected constructor()
    {
        // * Prevent direct instantiation

        const ctor = this.constructor

        if (Singleton._instances.has(ctor))
        {
            throw new Error(`${ctor.name} is a singleton and already instantiated`);
        }

        Singleton._instances.set(ctor, this);
    }
}