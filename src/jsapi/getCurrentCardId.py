from ..utils.JSCallable import JSCallable
from aqt import mw


@JSCallable
def getCurrentCardId():
    reviewer = mw.reviewer
    if reviewer.card:
        return reviewer.card.id
    return 0
