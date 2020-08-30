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

from PyQt5.Qt import QKeySequence


class Shortcutable:
    def shortcut(self, keySequence: str):
        kSeq = QKeySequence(keySequence)
        self.widget.setShortcut(kSeq)
        self.widget.setToolTip(kSeq.toString())
        return self

    def default(self):
        self.widget.setDefault(True)
        return self
