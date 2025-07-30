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
from aqt.addons import AddonManager
from anki.hooks import wrap

import os
import functools


@functools.cache
def getCurrentAddonName():
    fPath = os.path.dirname(os.path.abspath(__file__))
    fPath = fPath.replace(os.sep, "/")
    fPathParts = fPath.split("/")
    addons21Index = fPathParts.index("addons21")
    return fPathParts[addons21Index + 1]


def getConfig(key, default=None):
    config = getConfigAll()
    if not config:
        return default
    return config.get(key, default)


def setConfig(key, value):
    addonName = getCurrentAddonName()
    config = getConfigAll()

    if config is None:
        config = {}
    config[key] = value
    mw.addonManager.writeConfig(addonName, config)


# Configuration editor related code


def setConfigEditor(editorFunc):
    addonName = getCurrentAddonName()
    mw.addonManager.setConfigAction(addonName, editorFunc)


# Config update callback
_configUpdateCallbacks = []


def onConfigUpdate(func):
    _configUpdateCallbacks.append(func)


def cbConfigUpdated(_):
    for f in _configUpdateCallbacks:
        f()


mw.addonManager.setConfigUpdatedAction(getCurrentAddonName(), cbConfigUpdated)


# Config getter & cache


_config_cache = None


def getConfigAll():
    global _config_cache
    if _config_cache is None:
        addonName = getCurrentAddonName()
        _config_cache = mw.addonManager.getConfig(addonName)

    return _config_cache.copy()


def setConfigAll(newConfig):
    addonName = getCurrentAddonName()
    config = mw.addonManager.getConfig(addonName)
    for k, v in newConfig.items():
        config[k] = v
    mw.addonManager.writeConfig(addonName, config)


def _resetConfigCache():
    global _config_cache
    _config_cache = None


onConfigUpdate(_resetConfigCache)
