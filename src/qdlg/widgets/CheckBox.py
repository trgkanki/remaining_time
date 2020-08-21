from ..stack import qDlgStackTop
from ..utils import continuationHelper
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

    checked = continuationHelper(
        lambda self: self.checkBox.isChecked(),
        lambda self, v: self.checkBox.setChecked(v),
    )

    def model(self, obj, attrName):
        configureModel(obj, attrName, self.onChange, self.checked)
