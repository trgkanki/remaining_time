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

from PyQt5.Qt import QDialog, QVBoxLayout, Qt

from .stack import pushQDlgStack, popQDlgStack, qDlgStackGetDialog
from .utils import addLayoutOrWidget


def QDlg(title, size=None):
    class _QDlg:
        def __init__(self, constructor):
            self.constructor = constructor

        def run(self, *args, **kwargs):
            """Create & show dialog

            Args:
                onClose(accepted): Function to run on close. Defaults to None.
            """
            dlg = QDialog()
            dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            dlg.setWindowTitle(title)

            layout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            self.layout = layout
            dlg.setLayout(layout)

            pushQDlgStack(self)
            self.constructor(dlg, *args, **kwargs)
            popQDlgStack(self)

            dlg.setWindowModality(Qt.WindowModal)
            if size:
                dlg.resize(size[0], size[1])
            dlg.show()
            return dlg.exec_() == QDialog.Accepted

        def addChild(self, child):
            addLayoutOrWidget(self.layout, child)

    return _QDlg
