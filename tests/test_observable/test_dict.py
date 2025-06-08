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
from .notified import (
    registerNotification,
    assertNotified,
    resetNotification,
)

a = observable({})


def setup_func():
    global a
    a = observable({"a": 1, "b": 2, "c": 3})
    registerNotification(a)
    resetNotification()


def teardown_func():
    pass


class TestDict:
    def setup_method(self, method):
        global a
        a = observable({"a": 1, "b": 2, "c": 3})
        registerNotification(a)
        resetNotification()

    def teardown_method(self, method):
        pass

    # Test for notifying things
    def test_dict_setitem(self):
        a["a"] = 3
        assert a == {"a": 3, "b": 2, "c": 3}
        assertNotified(
            [
                (a, 1),
            ]
        )

    def test_dict_delitem(self):
        del a["a"]
        assert a == {"b": 2, "c": 3}
        assertNotified(
            [
                (a, 1),
            ]
        )

    def test_dict_getitem(self):
        assert a["a"] == 1
        assert a == {"a": 1, "b": 2, "c": 3}
        assertNotified()

    def test_dict_get(self):
        assert a.get("a", None) == 1
        assert a.get("d", None) == None
        assertNotified()

    def test_dict_keys(self):
        k = set(a.keys())
        assert k == {"a", "b", "c"}
        assertNotified()

    def test_dict_items(self):
        k = set(a.items())
        assert k == {("a", 1), ("b", 2), ("c", 3)}
        assertNotified()


def test_nested_dict_list_dict():
    k = observable({"a": [{"b": 1, "c": 2}, {"b": 2, "c": 3}], "b": [{"b": 3, "c": 4}]})
    registerNotification(k)
    registerNotification(k["a"])
    registerNotification(k["a"][0])
    registerNotification(k["a"][1])
    registerNotification(k["b"])
    registerNotification(k["b"][0])

    resetNotification()
    assert k["a"][0]["b"] == 1
    assertNotified()

    k["a"][0]["b"] = 2
    assert k["a"][0]["b"] == 2
    assertNotified(
        [
            (k, 1),
            (k["a"], 1),
            (k["a"][0], 1),
        ]
    )


def test_nested_list_dict_bug():
    k = observable({"a": [{"b": 1, "c": 2}, {"b": 2, "c": 3}], "b": [{"b": 3, "c": 4}]})

    resetNotification()
    registerNotification(k)
    registerNotification(k["a"])
    registerNotification(k["a"][0])
    registerNotification(k["a"][1])
    registerNotification(k["b"])
    registerNotification(k["b"][0])

    k["a"] = [{"b": 0, "c": 7}]  # This should not throw
    assertNotified(
        [
            (k, 1),
            (k["a"], 1),
        ]
    )

    resetNotification()
    k["c"] = [{"b": 3, "c": 5}]  # This should not throw
    assertNotified([(k, 1)])
    assert k == {
        "a": [{"b": 0, "c": 7}],
        "b": [{"b": 3, "c": 4}],
        "c": [{"b": 3, "c": 5}],
    }


def test_configurator():
    """Test case while making wautocomplete configurator"""
    allDecks = [
        {"id": 1, "name": "Default"},
        {"id": 2, "name": "Default 2"},
        {"id": 3, "name": "Default 3"},
        {"id": 4, "name": "Default 4"},
        {"id": 5, "name": "Default 5"},
        {"id": 6, "name": "Default 6"},
    ]

    addonConfig = observable(
        {
            "blacklistDeckIds": [],
            "firstCommitHotkey": "tab",
            "numberedCommitHotkey": "ctrl+?",
        }
    )

    registerNotification(addonConfig, addonConfig["blacklistDeckIds"])
    resetNotification()

    addonConfig["blacklistDeckIds"] = allDecks[:3]
    assertNotified(
        [
            (addonConfig, 1),
            (addonConfig["blacklistDeckIds"], 1),
        ]
    )
