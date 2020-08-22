from .utils import bind, _forwardMethod
from .ObservableBase import ObservableBase
from .makeObservable import makeObservable
import inspect


_observableMethods = {"registerObserver", "notify", "observableAssign", "_obj"}


def nonObservableAttribute(obj, attrName):
    return (
        attrName.startswith("__")
        or inspect.ismethod(getattr(obj, attrName))  # User-defined method
        or inspect.isbuiltin(getattr(obj, attrName))  # list::append thjngs
        or attrName in _observableMethods
    )


def observableAttributes(obj):
    if isinstance(obj, ObservableObject):
        return observableAttributes(obj._obj)

    return sorted(n for n in dir(obj) if not nonObservableAttribute(obj, n))


class ObservableObject(ObservableBase):
    _observable = True

    def __init__(self, obj, *, parent):
        super().__init__(parent)

        # observableAssign uses dir(self._obj) to figure out what keys to assign.
        # so we first need to set self._obj to obj
        self._obj = obj
        self.observableAssign(obj)

    ##
    __hash__ = _forwardMethod("__hash__", False)

    def __getattr__(self, name):
        ret = getattr(self._obj, name)
        if inspect.ismethod(ret):
            # TODO: a proper implementation?
            # How can we make the changes in method be notified?
            return bind(self, getattr(type(self._obj), name))
        else:
            return ret

    def __setattr__(self, name, value):
        if name == "_obj" or name == "_handlerList" or name == "_parent":
            return super().__setattr__(name, value)

        if not nonObservableAttribute(self, name):
            target = getattr(self._obj, name)
            try:
                target.observableAssign(value)
            except AttributeError:
                setattr(self._obj, name, value)
            self.notify()
        else:
            setattr(self._obj, name, value)

    def observableAssign(self, obj):
        for name in observableAttributes(self._obj):
            old = getattr(obj, name)
            setattr(self._obj, name, makeObservable(old, parent=self))

        self.notify()

    def __eq__(self, obj):
        assignerAttributes = observableAttributes(self)
        assigneeAttributes = observableAttributes(obj)
        if assigneeAttributes != assigneeAttributes:
            return False
        for k in assignerAttributes:
            if getattr(self, k) != getattr(self._obj, k):
                return False
        return True
