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
# remaining_time v20.12.13i151
#
# Copyright: trgk (phu54321@naver.com)
# License: GNU AGPL, version 3 or later;
# See http://www.gnu.org/licenses/agpl.html

from .utils import openChangelog
from .utils import uuid  # duplicate UUID checked here
from .utils import debugLog  # debug log registered here

from .utils.JSEval import execJSFile
from .utils.configrw import getConfig, onConfigUpdate
from .utils.resource import updateMedia, readResource

from aqt.reviewer import Reviewer
from anki.hooks import wrap, addHook

from .mobileSupport.modelModifier import registerMobileScript
from . import jsapi

addHook("profileLoaded", registerMobileScript)
onConfigUpdate(registerMobileScript)


def afterInitWeb(self):
    # always update medial/_remainingtime.min.js on webview init
    # aids for better development

    if getConfig("runOnMobile"):
        updateMedia(
            "_remainingtime.min.js", readResource("js/main.min.js").encode("utf-8")
        )


def afterNextCard(self):
    # Script will auto-run via card template when runOnMobile is set.
    # Manually run script only when it's not set.
    if not getConfig("runOnMobile"):
        execJSFile(self.web, "js/main.min.js")


Reviewer._initWeb = wrap(Reviewer._initWeb, afterInitWeb, "after")
Reviewer.nextCard = wrap(Reviewer.nextCard, afterNextCard, "after")
