from nose.tools import assert_equal
from functools import partial

_notified = {}


def registerNotification(*items):
    for v in items:

        def _(v):
            _notified[id(v)] = _notified.get(id(v), 0) + 1

        v.registerObserver(partial(_, v))


def assertNotified(*items):
    assert len(items) == len(_notified)
    for item in items:
        assert id(item) in _notified


def assertNotifiedCount(v, count):
    assert_equal(_notified.get(id(v), 0), count)


def resetNotification():
    _notified.clear()
