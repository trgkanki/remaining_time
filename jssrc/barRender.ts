import $ from 'jquery'

import { Estimator } from './estimator'
import { getRemainingReviews, t2s, getRemainingCardLoad as reviewLoad } from './utils'
import { Base64 } from 'js-base64'

import './basestyle.scss'

// Drawing settings
const clampMinTime = 10
const clampMaxTime = 120
const minAlpha = 0.3
const maxAlpha = 0.7

const againColor = '239, 103, 79' // Again
const goodColor = '114, 166, 249' // Good/Easy

// TODO: support dark mode
const backgroundColor = 'black'

function updateDOM (b64svg: string, progressBarMessage: string) {
  let $barEl = $('#remainingTimeBar')
  if ($barEl.length === 0) {
    $barEl = $('<div></div>')
    $barEl.attr('id', 'remainingTimeBar')
    $('body').append($barEl)
  }

  // TODO: port _rt_pgreset to JS space
  $barEl.html(`${progressBarMessage} &nbsp; <a href=#resetRT onclick="pycmd('_rt_pgreset');return false;" title='Reset progress bar for this deck'>[⥻]</a>`)

  let styleEl = document.getElementById('remainingTimeStylesheet')
  if (!styleEl) {
    styleEl = document.createElement('style')
    styleEl.id = 'remainingTimeStylesheet'
    document.head.appendChild(styleEl)
  }
  styleEl.textContent = `
    #remainingTimeBar {
      background: url('data:image/svg+xml;base64,${b64svg}')
    }
  `
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

  const b64svg = Base64.encode(`
  <svg width="1" height="1" xmlns="http://www.w3.org/2000/svg">
      <path d="M0 0 h1 V1 h-1 Z" fill="${backgroundColor}" />
      ${pathSVGs.join('')}
  </svg>
  `)
  updateDOM(b64svg, message)
}
