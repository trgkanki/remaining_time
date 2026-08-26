// Mobile version of review logger - Currently works for AnkiDroidJS 0.03 api
// Since ankidroid doesn't expose what ease did the user just pressed,
// we can only guess from new/lrn/rev count diffs, which is kinda fragile
// We'll accept this as incompleteness, and just document that the bar colors
// will be kinda random. (biased to wrongs)
//
// ETA calculation is not affected by this classification heuristic: weighted
// work progress is calculated separately from the shared card-count delta.

import { Estimator } from '../estimator'
import { RemainingCardCounts, now, getCurrentCardId } from '../utils'
import { onSameReviewSession } from '../isDoingReview'
import { debugLog } from '../utils/debugLog'
import CRC32 from 'crc-32'
import { EstimatorInst, ReviewLogger, RCCTConst } from './types'

async function getReviewHash (rcc: RemainingCardCounts): Promise<number> {
  const cardId = await getCurrentCardId()
  return CRC32.str(JSON.stringify({ rcc, cardId }))
}

async function getEstimatorInstruction (
  currentReviewHash: number,
  estimator: Estimator,
  currentRemainingCards: RemainingCardCounts,
  previousRemainingCards: RemainingCardCounts | null
): Promise<EstimatorInst> {
  // Edit card check
  if (
    estimator.logs.length >= 1 &&
    estimator.logs[estimator.logs.length - 1].reviewHash === currentReviewHash
  ) {
    return {
      instType: RCCTConst.IGNORE
    }
  }

  // Undo check
  if (
    estimator.logs.length >= 2 &&
    estimator.logs[estimator.logs.length - 2].reviewHash === currentReviewHash
  ) {
    return {
      instType: RCCTConst.UNDO
    }
  }

  // Comparing!
  if (!previousRemainingCards) return { instType: RCCTConst.RESET }

  const { nu: nu0, lrn: lrn0, rev: rev0 } = previousRemainingCards
  const { nu: nu1, lrn: lrn1, rev: rev1 } = currentRemainingCards

  // See the new card for the first time
  if (
    // Because of 'bury related new cards' options,
    // nu1 may be decremented more than 1
    nu0 > nu1 &&
    rev0 === rev1 &&
    lrn0 <= lrn1
  ) {
    return { instType: RCCTConst.UPDATE, reviewHash: currentReviewHash, logType: 'new' }
  }

  // Re-learn or learn the current learning card
  if (
    nu0 === nu1 &&
    rev0 === rev1
  ) {
    // This might happen also in undo scenario, but we're, quite open to such scenario.
    // some minor inaccuracies could be tolerated?
    if (lrn0 > lrn1) return { instType: RCCTConst.UPDATE, reviewHash: currentReviewHash, logType: 'good' }
    else return { instType: RCCTConst.UPDATE, reviewHash: currentReviewHash, logType: 'again' }
  }

  // Learning review cards
  if (
    nu0 === nu1 &&
    lrn0 <= lrn1 &&
    rev0 > rev1
  ) {
    if (lrn0 === lrn1) return { instType: RCCTConst.UPDATE, reviewHash: currentReviewHash, logType: 'rev-good' }
    else return { instType: RCCTConst.UPDATE, reviewHash: currentReviewHash, logType: 'rev-again' }
  }

  // maybe undo?
  if (
    (nu0 < nu1 && rev0 === rev1) ||
    (rev0 < rev1 && nu0 === nu1)
  ) {
    if (await onSameReviewSession()) {
      return { instType: RCCTConst.UPDATE, reviewHash: currentReviewHash, logType: 'unknown' }
    }
  }

  // Ignore otherwise
  // This could happen on multiple cases, like suspending multiple cards at once,...
  return { instType: RCCTConst.IGNORE }
}

export class MobileReviewLogger implements ReviewLogger {
  private lastEpoch = 0

  async poll (
    currentRemainingCards: RemainingCardCounts,
    previousRemainingCards: RemainingCardCounts | null
  ): Promise<EstimatorInst[]> {
    const reviewHash = await getReviewHash(currentRemainingCards)
    const estimator = await Estimator.instance()

    const instruction = await getEstimatorInstruction(
      reviewHash,
      estimator,
      currentRemainingCards,
      previousRemainingCards
    )
    const epoch = now()

    await debugLog(` - Output instruction: ${JSON.stringify(instruction)}`)

    // Due to how run() is called on index.ts, on desktop anki
    // run() might be called twice with qFade(100ms) duration.
    // on android this duration may goes up to 500ms.
    // This prevents them being counted as two reviews
    const isInitializing = (epoch - this.lastEpoch < 1)
    this.lastEpoch = epoch
    if (isInitializing) return []

    return [instruction]
  }
}
