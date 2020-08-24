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

from .utils import _forwardMethod
from .ObservableBase import ObservableBase
from .makeObservable import makeObservable, unobserved


class ObservableList(ObservableBase):
    _observable = True

    def __init__(self, data, *, parent):
        super().__init__(parent)
        self._observableAssign(data)

    def unobserved(self):
        return [unobserved(v) for v in self._obj]

    # Read-only methods
    __len__ = _forwardMethod("__len__", False)
    __getitem__ = _forwardMethod("__getitem__", False)
    index = _forwardMethod("index", False)
    count = _forwardMethod("count", False)

    # Writing methods
    pop = _forwardMethod("pop", True)
    clear = _forwardMethod("clear", True)

    def __setitem__(self, index, item):
        with self._noNotify():
            if isinstance(index, slice):
                items = [makeObservable(d, parent=self) for d in item]
                try:
                    targets = self._obj[index]
                    for t, i in zip(targets, items):
                        t._observableAssign(i)
                except AttributeError:
                    self._obj[index] = items

            else:
                item = makeObservable(item, parent=self)
                try:
                    self._obj[index]._observableAssign(item)
                except AttributeError:
                    self._obj[index] = item

        self.notify()

    def append(self, item):
        with self._noNotify():
            self._obj.append(makeObservable(item, parent=self))
        self.notify()

    def extend(self, iterable):
        with self._noNotify():
            self._obj.extend(makeObservable(d, parent=self) for d in iterable)
        self.notify()

    def insert(self, index, item):
        with self._noNotify():
            self._obj.insert(index, makeObservable(item, parent=self))
        self.notify()

    def _observableAssign(self, obj):
        with self._noNotify():
            self._obj = [makeObservable(d, parent=self) for d in obj]
        self.notify()

    def __eq__(self, obj):
        if len(self) != len(obj):
            return False

        for a, b in zip(self, obj):
            if a != b:
                return False
        return True
