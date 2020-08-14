from aqt import mw
from aqt.main import AnkiQt
from aqt.reviewer import Reviewer
from aqt.theme import ThemeManager
from anki.collection import _Collection
from anki.hooks import addHook, wrap
from aqt.utils import askUser
from base64 import b64encode
from .ExponentialSmoother import ExponentialSmoother
import time
import datetime

from .utils.JSEval import evalJS, execJSFile
from .utils.configrw import getConfig

config = mw.addonManager.getConfig(__name__)
if config is None:
    config = {}

##########


def getRemainingReviews():
    counts = list(mw.col.sched.counts(mw.reviewer.card))
    nu, lrn, rev = counts[:3]
    return rev + 2 * nu + lrn


_cardReviewStart = 0
estimatorMap = {}


def getCurrentDeckEstimator():
    did = mw.col.decks.current()["id"]
    try:
        return estimatorMap[did]
    except KeyError:
        estimator = ExponentialSmoother()
        estimatorMap[did] = estimator
        return estimator


##########


def _afterMoveToState(self, state, *args):
    if state == "review":
        renderBar()


AnkiQt.moveToState = wrap(AnkiQt.moveToState, _afterMoveToState, "after")


##########


def _newAnswerCard(self, ease, _old=None):
    if self.mw.state != "review":
        _old(self, ease)
        return
    if self.state != "answer":
        _old(self, ease)
        return
    if self.mw.col.sched.answerButtons(self.card) < ease:
        _old(self, ease)
        return

    y0 = getRemainingReviews()
    reviewedCardID = self.card.id
    ret = _old(self, ease)
    y1 = getRemainingReviews()
    dy = y0 - y1
    estimator = getCurrentDeckEstimator()
    estimator.update(time.time(), dy, ease, reviewedCardID)
    renderBar()
    return ret


Reviewer._answerCard = wrap(Reviewer._answerCard, _newAnswerCard, "around")


def _newLinkHandler(self, url, _old=None):
    if url == "_rt_pgreset":
        if askUser("Really reset progres bar for this deck?"):
            getCurrentDeckEstimator().reset()
            renderBar()
    else:
        _old(self, url)


Reviewer._linkHandler = wrap(Reviewer._linkHandler, _newLinkHandler, "around")


def _newUndoReview(self, _old=None):
    cid = _old(self)
    estimator = getCurrentDeckEstimator()
    if estimator.logs:
        if estimator.logs[-1].cid == cid:
            estimator.undoUpdate()
            renderBar()

    return cid


_Collection._undoReview = wrap(_Collection._undoReview, _newUndoReview, "around")

##########

## Drawing settings
clampMinTime = 10
clampMaxTime = 120
minAlpha = 0.3
maxAlpha = 0.7

againColor = (239, 103, 79)  # Again
goodColor = (114, 166, 249)  # Good/Easy


def t2s(time):
    if time < 60:
        return "%ds" % time
    elif time < 86400:
        return "%dm" % (time / 60)
    else:
        return " > day"


def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()


def renderBar():
    global _cardReviewStart

    currentRemainingReviews = getRemainingReviews()
    if currentRemainingReviews == 0:
        return

    _cardReviewStart = time.time()

    estimator = getCurrentDeckEstimator()
    elapsedTime = estimator.elapsedTime
    remainingTime = currentRemainingReviews / estimator.getSlope()
    progress = elapsedTime / (elapsedTime + remainingTime)

    ETA = addSecs(datetime.datetime.now().time(), remainingTime)

    message = "Elapsed %s,  Remaining %s, ETA %s" % (
        t2s(elapsedTime),
        t2s(remainingTime),
        ETA.strftime("%H:%M") if remainingTime < 86400 else ">day",
    )

    pathSVGs = []
    timeSum = sum(log.dt for log in estimator.logs)
    rectX = 0

    for log in estimator.logs:
        rectW = log.dt / timeSum * progress
        if log.dt < clampMinTime:
            rectAlpha = maxAlpha
        elif log.dt > clampMaxTime:
            rectAlpha = minAlpha / 2
        else:
            rectAlpha = maxAlpha - (log.dt - clampMinTime) / (
                clampMaxTime - clampMinTime
            ) * (maxAlpha - minAlpha)
        rectColor = str(againColor if log.ease == 1 else goodColor)[1:-1]

        pathSVGs.append(
            f'<path d="M{rectX} 0 h{rectW} V1 h-{rectW} Z" fill="rgba({rectColor}, {rectAlpha})" shape-rendering="crispEdges" />'
        )
        rectX += rectW

    svgContent = f"""
    <svg width="1" height="1" xmlns="http://www.w3.org/2000/svg">
        {''.join(pathSVGs)}
    </svg>
    """

    b64svg = b64encode(svgContent.encode("utf-8")).decode("ascii")

    def cb():
        mw.web.eval(
            f"""
        window.__remainingTime.updateProgressBar(
            "{b64svg}",
            "{message}"
        )"""
        )

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


ThemeManager.body_class = wrap(ThemeManager.body_class, new_body_class, "asround")
