from ..stack import qDlgStackTop

from PyQt5.Qt import QLabel


class Text:
    def __init__(self, text):
        self.label = QLabel(text)
        qDlgStackTop().addChild(self.label)

    def wordWrap(self, enabled):
        self.label.setWordWrap(enabled)
        return self
