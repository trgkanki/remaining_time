import time
import collections

_LogEntry = collections.namedtuple('ReviewLogEntry', 'elapsedTime newPercent')

class ExponentialSmoother:
    def __init__(self):
        self.reset()

    def reset(self):
        self.logs = []
        self.lastTime = time.time()
        self.startTime = time.time()
        self.elapsedTime = 0

    def update(self, newPercent):
        timeSpent = time.time() - self.lastTime
        self.logs.append(_LogEntry(timeSpent, newPercent))
        self.lastTime = time.time()
        self.elapsedTime = self.lastTime - self.startTime

    def getSlope(self):
        if len(self.logs) < 2:
            return 1e-6
        totTime = 0
        percentChange = 0
        for i in range(
            max(len(self.logs) - 100, 0),
            len(self.logs)
        ):
            r = 1.005 ** i
            totTime += r * (self.logs[i - 1].elapsedTime)
            percentChange += r * (self.logs[i].newPercent - self.logs[i - 1].newPercent)
        if totTime < 1:
            return 1
        return max(percentChange / totTime, 1e-6)
