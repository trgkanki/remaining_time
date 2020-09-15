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
from aqt.utils import openLink
from aqt.qt import (
    QDesktopServices,
    QUrl,
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QTextBrowser,
)
from anki.utils import noBundledLibs

import os

from .configrw import getCurrentAddonName
from .resource import readResource, getResourcePath
from aqt.utils import showText


def getCurrentAddonVersion():
    return readResource("VERSION")


def showChangelogOnUpdate():
    addonVersion = getCurrentAddonVersion()
    addonName = getCurrentAddonName()

    addonMeta = mw.addonManager.addonMeta(addonName)
    if addonMeta.get("human_version", None) != addonVersion:
        addonMeta["human_version"] = addonVersion
        mw.addonManager.writeAddonMeta(addonName, addonMeta)

        changelogPath = getResourcePath("CHANGELOG.html")
        if os.path.exists(changelogPath):
            with noBundledLibs():
                diag, _ = showText(
                    readResource("CHANGELOG.html"),
                    type="html",
                    title="Changelog",
                    run=False,
                    minWidth=800,
                    minHeight=600,
                )
                diag.setParent(None)
                diag.exec_()


showChangelogOnUpdate()
