from qdlgproxy import observable


class TestClass:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2


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
