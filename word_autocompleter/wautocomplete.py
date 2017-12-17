"""
Word-based autocompleter v0.03

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


def readResource(fname):
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    ifname = os.path.join(scriptDir, 'wcomplete', fname)
    return open(ifname, 'r').read()


wordset = set()
wsdict = {}
alphaNumeric = re.compile("[a-zA-Z][a-zA-Z0-9]{4,}")


def initWordSet(col):
    """ Initialize wordSet from preexisting collections """
    global wordset, wsdict, alphaNumeric

    wordset.clear()

    for (fld,) in col.db.execute("select flds from notes"):
        try:
            wordset.update(wsdict[fld])
        except KeyError:
            words = [w.lower() for w in alphaNumeric.findall(fld)]
            wsdict[fld] = words
            wordset.update(words)

    return wordset


def onLoadNote(self):
    col = self.mw.col
    wordset = initWordSet(col)

    # Update wordSet
    jqueryJs = readResource('_jquery-3.2.1.min.js')
    wcAdapterJs = readResource('_adapter.js')

    self.web.eval(jqueryJs)
    self.web.eval(wcAdapterJs)
    self.web.eval("wordSet = [" + ''.join('"%s", ' % w for w in wordset) + "]")


Editor.loadNote = wrap(Editor.loadNote, onLoadNote, 'after')
