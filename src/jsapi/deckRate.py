from ..utils.JSCallable import JSCallable
from aqt import mw

# Small, bounded blob: one rate number per deck. Collection config syncs via
# AnkiWeb and survives restarts, unlike ankiLocalStorage.py's in-memory dict -
# but its docstring warns to keep it to "a few kilobytes", so this is kept as
# its own store rather than folded into ankiLocalStorage.py (which also holds
# the much larger transient DOM-snapshot cache from rtContainer.ts).
_CONFIG_KEY = "remainingTimeDeckRates"


@JSCallable
def getCurrentDeckName():
    card = mw.reviewer.card
    if not card:
        return None
    return mw.col.decks.name(card.current_deck_id())


@JSCallable
def getDeckRateConfig():
    return mw.col.get_config(_CONFIG_KEY, {})


@JSCallable
def setDeckRateConfig(data):
    mw.col.set_config(_CONFIG_KEY, data)
