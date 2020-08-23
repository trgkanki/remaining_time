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

from contextlib import contextmanager


class ObservableBase:
    def __init__(self, parent):
        self._handlerList = []
        self._parent = parent
        self._suppressNotification = 0

    def registerObserver(self, handler):
        self._handlerList.append(handler)

    def notify(self):
        if self._suppressNotification:
            return

        for handler in self._handlerList:
            handler()

        if self._parent is not None:
            self._parent.notify()

    def unobserved(self):
        """Generate non-observable copy of this object"""
        raise NotImplementedError

    @contextmanager
    def _noNotify(self):
        self._suppressNotification += 1
        yield
        self._suppressNotification -= 1

    def _observableAssign(self, obj):
        raise NotImplementedError

    def __str__(self):
        return "observable(%s)" % self._obj

    def __repr__(self):
        return "observable(%s)" % repr(self._obj)


def isObservable(obj):
    return isinstance(obj, ObservableBase)
