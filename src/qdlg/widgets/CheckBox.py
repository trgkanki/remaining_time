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
