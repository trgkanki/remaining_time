from aqt import mw
from aqt.utils import askUser
import os


def getCurrentAddonName():
    fPath = os.path.dirname(os.path.abspath(__file__))
    fPath = fPath.replace(os.sep, "/")
    fPathParts = fPath.split("/")
    addons21Index = fPathParts.index("addons21")
    return fPathParts[addons21Index + 1]


def getConfig(key, default=None):
    addonName = getCurrentAddonName()
    config = mw.addonManager.getConfig(addonName)
    if not config:
        return default
    return config.get(key, default)


def setConfig(key, value):
    addonName = getCurrentAddonName()
    config = mw.addonManager.getConfig(addonName)
    if config is None:
        config = {}
    config[key] = value
    mw.addonManager.writeConfig(addonName, config)
