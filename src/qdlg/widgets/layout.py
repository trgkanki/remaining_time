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
from ..container import QDlgContainer
from ..utils import addLayoutOrWidget

from PyQt5.Qt import QVBoxLayout, QHBoxLayout


class LayoutBase(QDlgContainer):
    def __init__(self, LayoutClass, margin=0):
        self.layout = LayoutClass()
        self.layout.setContentsMargins(margin, margin, margin, margin)
        qDlgStackTop().addChild(self.layout)

    def addChild(self, child):
        addLayoutOrWidget(self.layout, child)
        return self


class VStack(LayoutBase):
    def __init__(self, margin=0):
        super().__init__(QVBoxLayout, margin)


class HStack(LayoutBase):
    def __init__(self, margin=0):
        super().__init__(QHBoxLayout, margin)
