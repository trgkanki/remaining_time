from ..stack import qDlgStackTop
from ..utils import continuationHelper
from ..modelHandler import configureModel
from .Style import StylableWidget

from PyQt5.Qt import QRadioButton


class RadioButton(StylableWidget):
    def __init__(self, title: str, value=None, initialEnabled=False):
        super().__init__()
        self.widget = QRadioButton(title)
        self.widget.setChecked(initialEnabled)
        self.title = title

        if value is None:
            self.value = title
        else:
            self.value = value
        qDlgStackTop().addChild(self.widget)

    def onChange(self, callback):
        self.widget.toggled.connect(callback)
        return self

    def onSelect(self, callback):
        def _(selected):
            if selected:
                callback(self.value)

        self.widget.toggled.connect(_)
        return self

    checked = continuationHelper(
        lambda self: self.widget.isChecked(), lambda self, v: self.widget.setChecked(v),
    )

    def model(self, obj, attr=None, index=None):
        def setter(value):
            if value == self.value:
                self.checked(True)

        configureModel(obj, self.onSelect, setter, attr=attr, index=index)
        return self
