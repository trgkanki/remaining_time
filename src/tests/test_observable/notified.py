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
