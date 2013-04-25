"""
Blueprint configuration module.

Provides a get() function to access the blueprint configuration with a
dot notation style.

Example:

maya_renderer = conf.get("modules.maya.renderer")

"""
import os
import simplejson
import logging

import blueprint.exception

logger = logging.getLogger(__name__)

class _Default(object):
    def __init__(self):
        pass

class _Raise(object):
    def __init__(self):
        pass

__Config = { }

__EnvMap = { }

Default = _Default()

Raise = _Raise()

def __init(config, envmap):
    """
    Initialize the plow configuration.
    """
    search_path = os.environ.get("BLUEPRINT_CFG", ":".join((
        os.path.join(os.environ.get("BLUEPRINT_ROOT", "/usr/local"), "/etc/blueprint/blueprint.cfg"),
        os.path.expanduser("~/.blueprint/blueprint.cfg"))))

    try:
        for path in search_path.split(":"):
            print path
            logger.debug("Checking %s for a blueprint configuration." % path)
            if os.path.isfile(path):
                data = open(path).read()
                config.update(simplejson.loads(data))
                envmap.update(dict(((k, os.environ.get(k, "")) 
                    for k in config["env"]["interpolate"])))
                return
    except Exception, e:
        raise blueprint.exception.BlueprintException(
            "Failed to parse plow configuration: %s" % e)

    raise blueprint.exception.BlueprintException(
        "Unable to find plow configuration at: %s" % search_path)

def interp(value, **kwargs):
    kwargs.update(__EnvMap)
    return value % kwargs

def get(key, default=Default, **kwargs):
    """
    Return the specification configuration value.  If the
    value is undefined, return the default.  If the default is
    conf.Raise, then a BlueprintException is thrown.

    If an environment variable named with key.upper().replace(".","_")
    exists, that value is returned instead.

    For example, a key of "blueprint.project" would 
    translate to the BLUEPRINT_PROJECT environment variable.
    """
    env_value = os.environ.get(key.upper().replace(".", "_"))
    if env_value:
        return env_value

    elements = key.split(".")
    part = __Config
    try:
        for e in elements:
            part = part[e]
    except KeyError:
        if default == Raise:
            raise blueprint.exception.BlueprintException(
                "Invalid configuration option: %s" % key)
        return default

    if isinstance(part, basestring):
        part = interp(part, **kwargs)
    return part

# Initialize the configuration.
__init(__Config, __EnvMap)
