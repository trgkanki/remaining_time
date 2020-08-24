from ..stack import qDlgStackTop
from ..utils import continuationHelper
from ..modelHandler import configureModel
from .Style import StylableWidget
from .Shortcutable import Shortcutable

from PyQt5.Qt import QCheckBox


class CheckBox(StylableWidget, Shortcutable):
    def __init__(self, initialEnabled=False):
        super().__init__()
        self.widget = QCheckBox()
        self.widget.setChecked(initialEnabled)
        qDlgStackTop().addChild(self.widget)

    def onChange(self, callback):
        self.widget.toggled.connect(callback)
        return self

    checked = continuationHelper(
        lambda self: self.widget.isChecked(), lambda self, v: self.widget.setChecked(v),
    )

    def model(self, obj, *, attr=None, index=None):
        configureModel(obj, self.onChange, self.checked, attr=attr, index=index)
        return self
