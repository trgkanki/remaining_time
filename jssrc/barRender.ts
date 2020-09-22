import { Estimator } from './estimator'
import { getRemainingReviews, t2s, getRemainingCardLoad as reviewLoad } from './utils'
import './basestyle.scss'
import { getAddonConfig } from './utils/addonConfig'
// eslint-disable-next-line
const innerCSSText = require('!!raw-loader!sass-loader!./basestyle.scss').default as string

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

function HHmmFormat12 (date: Date) {
  const amPm = date.getHours() >= 12 ? 'PM' : 'AM'
  return `${zf((date.getHours() - 1) % 12 + 1, 2)}:${zf(date.getMinutes(), 2)} ${amPm}`
}

function updateDOM (svgHtml: string, progressBarMessage: string) {
  let barEl = document.getElementById('rtContainer')
  if (!barEl) {
    barEl = document.createElement('div')
    barEl.id = 'rtContainer'
    barEl.classList.add('rt-container')
    document.body.append(barEl)
  }

  // Shadow DOM to isolate styling from external CSS
  const shadowRoot = barEl.shadowRoot || barEl.attachShadow({ mode: 'open' })
  shadowRoot.innerHTML = `
  <div class='rt-container' id='rtContainer'>
  <style>${innerCSSText}</style>
  ${svgHtml}
  <div class='rt-message'>${progressBarMessage}</div>
  <a class='rt-reset' href=#resetRT title='Reset progress bar for this deck'>[⥻]</a>
  </div>
  `
  // since shadow DOM isloates CSS hierarchy, we should manually add night mode classes
  // back to shadow dom root
  if (document.body.classList.contains('nightMode')) {
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    shadowRoot.getElementById('rtContainer')!.classList.add('nightMode')
  }

  const resetButton = shadowRoot.querySelector('.rt-reset')
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
  const totalTime = elapsedTime + remainingTime
  const CPM = (estimator.getSlope() * 60).toFixed(2)
  const ETA = new Date()
  ETA.setSeconds(ETA.getSeconds() + remainingTime)
  const ETAString24 = (remainingTime >= 86400) ? '> day' : HHmmFormat(ETA)
  const ETAString12 = (remainingTime >= 86400) ? '> day' : HHmmFormat12(ETA)

  let message = (await getAddonConfig()).messageFormat as string
  message = message.replace('%(elapsedTime)', t2s(elapsedTime))
  message = message.replace('%(remainingTime)', t2s(remainingTime))
  message = message.replace('%(totalTime)', t2s(totalTime))
  message = message.replace('%(ETA)', ETAString24)
  message = message.replace('%(ETA12)', ETAString12)
  message = message.replace('%(CPM)', CPM)

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
