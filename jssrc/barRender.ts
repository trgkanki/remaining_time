import $ from 'jquery'

import { Estimator } from './estimator'
import { getRemainingReviews, t2s, getRemainingCardLoad as reviewLoad } from './utils'

import './basestyle.scss'

// Drawing settings
const clampMinTime = 10
const clampMaxTime = 120
const minAlpha = 0.3
const maxAlpha = 0.7

const againColor = '239, 103, 79' // Again
const goodColor = '114, 166, 249' // Good/Easy

function updateDOM (svgHtml: string, progressBarMessage: string) {
  let $barEl = $('#rtContainer')
  if ($barEl.length === 0) {
    $barEl = $('<div></div>')
    $barEl.attr('id', 'rtContainer')
    $barEl.addClass('rt-container')
    $('body').append($barEl)
  }

  // TODO: port _rt_pgreset to JS space
  $barEl.html(`
    ${svgHtml}
    <div class='rt-message'>${progressBarMessage}</div>
    <a class='rt-reset' href=#resetRT onclick="pycmd('_rt_pgreset');return false;" title='Reset progress bar for this deck'>[⥻]</a>
  `)
}

export async function updateProgressBar () {
  const currentRemainingReviews = await getRemainingReviews()
  const remainingLoad = reviewLoad(currentRemainingReviews)
  if (remainingLoad === 0) return

  const estimator = await Estimator.instance()
  const elapsedTime = estimator.elapsedTime
  const remainingTime = remainingLoad / estimator.getSlope()
  const message = `Elapsed ${t2s(elapsedTime)},  Remaining ${t2s(remainingTime)}, Total ${t2s(elapsedTime + remainingTime)}`

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
    const rectColor = (log.ease === 1) ? againColor : goodColor
    pathSVGs.push(`<path d="M${rectX} 0 h${rectW} V1 h-${rectW} Z" fill="rgba(${rectColor}, ${rectAlpha})" shape-rendering="crispEdges" />`)
    rectX += rectW
  }

  const svgHtml = `
  <svg class='rt-bar' viewBox="0 0 1 1" preserveaspectratio="none" xmlns="http://www.w3.org/2000/svg">
      ${pathSVGs.join('')}
  </svg>
  `
  updateDOM(svgHtml, message)
}
