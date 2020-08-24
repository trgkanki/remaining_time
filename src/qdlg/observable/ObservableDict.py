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


class ObservableDict(ObservableBase):
    _observable = True

    def __init__(self, obj, *, parent):
        super().__init__(parent)
        with self._noNotify():
            self._observableAssign(obj)

    def unobserved(self):
        return {k: unobserved(v) for k, v in self._obj.items()}

    # Read-only methods
    __len__ = _forwardMethod("__len__", False)
    __getitem__ = _forwardMethod("__getitem__", False)
    get = _forwardMethod("get", False)
    items = _forwardMethod("items", False)
    keys = _forwardMethod("keys", False)
    values = _forwardMethod("values", False)

    # Writing methods
    __delitem__ = _forwardMethod("__delitem__", True)
    pop = _forwardMethod("pop", True)
    clear = _forwardMethod("clear", True)

    def __setitem__(self, key, item):
        with self._noNotify():
            try:
                self._obj[key]._observableAssign(item)
            except (AttributeError, KeyError):
                item = makeObservable(item, parent=self)
                self._obj[key] = item

        self.notify()

    def update(self, d):
        with self._noNotify():
            self._obj.update({k: makeObservable(v, parent=self) for k, v in d.items()})

        self.notify()

    #######

    def _observableAssign(self, obj):
        with self._noNotify():
            self._obj = {k: makeObservable(v, parent=self) for k, v in obj.items()}
        self.notify()

    def __eq__(self, obj):
        if len(self) != len(obj):
            return False

        for k in self.keys():
            try:
                if self[k] != obj[k]:
                    return False
            except KeyError:
                return False
        return True
