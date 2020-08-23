from contextlib import contextmanager


class ObservableBase:
    def __init__(self, parent):
        self._handlerList = []
        self._parent = parent
        self._suppressNotification = 0

    def registerObserver(self, handler):
        self._handlerList.append(handler)

    def notify(self):
        if self._suppressNotification:
            return

        for handler in self._handlerList:
            handler()

        if self._parent is not None:
            self._parent.notify()

    def unobserved(self):
        """Generate non-observable copy of this object"""
        raise NotImplementedError

    @contextmanager
    def _noNotify(self):
        self._suppressNotification += 1
        yield
        self._suppressNotification -= 1

    def _observableAssign(self, obj):
        raise NotImplementedError

    def __str__(self):
        return "observable(%s)" % self._obj

    def __repr__(self):
        return "observable(%s)" % repr(self._obj)


def isObservable(obj):
    return isinstance(obj, ObservableBase)
