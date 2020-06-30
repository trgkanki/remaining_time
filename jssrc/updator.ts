import { Estimator } from './estimator'
import { RemainingCardCounts, getRemainingCardLoad, getRemainingReviews } from './utils'

enum RCCTConst {
  RESET,
  UPDATE,
  IGNORE
}

interface InstReset {
  type: RCCTConst.RESET;
}

interface InstIgnore {
  type: RCCTConst.IGNORE;
}

interface InstUpdate {
  type: RCCTConst.UPDATE;
  dy: number;
  ease: 1 | 2;
}

type EstimatorInst = InstReset | InstIgnore | InstUpdate

export async function updateEstimator () {
  const inst = await processRemainingCountDiff()
  const estimator = Estimator.instance()
  switch (inst.type) {
    case RCCTConst.IGNORE:
      return

    case RCCTConst.RESET:
      estimator.reset()
      estimator.save()
      return

    case RCCTConst.UPDATE:
      estimator.update(new Date().getTime() / 1000, inst.dy, inst.ease)
      estimator.save()
  }
}
/// /

async function processRemainingCountDiff (): Promise<EstimatorInst> {
  const currentRemainingCards = await getRemainingReviews()
  try {
    const prevRemainingCards = getRCC()
    if (!prevRemainingCards) return { type: RCCTConst.RESET }
    const previousReviewLoad = getRemainingCardLoad(prevRemainingCards)
    const nextReviewLoad = getRemainingCardLoad(currentRemainingCards)
    const dy = previousReviewLoad - nextReviewLoad

    const { nu: nu0, lrn: lrn0, rev: rev0 } = prevRemainingCards
    const { nu: nu1, lrn: lrn1, rev: rev1 } = currentRemainingCards

    // Same → Maybe edit cards
    if (
      nu0 === nu1 &&
      rev0 === rev1 &&
      lrn0 === lrn1
    ) return { type: RCCTConst.IGNORE }

    // See the new card for the first time
    if (
      // Because of 'bury related new cards' options,
      // nu1 may be decremented more than 1
      nu0 > nu1 &&
      rev0 === rev1 &&
      lrn0 <= lrn1
    ) {
      if (lrn0 === lrn1) {
        return { type: RCCTConst.UPDATE, dy, ease: 2 }
      }
      // Cannot determine if the review was again or good. :(
      return { type: RCCTConst.IGNORE }
    }

    // Re-learn or learn the current learning card
    if (
      nu0 === nu1 &&
      rev0 === rev1
    ) {
      if (lrn0 > lrn1) return { type: RCCTConst.UPDATE, dy, ease: 2 }
      else return { type: RCCTConst.UPDATE, dy, ease: 1 }
    }

    // Learning review cards
    if (
      nu0 === nu1 &&
      lrn0 <= lrn1 &&
      rev0 > rev1
    ) {
      if (lrn0 === lrn1) return { type: RCCTConst.UPDATE, dy, ease: 2 }
      else return { type: RCCTConst.UPDATE, dy, ease: 1 }
    }

    // Reset otherwise
    return { type: RCCTConst.RESET }
  } finally {
    saveRCC(currentRemainingCards)
  }
}

function getRCC () {
  const s = localStorage.getItem('__rt__lastrcc__')
  if (!s) return null
  return JSON.parse(s) as RemainingCardCounts
}

function saveRCC (rcc: RemainingCardCounts) {
  localStorage.setItem('__rt__lastrcc__', JSON.stringify(rcc))
}
