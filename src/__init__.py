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

def onLoadNote(self, focusTo=None):
    # main.min.j should be loaded only once
    execJSFile(self.web, "js/main.min.js", once=True)
    execJSFile(self.web, "js/main.min.js", once=True)
    execJSFile(self.web, "js/main.min.js", once=True)

Editor.loadNote = wrap(Editor.loadNote, onLoadNote, "after")

