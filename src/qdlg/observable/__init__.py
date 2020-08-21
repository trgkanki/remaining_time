import inspect
import types

_immutableTypes = {int, str, bool, float}
_iterableType = {list, tuple}


def isImmutable(obj):
    return type(obj) in _immutableTypes or obj is None or callable(obj)


def isObservable(obj):
    return hasattr(obj, "_observable")


def observable(obj):
    from .list import ObservableList
    from .object import ObservableObject

    if isImmutable(obj) or isObservable(obj):
        return obj

    if type(obj) in _iterableType:
        return ObservableList(obj)

    return ObservableObject(obj)
