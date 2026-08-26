/**
 * Port of ExponentialSmoother.py
 */

import ankiPersistentStorage from './utils/ankiPersistentStorage'
import { pakob64Deflate, pakob64Inflate } from './utils/pakob64'
import { now, RemainingCardCounts } from './utils'
import { InstLogType } from './reviewLogger/types'
import { getAddonConfig } from './utils/addonConfig'
import { getCurrentDeckName, getDeckRate, RateState } from './utils/deckRate'
import { isAnkiDroid } from './utils/apiAnkiDroid'
import { debugLog } from './utils/debugLog'

const historyDecay = 1 / 1.005
const minimumRate = 1e-6

export function getRemainingCardLoad ({ nu, lrn, rev }: RemainingCardCounts) {
  return 2 * nu + lrn + rev
}

export interface LogEntry {
  epoch: number;
  dt: number;
  dy: number;
  logType: InstLogType;
  reviewHash: number | null; // May be null to save spaces on ankidroid
}

const ESTIMATOR_SCHEMA_VERSION = 6

// How many of the most recent log entries keep their reviewHash on
// serialization. Only mobileReviewLogger ever reads a persisted reviewHash
// back (its edit/undo checks look at the newest 1-2 entries; 10 gives
// headroom for a run of several undos in one poll) - desktopReviewLogger
// dedupes via its own seq counter instead, so on desktop there's no reason
// to pay to persist a reviewHash (high-entropy CRC32, doesn't compress) for
// any entry at all.
const persistedReviewHashTailLength = isAnkiDroid() ? 10 : 0

const logTypeCodes: InstLogType[] = ['new', 'good', 'again', 'rev-good', 'rev-again', 'unknown']

// epoch and reviewHash are dropped from the serialized form (epoch is
// reconstructed by accumulating dt from startTime; reviewHash is only kept
// for the newest `persistedReviewHashTailLength` entries) to keep a long
// session's payload small - see the module comment on why this data lives in
// a size-limited cookie on AnkiDroid.
function serializeLogs (logs: LogEntry[]): unknown[] {
  const s: unknown[] = [logs.length]
  for (const log of logs) {
    s.push(log.dt, log.dy, logTypeCodes.indexOf(log.logType))
  }
  const tailStart = Math.max(0, logs.length - persistedReviewHashTailLength)
  s.push(logs.length - tailStart)
  for (let i = tailStart; i < logs.length; i++) {
    s.push(logs[i].reviewHash)
  }
  return s
}

function deserializeLogs (s: unknown[], cursor: number, startTime: number): { logs: LogEntry[]; cursor: number } {
  const count = s[cursor++] as number
  const logs: LogEntry[] = []
  let epoch = startTime
  for (let i = 0; i < count; i++) {
    const dt = s[cursor++] as number
    const dy = s[cursor++] as number
    const logType = logTypeCodes[s[cursor++] as number]
    epoch += dt
    // Patched in below for the persisted tail; older entries never have
    // their reviewHash read.
    logs.push({ epoch, dt, dy, logType, reviewHash: null })
  }

  const tailCount = s[cursor++] as number
  const tailStart = logs.length - tailCount
  for (let i = tailStart; i < logs.length; i++) {
    logs[i].reviewHash = s[cursor++] as number
  }

  return { logs, cursor }
}

// Persistence
export const kRtEstimatorSchema = '__rt__estimator__schema__'

// Implementation

interface EstimatorInitializer {
  reviewTimeCutoff: number;
  rate: RateState;
}

function emptyRateState (): RateState {
  return { weightedTime: 0, weightedWork: 0 }
}

export class Estimator {
  logs: LogEntry[] = []
  // A single exponential smoother over weighted work completed per second.
  // Persisting the raw accumulators lets the same EMA continue across
  // sittings without introducing a second blending stage.
  rate: RateState

  private startTime = now()
  private reviewTimeCutoff: number
  // eslint-disable-next-line no-use-before-define
  private static cache: Estimator | null = null

  constructor (args: EstimatorInitializer) {
    this.reviewTimeCutoff = args.reviewTimeCutoff
    this.rate = args.rate
  }

  get elapsedTime () {
    return now() - this.startTime
  }

  /** Epoch of the most recent review, or the sitting's start if none yet. */
  get lastActivityEpoch () {
    return this.logs.length ? this.logs[this.logs.length - 1].epoch : this.startTime
  }

  reset () {
    this.logs = []
    this.startTime = now()
    // this.rate is deliberately left untouched - it's the deck's long-run
    // learned pace, not sitting-scoped state.
  }

  resetRate () {
    this.rate = emptyRateState()
  }

  private applyRateSample (dt: number, dy: number) {
    const state = this.rate
    const withinCutoff = dt <= this.reviewTimeCutoff
    const cappedDt = withinCutoff ? dt : this.reviewTimeCutoff
    const oldWeightedTime = state.weightedTime
    const oldWeightedWork = state.weightedWork
    state.weightedTime = state.weightedTime * historyDecay + cappedDt * (1 - historyDecay)
    state.weightedWork = state.weightedWork * historyDecay + (withinCutoff ? dy : 0) * (1 - historyDecay)
    debugLog(`[applyRateSample] dt ${dt}, dy ${dy}, weightedTime ${oldWeightedTime} -> ${state.weightedTime}, weightedWork ${oldWeightedWork} -> ${state.weightedWork}`)
  }

  /** Exact inverse of applyRateSample, for undo. */
  private reverseRateSample (dt: number, dy: number) {
    const state = this.rate
    const withinCutoff = dt <= this.reviewTimeCutoff
    const cappedDt = withinCutoff ? dt : this.reviewTimeCutoff
    state.weightedTime = (state.weightedTime - cappedDt * (1 - historyDecay)) / historyDecay
    state.weightedWork = (state.weightedWork - (withinCutoff ? dy : 0) * (1 - historyDecay)) / historyDecay
  }

  update (reviewHash: number, dy: number, logType: InstLogType) {
    const logLength = this.logs.length
    const epoch = now()
    const dt =
      logLength
        ? epoch - this.logs[this.logs.length - 1].epoch
        : epoch - this.startTime

    // Keep an unusual queue-count jump from dominating the persisted EMA.
    dy = Math.max(-10, Math.min(10, dy))
    this.applyRateSample(dt, dy)

    this.logs.push({ reviewHash, epoch, dt, dy, logType })
  }

  undo () {
    const removed = this.logs.pop()
    if (!removed) return

    this.reverseRateSample(removed.dt, removed.dy)
  }

  /** Weighted units of remaining work completed per second. */
  getRate () {
    const { weightedTime, weightedWork } = this.rate
    // Ratio of weighted totals, not an average of per-review dy/dt rates.
    // weightedTime <= 0 means that no timing samples exist. weightedWork may
    // legitimately be 0 after real samples - for example, pressing Again on
    // a learning card may leave 2 * new + learning + review unchanged. Such
    // zero-progress time is still evidence and remains part of the pace.
    if (weightedTime <= 0) return minimumRate
    return Math.max(weightedWork / weightedTime, minimumRate)
  }

  /** Weighted remaining work divided by the aggregate weighted-work pace. */
  getRemainingTime (remainingReviews: RemainingCardCounts) {
    return getRemainingCardLoad(remainingReviews) / this.getRate()
  }

  save () {
    // serialize
    const s: unknown[] = [ESTIMATOR_SCHEMA_VERSION, this.startTime]
    s.push(...serializeLogs(this.logs))

    const storage = (isAnkiDroid()) ? localStorage : ankiPersistentStorage
    storage.setItem(
      kRtEstimatorSchema,
      pakob64Deflate(JSON.stringify(s, function (_key, val) {
        return val.toFixed ? Number(val.toFixed(1)) : val
      }))
    )
  }

  static async instance (): Promise<Estimator> {
    if (Estimator.cache) return Estimator.cache

    const storage = (isAnkiDroid()) ? localStorage : ankiPersistentStorage
    const content = await storage.getItem(kRtEstimatorSchema)
    const reviewTimeCutoff = (await getAddonConfig('reviewTimeCutoff')) as number

    const deckName = await getCurrentDeckName()
    const rate = deckName ? await getDeckRate(deckName) : null

    if (!content) Estimator.cache = new Estimator({ reviewTimeCutoff, rate: rate ?? emptyRateState() })
    else {
      try {
        const s = JSON.parse(pakob64Inflate(content))
        let cursor = 0
        if (s[cursor++] !== ESTIMATOR_SCHEMA_VERSION) {
          throw new Error('Old schema')
        }
        const obj = new Estimator({ reviewTimeCutoff, rate: rate ?? emptyRateState() })
        obj.startTime = s[cursor++]
        const deserialized = deserializeLogs(s, cursor, obj.startTime)
        obj.logs = deserialized.logs
        cursor = deserialized.cursor
        if (cursor !== s.length) {
          throw new Error('Length mismatch - RTT')
        }

        // re-update elapsed time
        Estimator.cache = obj
      } catch {
        Estimator.cache = new Estimator({ reviewTimeCutoff, rate: rate ?? emptyRateState() })
      }
    }
    return Estimator.cache
  }
}
