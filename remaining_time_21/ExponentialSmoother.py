import time

cutoffDt = 300
historyDecay = 1 / 1.005
historyLength = 100

class LogEntry:
    def __init__(self, epoch, dt, dy, ease, cid):
        self.epoch = epoch
        self.dt = dt
        self.dy = dy
        self.ease = ease
        self.cid = cid

class ExponentialSmoother:
    def __init__(self):
        self.reset()

    def reset(self):
        self.logs = []
        self.elapsedTime = 0
        self._startTime = time.time()

    def update(self, epoch, dy, ease, cid):
        if self.logs:
            dt = epoch - self.logs[-1].epoch
        else:
            dt = epoch - self._startTime
        self.logs.append(LogEntry(epoch, dt, dy, ease, cid))
        self.elapsedTime = time.time() - self._startTime

    def undoUpdate(self):
        self.logs.pop()
        self.elapsedTime = time.time() - self._startTime

    def updateLastEntryEase(self, ease):
        if not self.logs:
            return
        self.lastAnswerEase = ease

    def getSlope(self):
        if len(self.logs) < 2:
            return 1e-6

        totTime = 0
        totY = 0

        for i, log in enumerate(self.logs[-historyLength:]):
            r = (1 / historyDecay) ** i
            if log.dt <= cutoffDt:
                totTime += r * log.dt
                totY += r * log.dy
            else:
                # If user paused more than `cutoffDt` time, don't use dy
                # If user reviewed a lot of card on the other device
                # during the pause, dy may be massive. We don't want to
                # account that. Also, if user just procrastinated a lot
                # and left the review session, dy/dt should be close to
                # zero, and it's safe to set dy to 0.
                totTime += r * cutoffDt

        if totTime < 1:
            return 1
        return max(totY / totTime, 1e-6)
