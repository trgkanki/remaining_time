/**
 * Port of ExponentialSmoother.py
 */

import ankiLocalStorage from './utils/ankiLocalStorage'
import { pakob64Deflate, pakob64Inflate } from './utils/pakob64'
import { now } from './utils'
import { InstLogType } from './reviewLogger/types'
import { getAddonConfig } from './utils/addonConfig'
import { getCurrentDeckName, getDeckRate } from './utils/deckRate'

const historyDecay = 1 / 1.005
const historyLength = 100

// How much pseudo-time (in seconds) the persisted deck rate counts for when
// seeding a fresh sitting - the seed's influence decays smoothly as real
// logs accumulate past this, rather than being thrown away outright once a
// couple of real data points exist.
const deckRateSeedWeightSeconds = 600

export interface LogEntry {
  epoch: number;
  dt: number;
  dy: number;
  logType: InstLogType;
  reviewHash: number;
}

const ESTIMATOR_SCHEMA_VERSION = 2

// Persistence
const kRtEstimatorSchema = '__rt__estimator__schema__'

// Implementation

interface EstimatorInitializer {
  reviewTimeCutoff: number;
  seedRate: number;
  seedWeightSeconds: number;
}

export class Estimator {
  logs: LogEntry[] = []

  private startTime = now()
  private reviewTimeCutoff: number
  private seedRate: number
  private seedWeightSeconds: number
  // eslint-disable-next-line no-use-before-define
  private static cache: Estimator | null = null

  constructor (args: EstimatorInitializer) {
    this.reviewTimeCutoff = args.reviewTimeCutoff
    this.seedRate = args.seedRate
    this.seedWeightSeconds = args.seedWeightSeconds
  }

  get elapsedTime () {
    return now() - this.startTime
  }

  reset () {
    this.logs = []
    this.startTime = now()
  }

  update (reviewHash: number, dy: number, logType: InstLogType) {
    const logLength = this.logs.length
    const epoch = now()
    const dt =
      logLength
        ? epoch - this.logs[this.logs.length - 1].epoch
        : epoch - this.startTime

    // Prevent estimator fallout d/t unexpected events
    // e.g) massive new cards, changing deck of multiple cards
    if (dy < -10) dy = -10 // could happen on massive new cards
    if (dy > 10) dy = 10

    this.logs.push({ reviewHash, epoch, dt, dy, logType })
  }

  undo () {
    this.logs.pop()
  }

  getSlope () {
    const logLength = this.logs.length
    // No persisted history and no real data yet - nothing to compute from.
    if (logLength === 0 && this.seedWeightSeconds <= 0) return 1e-6

    // Seed the accumulation with the persisted deck rate as a decaying prior
    // (weighted like an old log entry), so a fresh sitting starts accurate
    // instead of a hard cutover once a couple of real logs exist.
    let totTime = this.seedWeightSeconds
    let totY = this.seedWeightSeconds * this.seedRate
    for (let i = Math.max(0, logLength - historyLength); i < logLength; i++) {
      const r = Math.pow(historyDecay, logLength - i)
      const log = this.logs[i]
      if (log.dt <= this.reviewTimeCutoff) {
        totTime += r * log.dt
        totY += r * log.dy
      } else {
        // If user paused more than `reviewTimeCutoff` time, don't use dy
        // If user reviewed a lot of card on the other device
        // during the pause, dy may be massive. We don't want to
        // account that. Also, if user just procrastinated a lot
        // and left the review session, dy/dt should be close to
        // zero, and it's safe to set dy to 0.
        totTime += r * this.reviewTimeCutoff
      }
    }

    if (totTime < 1) return 1
    return Math.max(totY / totTime, 1e-6)
  }

  save () {
    // serialize
    const s = []
    s.push(ESTIMATOR_SCHEMA_VERSION)
    s.push(this.startTime)
    for (const log of this.logs) {
      s.push(log.epoch, log.dt, log.dy, log.logType, log.reviewHash)
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
    const persistedRate = deckName ? await getDeckRate(deckName) : null
    const seedArgs = persistedRate !== null
      ? { seedRate: persistedRate, seedWeightSeconds: deckRateSeedWeightSeconds }
      : { seedRate: 1e-6, seedWeightSeconds: 0 }

    if (!content) Estimator.cache = new Estimator({ reviewTimeCutoff, ...seedArgs })
    else {
      try {
        const s = JSON.parse(pakob64Inflate(content))
        let cursor = 0
        if (s[cursor++] !== ESTIMATOR_SCHEMA_VERSION) {
          throw new Error('Old schema')
        }
        const obj = new Estimator({ reviewTimeCutoff, ...seedArgs })
        obj.startTime = s[cursor++]
        while (cursor < s.length) {
          obj.logs.push({
            epoch: s[cursor + 0],
            dt: s[cursor + 1],
            dy: s[cursor + 2],
            logType: s[cursor + 3],
            reviewHash: s[cursor + 4]
          })
          cursor += 5
        }
        if (!cursor === s.length) {
          throw new Error('Length mismatch - RTT')
        }

        // re-update elapsed time
        Estimator.cache = obj
      } catch {
        Estimator.cache = new Estimator({ reviewTimeCutoff, ...seedArgs })
      }
    }
    return Estimator.cache
  }
}
