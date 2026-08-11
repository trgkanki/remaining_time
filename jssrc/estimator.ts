/**
 * Port of ExponentialSmoother.py
 */

import ankiPersistentStorage from './utils/ankiPersistentStorage'
import { pakob64Deflate, pakob64Inflate } from './utils/pakob64'
import { now, RemainingCardCounts } from './utils'
import { InstLogType } from './reviewLogger/types'
import { getAddonConfig } from './utils/addonConfig'
import { getCurrentDeckName, getDeckRates, RateState } from './utils/deckRate'
import { isAnkiDroid } from './utils/apiAnkiDroid'

const historyDecay = 1 / 1.005
const minimumRate = 1e-6

export interface LogEntry {
  epoch: number;
  dt: number;
  logType: InstLogType;
  reviewHash: number | null; // May be null to save spaces on ankidroid
}

// Anki's own nu/lrn/rev counts are coupled (answering a new card can inject
// a learning-queue entry, a review lapse can too), and lrn's count in
// particular isn't a stable "work remaining" figure - it gets replenished by
// nu/rev processing rather than draining monotonically. So the ETA is only
// budgeted from new and review pace; lrn is deliberately excluded (see the
// anchor-skipping comment on anchorEpochBefore for how its time is still
// accounted for without needing its count).
export type RateCategory = 'new' | 'rev'

export function categoryForLogType (logType: InstLogType): RateCategory | null {
  switch (logType) {
    case 'new':
      return 'new'
    case 'rev-good':
    case 'rev-again':
      return 'rev'
    case 'good':
    case 'again':
    case 'unknown':
      return null
  }
}

const ESTIMATOR_SCHEMA_VERSION = 4

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
    s.push(log.dt, logTypeCodes.indexOf(log.logType))
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
    const logType = logTypeCodes[s[cursor++] as number]
    epoch += dt
    // Patched in below for the persisted tail; older entries never have
    // their reviewHash read.
    logs.push({ epoch, dt, logType, reviewHash: null })
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
  rates: Record<RateCategory, RateState>;
}

function emptyRateState (): RateState {
  return { weightedTime: 0, weightedCount: 0 }
}

export class Estimator {
  logs: LogEntry[] = []
  // A pure exponential smoother's raw accumulator per category, decayed on
  // every real sample regardless of which sitting it happened in. This is
  // the same object the persisted per-deck rate is loaded into and saved
  // from (see updater.ts) - there's no separate "seed" concept blended in
  // through a second, differently-tuned smoother; continuing to decay this
  // state across a sitting boundary *is* how the rate persists.
  rates: Record<RateCategory, RateState>

  private startTime = now()
  private reviewTimeCutoff: number
  // eslint-disable-next-line no-use-before-define
  private static cache: Estimator | null = null

  constructor (args: EstimatorInitializer) {
    this.reviewTimeCutoff = args.reviewTimeCutoff
    this.rates = args.rates
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
    // this.rates is deliberately left untouched - it's the deck's long-run
    // learned pace, not sitting-scoped state.
  }

  /**
   * Epoch of the closest new/rev log entry strictly before `beforeIndex`
   * (skipping lrn entries), or the sitting's start if none exist yet. Used
   * to fold an lrn interruption's time cost into whichever new/rev card
   * follows it, rather than needing lrn's own count (which isn't a stable
   * "work remaining" figure - see the RateCategory comment above). Which of
   * new/rev absorbs a given lrn interruption is whichever happens to come
   * next chronologically, not a precise per-category attribution - but Anki
   * tends to front-load a sitting with a long consecutive run of review
   * cards before mixing in new ones, so for most of a sitting there's no
   * real ambiguity; it only becomes an approximation during a genuinely
   * interleaved stretch, and decayed averaging over many samples smooths
   * that out.
   */
  private anchorEpochBefore (beforeIndex: number): number {
    for (let i = beforeIndex - 1; i >= 0; i--) {
      if (categoryForLogType(this.logs[i].logType) !== null) return this.logs[i].epoch
    }
    return this.startTime
  }

  /** Folds one new/rev sample into that category's running pace. */
  private applyRateSample (category: RateCategory, dt: number) {
    const state = this.rates[category]
    const withinCutoff = dt <= this.reviewTimeCutoff
    const cappedDt = withinCutoff ? dt : this.reviewTimeCutoff
    const oldWeightedTime = state.weightedTime
    const oldWeightedCount = state.weightedCount
    state.weightedTime = state.weightedTime * historyDecay + cappedDt
    state.weightedCount = state.weightedCount * historyDecay + (withinCutoff ? 1 : 0)
    console.log(`[applyRateSample] category ${category}, dt ${dt}, weightedTime ${oldWeightedTime} -> ${state.weightedTime}, weightedCount ${oldWeightedCount} -> ${state.weightedCount}`)
  }

  /** Exact inverse of applyRateSample, for undo. */
  private reverseRateSample (category: RateCategory, dt: number) {
    const state = this.rates[category]
    const withinCutoff = dt <= this.reviewTimeCutoff
    const cappedDt = withinCutoff ? dt : this.reviewTimeCutoff
    state.weightedTime = (state.weightedTime - cappedDt) / historyDecay
    state.weightedCount = (state.weightedCount - (withinCutoff ? 1 : 0)) / historyDecay
  }

  update (reviewHash: number, logType: InstLogType) {
    const logLength = this.logs.length
    const epoch = now()
    const dt =
      logLength
        ? epoch - this.logs[this.logs.length - 1].epoch
        : epoch - this.startTime

    const category = categoryForLogType(logType)
    if (category) {
      const anchorEpoch = this.anchorEpochBefore(logLength)
      this.applyRateSample(category, epoch - anchorEpoch)
    }

    this.logs.push({ reviewHash, epoch, dt, logType })
  }

  undo () {
    const removed = this.logs.pop()
    if (!removed) return

    const category = categoryForLogType(removed.logType)
    if (category) {
      const anchorEpoch = this.anchorEpochBefore(this.logs.length)
      this.reverseRateSample(category, removed.epoch - anchorEpoch)
    }
  }

  /** Cards/sec pace for one category (new or review). */
  getRate (category: RateCategory) {
    const { weightedTime, weightedCount } = this.rates[category]
    // No persisted history and no real data yet - nothing to compute from.
    if (weightedTime <= 0) return minimumRate
    if (weightedTime < 1) return 1
    return Math.max(weightedCount / weightedTime, minimumRate)
  }

  /** New/review remaining counts, each divided by that category's own pace. */
  getRemainingTime (remainingReviews: RemainingCardCounts) {
    let newRate = this.getRate('new')
    let revRate = this.getRate('rev')

    // Maybe user might have done only new cards or review cards till now.
    // We don't want to show remaining time > day endlessly d/t untouched half.
    // Do a non-accurate but practical clamping of rates here.
    if (newRate <= 2 * minimumRate) newRate = Math.max(newRate, revRate * 0.1)
    if (revRate <= 2 * minimumRate) revRate = Math.max(revRate, newRate)

    return (
      remainingReviews.nu / newRate +
      remainingReviews.rev / revRate
    )
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
    const persistedRates = deckName ? await getDeckRates(deckName) : null
    const rates: Record<RateCategory, RateState> = {
      new: persistedRates?.new ?? emptyRateState(),
      rev: persistedRates?.rev ?? emptyRateState()
    }

    if (!content) Estimator.cache = new Estimator({ reviewTimeCutoff, rates })
    else {
      try {
        const s = JSON.parse(pakob64Inflate(content))
        let cursor = 0
        if (s[cursor++] !== ESTIMATOR_SCHEMA_VERSION) {
          throw new Error('Old schema')
        }
        const obj = new Estimator({ reviewTimeCutoff, rates })
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
        Estimator.cache = new Estimator({ reviewTimeCutoff, rates })
      }
    }
    return Estimator.cache
  }
}
