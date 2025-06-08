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

from .obsproxy import observable
from .notified import registerNotification, assertNotified, resetNotification


a = observable([])


class TestList:
    def setup_method(self, method):
        global a
        a = observable([1, 3])
        registerNotification(a)
        resetNotification()

    def teardown_method(self, method):
        pass

    # Test for notifying things
    def test_list_setitem(self):
        a[0] = 2
        assert a == [2, 3]
        assertNotified([(a, 1)])

    def test_list_append(self):
        a.append(4)
        assertNotified([(a, 1)])
        assert a == [1, 3, 4]

    def test_list_pop(self):
        a.pop()
        assertNotified([(a, 1)])
        assert a == [1]

    def test_list_pop(self):
        a.clear()
        assertNotified([(a, 1)])
        assert a == []

    def test_list_extend(self):
        a.extend([4, 7])
        assertNotified([(a, 1)])
        assert a == [1, 3, 4, 7]

    def test_list_insert(self):
        a.insert(1, 5)
        assertNotified([(a, 1)])
        assert a == [1, 5, 3]

    # Test for non-notifying tests

    def test_list_getitem(self):
        assert a[1] == 3
        assertNotified()
        assert a == [1, 3]

    def test_list_str_repr(self):
        assert str(a) == "observable([1, 3])"
        assert repr(a) == "observable([1, 3])"
        assertNotified()

    def test_list_len(self):
        assert len(a) == 2
        assertNotified()

    def test_list_index(self):
        assert a.index(3) == 1
        assertNotified()

    def test_list_count(self):
        assert a.count(1) == 1
        assert a.count(4) == 0
        assertNotified()


def test_nested_list():
    a = observable([[1, 2], [3, 4]])
    registerNotification(a)
    registerNotification(a[0])
    registerNotification(a[1])

    resetNotification()
    a[0][0] = 0
    assert a == [[0, 2], [3, 4]]
    assertNotified(
        [
            (a, 1),
            (a[0], 1),
        ]
    )


class ClassHavingListAttribute:
    def __init__(self):
        self.l = [1, 2]


def test_nested_object_list():
    a = observable(ClassHavingListAttribute())
    registerNotification(a)
    registerNotification(a.l)

    resetNotification()
    a.l[0] = 3
    assert a.l == [3, 2]
    assertNotified(
        [
            (a, 1),
            (a.l, 1),
        ]
    )


class ClassHavingAttribute:
    def __init__(self):
        self.a = 4


def test_nested_list_object():
    a = observable([ClassHavingAttribute(), ClassHavingAttribute()])
    registerNotification(a)
    registerNotification(a[0])
    registerNotification(a[1])

    resetNotification()
    assert a[0].a == 4
    assertNotified()
    a[0].a = 3
    assert a[0].a == 3
    assertNotified(
        [
            (a, 1),
            (a[0], 1),
        ]
    )


def test_notification_count():
    """Test case while making word autocomplete configurator"""
    allDecks = observable(
        [
            {"id": 1, "name": "Default"},
            {"id": 2, "name": "Default 2"},
            {"id": 3, "name": "Default 3"},
            {"id": 4, "name": "Default 4"},
            {"id": 5, "name": "Default 5"},
            {"id": 6, "name": "Default 6"},
        ]
    )

    registerNotification(allDecks, allDecks[0])
    resetNotification()

    allDecks[0] = {"id": 7, "name": "Default 7"}
    assertNotified([(allDecks, 1), (allDecks[0], 1)])
