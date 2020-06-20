/**
 * Port of ExponentialSmoother.py
 */

const cutoffDt = 300
const historyDecay = 1 / 1.005
const historyLength = 100

export interface LogEntry {
  epoch: number;
  dt: number;
  dy: number;
  ease: number;
}

export class Estimator {
  logs: LogEntry[] = []
  elapsedTime = 0
  _startTime = 0
  _lastAnswerEase = 0

  constructor () {
    this.reset()
  }

  reset () {
    this.logs = []
    this.elapsedTime = 0
    this._startTime = Date.now() / 1000
  }

  update (epoch: number, dy: number, ease: number) {
    const logLength = this.logs.length
    const dt =
      logLength ? epoch - this.logs[logLength - 1].epoch
        : epoch - this._startTime
    this.logs.push({ epoch, dt, dy, ease })
    this.elapsedTime = Date.now() / 1000 - this._startTime
  }

  undoUpdate () {
    this.logs.pop()
    this.elapsedTime = Date.now() / 1000 - this._startTime
  }

  updateLastEntryEase (ease: number) {
    if (!this.logs.length) return
    this._lastAnswerEase = ease
  }

  getSlope () {
    const logLength = this.logs.length
    if (logLength < 2) return 1e-6

    let totTime = 0
    let totY = 0
    for (let i = Math.max(0, logLength - historyLength); i < logLength; i++) {
      const r = Math.pow(1 / historyDecay, i)
      const log = this.logs[i]
      if (log.dt <= cutoffDt) {
        totTime += r * log.dt
        totY += r * log.dy
      } else {
        // If user paused more than `cutoffDt` time, don't use dy
        // If user reviewed a lot of card on the other device
        // during the pause, dy may be massive. We don't want to
        // account that. Also, if user just procrastinated a lot
        // and left the review session, dy/dt should be close to
        // zero, and it's safe to set dy to 0.
        totTime += r * cutoffDt
      }
    }

    if (totTime < 1) return 1
    return Math.max(totY / totTime, 1e-6)
  }
}
