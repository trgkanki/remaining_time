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
from qdlgproxy import QDlg, Text, Button  # type: ignore
from aqt.qt import QApplication, QMessageBox


@QDlg("Test dialog", size=[640, 480])
def qDlgClass(dlg):
    Text("Hello world!")

    def onClick():
        QMessageBox.warning(
            None,
            "test msgbox",
            "content",
        )

    Button("Hello world!").onClick(onClick)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qDlgClass.run()
