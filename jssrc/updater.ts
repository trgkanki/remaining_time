import { Estimator, RateCategory, categoryForLogType } from './estimator'
import { EstimatorInst, RCCTConst } from './reviewLogger/types'
import { getReviewLogger } from './reviewLogger'
import { getCurrentDeckName, saveDeckRates, DeckRates } from './utils/deckRate'

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
      estimator.update(instruction.reviewHash, instruction.logType)
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

  const touchedCategories = new Set<RateCategory>()
  for (const instruction of instructions) {
    if (instruction.instType !== RCCTConst.UPDATE) continue
    const category = categoryForLogType(instruction.logType)
    if (category) touchedCategories.add(category)
  }

  if (touchedCategories.size > 0) {
    const deckName = await getCurrentDeckName()
    if (deckName) {
      const newRates: DeckRates = {}
      for (const category of touchedCategories) {
        newRates[category] = estimator.rates[category]
      }
      await saveDeckRates(deckName, newRates)
    }
  }
}
