import time
import collections

class LogEntry:
    def __init__(self, elapsedTime, newPercent, answerEase):
        self.elapsedTime = elapsedTime
        self.newPercent = newPercent
        self.answerEase = answerEase

class ExponentialSmoother:
    def __init__(self):
        self.reset()

    def reset(self):
        self.logs = []
        self.lastTime = time.time()
        self.startTime = time.time()
        self.elapsedTime = 0
        self.lastAnswerEase = None

    def update(self, newPercent):
        timeSpent = time.time() - self.lastTime
        self.logs.append(LogEntry(timeSpent, newPercent, self.lastAnswerEase))
        self.lastTime = time.time()
        self.elapsedTime = self.lastTime - self.startTime

    def updateLastEntryEase(self, ease):
        if not self.logs:
            return
        self.lastAnswerEase = ease

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
