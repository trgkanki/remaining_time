from ..utils.JSCallable import JSCallable
from aqt import mw

# All keys written through ankiPersistentStorage.ts's setItem/getItem share one
# collection-config entry, namespaced by their own key. Collection config
# syncs via AnkiWeb and survives restarts - keep values here small, since the
# whole dict round-trips on every read/write.
_CONFIG_KEY = "remainingTimeStorage"


def _readAll():
    return mw.col.get_config(_CONFIG_KEY, {})


@JSCallable
def localStorageSetItem(key, data):
    storage = _readAll()
    storage[key] = data
    mw.col.set_config(_CONFIG_KEY, storage)


@JSCallable
def localStorageGetItem(key):
    return _readAll().get(key, None)


@JSCallable
def localStorageHasItem(key):
    return key in _readAll()
