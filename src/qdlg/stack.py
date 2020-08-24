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

import threading

local = threading.local()


def getQDlgStack():
    try:
        return local.qDlgStack
    except AttributeError:
        local.qDlgStack = []
        return local.qDlgStack


def pushQDlgStack(el):
    getQDlgStack().append(el)


def popQDlgStack(el):
    lastEl = getQDlgStack().pop()
    assert lastEl == el


def qDlgStackTop():
    return getQDlgStack()[-1]


def qDlgStackGetDialog():
    return getQDlgStack()[0]
