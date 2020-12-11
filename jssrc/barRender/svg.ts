import { Estimator } from '../estimator'
import { t2s } from '../utils'

const segmentAlphaConsts = {
  clampMinTime: 10,
  clampMaxTime: 120,
  minAlpha: 0.3,
  maxAlpha: 0.7
}

const longSegmentClampMinTime = 1800

/// helper functions

function linearInterpolate (start: number, end: number, t: number) {
  return start + (end - start) * t
}

/// main

export function getSVG (estimator: Estimator, remainingLoad: number, options: {
  fixedWidth: boolean;
}): string {
  const elapsedTime = estimator.elapsedTime
  const remainingTime = remainingLoad / estimator.getSlope()

  const progress = elapsedTime / (elapsedTime + remainingTime)
  const pathSVGs: string[] = []
  let rectX = 0

  let timeSum = 0
  const { logs } = estimator
  for (const { dt } of logs) {
    timeSum += dt
  }

  for (const log of logs) {
    const clampedDt = Math.min(log.dt, longSegmentClampMinTime)
    const rectW = options.fixedWidth ? progress / logs.length : clampedDt / timeSum * progress
    const rectAlpha =
      log.dt > longSegmentClampMinTime ? segmentAlphaConsts.minAlpha / 4
        : (clampedDt < segmentAlphaConsts.clampMinTime) ? segmentAlphaConsts.maxAlpha
          : (clampedDt > segmentAlphaConsts.clampMaxTime) ? segmentAlphaConsts.minAlpha / 2
            : linearInterpolate(
              segmentAlphaConsts.maxAlpha,
              segmentAlphaConsts.minAlpha,
              (clampedDt - segmentAlphaConsts.clampMinTime) / (segmentAlphaConsts.clampMaxTime - segmentAlphaConsts.clampMinTime)
            )

    // To utilize @typescript-eslint/switch-exhaustiveness-check rule, we use switch here
    // instead of more straightforward dictionary method.
    let logTooltip: string
    switch (log.logType) {
      case 'again':
        logTooltip = 'Wrong'
        break
      case 'good':
        logTooltip = 'Correct'
        break
      case 'new':
        logTooltip = 'New card'
        break
      case 'rev-good':
        logTooltip = '(Review) Correct'
        break
      case 'rev-again':
        logTooltip = '(Review) Wrong'
        break
      case 'unknown':
        logTooltip = '[unrecognized]'
        break
    }
    logTooltip = `${logTooltip} (${t2s(log.dt)})`

    pathSVGs.push(`
      <path class="rt-log-segment rt-log-${log.logType}" d="M${rectX} 0 h${rectW} V1 h-${rectW} Z" opacity="${rectAlpha}">
        <title>${logTooltip}</title>
      </path>`)

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
  return svgHtml
}
