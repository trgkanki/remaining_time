from ..utils.JSCallable import JSCallable
from aqt import mw
from anki.utils import pointVersion


@JSCallable
def getCurrentRemainingCardCount():
    reviewer = mw.reviewer

    # Pre 23.10 code
    if pointVersion() < 230000:
        # Code from aqt.reviewer.Reviewer._remaining()
        if reviewer.hadCardQueue:
            # if it's come from the undo queue, don't count it separately
            counts = list(mw.col.sched.counts())
        else:
            counts = list(mw.col.sched.counts(reviewer.card))

    # 23.10 code
    else:
        if (v3 := reviewer._v3) is not None:
            _, counts = v3.counts()
        else:
            counts = (0, 0, 0)

    nu, lrn, rev = counts
    return nu, lrn, rev
