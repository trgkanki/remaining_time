import inspect
import types

_immutableTypes = {int, str, bool, float}
_iterableType = {list, tuple}


def bind(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the 
    instance as the first argument, i.e. "self".

    from https://stackoverflow.com/questions/1015307/python-bind-an-unbound-method
    """
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method


def isObservable(obj):
    return (
        type(obj) in _immutableTypes
        or obj is None
        or hasattr(obj, "_observable")
        or callable(obj)  # immutable
    )


def observable(obj):
    if isObservable(obj):
        return obj

    if type(obj) in _iterableType:
        return ObservableList(obj)

    makeObjectObservable(obj)
    for attr in dir(obj):
        if not attr.startswith("_"):
            setattr(obj, attr, getattr(obj, attr))

    return obj


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
    __nonzero__ = _forwardMethod("__nonzero__", False)

    __getitem__ = _forwardMethod("__getitem__", False)
    index = _forwardMethod("index", False)
    count = _forwardMethod("count", False)
    copy = _forwardMethod("copy", False)

    # Writing methods
    pop = _forwardMethod("pop", True)
    clear = _forwardMethod("clear", True)

    def __setitem__(self, index, item):
        self._data[index] = observable(item)
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


def makeObjectObservable(obj):
    obj._observable = True

    oldInit = obj.__init__
    _attrObserversDict = {}

    # observer notification for attributes
    def _registerAttrObserver(self, name, handler):
        try:
            handlerList = _attrObserversDict[name]
        except KeyError:
            handlerList = []
            _attrObserversDict[name] = handlerList
        handlerList.append(handler)

    obj._registerAttrObserver = bind(obj, _registerAttrObserver)

    # Setters for attributes
    # note that to override special functions one has to modify its underlying type
    cls = type(obj)
    if not hasattr(cls, "_canBeObservable"):
        cls._canBeObservable = True

        oldSetAttr = cls.__setattr__

        def newSetAttr(self, name, value):
            if not isObservable(self):
                return oldSetAttr(obj, name, value)

            value = observable(value)
            oldSetAttr(obj, name, value)

            if not name.startswith("_"):  # ignore builtins/private
                for handler in _attrObserversDict.get(name, []):
                    handler(value)

        cls.__setattr__ = newSetAttr

    # setitem prohibited
    def prohibited(self, *args, **kwargs):
        raise RuntimeError("Cannot use the method on observable object")

    obj.__setitem__ = bind(obj, prohibited)
    obj.__getitem__ = bind(obj, prohibited)
