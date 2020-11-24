import { Estimator } from './estimator'
import { RemainingCardCounts, getRemainingCardLoad, getRemainingReviews, now, getCurrentCardId } from './utils'
import ankiLocalStorage from './utils/ankiLocalStorage'
import { onSameReviewSession } from './isDoingReview'
import { debugLog } from './utils/debugLog'
import CRC32 from 'crc-32'

enum RCCTConst {
  RESET,
  UPDATE,
  IGNORE,
  UNDO
}

interface InstReset {
  instType: RCCTConst.RESET;
}

interface InstUndo {
  instType: RCCTConst.UNDO;
}

interface InstIgnore {
  instType: RCCTConst.IGNORE;
}

export type InstLogType = 'new' | 'good' | 'again' | 'rev-good' | 'rev-again' | 'unknown'

interface InstUpdate {
  instType: RCCTConst.UPDATE;
  dy: number;
  logType: InstLogType;
}

type EstimatorInst = InstReset | InstIgnore | InstUpdate | InstUndo

let lastEpoch = 0

/// /

async function getReviewHash (rcc: RemainingCardCounts): Promise<number> {
  const cardId = await getCurrentCardId()
  return CRC32.str(JSON.stringify({ rcc, cardId }))
}

export async function updateEstimator () {
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
  const isInitializing = (epoch - lastEpoch < 1)
  lastEpoch = epoch
  if (isInitializing) return

  switch (instruction.instType) {
    case RCCTConst.IGNORE:
      break

    case RCCTConst.UNDO:
      estimator.undo()
      break

    case RCCTConst.RESET:
      estimator.reset()
      break

    case RCCTConst.UPDATE:
      estimator.update(reviewHash, instruction.dy, instruction.logType)
      break
  }
  estimator.save()
}

/// /

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
    const previousReviewLoad = getRemainingCardLoad(prevRemainingCards)
    const nextReviewLoad = getRemainingCardLoad(currentRemainingCards)
    const dy = previousReviewLoad - nextReviewLoad

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
      return { instType: RCCTConst.UPDATE, dy, logType: 'new' }
    }

    // Re-learn or learn the current learning card
    if (
      nu0 === nu1 &&
      rev0 === rev1
    ) {
      // This might happen also in undo scenario, but we're, quite open to such scenario.
      // some minor inaccuracies could be tolerated?
      if (lrn0 > lrn1) return { instType: RCCTConst.UPDATE, dy, logType: 'good' }
      else return { instType: RCCTConst.UPDATE, dy, logType: 'again' }
    }

    // Learning review cards
    if (
      nu0 === nu1 &&
      lrn0 <= lrn1 &&
      rev0 > rev1
    ) {
      if (lrn0 === lrn1) return { instType: RCCTConst.UPDATE, dy, logType: 'rev-good' }
      else return { instType: RCCTConst.UPDATE, dy, logType: 'rev-again' }
    }

    // maybe undo?
    if (
      (nu0 < nu1 && rev0 === rev1) ||
      (rev0 < rev1 && nu0 === nu1)
    ) {
      if (await onSameReviewSession()) {
        return { instType: RCCTConst.UPDATE, dy, logType: 'unknown' }
      }
    }

    // Ignore otherwise
    // This could happen on multiple cases, like suspending multiple cards at once,...
    return { instType: RCCTConst.IGNORE }
  } finally {
    saveLastRCC(currentRemainingCards)
  }
}

const kLastRCC = '__rt__lastrcc__'
async function getLastRCC () {
  const s = await ankiLocalStorage.getItem(kLastRCC)
  if (!s) return null
  return JSON.parse(s) as RemainingCardCounts
}

function saveLastRCC (rcc: RemainingCardCounts) {
  ankiLocalStorage.setItem(kLastRCC, JSON.stringify(rcc))
}
