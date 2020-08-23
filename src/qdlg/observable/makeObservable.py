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

from .ObservableBase import ObservableBase, isObservable


_immutableTypes = {int, str, bytes, bool, float}
_unsupportedTypes = {bytearray}
_iterableType = {list, tuple}


def isImmutable(obj):
    return type(obj) in _immutableTypes or obj is None or callable(obj)


def makeObservable(obj, *, parent):
    from .ObservableObject import ObservableObject
    from .ObservableList import ObservableList
    from .ObservableDict import ObservableDict

    if type(obj) in _unsupportedTypes:
        raise RuntimeError(
            "Object %s of type %s is not yet made observable." % (obj, type(obj))
        )

    if isinstance(obj, ObservableBase):
        assert obj._parent is parent
        return obj

    if isImmutable(obj):
        return obj

    if type(obj) in _iterableType:
        return ObservableList(obj, parent=parent)

    if type(obj) is dict:
        return ObservableDict(obj, parent=parent)

    return ObservableObject(obj, parent=parent)


def unobserved(obj):
    if isinstance(obj, ObservableBase):
        return obj.unobserved()
    else:
        return obj
