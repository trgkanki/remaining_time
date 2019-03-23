from aqt import mw
from anki.hooks import addHook
from base64 import b64encode
from .ExponentialSmoother import ExponentialSmoother


def getRemainingReviews():
    counts = list(mw.col.sched.counts())
    nu, lrn, rev = counts[:3]
    return rev + 2 * nu + lrn


estimator = ExponentialSmoother()
# Should be updated on `onShowQuestion`. Set to 1, not 0 to avoid division by 0
maxRemainingReviews = 1


def onStateChange(state, oldState, *args):
    if state == 'review':
        global maxRemainingReviews
        estimator.reset()
        maxRemainingReviews = 1


addHook('beforeStateChange', onStateChange)


def t2s(time):
    return "%.1fm" % (time / 60.0)

    if time < 60:
        return "%ds" % time
    elif time < 3600:
        return "%dm" % (time / 60)
    elif time < 86400:
        return "%.1fh" % (time / 3600.0)
    else:
        return " > day"


## Drawing settings
clampMinTime = 10
clampMaxTime = 120
minAlpha = 0.2

## code

def onShowQuestion():

    global maxRemainingReviews
    currentRemainingReviews = getRemainingReviews()
    maxRemainingReviews = max(maxRemainingReviews, currentRemainingReviews)
    progress = 1 - currentRemainingReviews / maxRemainingReviews
    estimator.update(progress)

    elapsedTime = estimator.elapsedTime
    remainingTime = (1 - progress) / estimator.getSlope()

    message = "Elapsed %s,  Remaining %s, Total %s" % (
        t2s(elapsedTime),
        t2s(remainingTime),
        t2s(elapsedTime + remainingTime)
    )

    pathSVGs = []
    timeSum = sum(log.elapsedTime for log in estimator.logs)
    rectX = 0
    for log in estimator.logs:

        rectW = log.elapsedTime / timeSum * progress
        if log.elapsedTime < clampMinTime:
            rectAlpha = 1
        elif log.elapsedTime > 120:
            rectAlpha = minAlpha
        else:
            rectAlpha = (log.elapsedTime - clampMinTime) / (clampMaxTime - clampMinTime) * minAlpha + (1 - minAlpha)

        pathSVGs.append(
            f'<path d="M{rectX} 0 h{rectW} V1 h-{rectW} Z" fill="rgba(114, 166, 249, {rectAlpha})" shape-rendering="crispEdges" />'
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


addHook('showQuestion', onShowQuestion)
