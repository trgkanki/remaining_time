import { Estimator } from './estimator'
import { EstimatorInst, RCCTConst } from './reviewLogger/types'
import { getReviewLogger } from './reviewLogger'
import { getCurrentDeckName, getDeckRate, saveDeckRate, blendDeckRate } from './utils/deckRate'

function applyInstruction (estimator: Estimator, instruction: EstimatorInst) {
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
      estimator.update(instruction.reviewHash, instruction.dy, instruction.logType)
      break
  }
}

export async function updateEstimator () {
  const estimator = await Estimator.instance()
  const logger = await getReviewLogger()
  const instructions = await logger.poll()

  for (const instruction of instructions) {
    applyInstruction(estimator, instruction)
  }
  estimator.save()

  const hadUpdate = instructions.some(instruction => instruction.instType === RCCTConst.UPDATE)
  if (hadUpdate) {
    const deckName = await getCurrentDeckName()
    if (deckName) {
      const oldRate = await getDeckRate(deckName)
      await saveDeckRate(deckName, blendDeckRate(oldRate, estimator.getSlope()))
    }
  }
}
