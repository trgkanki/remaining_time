from ..stack import qDlgStackTop
from .Style import StylableWidget

from PyQt5.Qt import QLabel


class Text(StylableWidget):
    def __init__(self, text):
        super().__init__()
        self.widget = QLabel(text)
        qDlgStackTop().addChild(self.widget)

    def wordWrap(self, enabled):
        self.widget.setWordWrap(enabled)
        return self
