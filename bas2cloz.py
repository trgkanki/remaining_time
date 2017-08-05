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

from aqt.editor import Editor
from anki.hooks import wrap
from anki.hooks import runHook
from aqt.utils import tooltip
from anki.lang import _


###############################################################################

basic_note_type = 'Basic'
cloze_note_type = 'Cloze'

###############################################################################


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


def onCloze(self):
    if self.addMode:
        if self.note.model()['name'] == 'Basic':
            chooser = self.parentWindow.modelChooser
            change_model_to(chooser, "Cloze")
            tooltip(_("Automatic switch from Basic to Cloze"))


Editor.onCloze = wrap(Editor.onCloze, onCloze, "before")
