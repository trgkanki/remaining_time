/**
 * Port of ExponentialSmoother.py
 */

import ankiLocalStorage from './utils/ankiLocalStorage'

const cutoffDt = 300
const historyDecay = 1 / 1.005
const historyLength = 100

export interface LogEntry {
  epoch: number;
  dt: number;
  dy: number;
  logType: string;
}

const ESTIMATOR_SCHEMA_VERSION = 0

// Persistence
let cache: Estimator
function getLocalStorageKey () {
  return `__rt__estimator__${ESTIMATOR_SCHEMA_VERSION}__`
}

// Implementation
export class Estimator {
  logs: LogEntry[] = []
  elapsedTime = 0
  _startTime = Date.now() / 1000
  _lastAnswerType = 0
  _lastLogEpoch = 0

  reset () {
    this.logs = []
    this.elapsedTime = 0
    this._startTime = Date.now() / 1000
    this.save()
  }

  update (epoch: number, dy: number, logType: string) {
    const logLength = this.logs.length
    const dt =
      logLength ? epoch - this._lastLogEpoch
        : epoch - this._startTime
    this.logs.push({ epoch, dt, dy, logType })
    this.elapsedTime = Date.now() / 1000 - this._startTime
    this._lastLogEpoch = epoch
    this.save()
  }

  skipUpdate (epoch: number) {
    this._lastLogEpoch = epoch
  }

  undoUpdate () {
    this.logs.pop()
    this.elapsedTime = Date.now() / 1000 - this._startTime
  }

  updateLastEntryType (logType: number) {
    if (!this.logs.length) return
    this._lastAnswerType = logType
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

  save () {
    // serialize
    const s = []
    s.push(ESTIMATOR_SCHEMA_VERSION)
    s.push(this.elapsedTime, this._startTime, this._lastAnswerType, this._lastLogEpoch)
    for (const log of this.logs) {
      s.push(log.epoch, log.dt, log.dy, log.logType)
    }

    ankiLocalStorage.setItem(
      getLocalStorageKey(),
      JSON.stringify(s, function (_key, val) {
        return val.toFixed ? Number(val.toFixed(1)) : val
      })
    )
  }

  static async instance (): Promise<Estimator> {
    if (cache) return cache

    const content = await ankiLocalStorage.getItem(getLocalStorageKey())
    if (!content) cache = new Estimator()
    else {
      try {
        const s = JSON.parse(content)
        let cursor = 0
        if (s[cursor++] !== ESTIMATOR_SCHEMA_VERSION) {
          throw new Error('Old schema')
        }
        const obj = new Estimator()
        obj.elapsedTime = s[cursor++]
        obj._startTime = s[cursor++]
        obj._lastAnswerType = s[cursor++]
        obj._lastLogEpoch = s[cursor++]
        while (cursor < s.length) {
          obj.logs.push({
            epoch: s[cursor + 0],
            dt: s[cursor + 1],
            dy: s[cursor + 2],
            logType: s[cursor + 3]
          })
          cursor += 4
        }
        if (!cursor === s.length) {
          console.log(s, cursor, obj)
          throw new Error('Length mismatch - RTT')
        }
        cache = obj
      } catch {
        cache = new Estimator()
      }
    }
    return cache
  }
}
