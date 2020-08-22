from qdlgproxy import observable


class TestClass:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2


class TestClass2:
    def __init__(self):
        self.t = TestClass()


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
