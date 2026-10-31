import abc

class Singleton(abc.ABC):

    _instances = {}

    def __new__(cls, *args, **kwargs):

        if cls not in cls._instances:

            obj = super().__new__(cls)

            cls._instances[cls] = obj

            obj._singleton_init(*args, **kwargs)

        return cls._instances[cls]

    @abc.abstractmethod
    def _singleton_init(self, *args, **kwargs):
        """
        Initialization executed once.
        """
        
        pass
