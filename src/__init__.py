"""
v0.04 : OK
v0.03 : Bugfix / feature improvement
v0.02 : Delayed autocomplete implemented.

Code borrowed from:
    - https://github.com/gr2m/contenteditable-autocomplete
    - Editor Autocomplete add-on (https://ankiweb.net/shared/info/924298715)
"""

from aqt.editor import Editor
from anki.hooks import wrap

import re
import os

def readResource(filename):
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    inputFilePath = os.path.join(scriptDir, filename)
    return open(inputFilePath, 'r', encoding='utf-8').read()


wordSet = set()
wordSetDict = {}
alphaNumeric = re.compile("[a-zA-Z][a-zA-Z0-9]{4,}")


def initWordSet(col):
    """ Initialize wordSet from preexisting collections """
    global wordSet, wordSetDict, alphaNumeric

    wordSet.clear()

    for (field,) in col.db.execute("select flds from notes"):
        try:
            wordSet.update(wordSetDict[field])
        except KeyError:
            words = [w.lower() for w in alphaNumeric.findall(field)]
            wordSetDict[field] = words
            wordSet.update(words)

    return wordSet


def onLoadNote(self, focusTo=None):
    col = self.mw.col
    wordSet = initWordSet(col)

    wcAdapterJs = readResource('main.min.js')
    self.web.eval(wcAdapterJs)
    self.web.eval("wordSet = [" + ''.join('"%s", ' % w for w in wordSet) + "]")


Editor.loadNote = wrap(Editor.loadNote, onLoadNote, 'after')
