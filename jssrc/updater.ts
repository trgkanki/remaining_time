import { Estimator, getRemainingCardLoad } from './estimator'
import { EstimatorInst, RCCTConst } from './reviewLogger/types'
import { getReviewLogger } from './reviewLogger'
import { getCurrentDeckName, saveDeckRate } from './utils/deckRate'
import { debugLog } from './utils/debugLog'
import { getRemainingReviews } from './utils'
import { getLastRCC, saveLastRCC } from './utils/lastRCC'

function applyInstruction (estimator: Estimator, instruction: EstimatorInst, dy: number) {
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
      estimator.update(instruction.reviewHash, dy, instruction.logType)
      break
  }
}

export async function updateEstimator () {
  const currentRemainingCards = await getRemainingReviews()
  const previousRemainingCards = await getLastRCC()
  const estimator = await Estimator.instance()
  const logger = await getReviewLogger()
  const instructions = await logger.poll(currentRemainingCards, previousRemainingCards)
  await saveLastRCC(currentRemainingCards)

  let dy = previousRemainingCards
    ? getRemainingCardLoad(previousRemainingCards) - getRemainingCardLoad(currentRemainingCards)
    : 0
  await debugLog(`[updateEstimator] RCC prev: ${JSON.stringify(previousRemainingCards)}, current: ${JSON.stringify(currentRemainingCards)}, dy: ${dy}`)

  for (const instruction of instructions) {
    await debugLog(`[updateEstimator] new instruction: ${JSON.stringify(instruction)}`)
    applyInstruction(estimator, instruction, dy)
    if (instruction.instType === RCCTConst.UPDATE) dy = 0
  }
  estimator.save()

  const rateChanged = instructions.some(instruction =>
    instruction.instType === RCCTConst.UPDATE || instruction.instType === RCCTConst.UNDO
  )
  if (rateChanged) {
    const deckName = await getCurrentDeckName()
    if (deckName) {
      await saveDeckRate(deckName, estimator.rate)
    }
  }
}
