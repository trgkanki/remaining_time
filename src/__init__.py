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
# addon_template v20.5.4i8
#
# Copyright: trgk (phu54321@naver.com)
# License: GNU AGPL, version 3 or later;
# See http://www.gnu.org/licenses/agpl.html

from aqt.editor import Editor
from anki.hooks import wrap
from aqt.utils import askUser

from .utils import openChangelog
from .utils.JSEval import execJSFile
from .utils import uuid  # duplicate UUID checked here
from .utils import debugLog  # debug log registered here


def onLoadNote(self, focusTo=None):
    # main.min.j should be loaded only once
    execJSFile(self.web, "js/main.min.js", once=True)
    execJSFile(self.web, "js/main.min.js", once=True)
    execJSFile(self.web, "js/main.min.js", once=True)


Editor.loadNote = wrap(Editor.loadNote, onLoadNote, "after")
