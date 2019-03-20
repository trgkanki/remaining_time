# -*- mode: Python ; coding: utf-8 -*-
#
# Copyright © 2017 Hyun Woo Park (phu54321@naver.com)
#
# Lots of code from "Quick note and deck buttons" written by Roland Sieker
#
# Provenance from original plugin.
#   The idea, original version and large parts of this code
#   written by Steve AW <steveawa@gmail.com>
#
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#

from aqt import mw
from aqt.addcards import AddCards
from anki.hooks import wrap
from anki.hooks import addHook, runHook
from aqt.utils import tooltip
from anki.lang import _
from anki import version

import re

anki21 = version.startswith("2.1.")


def modelExists(model_name):
    return bool(mw.col.models.byName(model_name))


def findModelName():
    """Prepare note type"""
    global basic_note_type
    global cloze_note_type

    basic_note_type = list(filter(modelExists, ['Basic', _('Basic')]))
    cloze_note_type = list(filter(modelExists, ['Cloze', _('Cloze')]))

    if not basic_note_type:
        tooltip('[Automatic basic to cloze] Cannot find source \'Basic\' model')
        basic_note_type = None

    if not cloze_note_type:
        tooltip('[Automatic basic to cloze] Cannot find target \'Cloze\' model')
        cloze_note_type = None
    else:
        cloze_note_type = cloze_note_type[0]


addHook("profileLoaded", findModelName)


def change_model_to(chooser, model_name):
    """Change to model with name model_name"""
    # Mostly just a copy and paste from the bottom of onModelChange()
    m = chooser.deck.models.byName(model_name)
    chooser.deck.conf['curModel'] = m['id']
    cdeck = chooser.deck.decks.current()
    cdeck['mid'] = m['id']
    chooser.deck.decks.save(cdeck)
    runHook("currentModelChanged")
    chooser.mw.reset()


def isClozeNote(note):
    for name, val in note.items():
        if re.search(r'\{\{c(\d+)::', val):
            return True
    return False


def callWithCallback(f, cb):
    """Mediates callback-accepting anki 2.1 & non-callback anki 2.0"""
    if anki21:
        f(cb)
    else:
        f()
        cb()


def newAddCards(self, _old):
    if not (basic_note_type and cloze_note_type):
        return _old(self)

    note = self.editor.note
    if note.model()['name'] in basic_note_type and isClozeNote(note):
        oldModelName = [None]

        def cb1():
            oldModelName[0] = note.model()['name']
            change_model_to(self.modelChooser, cloze_note_type)

            callWithCallback(self.editor.saveNow, cb2)

        def cb2():
            if anki21:
                self._addCards()
            else:
                self.addCards()

            change_model_to(self.modelChooser, oldModelName[0])
            tooltip(_('[Basic2Cloze] %s -> %s' %
                      (oldModelName[0], cloze_note_type)))

        callWithCallback(self.editor.saveNow, cb1)
    else:
        return _old(self)


AddCards.addCards = wrap(AddCards.addCards, newAddCards, "around")
