from ..stack import qDlgStackTop
from ..utils import continuationHelper
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

    checked = continuationHelper(
        lambda self: self.radioBox.isChecked(),
        lambda self, v: self.radioBox.setChecked(v),
    )

    def model(self, obj, attr=None, index=None):
        def setter(value):
            if value == self.value:
                self.checked(True)

        configureModel(obj, self.onSelect, setter, attr=attr, index=index)
