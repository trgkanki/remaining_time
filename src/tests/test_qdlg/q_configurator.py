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

from qdlgproxy import (
    QDlg,
    Text,
    Button,
    ListBox,
    LineEdit,
    observable,
    HStack,
    Table,
    Tr,
    Td,
)

from PyQt5.Qt import QApplication, QAbstractItemView
import sys

# # Word autocompltete - configuration

# ## firstCommitHotkey

# - Pressing this key will commit the first suggestion
# - Default: `tab`

# ## numberedCommitHotkey

# - Pressing this key will commit the `n`-th suggestion, where `?` is replaced by `n`
# - Example: When this field is `ctrl+?`, a set of hotkey `ctrl+1`, `ctrl+2`, .. , `ctrl+9` commits 1st, 2nd, ... , and 9th suggestions.
# - Default: `ctrl+?`


@QDlg("Configure word_autocomplete", (400, 600))
def addonConfigWindow(dlg, allDecks, config):
    with Table():
        with Tr():
            with Td():
                Text("1st suggestion hotkey")
            with Td():
                LineEdit().model(config, index="firstCommitHotkey")

        with Tr():
            with Td():
                Text("ntt suggestion hotkey")
            with Td():
                LineEdit().model(config, index="numberedCommitHotkey")

        with Tr():
            with Td(colspan=2):
                Text("Deck blacklist")

        with Tr():
            with Td(colspan=2):
                (
                    ListBox(allDecks, renderer=lambda d: d["name"])
                    .multiselect(QAbstractItemView.MultiSelection)
                    .model(config, index="blacklistDeckIds")
                )

    with HStack():
        Button("OK").onClick(lambda: dlg.accept())
        Button("Cancel").onClick(lambda: dlg.reject())


if __name__ == "__main__":
    allDecks = [
        {"id": 1, "name": "Default"},
        {"id": 2, "name": "Default 2"},
        {"id": 3, "name": "Default 3"},
    ]

    addonConfig = observable(
        {
            "blacklistDeckIds": [],
            "firstCommitHotkey": "tab",
            "numberedCommitHotkey": "ctrl+?",
        }
    )

    app = QApplication(sys.argv)
    if addonConfigWindow.run(allDecks, addonConfig):
        print(addonConfig)
