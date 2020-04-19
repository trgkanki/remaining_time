"""
Example plugin.
"""

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
