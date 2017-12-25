# -*- mode: Python ; coding: utf-8 -*-
#
# Cloze (Hide All) - v4
#   Adds a new card type "Cloze (Hide All)", which hides all clozes on its
#   front and optionally on the back.
#
# Changelog
#  v5 : DOM-boundary crossing clozes will be handled properly
#  v4 : Prefixing cloze content with ! will make it visibile on other clozes.
#        Other hidden content's size will be fixed. (No automatic update)
#  .1 : Fixed bug when editing notes (EditCurrent hook, better saveNow hook)
#       Fixed issues where wrong fields are marked as 'sticky'
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
from aqt.editcurrent import EditCurrent
from aqt.browser import ChangeModel
from aqt.utils import askUser
from anki.hooks import addHook, wrap

from anki.consts import MODEL_CLOZE
from aqt import mw


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ TEMPALTES

model_name = u'Cloze (Hide all)'

czhd_def = '''\
<script>
/* --- DO NOT DELETE OR EDIT THIS SCRIPT --- */
setTimeout(function() {
    var clozeBoxes = document.querySelector(".cloze cloze2_w");
    var elements = document.querySelectorAll("cloze2." + clozeBoxes.className);
    for(var i = 0 ; i < elements.length ; i++) {
        elements[i].style.display="inline";
    }
}, 0);
/* --- DO NOT DELETE OR EDIT THIS SCRIPT --- */
</script>

'''

card_front = '''
<style>
cloze2 {
    display: none;
}

cloze2_w {
    display: inline-block;
    width: 5em;
    height: 1em;
    background-color: #ffeba2;
}
</style>
{{cloze:Text}}
'''

card_back = '''
{{cloze:Text}}
{{#Extra}}
<hr>
{{Extra}}
{{/Extra}}
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

cz_hide {
    display: none;
}
'''

hideback_caption = u'Hide others on the back side'

hideback_html = '''<style>
cloze2 {
    display: none;
}

cloze2_w {
    display: inline-block;
    width: 5em;
    height: 1em;
    background-color: #ffeba2;
}

.cloze cloze2 {
    display: inline;
}

.cloze cloze2_w {
    display: none;
}

cloze2.reveal-cloze2 {
    display: inline;
}

cloze2_w.reveal-cloze2 {
    display: none;
}

.cloze2-toggle {
    -webkit-appearance: none;
    display: block;
    font-size: 1.3em;
    height: 2em;
    background-color: #ffffff;
    width: 100%;
    margin-top: 20px;
}

.cloze2-toggle:active {
    background-color: #ffffaa;
}
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


warningMsg = ("ClozeHideAll will update its card template. "
              "Sync your deck to AnkiWeb before pressing OK")


def updateClozeModel(col, warnUserUpdate=True):
    models = col.models
    clozeModel = mw.col.models.byName(model_name)
    if hideback_caption not in models.fieldNames(clozeModel):
        if warnUserUpdate and not askUser(warningMsg):
            return
        fld = models.newField(hideback_caption)
        fld["sticky"] = True
        models.addField(clozeModel, fld)

        template = clozeModel['tmpls'][0]
        template['afmt'] += "\n{{#%s}}\n%s\n{{/%s}}" % (
            hideback_caption, hideback_html, hideback_caption)

        models.save()

    template = clozeModel['tmpls'][0]
    if czhd_def not in template['afmt']:
        template['afmt'] = czhd_def + '\n' + template['afmt']
        models.save()


def registerClozeModel():
    """Prepare note type"""
    if not mw.col.models.byName(model_name):
        addClozeModel(mw.col)
    updateClozeModel(mw.col)


addHook("profileLoaded", registerClozeModel)

# Editor


def stripClozeHelper(html):
    return re.sub(
        r"</?(cz_hide|cloze2|cloze2_w)>|" +
        r"<(cloze2_w|cloze2) class=(\"|')cz-\d+(\"|')>|" +
        r"<script( class=(\"|')cz-\d+(\"|'))?>_czha\(\d+\)</script>",
        "",
        html
    )


_voidElements = {
    'area', 'base', 'basefont', 'bgsound', 'br', 'col',
    'command', 'embed', 'frame', 'hr', 'image', 'img', 'input', 'isindex',
    'keygen', 'link', 'menuitem', 'meta', 'nextid', 'param', 'source',
    'track', 'wbr'
}


clozeId = 0


def wrapClozeTag(s):
    """
    Cloze may span across DOM boundary. This ensures that clozed text
    in elements different from starting element to be properly hidden
    by enclosing them by <cloze2>
    """
    global clozeId

    PARSE_DATA = 0
    PARSE_TAG = 1
    mode = PARSE_DATA

    output = ["<cloze2_w class='cz-%d'></cloze2_w>" % clozeId]
    dataCh = []
    tagCh = []
    tagStack = []

    cloze_header = "<cloze2 class='cz-%d'>" % clozeId
    cloze_footer = "</cloze2>"

    clozeId += 1

    def emitData():
        data = ''.join(dataCh)
        dataCh[:] = []

        if not data:
            return

        output.append("%s%s%s" % (cloze_header, data, cloze_footer))

    def emitTag():
        tag = ''.join(tagCh)
        tagCh[:] = []

        # Process starting tag & Ending tag
        tagStartMatch = re.match("<\s*([a-zA-Z0-9]+)", tag)
        tagEndMatch = re.match("<\s*/\s*([a-zA-Z0-9]+)", tag)

        if tagStartMatch:
            tagName = tagStartMatch.group(1)
            # If tagStack is not empty, then a parent of this dom element have
            # been applied cloze2, so we don't need to apply it once again.
            if not tagStack:
                output.append(cloze_header)

            if tagName not in _voidElements:
                # Push tag name to stack to trace where we're in
                # current DOM tree.
                tagStack.append(tagName)
                output.append(tag)

            else:
                output.append(tag)
                # void elements won't have corresponding closing tags, so
                # we should close cloze2 tag here.
                if not tagStack:
                    output.append(cloze_footer)

        elif tagEndMatch:
            tagName = tagEndMatch.group(1)
            if tagName not in _voidElements:
                # Still in tag stack
                if tagStack:
                    if tagStack.pop() != tagName:
                        # Invalid HTML found. Don't do further processing.
                        return s

                    output.append(tag)

                    # If dom is broken and all elements have been
                    # processed, add a cloze2
                    if not tagStack:
                        output.append(cloze_footer)

                # We're out of original DOM tree we've started from.
                # This can happen. :)
                else:
                    output.append(tag)

    for ch in s:
        if mode == PARSE_DATA:
            # Tag start/end -> switch to tag parsing mode
            if ch == '<':
                mode = PARSE_TAG
                emitData()
                tagCh.append('<')

            # Emit character as-is
            else:
                dataCh.append(ch)

        elif mode == PARSE_TAG:
            tagCh.append(ch)

            if ch == '>':
                mode = PARSE_DATA
                emitTag()

    if mode == PARSE_DATA:
        emitData()
    else:
        emitTag()

    return ''.join(output)


def makeClozeCompatiable(html):
    html = re.sub(
        r'\{\{c(\d+)::([^!]([^:}]|:[^:}])*?)\}\}',
        lambda match:
            '{{c%s::%s}}' %
            (match.group(1), wrapClozeTag(match.group(2))),
        html
    )
    html = re.sub(
        r'\{\{c(\d+)::([^!]([^:}]|:[^:}])*?)::(([^:}]|:[^:}])*?)\}\}',
        lambda match:
            '{{c%s::%s::%s}}' %
            (match.group(1), wrapClozeTag(match.group(2)), match.group(4)),
        html
    )
    html = re.sub(
        r'\{\{c(\d+)::!',
        '{{c\\1::<cz_hide>!</cz_hide>',
        html
    )
    return html


def updateNote(note):
    global clozeId
    clozeId = 1

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
        self.web.eval("saveField('blur');")
        updateNote(note)
        self.setNote(note)


Editor.saveNow = wrap(Editor.saveNow, onEditorSave, "before")


def onEditCurrent(self, *args):
    ed = self.editor
    note = self.editor.note
    if note is None:
        return

    if note.model()["name"] == model_name:
        ed.web.eval("saveField('blur');")
        updateNote(note)
        ed.loadNote()


EditCurrent.onSave = wrap(EditCurrent.onSave, onEditCurrent, "before")


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
