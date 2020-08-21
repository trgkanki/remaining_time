from ..stack import qDlgStackTop
from .Style import StylableWidget

from PyQt5.Qt import QPushButton


class Button(StylableWidget):
    def __init__(self, label):
        super().__init__()
        self.widget = QPushButton(label)
        self.widget.setAutoDefault(False)
        qDlgStackTop().addChild(self.widget)

    def onClick(self, callback):
        self.widget.clicked.connect(callback)
        return self

    def setDefault(self, enabled=True):
        self.widget.setDefault(enabled)
        return self
