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
from .Style import StylableWidget
from .Shortcutable import Shortcutable

from PyQt5.Qt import QPushButton, QKeySequence


class Button(StylableWidget, Shortcutable):
    def __init__(self, label):
        super().__init__()
        self.widget = QPushButton(label)
        self.widget.setAutoDefault(False)
        qDlgStackTop().addChild(self.widget)

    def onClick(self, callback):
        self.widget.clicked.connect(callback)
        return self
