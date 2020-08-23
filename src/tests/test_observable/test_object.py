from .obsproxy import observable
from nose.tools import assert_raises, assert_equal
from .notified import registerNotification, assertNotified, resetNotification


class TestClass:
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


class TestClass2:
    def __init__(self, p=None):
        if p is None:
            self.t = TestClass()
        else:
            self.t = p


def test_object_notification():
    a = observable(TestClass())

    resetNotification()
    registerNotification(a)
    assertNotified()

    a.attr1 = 2
    assertNotified(
        [(a, 1),]
    )
    assert_equal(a.attr1, 2)  # properly changed?


def test_nested_object_notification():
    a = observable(TestClass2())

    registerNotification(a)
    registerNotification(a.t)
    resetNotification()
    oldAT = a.t

    a.t.attr1 = 2
    assertNotified(
        [(a, 1), (a.t, 1),]
    )
    assert_equal(a.t.attr1, 2)  # properly changed?
    assert_equal(oldAT, a.t)

    resetNotification()
    a.t = TestClass()
    assertNotified(
        [(a, 1), (a.t, 1),]
    )


def test_no_shared_observable():
    a = observable(TestClass2())
    with assert_raises(AssertionError):
        observable(TestClass2(a.t))


def test_str_repr():
    a = observable(TestClass())
    assert_equal(str(a), "observable(str_0)")
    assert_equal(repr(a), "observable(repr_0)")


def test_obj_method_const():
    a = observable(TestClass())
    registerNotification(a)
    resetNotification()
    assert_equal(a.attrsum(), 3)
    assertNotified()
    a.mod()
    assertNotified(
        [(a, 1),]
    )
    assert_equal(a.attrsum(), 5)
