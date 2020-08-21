from ..stack import qDlgStackTop
from ..modelHandler import configureModel

from PyQt5.Qt import QRadioButton


class RadioButton:
    def __init__(self, title: str, value=None, initialEnabled=False):
        self.radioBox = QRadioButton(title)
        self.radioBox.setChecked(initialEnabled)
        self.title = title

        if value is None:
            self.value = title
        else:
            self.value = value
        qDlgStackTop().addChild(self.radioBox)

    def onChange(self, callback):
        self.radioBox.toggled.connect(callback)
        return self

    def onSelect(self, callback):
        def _(selected):
            if selected:
                callback(self.value)

        self.radioBox.toggled.connect(_)
        return self

    def checked(self, newValue=None):
        if newValue is None:
            return self.radioBox.isChecked()
        else:
            self.radioBox.setChecked(newValue)
            return self

    def model(self, obj, attrName):
        def setter(value):
            if value == self.value:
                self.checked(True)

        configureModel(obj, attrName, self.onSelect, setter)
