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
