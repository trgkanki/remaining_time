from ..stack import qDlgStackTop
from ..utils import continuationHelper
from ..modelHandler import configureModel

from PyQt5.Qt import QLineEdit


class LineEdit:
    def __init__(self, initialText=""):
        self.edit = QLineEdit()
        if initialText:
            self.edit.setText(initialText)
        qDlgStackTop().addChild(self.edit)

    placeholderText = continuationHelper(
        lambda self: self.edit.placeholderText(),
        lambda self, v: self.edit.setPlaceholderText(v),
    )

    text = continuationHelper(
        lambda self: self.edit.text(), lambda self, v: self.edit.setText(v)
    )

    def passwordInput(self, enabled=True):
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

    def model(self, obj, *, attr=None, index=None):
        configureModel(obj, self.onInput, self.text, attr=attr, index=index)
