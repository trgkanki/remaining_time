# -*- mode: Python ; coding: utf-8 -*-
#
# Copyright © 2017 Hyun Woo Park (phu54321@naver.com)
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Lots of code from "Cloze overlapper" by Glutaminate
#

import re

from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from anki.hooks import addHook, wrap

from anki.consts import MODEL_CLOZE
from aqt import mw


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ TEMPALTES

model_name = 'Cloze (Reveal 1)'

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
    template = models.newTemplate('cloze-ro')
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


re_cloze = re.compile(r'\{\{c(\d+)::(([^:]|:[^:])*?)\}\}')
re_cloze_with_hint = re.compile(r'\{\{c(\d+)::(([^:]|:[^:])*?)::(.*?)\}\}')


def stripClozeHelper(html):
    return (html
            .replace("<cloze2_w>", "")
            .replace("<cloze2>", "")
            .replace("</cloze2_w>", "")
            .replace("</cloze2>", ""))


def makeClozeCompatiable(html):
    html = re.sub(
        r'\{\{c(\d+)::(([^:]|:[^:])*?)\}\}',
        '{{c\\1::%s\\2%s}}' % (cloze_header, cloze_footer),
        html
    )
    return html


# AddCards and EditCurrent windows

def onCardAddUpdate(self, _old):
    """Automatically generate overlapping clozes before adding cards"""
    note = self.editor.note
    if note.model()["name"] != model_name:
        return _old(self)

    html = note['Text']
    html = stripClozeHelper(html)
    html = makeClozeCompatiable(html)
    note['Text'] = html

    return _old(self)


AddCards.addCards = wrap(AddCards.addCards, onCardAddUpdate, "around")
EditCurrent.onSave = wrap(EditCurrent.onSave, onCardAddUpdate, "around")
