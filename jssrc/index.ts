/* eslint-disable @typescript-eslint/camelcase */

import { updateEstimator } from './updator'
import { updateProgressBar } from './barRender'

async function main () {
  await updateEstimator()
  await updateProgressBar()
}

(function () {
  const windowAny = window as any
  if (!windowAny.__rtt_initialized) {
    windowAny.__rtt_initialized = true
    windowAny.__rtt_run = main

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
