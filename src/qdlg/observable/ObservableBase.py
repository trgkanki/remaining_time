class ObservableBase:
    def __init__(self, parent):
        self._handlerList = []
        self._parent = parent

    def registerObserver(self, handler):
        self._handlerList.append(handler)

    def notify(self):
        for handler in self._handlerList:
            handler()

        if self._parent is not None:
            self._parent.notify()

    def observableAssign(self, obj):
        raise NotImplementedError

    def __str__(self):
        return "observable(%s)" % self._obj

    def __repr__(self):
        return "observable(%s)" % repr(self._obj)


def isObservable(obj):
    return isinstance(obj, ObservableBase)
