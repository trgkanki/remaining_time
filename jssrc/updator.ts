import { Estimator } from './estimator'
import { RemainingCardCounts, getRemainingCardLoad, getRemainingReviews } from './utils'
import ankiLocalStorage from './utils/ankiLocalStorage'
import { onSameReviewSession } from './isDoingReview'

enum RCCTConst {
  RESET,
  UPDATE,
  IGNORE
}

interface InstReset {
  instType: RCCTConst.RESET;
}

interface InstIgnore {
  instType: RCCTConst.IGNORE;
}

interface InstUpdate {
  instType: RCCTConst.UPDATE;
  dy: number;
  logType: 'new' | 'good' | 'again' | 'unknown';
}

type EstimatorInst = InstReset | InstIgnore | InstUpdate

let lastEpoch = 0

export async function updateEstimator () {
  const instruction = await processRemainingCountDiff()
  const epoch = new Date().getTime() / 1000
  const estimator = await Estimator.instance()

  // Due to how run() is called on index.ts, on desktop anki
  // run() might be called twice with qFade(100ms) duration.
  // on android this duration may goes up to 500ms.
  // This prevents them being counted as two reviews
  const isInitializing = (epoch - lastEpoch < 1)
  lastEpoch = epoch
  if (isInitializing) return

  console.log('inst', instruction)

  switch (instruction.instType) {
    case RCCTConst.IGNORE:
      estimator.skipUpdate(epoch)
      return

    case RCCTConst.RESET:
      estimator.reset()
      return

    case RCCTConst.UPDATE:
      estimator.update(epoch, instruction.dy, instruction.logType)
  }
}
/// /

async function processRemainingCountDiff (): Promise<EstimatorInst> {
  const currentRemainingCards = await getRemainingReviews()
  console.log('crc', currentRemainingCards)
  try {
    const prevRemainingCards = await getRCC()
    console.log('prc', prevRemainingCards)
    if (!prevRemainingCards) return { instType: RCCTConst.RESET }
    const previousReviewLoad = getRemainingCardLoad(prevRemainingCards)
    const nextReviewLoad = getRemainingCardLoad(currentRemainingCards)
    const dy = previousReviewLoad - nextReviewLoad

    const { nu: nu0, lrn: lrn0, rev: rev0 } = prevRemainingCards
    const { nu: nu1, lrn: lrn1, rev: rev1 } = currentRemainingCards

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
      if (lrn0 > lrn1) return { instType: RCCTConst.UPDATE, dy, logType: 'good' }
      else return { instType: RCCTConst.UPDATE, dy, logType: 'again' }
    }

    // Learning review cards
    if (
      nu0 === nu1 &&
      lrn0 <= lrn1 &&
      rev0 > rev1
    ) {
      if (lrn0 === lrn1) return { instType: RCCTConst.UPDATE, dy, logType: 'good' }
      else return { instType: RCCTConst.UPDATE, dy, logType: 'again' }
    }

    // maybe undo?
    if (
      nu0 <= nu1 &&
      rev0 <= rev1
    ) {
      if (await onSameReviewSession()) {
        return { instType: RCCTConst.UPDATE, dy, logType: 'unknown' }
      }
    }

    // Reset otherwise
    return { instType: RCCTConst.RESET }
  } finally {
    saveRCC(currentRemainingCards)
  }
}

async function getRCC () {
  const s = await ankiLocalStorage.getItem('__rt__lastrcc__')
  if (!s) return null
  return JSON.parse(s) as RemainingCardCounts
}

function saveRCC (rcc: RemainingCardCounts) {
  ankiLocalStorage.setItem('__rt__lastrcc__', JSON.stringify(rcc))
}
