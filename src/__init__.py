from .utils import openChangelog
from .utils import uuid  # duplicate UUID checked here

from .utils.JSEval import execJSFile
from .utils.configrw import getConfig
from .utils.JSCallable import JSCallable

from .utils import ankiLocalStorage

from aqt import mw
from aqt.main import AnkiQt
from aqt.reviewer import Reviewer
from aqt.theme import ThemeManager
from anki.hooks import wrap

import time


@JSCallable
def getCurrentRemainingCardCount():
    counts = list(mw.col.sched.counts(mw.reviewer.card))
    nu, lrn, rev = counts[:3]
    return nu, lrn, rev


##########


def _afterMoveToState(self, state, *args):
    if state == "review":
        renderBar()


AnkiQt.moveToState = wrap(AnkiQt.moveToState, _afterMoveToState, "after")


##########


def afterAnswerCard(self, ease):
    renderBar()


Reviewer._answerCard = wrap(Reviewer._answerCard, afterAnswerCard, "after")


def renderBar():
    def cb():
        mw.web.eval(f"""window.__rtt_run()""")

    execJSFile(mw.web, "js/main.min.js", cb, once=True)


# Theme manager


def new_body_class(self, _old):
    showAtBottom = getConfig("showAtBottom", False)
    if showAtBottom:
        rtClass = "remaining-time-bar-bottom"
    else:
        rtClass = "remaining-time-bar-top"

    classes = _old(self)
    return classes + " " + rtClass


ThemeManager.body_class = wrap(ThemeManager.body_class, new_body_class, "around")
