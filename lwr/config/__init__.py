"""
lwr.config.configfile

module for handling configuration files
"""

from lwr.plugins import load_plugin

def dictFromSection(config, section):
    """Returns a dictionary of values from the specified config section.

    `config` should be a ConfigParser.ConfigParser object
    `section` should be a section name
    """
    retval = {}
    for option in config.options(section):
        try:
            retval[option] = config.getint(section, option)
            continue
        except ValueError:
            pass
        try:
            retval[option] = config.getfloat(section, option)
            continue
        except ValueError:
            pass
        try:
            retval[option] = config.getboolean(section, option)
            continue
        except ValueError:
            pass
        retval[option] = config.get(section, option)
    return retval

def pluginFromDict(config, interface):
    """
    Instantiates a plugin from the given config dict
    The section must have a "plugin" option
    """
    plugin_name = config['plugin']

    if ':' in plugin_name:
        module_name, object_name = plugin_name.split(":", 1)
        plugin = load_plugin(module_name, object_name=object_name)
        return plugin(config)

    plugin = load_plugin(plugin_name, interface)
    return plugin(config)
