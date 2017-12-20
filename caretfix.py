"""
Basic Caret fixer for non-English environments
"""

from aqt.editor import Editor
from anki.hooks import wrap


def onLoadNote(self):
    self.web.eval("""
if (!window._caretFixed) {
    window._caretFixed = true;
    (function() {
        var LEFT = 37, RIGHT = 39;

        var tempInput = document.createElement('input');
        tempInput.style.position = 'absolute';
        tempInput.style.opacity = '0';
        tempInput.style.left = '-99999px';
        document.body.appendChild(tempInput);

        var oldRange = null;
        var prevElement = null;

        document.addEventListener('keyup', function(event) {
            if (event.target.hasAttribute('contenteditable')) {
                // Left / Right arrow key -> Reset cursor.
                if (event.keyCode == LEFT || event.keyCode == RIGHT) {
                    var sel = window.getSelection();
                    oldRange = sel.getRangeAt(0).cloneRange();
                    if(oldRange.collapsed) {
                        tempInput.focus();
                        prevElement = event.target;
                        py.run("refreshCaret");
                    }
                }
            }
        }, false);

        tempInput.addEventListener('focus', function() {
            if(prevElement !== null) {
                prevElement.focus();
                prevElement = null;
                setTimeout(function() {
                    var sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(oldRange);
                    oldRange = null;
                }, 0);
            }
        });
    })();
}

""")


def caretResetBridge(self, str, _old=None):
    if str.startswith("refreshCaret"):
        self.web.clearFocus()
        self.web.setFocus()
    else:
        _old(self, str)


Editor.bridge = wrap(Editor.bridge, caretResetBridge, 'around')
Editor.loadNote = wrap(Editor.loadNote, onLoadNote, 'after')
