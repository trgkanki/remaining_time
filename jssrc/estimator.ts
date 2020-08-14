/**
 * Port of ExponentialSmoother.py
 */

import ankiLocalStorage from './utils/ankiLocalStorage'
import MsgPack from 'msgpack-lite'
import base64js from 'base64-js'

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
  _startTime = 0
  _lastAnswerType = 0
  _lastLogEpoch = 0
  version = ESTIMATOR_SCHEMA_VERSION

  constructor () {
    this.reset()
  }

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
    ankiLocalStorage.setItem(
      getLocalStorageKey(),
      base64js.fromByteArray(MsgPack.encode(this))
    )
  }

  static async instance (): Promise<Estimator> {
    if (cache) return cache

    const content = await ankiLocalStorage.getItem(getLocalStorageKey())
    if (!content) cache = new Estimator()
    else {
      const obj = MsgPack.decode(base64js.toByteArray(content))
      if (obj.version === ESTIMATOR_SCHEMA_VERSION) {
        cache = Object.create(Estimator.prototype, Object.getOwnPropertyDescriptors(obj))
      } else {
        cache = new Estimator()
      }
    }
    return cache
  }
}
