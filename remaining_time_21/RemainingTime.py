from aqt import mw
from aqt.main import AnkiQt
from aqt.reviewer import Reviewer
from anki.collection import _Collection
from anki.hooks import addHook, wrap
from base64 import b64encode
from .ExponentialSmoother import ExponentialSmoother
import time

config = mw.addonManager.getConfig(__name__)
if config is None:
    config = {}

##########

def getRemainingReviews():
    counts = list(mw.col.sched.counts(mw.reviewer.card))
    nu, lrn, rev = counts[:3]
    return rev + nu + lrn

_cardReviewStart = 0
estimatorMap = {}

def getCurrentDeckEstimator():
    did = mw.col.decks.current()['id']
    try:
        return estimatorMap[did]
    except KeyError:
        estimator = ExponentialSmoother()
        estimatorMap[did] = estimator
        return estimator


##########


def _afterMoveToState(self, state, *args):
    if state == 'review':
        renderBarAndResetCardTimer()

AnkiQt.moveToState = wrap(AnkiQt.moveToState, _afterMoveToState, 'after')


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
    renderBarAndResetCardTimer()
    return ret

Reviewer._answerCard = wrap(Reviewer._answerCard, _newAnswerCard, 'around')

def _newUndoReview(self, _old=None):
    cid = _old(self)
    estimator = getCurrentDeckEstimator()
    if estimator.logs:
        if estimator.logs[-1].cid == cid:
            estimator.undoUpdate()
            renderBarAndResetCardTimer()

    return cid

_Collection._undoReview = wrap(_Collection._undoReview, _newUndoReview, 'around')

##########

## Drawing settings
clampMinTime = 10
clampMaxTime = 120
minAlpha = 0.2
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

def renderBarAndResetCardTimer():
    global _cardReviewStart

    currentRemainingReviews = getRemainingReviews()
    if currentRemainingReviews == 0:
        return

    _cardReviewStart = time.time()

    estimator = getCurrentDeckEstimator()
    elapsedTime = estimator.elapsedTime
    remainingTime = currentRemainingReviews / estimator.getSlope()
    progress = elapsedTime / (elapsedTime + remainingTime)

    message = "Elapsed %s,  Remaining %s, Total %s" % (
        t2s(elapsedTime),
        t2s(remainingTime),
        t2s(elapsedTime + remainingTime)
    )

    pathSVGs = []
    timeSum = sum(log.dt for log in estimator.logs)
    rectX = 0
    for log in estimator.logs:
        rectW = log.dt / timeSum * progress
        if log.dt < clampMinTime:
            rectAlpha = maxAlpha
        elif log.dt > clampMaxTime:
            rectAlpha = minAlpha
        else:
            rectAlpha = maxAlpha - (log.dt - clampMinTime) / (clampMaxTime - clampMinTime) * (maxAlpha - minAlpha)
        rectColor = str(againColor if log.ease == 1 else goodColor)[1:-1]

        pathSVGs.append(
            f'<path d="M{rectX} 0 h{rectW} V1 h-{rectW} Z" fill="rgba({rectColor}, {rectAlpha})" shape-rendering="crispEdges" />'
        )
        rectX += rectW

    svgContent = f'''
    <svg width="1" height="1" xmlns="http://www.w3.org/2000/svg">
        <path d="M0 0 h1 V1 h-1 Z" fill="white" />
        {''.join(pathSVGs)}
    </svg>
    '''

    b64svg = b64encode(svgContent.encode('utf-8')).decode('ascii')

    showAtBottom = config.get('showAtBottom', False)
    barPositioningCSS = (
        '''
        body.card {
            padding-top: 1rem;
        }

        #remainingTimeBar {
            position: fixed;

            left: 0;
            right: 0;
            top: 0;

            border-bottom: 1px solid #aaa;
        }
        ''' if not showAtBottom else
        '''
        body.card {
            padding-bottom: 1rem;
        }

        #remainingTimeBar {
            position: fixed;

            left: 0;
            right: 0;
            bottom: 0;

            border-top: 1px solid #aaa;
        }
        '''
    )

    mw.web.eval(f'''
    (function () {{
        let styleEl = $('#remainingTimeStylesheet')
        if (styleEl.length === 0) {{
            styleEl = $('<style></style>')
            styleEl.attr('id', 'remainingTimeStylesheet')
            $('head').append(styleEl)
        }}

        let barEl = $('#remainingTimeBar')
        if (barEl.length === 0) {{
            barEl = $('<div></div>')
            barEl.attr('id', 'remainingTimeBar')
            $('body').append(barEl)
        }}

        barEl.text("{message}")

        styleEl.html(`
        {barPositioningCSS}

        body.card {{
            padding-top: 1rem;
        }}

        #remainingTimeBar {{
            font-family: sans-serif;
            z-index: 100;

            height: 1rem;
            line-height: 1rem;
            font-size: .8rem;
            color: black !important;

            background: url('data:image/svg+xml;base64,{b64svg}');
            background-repeat: no-repeat;
            background-size: cover;

            text-align: center;
        }}
        `)
    }})()
    ''')
