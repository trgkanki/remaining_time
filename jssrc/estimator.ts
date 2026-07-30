/**
 * Port of ExponentialSmoother.py
 */

import ankiLocalStorage from './utils/ankiLocalStorage'
import { pakob64Deflate, pakob64Inflate } from './utils/pakob64'
import { now, RemainingCardCounts } from './utils'
import { InstLogType } from './reviewLogger/types'
import { getAddonConfig } from './utils/addonConfig'
import { getCurrentDeckName, getDeckRates } from './utils/deckRate'

const historyDecay = 1 / 1.005
const historyLength = 100
const minimumRate = 1e-6

// How much pseudo-time (in seconds) the persisted deck rate counts for when
// seeding a fresh sitting - the seed's influence decays smoothly as real
// logs accumulate past this, rather than being thrown away outright once a
// couple of real data points exist.
const deckRateSeedWeightSeconds = 600

export interface LogEntry {
  epoch: number;
  dt: number;
  logType: InstLogType;
  reviewHash: number;
}

// Anki's own nu/lrn/rev counts are coupled (answering a new card can inject
// a learning-queue entry, a review lapse can too), and lrn's count in
// particular isn't a stable "work remaining" figure - it gets replenished by
// nu/rev processing rather than draining monotonically. So the ETA is only
// budgeted from new and review pace; lrn is deliberately excluded (see the
// anchor-skipping comment in getRate for how its time is still accounted
// for without needing its count).
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

interface CategorySeed {
  rate: number;
  weightSeconds: number;
}

function seedFor (rate: number | undefined): CategorySeed {
  return rate !== undefined
    ? { rate, weightSeconds: deckRateSeedWeightSeconds }
    : { rate: minimumRate, weightSeconds: 0 }
}

const ESTIMATOR_SCHEMA_VERSION = 3

// Persistence
const kRtEstimatorSchema = '__rt__estimator__schema__'

// Implementation

interface EstimatorInitializer {
  reviewTimeCutoff: number;
  seeds: Record<RateCategory, CategorySeed>;
}

export class Estimator {
  logs: LogEntry[] = []

  private startTime = now()
  private reviewTimeCutoff: number
  private seeds: Record<RateCategory, CategorySeed>
  // eslint-disable-next-line no-use-before-define
  private static cache: Estimator | null = null

  constructor (args: EstimatorInitializer) {
    this.reviewTimeCutoff = args.reviewTimeCutoff
    this.seeds = args.seeds
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
  }

  update (reviewHash: number, logType: InstLogType) {
    const logLength = this.logs.length
    const epoch = now()
    const dt =
      logLength
        ? epoch - this.logs[this.logs.length - 1].epoch
        : epoch - this.startTime

    this.logs.push({ reviewHash, epoch, dt, logType })
  }

  undo () {
    this.logs.pop()
  }

  /**
   * Cards/sec rate for one category (new or review).
   *
   * Rather than each entry's own immediate dt (time since the previous card
   * of any type), this uses time since the last new/rev entry - skipping
   * over any lrn entries in between, so a learning-card interruption's time
   * cost gets folded into whichever new/rev card follows it, rather than
   * silently dropped. This avoids needing lrn's count at all (which isn't a
   * stable "work remaining" figure - see the RateCategory comment) while
   * still accounting for the real time it costs.
   *
   * Which of new/rev absorbs a given lrn interruption is whichever happens
   * to come next chronologically, not a precise per-category attribution -
   * but Anki tends to front-load a sitting with a long consecutive run of
   * review cards before mixing in new ones, so for most of a sitting
   * there's no real ambiguity (no new cards are happening nearby to
   * misattribute to); it only becomes an approximation during the later,
   * genuinely interleaved stretch, and decayed averaging over many samples
   * smooths that out.
   */
  getRate (category: RateCategory) {
    const seed = this.seeds[category]

    const durations: number[] = []
    let anchorEpoch = this.startTime
    for (const log of this.logs) {
      const logCategory = categoryForLogType(log.logType)
      if (logCategory === null) continue
      const effectiveDt = log.epoch - anchorEpoch
      anchorEpoch = log.epoch
      if (logCategory === category) durations.push(effectiveDt)
    }

    const n = durations.length
    // No persisted history and no real data yet - nothing to compute from.
    if (n === 0 && seed.weightSeconds <= 0) return minimumRate

    // Seed the accumulation with the persisted deck rate as a decaying prior
    // (weighted like an old log entry), so a fresh sitting starts accurate
    // instead of a hard cutover once a couple of real logs exist.
    let totTime = seed.weightSeconds
    let totCount = seed.weightSeconds * seed.rate
    for (let i = Math.max(0, n - historyLength); i < n; i++) {
      const r = Math.pow(historyDecay, n - i)
      const dt = durations[i]
      if (dt <= this.reviewTimeCutoff) {
        totTime += r * dt
        totCount += r
      } else {
        // If user paused more than `reviewTimeCutoff` time, don't count this
        // card toward the pace - still charge the (capped) time against it
        // though.
        totTime += r * this.reviewTimeCutoff
      }
    }

    if (totTime < 1) return 1
    return Math.max(totCount / totTime, minimumRate)
  }

  /** New/review remaining counts, each divided by that category's own pace. */
  getRemainingTime (remainingReviews: RemainingCardCounts) {
    let newRate = this.getRate('new')
    let revRate = this.getRate('rev')

    // Maybe user might have done only new cards or review cards till now.
    // We don't want to show remaining time > day endlessly d/t untouched half.
    // Do a non-accurate but practical clamping of rates here.
    if (newRate === minimumRate) newRate = revRate * 0.2 // I guess this is a good approximation
    else if (revRate === minimumRate) revRate = newRate * 2 // Not inverse of above, but kinda conservative.

    return (
      remainingReviews.nu / newRate +
      remainingReviews.rev / revRate
    )
  }

  save () {
    // serialize
    const s = []
    s.push(ESTIMATOR_SCHEMA_VERSION)
    s.push(this.startTime)
    for (const log of this.logs) {
      s.push(log.epoch, log.dt, log.logType, log.reviewHash)
    }

    ankiLocalStorage.setItem(
      kRtEstimatorSchema,
      pakob64Deflate(JSON.stringify(s, function (_key, val) {
        return val.toFixed ? Number(val.toFixed(1)) : val
      }))
    )
  }

  static async instance (): Promise<Estimator> {
    if (Estimator.cache) return Estimator.cache

    const content = await ankiLocalStorage.getItem(kRtEstimatorSchema)
    const reviewTimeCutoff = (await getAddonConfig('reviewTimeCutoff')) as number

    const deckName = await getCurrentDeckName()
    const persistedRates = deckName ? await getDeckRates(deckName) : null
    const seeds: Record<RateCategory, CategorySeed> = {
      new: seedFor(persistedRates?.new),
      rev: seedFor(persistedRates?.rev)
    }

    if (!content) Estimator.cache = new Estimator({ reviewTimeCutoff, seeds })
    else {
      try {
        const s = JSON.parse(pakob64Inflate(content))
        let cursor = 0
        if (s[cursor++] !== ESTIMATOR_SCHEMA_VERSION) {
          throw new Error('Old schema')
        }
        const obj = new Estimator({ reviewTimeCutoff, seeds })
        obj.startTime = s[cursor++]
        while (cursor < s.length) {
          obj.logs.push({
            epoch: s[cursor + 0],
            dt: s[cursor + 1],
            logType: s[cursor + 2],
            reviewHash: s[cursor + 3]
          })
          cursor += 4
        }
        if (!cursor === s.length) {
          throw new Error('Length mismatch - RTT')
        }

        // re-update elapsed time
        Estimator.cache = obj
      } catch {
        Estimator.cache = new Estimator({ reviewTimeCutoff, seeds })
      }
    }
    return Estimator.cache
  }
}
