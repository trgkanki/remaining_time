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

# -*- coding: utf-8 -*-
#
# remaining_time v20.9.25i145
#
# Copyright: trgk (phu54321@naver.com)
# License: GNU AGPL, version 3 or later;
# See http://www.gnu.org/licenses/agpl.html

from .utils import openChangelog
from .utils import uuid  # duplicate UUID checked here

from .utils.JSEval import execJSFile
from .utils.configrw import getConfig
from .utils.resource import updateMedia, readResource
from .utils.debug import openLogWithPreferredEditor, isDebugMode

from aqt.reviewer import Reviewer
from anki.hooks import wrap, addHook
from aqt.qt import QAction
from aqt import mw

from .mobileSupport.modelModifier import registerMobileScript
from . import jsapi

addHook("profileLoaded", registerMobileScript)


def afterInitWeb(self):
    # always update medial/_remainingtime.min.js on webview init
    # aids for better development

    if getConfig("runOnMobile"):
        updateMedia(
            "_remainingtime.min.js", readResource("js/main.min.js").encode("utf-8")
        )

    execJSFile(self.web, "js/main.min.js")


Reviewer._initWeb = wrap(Reviewer._initWeb, afterInitWeb, "after")


## debug menu

if isDebugMode():
    action = QAction("Show addon log: Remaining time", mw)
    action.triggered.connect(openLogWithPreferredEditor)
    mw.form.menuHelp.addAction(action)
