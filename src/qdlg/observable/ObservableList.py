from .utils import _forwardMethod
from .ObservableBase import ObservableBase
from .makeObservable import makeObservable


class ObservableList(ObservableBase):
    _observable = True

    def __init__(self, data, *, parent):
        super().__init__(parent)
        self._obj = [makeObservable(d, parent=self) for d in data]

    # Read-only methods
    __str__ = _forwardMethod("__str__", False)
    __repr__ = _forwardMethod("__repr__", False)
    __len__ = _forwardMethod("__len__", False)
    __getitem__ = _forwardMethod("__getitem__", False)
    index = _forwardMethod("index", False)
    count = _forwardMethod("count", False)

    # Writing methods
    pop = _forwardMethod("pop", True)
    clear = _forwardMethod("clear", True)

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            items = [makeObservable(d, parent=self) for d in item]
            try:
                targets = self._obj[index]
                for t, i in zip(targets, items):
                    t.observableAssign(i)
            except AttributeError:
                self._obj[index] = items

        else:
            item = makeObservable(item, parent=self)
            try:
                self._obj[index].observableAssign(item)
            except AttributeError:
                self._obj[index] = item

        self.notify()

    def append(self, item):
        self._obj.append(makeObservable(item, parent=self))
        self.notify()

    def extend(self, iterable):
        self._obj.extend(makeObservable(d, parent=self) for d in iterable)
        self.notify()

    def insert(self, index, item):
        self._obj.insert(index, makeObservable(item, parent=self))
        self.notify()

    def observableAssign(self, obj):
        self._obj = [makeObservable(d, parent=self) for d in obj]
        self.notify()

    def __eq__(self, obj):
        if len(self) != len(obj):
            return False

        for a, b in zip(self, obj):
            if a != b:
                return False
        return True
