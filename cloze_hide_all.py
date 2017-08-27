# -*- mode: Python ; coding: utf-8 -*-
#
# Copyright © 2017 Hyun Woo Park (phu54321@naver.com)
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Lots of code from
#   - Cloze overlapper (by Glutaminate)
#   - Batch Note Editing (by Glutaminate)
#

import re

from aqt.editor import Editor
from aqt.browser import ChangeModel
from anki.hooks import addHook, wrap

from anki.consts import MODEL_CLOZE
from aqt import mw


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ TEMPALTES

model_name = u'Cloze (Hide all)'

card_front = '''
<style>cloze2 {opacity: 0;}cloze2_w {background-color: #ffeba2;}</style>
{{cloze:Text}}
'''

card_back = '''
{{cloze:Text}}
<hr>
{{Extra}}
'''

card_css = '''
.card {
    font-family: Arial;
    font-size: 20px;
    color: black;
    background-color: white;
}

.cloze {
    font-weight: bold;
    color: blue;
}
'''

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ TEMPALTES


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
# Main code
#
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def addClozeModel(col):
    models = col.models
    clozeModel = models.new(model_name)
    clozeModel['type'] = MODEL_CLOZE

    # Add fields
    for fieldName in ('Text', 'Extra'):
        fld = models.newField(fieldName)
        models.addField(clozeModel, fld)

    # Add template
    template = models.newTemplate('Cloze (Hide all)')
    template['qfmt'] = card_front
    template['afmt'] = card_back
    clozeModel['css'] = card_css
    models.addTemplate(clozeModel, template)
    models.add(clozeModel)
    return clozeModel


def registerClozeModel():
    """Prepare note type"""
    if not mw.col.models.byName(model_name):
        addClozeModel(mw.col)


addHook("profileLoaded", registerClozeModel)

# Editor
cloze_header = "<cloze2_w><cloze2>"
cloze_footer = "</cloze2></cloze2_w>"


def wrapClozeContent(clozeContent):
    return "%s%s%s" % (cloze_header, clozeContent, cloze_footer)


def stripClozeHelper(html):
    return (html
            .replace("<cloze2_w>", "")
            .replace("<cloze2>", "")
            .replace("</cloze2_w>", "")
            .replace("</cloze2>", ""))


def makeClozeCompatiable(html):
    html = re.sub(
        r'\{\{c(\d+)::(([^:}]|:[^:}])*?)\}\}',
        '{{c\\1::%s\\2%s}}' % (cloze_header, cloze_footer),
        html
    )
    html = re.sub(
        r'\{\{c(\d+)::(([^:}]|:[^:}])*?)::(([^:}]|:[^:}])*?)\}\}',
        '{{c\\1::%s\\2%s::\\4}}' % (cloze_header, cloze_footer),
        html
    )
    return html


def updateNote(note):
    html = note['Text']
    html = stripClozeHelper(html)
    html = makeClozeCompatiable(html)
    note['Text'] = html


# AddCards and EditCurrent windows

def onEditorSave(self, *args):
    """Automatically generate overlapping clozes before adding cards"""
    note = self.note
    if note is None:
        return

    if note.model()["name"] == model_name:
        updateNote(note)
        self.setNote(note)


Editor.saveNow = wrap(Editor.saveNow, onEditorSave, "before")


# Batch change node types on card type change

def applyClozeFormat(browser, nids):
    mw = browser.mw
    mw.checkpoint("Note type change to cloze (reveal one)")
    mw.progress.start()
    browser.model.beginReset()
    for nid in nids:
        note = mw.col.getNote(nid)
        updateNote(note)
        note.flush()
    browser.model.endReset()
    mw.requireReset()
    mw.progress.finish()
    mw.reset()


def onChangeModel(self):
    if self.targetModel['name'] == model_name:
        applyClozeFormat(self.browser, self.nids)


ChangeModel.accept = wrap(ChangeModel.accept, onChangeModel, "after")
