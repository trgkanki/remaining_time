import time

class ExponentialSmoother:
    def __init__(self):
        self.reset()

    def reset(self):
        self.logs = []
        self.elapsedTime = 0
        self._startTime = time.time()

    def update(self, dt, dy, ease):
        self.logs.append([dt, dy, ease])
        self.logs = self.logs[-100:]
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
        for i, (dt, dy, ease) in enumerate(self.logs):
            r = 1.005 ** i
            totTime += r * dt
            totY += r * dy

        if totTime < 1:
            return 1
        return max(totY / totTime, 1e-6)
