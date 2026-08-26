import json
import os

from ..utils.JSCallable import JSCallable
from ..utils.resource import getResourcePath

_STORAGE_PATH = getResourcePath("persistent_storage.json")
_TEMP_STORAGE_PATH = _STORAGE_PATH + ".tmp"


def _readAll():
    try:
        with open(_STORAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _writeAll(storage):
    with open(_TEMP_STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(storage, f, ensure_ascii=False, indent=2)
    os.replace(_TEMP_STORAGE_PATH, _STORAGE_PATH)


@JSCallable
def localStorageSetItem(key, data):
    storage = _readAll()
    storage[key] = data
    _writeAll(storage)


@JSCallable
def localStorageGetItem(key):
    return _readAll().get(key, None)


@JSCallable
def localStorageHasItem(key):
    return key in _readAll()


@JSCallable
def localStoragePurgeItem(key):
    storage = _readAll()
    if key in storage:
        del storage[key]
        _writeAll(storage)
