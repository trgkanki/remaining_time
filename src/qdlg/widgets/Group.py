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
from ..utils import addLayoutOrWidget
from ..container import QDlgContainer

from aqt.qt import QGroupBox, QVBoxLayout


class Group(QDlgContainer):
    def __init__(self, title: str):
        self.groupBox = QGroupBox(title)
        self.layout = QVBoxLayout()
        self.groupBox.setLayout(self.layout)
        qDlgStackTop().addChild(self.groupBox)

    def addChild(self, child):
        addLayoutOrWidget(self.layout, child)
        return self
