from ..utils.JSCallable import JSCallable
from aqt import mw


@JSCallable
def getCurrentRemainingCardCount():
    reviewer = mw.reviewer

    # Code from aqt.reviewer.Reviewer._remaining()
    if reviewer.hadCardQueue:
        # if it's come from the undo queue, don't count it separately
        counts = list(mw.col.sched.counts())
    else:
        counts = list(mw.col.sched.counts(reviewer.card))

    nu, lrn, rev = counts
    return nu, lrn, rev
