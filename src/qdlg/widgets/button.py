from ..stack import qDlgStackTop

from PyQt5.Qt import QPushButton


class Button:
    def __init__(self, label):
        self.button = QPushButton(label)
        self.button.setAutoDefault(False)
        qDlgStackTop().addChild(self.button)

    def onClick(self, callback):
        self.button.clicked.connect(callback)
        return self

    def setDefault(self, enabled=True):
        self.button.setDefault(enabled)
