# -*- coding: utf-8 -*-
#
# Cloze (Hide All) - v4
#   Adds a new card type "Cloze (Hide All)", which hides all clozes on its
#   front and optionally on the back.
#

from HTMLParser import HTMLParser
import cgi
import re
from aqt.editor import EditorWebView
from aqt.qt import QMimeData


# Tags that don't have ending tags.
_voidElements = {
    'area', 'base', 'basefont', 'bgsound', 'br', 'col',
    'command', 'embed', 'frame', 'hr', 'image', 'img', 'input', 'isindex',
    'keygen', 'link', 'menuitem', 'meta', 'nextid', 'param', 'source',
    'track', 'wbr'
}


# Tags that should be allowed
_allowedTags = {
    # Paragraph-related elements
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'blockquote', 'pre',

    # Useful inline elements
    'img', 'a', 'span', 'br', 'code',
    'b', 'em', 'i', 'u', 'strong',

    # Lists
    'ul', 'ol', 'li',

    # Useful layout elements
    'div', 'table', 'tr', 'td', 'thead', 'th', 'tbody',
}


# Tags that should be ignored: They are valid, but shouldn't be present in
# the output html
_ignoredTags = {
    'html', 'body',
}


# Allowed attributes
_allowedAttributes = {
    'style',

    'src', 'alt',  # img
    'href', 'title',  # a href

    'colspan', 'rowspan',  # table
}


# Allowed CSS styles
_allowedStyles = {
    # General text attributes
    'font-weight', 'color', 'background-color', 'font-style',

    # Block attributes
    'text-align', 'valign',

    # Table attributes
    'background', 'background-color',
}


# CleanHTML overrides some default styles
_overrideStyles = {
    'table': {
        'box-sizing': 'border-box',
        'width': '100%',
        'margin': '.5em',
        'border-collapse': 'collapse',
        'outline': '1px solid black',
    },

    'th': {
        'position': 'relative',
        'border': '1px solid black',
        'padding': '.4em',
        'font-size': '1.2em',
    },

    'td': {
        'position': 'relative',
        'border': '1px solid black',
        'padding': '.2em',
    },

    'div': {
        'padding': '.2em'
    },
}


##############################################
# Main implementation
##############################################

_styleRegex = re.compile('(.+?) *: *(.+?);')
_allowedTags |= _ignoredTags


class TagCleaner(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.nonAllowedTagCountInStack = 0
        self.output = []
        self.tagStack = []
        self.parseError = False

    def writeData(self, data):
        if self.nonAllowedTagCountInStack == 0:
            self.output.append(data)

    def handle_starttag(self, tag, attrs):
        if tag not in _voidElements:
            self.tagStack.append(tag)
            if tag not in _allowedTags:
                self.nonAllowedTagCountInStack += 1

        if tag in _ignoredTags:
            return

        # Parse attributes
        attrDict = {'style': ''}
        for k, v in attrs:
            if k in _allowedAttributes:
                attrDict[k] = v

        # Parse styles
        styleDict = {}
        for k, v in _styleRegex.findall(attrDict['style']):
            if k in _allowedStyles:
                styleDict[k] = v

        # Override styles
        if tag in _overrideStyles:
            for k, v in _overrideStyles[tag].items():
                styleDict[k] = v

        if styleDict:
            attrDict['style'] = ''.join(
                "%s:%s;" % (k, v) for k, v in styleDict.items()
            )
        else:
            del attrDict['style']

        if attrDict:
            attrStr = ' ' + ' '.join(
                '%s="%s"' % (k, cgi.escape(v)) for k, v in attrDict.items()
            )
        else:
            attrStr = ''

        # Write to stack
        self.writeData("<%s%s>" % (tag, attrStr))

    def handle_endtag(self, tag):
        # Do nothing for void elements
        if tag in _voidElements:
            return

        while self.tagStack and self.tagStack[-1] != tag:
            self.tagStack.pop()
            self.parseError = True

        if self.tagStack:
            self.tagStack.pop()

        if tag in _allowedTags:
            if tag not in _ignoredTags:
                self.writeData("</%s>" % tag)
        else:
            self.nonAllowedTagCountInStack -= 1

    def handle_data(self, data):
        self.writeData(data)

    def flush(self):
        return ''.join(self.output)


def cleanTag(data):
    parser = TagCleaner()
    parser.feed(data)
    data = parser.flush()
    data = re.sub('^\s*\n', '', data, flags=re.M)
    return data


def newProcessHtml(self, mime):
    html = mime.html()
    newMime = QMimeData()
    if self.strip and not html.startswith("<!--anki-->"):
        newMime.setHtml(cleanTag(html))
    else:
        if html.startswith("<!--anki-->"):
            html = html[11:]
        # no html stripping
        html = self.editor._filterHTML(html, localize=True)
        newMime.setHtml(html)
    return newMime


EditorWebView._processHtml = newProcessHtml
