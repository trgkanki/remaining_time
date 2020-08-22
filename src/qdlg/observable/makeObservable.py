from .ObservableBase import ObservableBase, isObservable


_immutableTypes = {int, str, bytes, bool, float}
_unsupportedTypes = {bytearray, dict}
_iterableType = {list, tuple}


def isImmutable(obj):
    return type(obj) in _immutableTypes or obj is None or callable(obj)


def makeObservable(obj, *, parent):
    from .ObservableObject import ObservableObject
    from .ObservableList import ObservableList

    if type(obj) in _unsupportedTypes:
        raise RuntimeError(
            "Object %s of type %s is not yet be made observable." % (obj, type(obj))
        )

    if isinstance(obj, ObservableBase):
        assert obj._parent is parent
        return obj

    if isImmutable(obj):
        return obj

    if type(obj) in _iterableType:
        return ObservableList(obj, parent=parent)

    return ObservableObject(obj, parent=parent)
