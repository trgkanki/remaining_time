from ..stack import qDlgStackTop

from PyQt5.Qt import QLineEdit


class LineEdit:
    def __init__(self, initialText=""):
        self.edit = QLineEdit()
        if initialText:
            self.edit.setText(initialText)
        qDlgStackTop().addChild(self.edit)

    def text(self, newText=None):
        if newText is None:
            return self.edit.text()
        else:
            self.edit.setText(newText)
            return self

    def setPasswordInput(self, enabled: bool):
        if enabled:
            self.edit.setEchoMode(QLineEdit.Password)
        else:
            self.edit.setEchoMode(QLineEdit.Normal)
        return self

    def onInput(self, callback):
        self.edit.textChanged.connect(callback)
        return self

    def onChange(self, callback):
        self.edit.editingFinished.connect(lambda: callback(self.text()))
        return self
