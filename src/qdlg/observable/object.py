from . import observable, isObservable
from .utils import bind


def ObservableObject(obj):
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

    # make attributes observable
    for attr in dir(obj):
        if not attr.startswith("_"):
            setattr(obj, attr, getattr(obj, attr))

    return obj
