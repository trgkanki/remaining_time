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

import sys
from qdlgproxy import QDlg, ListBox, observable
from PyQt5.Qt import QApplication, QAbstractItemView


class TestClass:
    def __init__(self):
        self.selectedList = [
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
        ]


@QDlg("ListBox test")
def qDlgClass(dlg):
    t = observable(TestClass())
    s = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
    ]
    ListBox(s, renderer=lambda item: "item %d" % item).multiselect(
        QAbstractItemView.MultiSelection
    ).model(t, attr="selectedList").onSelect(print)
    ListBox(t.selectedList, renderer=lambda item: "item %d" % item).sorted()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qDlgClass.run()
