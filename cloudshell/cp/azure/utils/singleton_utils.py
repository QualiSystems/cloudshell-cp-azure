import threading


class SingletonByArgsMeta(type):
    """Metaclass that allows to create single instances per same arguments.

    Example usage:
        >>> class Test(metaclass=SingletonByArgsMeta):
        >>>
        >>>     def __init__(self, a, b):
        >>>         self.a = a
        >>>         self.b = b
        >>>
        >>> Test("a1" , "b1") is Test("a1" , "b1")
        >>> True
        >>>
        >>> Test("a1" , "b1") is Test("a2" , "b2")
        >>> False
    """

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__instances_by_cls = {}
        cls.__lock = threading.Lock()

    def __call__(cls, *args, **kwargs):

        key = (cls, str(args), str(kwargs))

        with cls.__lock:
            instance = cls.__instances_by_cls.get(key)

            if not instance:
                instance = super(SingletonByArgsMeta, cls).__call__(*args, **kwargs)
                cls.__instances_by_cls[key] = instance

        return instance
