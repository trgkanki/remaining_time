from ..utils.JSCallable import JSCallable

storage = {}


@JSCallable
def localStorageSetItem(key, data):
    storage[key] = data


@JSCallable
def localStorageGetItem(key):
    return storage.get(key, None)


@JSCallable
def localStorageHasItem(key):
    return key in storage
