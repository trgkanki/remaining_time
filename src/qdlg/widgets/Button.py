from ..stack import qDlgStackTop
from .Style import StylableWidget
from .Shortcutable import Shortcutable

from PyQt5.Qt import QPushButton, QKeySequence


class Button(StylableWidget, Shortcutable):
    def __init__(self, label):
        super().__init__()
        self.widget = QPushButton(label)
        self.widget.setAutoDefault(False)
        qDlgStackTop().addChild(self.widget)

    def onClick(self, callback):
        self.widget.clicked.connect(callback)
        return self
