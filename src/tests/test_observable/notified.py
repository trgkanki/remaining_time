from nose.tools import assert_equal
from functools import partial

_notified = {}
_objMap = {}


def registerNotification(*items):
    for v in items:

        def _(v):
            _notified[id(v)] = _notified.get(id(v), 0) + 1

        v.registerObserver(partial(_, v))
        _objMap[id(v)] = v


def assertNotified(expectedPairList=None):
    if expectedPairList is None:
        expectedPairList = []

    idObjMap = {}
    for k, v in expectedPairList:
        _objMap[id(k)] = k

    expectedIdsDict = {id(k): v for k, v in expectedPairList}

    if expectedIdsDict != _notified:
        expectedIdSet = set((k, v) for k, v in expectedIdsDict.items())
        notifiedIdSet = set((k, v) for k, v in _notified.items())
        diffMissed = expectedIdSet - notifiedIdSet
        diffOvernotified = notifiedIdSet - expectedIdSet
        raise AssertionError(
            """\
Different notification from expected
 - Over-notified:
%s
 - Under-notified:
%s
"""
            % (
                "\n".join("  + %d: %s" % (v, _objMap[k]) for k, v in diffOvernotified),
                "\n".join("  + %d: %s" % (v, _objMap[k]) for k, v in diffMissed),
            )
        )


def resetNotification():
    _notified.clear()
