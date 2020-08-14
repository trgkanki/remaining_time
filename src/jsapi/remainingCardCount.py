from ..utils.JSCallable import JSCallable
from aqt import mw


@JSCallable
def getCurrentRemainingCardCount():
    counts = list(mw.col.sched.counts(mw.reviewer.card))
    nu, lrn, rev = counts[:3]
    return nu, lrn, rev
