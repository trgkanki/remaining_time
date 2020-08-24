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

from PyQt5.Qt import QLayout, QWidget


def addLayoutOrWidget(layout, child):
    if isinstance(child, QLayout):
        layout.addLayout(child)
    elif isinstance(child, QWidget):
        layout.addWidget(child)
    else:
        raise NotImplementedError


def continuationHelper(getter, setter):
    def _(self, newValue=None):
        if newValue is None:
            return getter(self)
        else:
            setter(self, newValue)
            return self

    return _
