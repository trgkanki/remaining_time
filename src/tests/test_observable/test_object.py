from .obsproxy import observable
from nose.tools import assert_raises


class TestClass:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2

    def __str__(self):
        return "str_0"

    def __repr__(self):
        return "repr_0"


class TestClass2:
    def __init__(self, p=None):
        if p is None:
            self.t = TestClass()
        else:
            self.t = p


notified = set()


def notifyLogger(v):
    def _():
        notified.add(v)

    return _


def test_object_notification():
    a = observable(TestClass())

    notified.clear()
    a.registerObserver(notifyLogger(a))
    assert len(notified) == 0

    a.attr1 = 2
    assert notified == {a}
    assert a.attr1 == 2  # properly changed?


def test_nested_object_notification():
    a = observable(TestClass2())

    notified.clear()
    a.registerObserver(notifyLogger(a))
    a.t.registerObserver(notifyLogger(a.t))
    assert len(notified) == 0

    oldAT = a.t

    a.t.attr1 = 2
    assert notified == {a, a.t}
    assert a.t.attr1 == 2  # properly changed?
    assert oldAT == a.t


def test_no_shared_observable():
    a = observable(TestClass2())
    with assert_raises(AssertionError):
        observable(TestClass2(a.t))


def test_str_repr():
    a = observable(TestClass())
    assert str(a) == "str_0"
    assert repr(a) == "repr_0"
