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
from nose.tools import with_setup, assert_equal
from .notified import registerNotification, assertNotified, resetNotification


a = observable([])


def setup_func():
    global a
    a = observable([1, 3])
    registerNotification(a)
    resetNotification()


def teardown_func():
    pass


# Test for notifying things
@with_setup(setup_func, teardown_func)
def test_list_setitem():
    a[0] = 2
    assert_equal(a, [2, 3])
    assertNotified([(a, 1)])


@with_setup(setup_func, teardown_func)
def test_list_append():
    a.append(4)
    assertNotified([(a, 1)])
    assert_equal(a, [1, 3, 4])


@with_setup(setup_func, teardown_func)
def test_list_pop():
    a.pop()
    assertNotified([(a, 1)])
    assert_equal(a, [1])


@with_setup(setup_func, teardown_func)
def test_list_pop():
    a.clear()
    assertNotified([(a, 1)])
    assert_equal(a, [])


@with_setup(setup_func, teardown_func)
def test_list_extend():
    a.extend([4, 7])
    assertNotified([(a, 1)])
    assert_equal(a, [1, 3, 4, 7])


@with_setup(setup_func, teardown_func)
def test_list_insert():
    a.insert(1, 5)
    assertNotified([(a, 1)])
    assert_equal(a, [1, 5, 3])


# Test for non-notifying tests


@with_setup(setup_func, teardown_func)
def test_list_getitem():
    assert_equal(a[1], 3)
    assertNotified()
    assert_equal(a, [1, 3])


@with_setup(setup_func, teardown_func)
def test_list_str_repr():
    assert_equal(str(a), "observable([1, 3])")
    assert_equal(repr(a), "observable([1, 3])")
    assertNotified()


@with_setup(setup_func, teardown_func)
def test_list_len():
    assert_equal(len(a), 2)
    assertNotified()


@with_setup(setup_func, teardown_func)
def test_list_index():
    assert_equal(a.index(3), 1)
    assertNotified()


@with_setup(setup_func, teardown_func)
def test_list_count():
    assert_equal(a.count(1), 1)
    assert_equal(a.count(4), 0)
    assertNotified()


def test_nested_list():
    a = observable([[1, 2], [3, 4]])
    registerNotification(a)
    registerNotification(a[0])
    registerNotification(a[1])

    resetNotification()
    a[0][0] = 0
    assert_equal(a, [[0, 2], [3, 4]])
    assertNotified(
        [(a, 1), (a[0], 1),]
    )


class TestClass:
    def __init__(self):
        self.l = [1, 2]


def test_nested_object_list():
    a = observable(TestClass())
    registerNotification(a)
    registerNotification(a.l)

    resetNotification()
    a.l[0] = 3
    assert_equal(a.l, [3, 2])
    assertNotified(
        [(a, 1), (a.l, 1),]
    )


class TestClass2:
    def __init__(self):
        self.a = 4


def test_nested_list_object():
    a = observable([TestClass2(), TestClass2()])
    registerNotification(a)
    registerNotification(a[0])
    registerNotification(a[1])

    resetNotification()
    assert_equal(a[0].a, 4)
    assertNotified()
    a[0].a = 3
    assert_equal(a[0].a, 3)
    assertNotified(
        [(a, 1), (a[0], 1),]
    )


def test_notification_count():
    """ Test case while making word autocomplete configurator """
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
