def args_based_singleton(the_class):
    """Decorator for a class to make a singleton dependent to init arguments."""
    class_instances = {}

    def get_instance(*args, **kwargs):
        """Creating or just return the one and only class instance.

        The singleton depends on the parameters used in __init__.
        """
        key = (the_class, args, str(kwargs))
        if key not in class_instances:
            class_instances[key] = the_class(*args, **kwargs)
        return class_instances[key]

    return get_instance
