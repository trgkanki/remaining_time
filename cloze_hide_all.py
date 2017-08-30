# -*- mode: Python ; coding: utf-8 -*-
#
# Cloze (Hide All) - v3
#   Adds a new card type "Cloze (Hide All)", which hides all clozes on its
#   front and optionally on the back.
#
# Changelog
#  v3 : Fixed issues which caused text to disappear on the mac version,
#        Added option to hide other clozes on the back.
#  v2 : Support clozes with hint
#  v1 : Initial release
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
from aqt.utils import askUser
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

hideback_caption = u'Hide others on the back side'

hideback_html = '''<style>
cloze2 { visibility: hidden; }
cloze2_w { background-color: #ffeba2; }
.cloze cloze2 { visibility: inherit; }
.cloze cloze2_w { background-color: inherit; }
cloze2_w.reveal-cloze2 { background-color: inherit; }
cloze2.reveal-cloze2 { visibility: inherit; }
.cloze2-toggle { display: block; width: 100%; margin-top: 20px; }
</style>

<script>
function toggle() {
var elements = document.querySelectorAll('cloze2, cloze2_w');
    for(var i = 0 ; i < elements.length ; i++) {
        elements[i].classList.toggle('reveal-cloze2');
    }
}
</script>

<button class='cloze2-toggle' onclick='toggle()'>Toogle mask</button>'''

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
        fld["sticky"] = True
        models.addField(clozeModel, fld)

    # Add template
    template = models.newTemplate('Cloze (Hide all)')
    template['qfmt'] = card_front
    template['afmt'] = card_back
    clozeModel['css'] = card_css
    models.addTemplate(clozeModel, template)
    models.add(clozeModel)
    updateClozeModel(col, False)
    return clozeModel


warningMsg = "ClozeHideAll will update its card template. Sync your deck to AnkiWeb before pressing OK"

def updateClozeModel(col, warnUserUpdate=True):
    models = col.models
    clozeModel = mw.col.models.byName(model_name)
    if hideback_caption not in models.fieldNames(clozeModel):
        if warnUserUpdate and not askUser(warningMsg):
            return
        fld = models.newField(hideback_caption)
        models.addField(clozeModel, fld)

        template = clozeModel['tmpls'][0]
        template['afmt'] += "\n{{#%s}}\n%s\n{{/%s}}" % (
            hideback_caption, hideback_html, hideback_caption)

        models.save()


def registerClozeModel():
    """Prepare note type"""
    if not mw.col.models.byName(model_name):
        addClozeModel(mw.col)
    updateClozeModel(mw.col)


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

    if note[hideback_caption]:
        note[hideback_caption] = "Clear to reveal other clozes on the back."


# AddCards and EditCurrent windows

def onEditorSave(self, *args):
    """Automatically generate overlapping clozes before adding cards"""
    note = self.note
    if note is None:
        return

    if note.model()["name"] == model_name:
        updateNote(note)
        self.setNote(note)


Editor.saveNow = wrap(Editor.saveNow, onEditorSave, "after")


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
