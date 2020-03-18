from aqt import mw
from aqt.main import AnkiQt
from anki.hooks import addHook, wrap
from aqt.reviewer import Reviewer
from base64 import b64encode
from .ExponentialSmoother import ExponentialSmoother

import time

def getRemainingReviews():
    counts = list(mw.col.sched.counts(mw.reviewer.card))
    nu, lrn, rev = counts[:3]
    return rev + nu + lrn

_cardReviewStart = 0
estimator = ExponentialSmoother()

##########

def _afterMoveToState(self, state, *args):
    if state == 'deckBrowser':
        estimator.reset()
    elif state == 'review':
        renderBarAndResetCardTimer()

AnkiQt.moveToState = wrap(AnkiQt.moveToState, _afterMoveToState, 'after')


##########

def _newAnswerCard(self, ease, _old=None):
    dt = min(time.time() - _cardReviewStart, 120)
    y0 = getRemainingReviews()
    ret = _old(self, ease)
    y1 = getRemainingReviews()
    dy = y0 - y1
    estimator.update(dt, dy, ease)
    renderBarAndResetCardTimer()
    return ret

Reviewer._answerCard = wrap(Reviewer._answerCard, _newAnswerCard, 'around')


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

    elapsedTime = estimator.elapsedTime
    remainingTime = currentRemainingReviews / estimator.getSlope()
    progress = elapsedTime / (elapsedTime + remainingTime)

    message = "Elapsed %s,  Remaining %s, Total %s" % (
        t2s(elapsedTime),
        t2s(remainingTime),
        t2s(elapsedTime + remainingTime)
    )

    pathSVGs = []
    timeSum = sum(log[0] for log in estimator.logs)
    rectX = 0
    for dt, dy, ease in estimator.logs[1:]:
        rectW = dt / timeSum * progress
        if dt < clampMinTime:
            rectAlpha = maxAlpha
        elif dt > clampMaxTime:
            rectAlpha = minAlpha
        else:
            rectAlpha = (dt - clampMinTime) / (clampMaxTime - clampMinTime) * minAlpha + (maxAlpha - minAlpha)
        rectColor = str(againColor if ease == 1 else goodColor)[1:-1]

        pathSVGs.append(
            f'<path d="M{rectX} 0 h{rectW} V1 h-{rectW} Z" fill="rgba({rectColor}, {rectAlpha})" shape-rendering="crispEdges" />'
        )
        rectX += rectW

    svgContent = f'''
    <svg width="1" height="1" xmlns="http://www.w3.org/2000/svg">
        {''.join(pathSVGs)}
    </svg>
    '''

    b64svg = b64encode(svgContent.encode('utf-8')).decode('ascii')

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
        body.card {{
            padding-top: 1rem;
        }}

        #remainingTimeBar {{
            position: fixed;
            font-family: sans-serif;
            z-index: 100;

            left: 0;
            right: 0;
            top: 0;
            height: 1rem;
            line-height: 1rem;
            font-size: .8rem;

            border-bottom: 1px solid #aaa;

            background: url('data:image/svg+xml;base64,{b64svg}');
            background-repeat: no-repeat;
            background-size: cover;

            text-align: center;
        }}
        `)
    }})()
    ''')
