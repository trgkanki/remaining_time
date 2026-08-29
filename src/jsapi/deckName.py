from ..utils.JSCallable import JSCallable
from aqt import mw


@JSCallable
def getCurrentDeckName():
    return mw.col.decks.current()["name"]
