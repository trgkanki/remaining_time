# Copyright (C) 2020 Hyun Woo Park
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from aqt import mw
from aqt.utils import askUser
from anki.hooks import addHook

from .resource import updateMedia
import os
import json


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
    _syncJSConfig()


# Configuration editor related code


def setConfigEditor(editorFunc):
    addonName = getCurrentAddonName()
    config = mw.addonManager.setConfigAction(addonName, editorFunc)


def getConfigAll():
    addonName = getCurrentAddonName()
    return mw.addonManager.getConfig(addonName)


def setConfigAll(newConfig):
    addonName = getCurrentAddonName()
    config = mw.addonManager.getConfig(addonName)
    for k, v in newConfig.items():
        config[k] = v
    mw.addonManager.writeConfig(addonName, config)
    _syncJSConfig()


# Js interop.


def _syncJSConfig():
    from .uuid import addonUUID

    config = getConfigAll()
    if config is None:  # addon doesn't have a config
        return

    # Due to CORB, we cannot use `.json` as file extension.
    configPathName = "_addon_config_%s.js" % addonUUID().replace("-", "_")
    jsonp = f"""window._ADDON_CONFIG_CALLBACK_{addonUUID().replace("-", "")}({json.dumps(config)})"""
    updateMedia(configPathName, jsonp.encode("utf-8"))


# sync on startup
addHook("profileLoaded", _syncJSConfig)
