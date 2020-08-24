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
    LineEdit,
    Button,
    Table,
    Tr,
    Td,
)
from PyQt5.Qt import QApplication


@QDlg("Table test")
def qDlgClass(dlg):
    with Table():
        with Tr():
            with Td():
                Text("Username")
            with Td():
                username = LineEdit()

        with Tr():
            with Td():
                Text("Password")
            with Td():
                password = LineEdit().passwordInput()

        with Tr():
            with Td(colspan=2):
                (
                    Button("Login")
                    .onClick(lambda: print(username.text(), password.text()))
                    .default()
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qDlgClass.run()
