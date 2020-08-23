from .makeObservable import makeObservable, unobserved
from .ObservableBase import isObservable


def observable(obj):
    return makeObservable(obj, parent=None)
