# Copyright (C) 2020 Hyun Woo Park
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ..stack import qDlgStackTop
from ..utils import continuationHelper
from ..modelHandler import configureModel
from .Style import StylableWidget

from PyQt5.Qt import QLineEdit


class LineEdit(StylableWidget):
    def __init__(self, initialText=""):
        super().__init__()
        self.widget = QLineEdit()
        if initialText:
            self.widget.setText(initialText)
        qDlgStackTop().addChild(self.widget)

    placeholderText = continuationHelper(
        lambda self: self.widget.placeholderText(),
        lambda self, v: self.widget.setPlaceholderText(v),
    )

    text = continuationHelper(
        lambda self: self.widget.text(), lambda self, v: self.widget.setText(v)
    )

    def passwordInput(self, enabled=True):
        if enabled:
            self.widget.setEchoMode(QLineEdit.Password)
        else:
            self.widget.setEchoMode(QLineEdit.Normal)
        return self

    def onInput(self, callback):
        self.widget.textChanged.connect(callback)
        return self

    def onChange(self, callback):
        self.widget.editingFinished.connect(lambda: callback(self.text()))
        return self

    def model(self, obj, *, attr=None, index=None):
        configureModel(obj, self.onInput, self.text, attr=attr, index=index)
        return self
