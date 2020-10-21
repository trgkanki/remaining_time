/* eslint-disable import/no-webpack-loader-syntax */
/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable @typescript-eslint/camelcase */

import { getAddonConfig } from './utils/addonConfig'

const rtbarTopCSS = require('!!raw-loader!./res/rtbar-top.css').default as string
const rtbarBottomCSS = require('!!raw-loader!./res/rtbar-bottom.css').default as string

(function () {
  const windowAny = window as any
  if (!windowAny.__rtt_initialized) {
    windowAny.__rtt_initialized = true

    // Import needed modules here, as importing them outside duplicate import check
    // might multiple-import css or event handlers.
    const { updateEstimator } = require('./updater')
    const { updateProgressBar } = require('./barRender')

    // eslint-disable-next-line no-inner-declarations
    async function main () {
      // showAtBottom implementation
      // note: Anki overwrites document.body.classList right after the HTML is loaded,
      // so we cannot just add classname to body for UI styling.
      const injectedCSS = (await getAddonConfig('showAtBottom')) ? rtbarBottomCSS : rtbarTopCSS
      let style = document.getElementById('rt-vertical-positioner')
      if (!style) {
        style = document.createElement('style')
        style.id = 'rt-vertical-positioner'
        document.head.appendChild(style)
      }
      style.innerHTML = injectedCSS

      // ignore running on answer side.
      // updateEstimator thinks the user got the question wrong if new/lrn/rev
      // haven't changed after the last updateEstimator() call. (which can happen
      // if you got the learning card wrong) So if updateEstimator gets called
      // both on question side and answer side, the time you spent thinking
      // the question will be regarded as 'wrong', polluting progress bar graphics
      //
      // Also, on AnkiDroid #qa has 'question' and 'answer' class name, but on desktop
      // #qa has neither of them. Hence we check the absence of .answer. On desktop
      // main() will be called only on question side anyway.
      const qaEl = document.getElementById('qa')
      if (qaEl && !qaEl.classList.contains('answer')) {
        await updateEstimator()
      }
      await updateProgressBar()
    }

    // AnkiDroid: to main() for each card review, we hook onPageFinished function
    if (windowAny.onPageFinished) {
      const _old = windowAny.onPageFinished
      windowAny.onPageFinished = function (...args: any[]) {
        _old(...args)
        main()
      }
      main()
    }

    // on desktop, main() will be called on Python side.
    if (windowAny._showQuestion) {
      const _old = windowAny._showQuestion
      windowAny._showQuestion = function (...args: any[]) {
        _old(...args)
        main()
      }
      main()
    }
  }
})()
