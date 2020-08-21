from ..stack import qDlgStackTop
from ..modelHandler import configureModel

from PyQt5.Qt import QCheckBox


class CheckBox:
    def __init__(self, initialEnabled=False):
        self.checkBox = QCheckBox()
        self.checkBox.setChecked(initialEnabled)
        qDlgStackTop().addChild(self.checkBox)

    def onChange(self, callback):
        self.checkBox.toggled.connect(callback)
        return self

    def checked(self, newValue=None):
        if newValue is None:
            return self.checkBox.isChecked()
        else:
            self.checkBox.setChecked(newValue)
            return self

    def model(self, obj, attrName):
        configureModel(obj, attrName, self.onChange, self.checked)
