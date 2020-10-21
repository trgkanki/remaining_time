import { Estimator } from './estimator'
import { getRemainingReviews, t2s, getRemainingCardLoad as reviewLoad } from './utils'
import './basestyle.scss'
import { getAddonConfig } from './utils/addonConfig'
// eslint-disable-next-line
const innerCSSText = require('!!raw-loader!sass-loader!./basestyle.scss').default as string

// Drawing settings
const segmentAlphaConsts = {
  clampMinTime: 10,
  clampMaxTime: 120,
  minAlpha: 0.3,
  maxAlpha: 0.7
}

const longSegmentClampMinTime = 1800

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

function linearInterpolate (start: number, end: number, t: number) {
  return start + (end - start) * t
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
      estimator.save()
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

  const progress = elapsedTime / (elapsedTime + remainingTime)
  const pathSVGs: string[] = []
  let rectX = 0

  let timeSum = 0
  for (const { dt } of estimator.logs) {
    timeSum += dt
  }

  for (const log of estimator.logs) {
    const clampedDt = Math.min(log.dt, longSegmentClampMinTime)
    const rectW = clampedDt / timeSum * progress
    const rectAlpha =
      log.dt > longSegmentClampMinTime ? segmentAlphaConsts.minAlpha / 4
        : (clampedDt < segmentAlphaConsts.clampMinTime) ? segmentAlphaConsts.maxAlpha
          : (clampedDt > segmentAlphaConsts.clampMaxTime) ? segmentAlphaConsts.minAlpha / 2
            : linearInterpolate(
              segmentAlphaConsts.maxAlpha,
              segmentAlphaConsts.minAlpha,
              (clampedDt - segmentAlphaConsts.clampMinTime) / (segmentAlphaConsts.clampMaxTime - segmentAlphaConsts.clampMinTime)
            )

    pathSVGs.push(`<path class="rt-log-segment rt-log-${log.logType}" d="M${rectX} 0 h${rectW} V1 h-${rectW} Z" opacity="${rectAlpha}" />`)

    // X sign for long segment
    if (log.dt > longSegmentClampMinTime) {
      pathSVGs.push(`<path class="rt-log-segment-truncated" d="M${rectX} .1 l${rectW} .8 Z M${rectX} .9 l${rectW} -.8 Z" />`)
    }
    rectX += rectW
  }

  const svgHtml = `
  <svg class='rt-bar' viewBox="0 0 1 1" preserveaspectratio="none" xmlns="http://www.w3.org/2000/svg">
      ${pathSVGs.join('')}
  </svg>
  `
  updateDOM(svgHtml, message)
}
