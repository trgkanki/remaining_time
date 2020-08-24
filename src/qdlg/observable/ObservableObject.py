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

from .utils import bind, _forwardMethod
from .ObservableBase import ObservableBase
from .makeObservable import makeObservable
import inspect


_observableMethods = {"registerObserver", "notify", "_observableAssign", "_obj"}


def nonObservableAttribute(obj, attrName):
    return (
        attrName.startswith("__")
        or inspect.ismethod(getattr(obj, attrName))  # User-defined method
        or inspect.isbuiltin(getattr(obj, attrName))  # list::append thjngs
        or attrName in _observableMethods
    )


def observableAttributes(obj):
    if isinstance(obj, ObservableObject):
        return observableAttributes(obj._obj)

    return sorted(n for n in dir(obj) if not nonObservableAttribute(obj, n))


_classAttributes = {"_handlerList", "_parent", "_suppressNotification", "_obj"}


class ObservableObject(ObservableBase):
    _observable = True

    def __init__(self, obj, *, parent):
        super().__init__(parent)

        # _observableAssign uses dir(self._obj) to figure out what keys to assign.
        # so we first need to set self._obj to obj
        self._obj = obj
        self._observableAssign(obj)

    def unobserved(self):
        # Class may have custom constructor and custom semantics which we cannot follow readily.
        # so we just give up on implementing this.
        raise NotImplementedError

    ##
    __hash__ = _forwardMethod("__hash__", False)

    def __getattr__(self, name):
        ret = getattr(self._obj, name)
        if inspect.ismethod(ret):
            return bind(self, getattr(type(self._obj), name))
        else:
            return ret

    def __setattr__(self, name, value):
        if name in _classAttributes:
            return super().__setattr__(name, value)

        if not nonObservableAttribute(self, name):
            target = getattr(self._obj, name)
            with self._noNotify():
                try:
                    target._observableAssign(value)
                except AttributeError:
                    setattr(self._obj, name, value)
            self.notify()
        else:
            setattr(self._obj, name, value)

    def _observableAssign(self, obj):
        with self._noNotify():
            for name in observableAttributes(self._obj):
                old = getattr(obj, name)
                setattr(self._obj, name, makeObservable(old, parent=self))
        self.notify()

    def __eq__(self, obj):
        assignerAttributes = observableAttributes(self)
        assigneeAttributes = observableAttributes(obj)
        if assigneeAttributes != assigneeAttributes:
            return False
        for k in assignerAttributes:
            if getattr(self, k) != getattr(self._obj, k):
                return False
        return True
