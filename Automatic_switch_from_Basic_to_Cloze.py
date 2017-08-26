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

from aqt.addcards import AddCards
from anki.hooks import wrap
from anki.hooks import addHook, runHook
from aqt.utils import tooltip
from anki.lang import _
import re
from aqt import mw


def modelExists(model_name):
    return bool(mw.col.models.byName(model_name))


def findModelName():
    """Prepare note type"""
    global basic_note_type
    global cloze_note_type

    basic_note_type = ['Basic']
    if modelExists(_('Basic')):
        basic_note_type.append(_('Basic'))

    cloze_note_type = _('Cloze')
    if not modelExists(cloze_note_type):
        cloze_note_type = 'Cloze'


addHook("profileLoaded", findModelName)


def change_model_to(chooser, model_name):
    """Change to model with name model_name"""
    # Mostly just a copy and paste from the bottom of onModelChange()
    m = chooser.deck.models.byName(model_name)
    chooser.deck.conf['curModel'] = m['id']
    # When you get a “TypeError: 'NoneType' object has no attribute
    # '__getitem__'” directing you here, the most likely explanation
    # is that the model names are not set up correctly in the
    # model_buttons list of dictionaries above.
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


def newAddCards(self, _old):
    note = self.editor.note
    if note.model()['name'] in basic_note_type and isClozeNote(note):
        change_model_to(self.modelChooser, cloze_note_type)
        _old(self)
        tooltip(_("Automatic switch from Basic to Cloze"))

    else:
        return _old(self)


AddCards.addCards = wrap(AddCards.addCards, newAddCards, "around")
