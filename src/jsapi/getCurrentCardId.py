from ..utils.JSCallable import JSCallable
from aqt import mw


@JSCallable
def getCurrentCardId():
    reviewer = mw.reviewer
    return reviewer.card.id
