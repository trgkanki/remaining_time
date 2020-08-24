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
