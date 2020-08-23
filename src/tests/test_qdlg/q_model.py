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
from qdlgproxy import (  # type: ignore
    QDlg,
    Text,
    Group,
    LineEdit,
    Button,
    CheckBox,
    RadioButton,
    Table,
    Tr,
    Td,
    observable,
)
from PyQt5.Qt import QApplication


class TestClass:
    def __init__(self):
        self.check1 = False
        self.selection1 = 3
        self.text1 = ""
        self.checkArray = [False, False, False]

    def __str__(self):
        return (
            f"({self.check1}, {self.selection1}, {repr(self.text1)}, {self.checkArray})"
        )


@QDlg("Table test")
def qDlgClass(dlg):
    obj = observable(TestClass())

    with Group("orig"):
        with Table():
            with Tr():
                with Td():
                    Text("LineEdit test")
                with Td():
                    LineEdit().model(obj, attr="text1")

            with Tr():
                with Td():
                    Text("Checkbox test")
                with Td():
                    CheckBox().model(obj, attr="check1")

            with Tr():
                with Td():
                    Text("Radiobutton test")
                with Td():
                    RadioButton("Item 1", value=1).model(obj, attr="selection1")
                    RadioButton("Item 2", value=2).model(obj, attr="selection1")
                    RadioButton("Item 3", value=3).model(obj, attr="selection1")
                    RadioButton("Item 4", value=4).model(obj, attr="selection1")
                    RadioButton("Item 5", value=5).model(obj, attr="selection1")

            with Tr():
                with Td():
                    Text("Array test")
                with Td():
                    CheckBox().model(obj.checkArray, index=0)
                    CheckBox().model(obj.checkArray, index=1)
                    CheckBox().model(obj.checkArray, index=2)

            with Tr():
                with Td(colspan=2):
                    Button("Dump").onClick(lambda: print(str(obj)))

    # Reactivity - should sync with above
    with Group("should sync with above"):
        with Table():
            with Tr():
                with Td():
                    Text("LineEdit test")
                with Td():
                    LineEdit().model(obj, attr="text1")

            with Tr():
                with Td():
                    Text("Checkbox test")
                with Td():
                    CheckBox().model(obj, attr="check1")

            with Tr():
                with Td():
                    Text("Radiobutton test")
                with Td():
                    RadioButton("Item 1", value=1).model(obj, attr="selection1")
                    RadioButton("Item 2", value=2).model(obj, attr="selection1")
                    RadioButton("Item 3", value=3).model(obj, attr="selection1")
                    RadioButton("Item 4", value=4).model(obj, attr="selection1")
                    RadioButton("Item 5", value=5).model(obj, attr="selection1")

            with Tr():
                with Td():
                    Text("Array test")
                with Td():
                    CheckBox().model(obj.checkArray, index=0)
                    CheckBox().model(obj.checkArray, index=1)
                    CheckBox().model(obj.checkArray, index=2)

            with Tr():
                with Td(colspan=2):
                    Button("Dump").onClick(lambda: print(str(obj)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qDlgClass.run()
