from .obsproxy import observable
from nose.tools import with_setup, assert_equal
from .notified import registerNotification, assertNotified, resetNotification

a = observable({})


def setup_func():
    global a
    a = observable({"a": 1, "b": 2, "c": 3})
    registerNotification(a)
    resetNotification()


def teardown_func():
    pass


# Test for notifying things
@with_setup(setup_func, teardown_func)
def test_dict_setitem():
    a["a"] = 3
    assert_equal(a, {"a": 3, "b": 2, "c": 3})
    assertNotified(a)


@with_setup(setup_func, teardown_func)
def test_dict_delitem():
    del a["a"]
    assert_equal(a, {"b": 2, "c": 3})
    assertNotified(a)


@with_setup(setup_func, teardown_func)
def test_dict_getitem():
    assert_equal(a["a"], 1)
    assert_equal(a, {"a": 1, "b": 2, "c": 3})
    assertNotified()


@with_setup(setup_func, teardown_func)
def test_dict_get():
    assert_equal(a.get("a", None), 1)
    assert_equal(a.get("d", None), None)
    assertNotified()


@with_setup(setup_func, teardown_func)
def test_dict_keys():
    k = set(a.keys())
    assert_equal(k, {"a", "b", "c"})
    assertNotified()


@with_setup(setup_func, teardown_func)
def test_dict_items():
    k = set(a.items())
    assert_equal(k, {("a", 1), ("b", 2), ("c", 3)})
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
    assert_equal(k["a"][0]["b"], 1)
    assertNotified()

    k["a"][0]["b"] = 2
    assert_equal(k["a"][0]["b"], 2)
    assertNotified(k, k["a"], k["a"][0])


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
    assertNotified(k, k["a"])

    resetNotification()
    k["c"] = [{"b": 3, "c": 5}]  # This should not throw
    assertNotified(k)
    assert_equal(
        k, {"a": [{"b": 0, "c": 7}], "b": [{"b": 3, "c": 4}], "c": [{"b": 3, "c": 5}],}
    )
