import { Estimator } from './estimator'
import { getRemainingReviews } from './utils'

// Drawing settings
const clampMinTime = 10
const clampMaxTime = 120
const minAlpha = 0.3
const maxAlpha = 0.7

const againColor = '239, 103, 79' // Again
const goodColor = '114, 166, 249' // Good/Easy

// TODO: support dark mode
const backgroundColor = 'black'

export function renderBarSVG (estimator: Estimator): string {
  let timeSum = 0
  for (const { dt } of estimator.logs) {
    timeSum += dt
  }

  const currentRemainingReviews = getRemainingReviews()
  const elapsedTime = estimator.elapsedTime
  const remainingTime = currentRemainingReviews / estimator.getSlope()
  const progress = elapsedTime / (elapsedTime + remainingTime)
  const pathSVGs: string[] = []
  let rectX = 0

  for (const log of estimator.logs) {
    const rectW = log.dt / timeSum * progress
    const rectAlpha =
     (log.dt < clampMinTime) ? maxAlpha
       : (log.dt > clampMaxTime) ? minAlpha / 2
         : maxAlpha - (log.dt - clampMinTime) / (clampMaxTime - clampMinTime) * (maxAlpha - minAlpha)
    const rectColor = (log.ease === 1) ? againColor : goodColor
    pathSVGs.push(`'<path d="M${rectX} 0 h${rectW} V1 h-${rectW} Z" fill="rgba(${rectColor}, ${rectAlpha})" shape-rendering="crispEdges" />`)
    rectX += rectW
  }

  return `
  <svg width="1" height="1" xmlns="http://www.w3.org/2000/svg">
      <path d="M0 0 h1 V1 h-1 Z" fill="${backgroundColor}" />
      ${pathSVGs.join('')}
  </svg>
  `
}
