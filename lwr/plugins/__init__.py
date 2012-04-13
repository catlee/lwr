import imp, os.path
def load_plugin(module_or_file_name, interface=None, object_name=None):
    """
    Loads a plugin from a module. Returns the plugin object.

    module_or_file_name can be the full path to the python file that implements
    the plugin, or if the path doesn't exist, it will be searched according to
    python's module search rules. ImportError will be raised if the module
    can't be found.

    Either interface or object_name must be set. If interface is set, the first
    object in the module for which isinstance(obj, interface) is true will be
    returned. If object_name is set then the object specifed by name will be
    returned. KeyError will be raised if it can't be found.
    """
    # Check that we have exactly one of these set
    assert bool(interface) ^ bool(object_name)

    # First check to see if module_or_file_name looks like a path
    g = {}
    if "/" in module_or_file_name:
        if not os.path.exists(module_or_file_name):
            raise ImportError("%s could not be found" % module_or_file_name)
        exec(compile(open(module_or_file_name).read(), module_or_file_name, 'exec'), g)
    else:
        parts = module_or_file_name.split(".")
        path = None
        for part in parts:
            filename, path, d = imp.find_module(part, path)
            path = [path]
        mod = imp.load_module(module_or_file_name, filename, path[0], d)
        g = mod.__dict__

    if interface:
        for name, obj in g.items():
            try:
                if issubclass(obj, interface):
                    return obj
            except TypeError:
                continue

    else:
        return g[object_name]
