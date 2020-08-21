from ..stack import qDlgStackTop
from ..utils import addLayoutOrWidget, continuationHelper
from ..container import QDlgContainer
from ..observable import isObservable
from ..observable.list import ObservableList
from ..modelHandler import configureModel
from .Style import StylableWidget

from PyQt5.Qt import QListWidget, QListWidgetItem, Qt

from typing import Union, List, Any


class ListBox(StylableWidget):
    def __init__(
        self,
        data: Union[list, ObservableList],
        *,
        renderer=lambda x: x,
        multiselect=False
    ):
        super().__init__()
        self.widget = QListWidget()
        self._data = data
        self._multiselect = multiselect
        self._renderer = renderer

        if multiselect:
            self.widget.setSelectionMode(QListWidget.ExtendedSelection)

        if isObservable(data):
            data._registerItemObserver(self._refillData)

        self._refillData()
        qDlgStackTop().addChild(self.widget)

    def _refillData(self):
        widget = self.widget

        widget.clear()
        for d in self._data:
            item = QListWidgetItem()
            item.setText(self._renderer(d))
            item.setData(Qt.UserRole, d)
            widget.addItem(item)

    def select(self, newValues=None):
        widget = self.widget

        if newValues is None:
            selItems = widget.selectedItems()
            if not selItems:
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
