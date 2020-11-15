
import { Estimator } from '../estimator'
import { t2s } from '../utils'
import { getAddonConfig } from '../utils/addonConfig'

function zf (n: number, cnt: number) {
  const s = n.toString()
  return '0'.repeat(cnt - s.length) + s
}

function HHmmFormat (date: Date) {
  return `${zf(date.getHours(), 2)}:${zf(date.getMinutes(), 2)}`
}

function HHmmFormat12 (date: Date) {
  const amPm = date.getHours() >= 12 ? 'PM' : 'AM'
  return `${zf((date.getHours() - 1) % 12 + 1, 2)}:${zf(date.getMinutes(), 2)} ${amPm}`
}

export async function getMessage (estimator: Estimator, remainingLoad: number): Promise<string> {
  const elapsedTime = estimator.elapsedTime
  const remainingTime = remainingLoad / estimator.getSlope()
  const totalTime = elapsedTime + remainingTime
  const CPM = (estimator.getSlope() * 60).toFixed(2)
  const ETA = new Date()
  ETA.setSeconds(ETA.getSeconds() + remainingTime)
  const ETAString24 = (remainingTime >= 86400) ? '> day' : HHmmFormat(ETA)
  const ETAString12 = (remainingTime >= 86400) ? '> day' : HHmmFormat12(ETA)

  const correctRevCount = estimator.logs.filter(x => x.logType === 'rev-good').length
  const againReviewCount = estimator.logs.filter(x => x.logType === 'rev-again').length
  const retentionRateString = `${(100 * correctRevCount / (correctRevCount + againReviewCount)).toFixed(1)}%`

  let message = (await getAddonConfig()).messageFormat as string
  message = message.replace('%(elapsedTime)', t2s(elapsedTime))
  message = message.replace('%(remainingTime)', t2s(remainingTime))
  message = message.replace('%(totalTime)', t2s(totalTime))
  message = message.replace('%(ETA)', ETAString24)
  message = message.replace('%(ETA12)', ETAString12)
  message = message.replace('%(CPM)', CPM)
  message = message.replace('%(RR)', retentionRateString)

  return message
}
