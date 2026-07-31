from ..utils.JSCallable import JSCallable
from aqt import mw


@JSCallable
def getCurrentDeckName():
    card = mw.reviewer.card
    if not card:
        return None
    return mw.col.decks.name(card.current_deck_id())
