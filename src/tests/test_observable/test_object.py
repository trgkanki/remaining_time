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

import pytest
from .obsproxy import observable
from .notified import registerNotification, assertNotified, resetNotification


class A:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2

    def __str__(self):
        return "str_0"

    def __repr__(self):
        return "repr_0"

    def attrsum(self):
        return self.attr1 + self.attr2

    def mod(self):
        self.attr1 = 3


class B:
    def __init__(self, p=None):
        if p is None:
            self.t = A()
        else:
            self.t = p


def test_object_notification():
    a = observable(A())

    resetNotification()
    registerNotification(a)
    assertNotified()

    a.attr1 = 2
    assertNotified(
        [
            (a, 1),
        ]
    )
    assert a.attr1 == 2  # properly changed?


def test_nested_object_notification():
    a = observable(B())

    registerNotification(a)
    registerNotification(a.t)
    resetNotification()
    oldAT = a.t

    a.t.attr1 = 2
    assertNotified(
        [
            (a, 1),
            (a.t, 1),
        ]
    )
    assert a.t.attr1 == 2  # properly changed?
    assert oldAT == a.t

    resetNotification()
    a.t = A()
    assertNotified(
        [
            (a, 1),
            (a.t, 1),
        ]
    )


def test_no_shared_observable():
    a = observable(B())
    with pytest.raises(AssertionError):
        observable(B(a.t))


def test_str_repr():
    a = observable(A())
    assert str(a) == "observable(str_0)"
    assert repr(a) == "observable(repr_0)"


def test_obj_method_const():
    a = observable(A())
    registerNotification(a)
    resetNotification()
    assert a.attrsum() == 3
    assertNotified()
    a.mod()
    assertNotified(
        [
            (a, 1),
        ]
    )
    assert a.attrsum() == 5
