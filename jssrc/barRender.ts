import { Estimator } from './estimator'
import { getRemainingReviews, t2s, getRemainingCardLoad as reviewLoad } from './utils'
import './basestyle.scss'

// Drawing settings
const clampMinTime = 10
const clampMaxTime = 120
const minAlpha = 0.3
const maxAlpha = 0.7

function zf (n: number, cnt: number) {
  const s = n.toString()
  return '0'.repeat(cnt - s.length) + s
}

function HHmmFormat (date: Date) {
  return `${zf(date.getHours(), 2)}:${zf(date.getMinutes(), 2)}`
}

function updateDOM (svgHtml: string, progressBarMessage: string) {
  let barEl = document.getElementById('rtContainer')
  if (!barEl) {
    barEl = document.createElement('div')
    barEl.id = 'rtContainer'
    barEl.classList.add('rt-container')
    document.body.append(barEl)
  }

  barEl.innerHTML = `
    ${svgHtml}
    <div class='rt-message'>${progressBarMessage}</div>
    <a class='rt-reset' href=#resetRT title='Reset progress bar for this deck'>[⥻]</a>
  `

  const resetButton = barEl.querySelector('.rt-reset')
  if (!resetButton) return
  resetButton.addEventListener('click', async () => {
    if (confirm('[Remaining time] Press OK to reset the progress bar.')) {
      const estimator = await Estimator.instance()
      estimator.reset()
      updateProgressBar()
    }
  })
}

export async function updateProgressBar () {
  const currentRemainingReviews = await getRemainingReviews()
  const remainingLoad = reviewLoad(currentRemainingReviews)
  if (remainingLoad === 0) return

  const estimator = await Estimator.instance()
  const elapsedTime = estimator.elapsedTime
  const remainingTime = remainingLoad / estimator.getSlope()
  const ETA = new Date()
  ETA.setSeconds(ETA.getSeconds() + remainingTime)
  const ETAString = (remainingTime >= 86400) ? '> day' : HHmmFormat(ETA)
  const message = `Elapsed ${t2s(elapsedTime)},  Remaining ${t2s(remainingTime)}, ETA ${ETAString}`

  const progress = elapsedTime / (elapsedTime + remainingTime)
  const pathSVGs: string[] = []
  let rectX = 0

  let timeSum = 0
  for (const { dt } of estimator.logs) {
    timeSum += dt
  }

  for (const log of estimator.logs) {
    const rectW = log.dt / timeSum * progress
    const rectAlpha =
     (log.dt < clampMinTime) ? maxAlpha
       : (log.dt > clampMaxTime) ? minAlpha / 2
         : maxAlpha - (log.dt - clampMinTime) / (clampMaxTime - clampMinTime) * (maxAlpha - minAlpha)
    pathSVGs.push(`<path class="rt-log-${log.logType}" d="M${rectX} 0 h${rectW} V1 h-${rectW} Z" opacity="${rectAlpha}" shape-rendering="crispEdges" />`)
    rectX += rectW
  }

  const svgHtml = `
  <svg class='rt-bar' viewBox="0 0 1 1" preserveaspectratio="none" xmlns="http://www.w3.org/2000/svg">
      ${pathSVGs.join('')}
  </svg>
  `
  updateDOM(svgHtml, message)
}
