from .obsproxy import observable
from nose.tools import with_setup, assert_equal


notified = set()


def register(v):
    def _():
        notified.add(id(v))

    v.registerObserver(_)


def assertNotified(*items):
    assert len(items) == len(notified)
    for item in items:
        assert id(item) in notified


a = observable({})


def setup_func():
    global a
    a = observable({"a": 1, "b": 2, "c": 3})
    register(a)
    notified.clear()


def teardown_func():
    pass


# Test for notifying things
@with_setup(setup_func, teardown_func)
def test_dict_setitem():
    a["a"] = 3
    assert a == {"a": 3, "b": 2, "c": 3}
    assert notified == {id(a)}


@with_setup(setup_func, teardown_func)
def test_dict_delitem():
    del a["a"]
    assert a == {"b": 2, "c": 3}
    assert notified == {id(a)}


@with_setup(setup_func, teardown_func)
def test_dict_getitem():
    assert_equal(a["a"], 1)
    assert a == {"a": 1, "b": 2, "c": 3}
    assert not notified


@with_setup(setup_func, teardown_func)
def test_dict_get():
    assert_equal(a.get("a", None), 1)
    assert_equal(a.get("d", None), None)
    assert not notified


@with_setup(setup_func, teardown_func)
def test_dict_keys():
    k = set(a.keys())
    assert_equal(k, {"a", "b", "c"})
    assert not notified


@with_setup(setup_func, teardown_func)
def test_dict_items():
    k = set(a.items())
    assert_equal(k, {("a", 1), ("b", 2), ("c", 3)})
    assert not notified


def test_nested_dict_list_dict():
    k = observable({"a": [{"b": 1, "c": 2}, {"b": 2, "c": 3}], "b": [{"b": 3, "c": 4}]})
    register(k)
    register(k["a"])
    register(k["a"][0])
    register(k["a"][1])
    register(k["b"])
    register(k["b"][0])

    notified.clear()
    assert_equal(k["a"][0]["b"], 1)
    assert not notified

    k["a"][0]["b"] = 2
    assert_equal(k["a"][0]["b"], 2)
    assertNotified(k, k["a"], k["a"][0])
