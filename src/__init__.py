#-*- coding: utf-8 -*-
#
# addon_template v20.5.4i8
#
# Copyright: trgk (phu54321@naver.com)
# License: GNU AGPL, version 3 or later;
# See http://www.gnu.org/licenses/agpl.html

from aqt.editor import Editor
from anki.hooks import wrap

import os

def readResource(filename):
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    inputFilePath = os.path.join(scriptDir, filename)
    return open(inputFilePath, 'r', encoding='utf-8').read()


def onLoadNote(self, focusTo=None):
    mainJs = readResource('main.min.js')
    self.web.eval(mainJs)


Editor.loadNote = wrap(Editor.loadNote, onLoadNote, 'after')
