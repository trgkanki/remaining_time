from . import observable


def _forwardMethod(key, callHandlersAfter):
    def _(self, *args, **kwargs):
        ret = getattr(self._data, key)(*args, **kwargs)
        if callHandlersAfter:
            self.notify()
        return ret

    return _


class ObservableList(list):
    _observable = True

    def __init__(self, data):
        self._data = [observable(d) for d in data]
        self._handlers = []

    def notify(self):
        for handler in self._handlers:
            handler()

    def _registerItemObserver(self, handler):
        self._handlers.append(handler)

    # Read-only methods
    __str__ = _forwardMethod("__str__", False)
    __repr__ = _forwardMethod("__repr__", False)
    __len__ = _forwardMethod("__len__", False)

    # TODO: below somehow doesn't work. need to know why
    # __iter___ = _forwardMethod("__iter___", False)
    def __iter__(self):
        return iter(self._data)

    __getitem__ = _forwardMethod("__getitem__", False)
    index = _forwardMethod("index", False)
    count = _forwardMethod("count", False)
    copy = _forwardMethod("copy", False)

    # Writing methods
    pop = _forwardMethod("pop", True)
    clear = _forwardMethod("clear", True)

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            item = [observable(d) for d in item]
        else:
            item = observable(item)
        self._data[index] = item
        self.notify()

    def append(self, item):
        self._data.append(observable(item))
        self.notify()

    def extend(self, iterable):
        self._data.extend(observable(d) for d in iterable)
        self.notify()

    def insert(self, index, item):
        self._data.insert(index, observable(item))
        self.notify()
