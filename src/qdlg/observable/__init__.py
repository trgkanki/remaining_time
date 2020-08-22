from .makeObservable import makeObservable
from .ObservableBase import isObservable


def observable(obj):
    return makeObservable(obj, parent=None)
