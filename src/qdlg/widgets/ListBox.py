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
from ..utils import addLayoutOrWidget, continuationHelper
from ..container import QDlgContainer
from ..observable import isObservable
from ..modelHandler import configureModel
from .Style import StylableWidget

from PyQt5.Qt import QListWidget, QListWidgetItem, Qt, QPoint, QAbstractItemView

from typing import Union, List, Any


class ListBox(StylableWidget):
    def __init__(self, data, *, renderer=lambda x: x):
        super().__init__()
        self.widget = QListWidget()
        self._data = data
        self._renderer = renderer

        self._multiselect = False
        self._sorted = False

        if isObservable(data):
            data.registerObserver(self._refillData)

        self._refillData()
        qDlgStackTop().addChild(self.widget)

    def _refillData(self):
        widget = self.widget

        oldBlockSignals = widget.blockSignals(True)
        oldAutoScroll = widget.hasAutoScroll()
        widget.setAutoScroll(False)

        # Scroll preserving code. From
        # https://stackoverflow.com/questions/34237006/qlistview-how-to-automatically-scroll-the-view-and-keep-current-selection-on-co
        vScrollBar = widget.verticalScrollBar()
        previousViewTopRow = widget.indexAt(QPoint(4, 4)).row()
        hasScrolledToBottom = vScrollBar.value() == vScrollBar.maximum()

        oldSelect = self.select()
        if oldSelect is None:
            oldSelect = []
        elif not self._multiselect:
            oldSelect = [oldSelect]

        widget.clear()
        for d in self._data:
            item = QListWidgetItem()
            item.setText(self._renderer(d))
            item.setData(Qt.UserRole, d)
            widget.addItem(item)
            if d in oldSelect:
                item.setSelected(True)

        if self._sorted:
            widget.sortItems()

        widget.scrollToTop()
        topIndex = widget.indexAt(QPoint(4, 4))
        widget.setAutoScroll(
            oldAutoScroll
        )  # Re-enable autoscroll before scrolling to appropriate position
        if hasScrolledToBottom:
            widget.scrollToBottom()
        else:
            widget.scrollTo(
                topIndex.sibling(previousViewTopRow, 0), QAbstractItemView.PositionAtTop
            )

        widget.blockSignals(oldBlockSignals)

        # Actually we should check that same set of items were selected before & after the change,
        # but widget only selects less when underlying data changes, so no more data could be
        # selected any other than oldSelect. So it's sufficient to only check the length to
        # see if two list are same irrespective of orderings.
        if len(widget.selectedItems()) != len(oldSelect):
            self.widget.itemSelectionChanged.emit()

    def select(self, newValues=None):
        widget = self.widget

        if newValues is None:
            selItems = widget.selectedItems()
            if not selItems:
                if self._multiselect:
                    return []
                else:
                    return None

            if self._multiselect:
                return [selItem.data(Qt.UserRole) for selItem in selItems]
            else:
                return selItems[0].data(Qt.UserRole)

        else:
            if not self._multiselect:
                newValues = [newValues]

            for index in range(widget.count()):
                item = widget.item(index)
                if item.data(Qt.UserRole) in newValues:
                    item.setSelected(True)
                else:
                    item.setSelected(False)

            return self

    def onSelect(self, callback):
        def _():
            callback(self.select())

        self.widget.itemSelectionChanged.connect(_)
        return self

    def model(self, obj, *, attr=None, index=None):
        configureModel(obj, self.onSelect, self.select, attr=attr, index=index)
        return self

    # QListWidget properties

    def multiselect(self, enabled=True):
        if enabled is True:
            enabled = QListWidget.ExtendedSelection
        elif enabled is False:
            enabled = QListWidget.SingleSelection

        self.widget.setSelectionMode(enabled)
        self._multiselect = enabled != QListWidget.SingleSelection
        return self

    def sorted(self, enabled=True):
        self._sorted = enabled
        self._refillData()
        return self
