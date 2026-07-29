import { Estimator } from '../estimator'
import { RemainingCardCounts, getRemainingReviews, now, getCurrentCardId } from '../utils'
import { onSameReviewSession } from '../isDoingReview'
import { debugLog } from '../utils/debugLog'
import CRC32 from 'crc-32'
import { getAddonConfig } from '../utils/addonConfig'
import { getLastRCC, saveLastRCC } from '../utils/lastRCC'
import { EstimatorInst, ReviewLogger, RCCTConst } from './types'

async function getReviewHash (rcc: RemainingCardCounts): Promise<number> {
  const cardId = await getCurrentCardId()
  return CRC32.str(JSON.stringify({ rcc, cardId }))
}

async function getEstimatorInstruction (
  currentReviewHash: number,
  estimator: Estimator,
  currentRemainingCards: RemainingCardCounts
): Promise<EstimatorInst> {
  try {
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
    const prevRemainingCards = await getLastRCC()
    if (!prevRemainingCards) return { instType: RCCTConst.RESET }

    const { nu: nu0, lrn: lrn0, rev: rev0 } = prevRemainingCards
    const { nu: nu1, lrn: lrn1, rev: rev1 } = currentRemainingCards

    debugLog('RCC - prev: %s, current: %s', JSON.stringify(prevRemainingCards), JSON.stringify(currentRemainingCards))

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
    if (await getAddonConfig('autoReset')) {
      return { instType: RCCTConst.RESET }
    } else {
      return { instType: RCCTConst.IGNORE }
    }
  } finally {
    saveLastRCC(currentRemainingCards)
  }
}

export class MobileReviewLogger implements ReviewLogger {
  private lastEpoch = 0

  async poll (): Promise<EstimatorInst[]> {
    const currentRemainingCards = await getRemainingReviews()
    const reviewHash = await getReviewHash(currentRemainingCards)
    const estimator = await Estimator.instance()

    const instruction = await getEstimatorInstruction(
      reviewHash,
      estimator,
      currentRemainingCards
    )
    const epoch = now()

    debugLog(' - Output instruction: %s', JSON.stringify(instruction))

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
