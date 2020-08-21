from ..stack import qDlgStackTop

from PyQt5.Qt import QRadioButton


class RadioButton:
    def __init__(self, title: str, value=None, initialEnabled=False):
        self.radioBox = QRadioButton(title)
        self.radioBox.setChecked(initialEnabled)
        self.title = title
        self.value = value
        qDlgStackTop().addChild(self.radioBox)

    def onChange(self, callback):
        self.radioBox.toggled.connect(callback)
        return self

    def onSelect(self, callback):
        def _(selected):
            if selected:
                if self.value is None:
                    callback(self.title)
                else:
                    callback(self.value)

        self.radioBox.toggled.connect(_)
        return self

    def checked(self, newValue=None):
        if newValue is None:
            return self.radioBox.isChecked()
        else:
            self.radioBox.setChecked(newValue)
            return self
