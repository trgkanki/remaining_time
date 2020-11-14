/* eslint-disable import/no-webpack-loader-syntax */
/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable @typescript-eslint/camelcase */

import { getAddonConfig } from './utils/addonConfig'
import { updateEstimator } from './updater'
import { updateProgressBar } from './barRender'
import isMobile from 'is-mobile'
import { callPyFunc } from './utils/pyfunc'

const rtbarTopCSS = require('!!raw-loader!./res/rtbar-top.css').default as string
const rtbarBottomCSS = require('!!raw-loader!./res/rtbar-bottom.css').default as string

async function isQuestionSide (): Promise<boolean> {
  // AnkiDroid
  if (isMobile()) {
    const qaEl = document.getElementById('qa')
    return !!(qaEl && !qaEl.classList.contains('answer'))
  } else {
    return callPyFunc('isQuestionSide')
  }
}

async function injectVerticalAlignCSS () {
  // showAtBottom implementation
  // note: Anki overwrites document.body.classList right after the HTML is loaded,
  // so we cannot just add classname to body for UI styling.
  // we need to manually inject appropriate stylesheet based on user config.
  const injectedCSS = (await getAddonConfig('showAtBottom')) ? rtbarBottomCSS : rtbarTopCSS
  let style = document.getElementById('rt-vertical-positioner')
  if (!style) {
    style = document.createElement('style')
    style.id = 'rt-vertical-positioner'
    document.head.appendChild(style)
  }
  style.innerHTML = injectedCSS
}

// eslint-disable-next-line no-inner-declarations
async function main () {
  await injectVerticalAlignCSS()

  if (await isQuestionSide()) {
    await updateEstimator()
  }
  await updateProgressBar()
}

main()
