/* eslint-disable @typescript-eslint/camelcase */

import { updateEstimator } from './updator'
import { updateProgressBar } from './barRender'

async function run () {
  await updateEstimator()
  await updateProgressBar()
}

(function () {
  const windowAny = window as any
  if (!windowAny.__rtt_initialized) {
    windowAny.__rtt_initialized = true
    windowAny.__rtt_run = run

    // Ankidroid: hook onPageFinished function
    if (windowAny.onPageFinished) {
      const oldOnPageFinished = windowAny.onPageFinished
      windowAny.onPageFinished = function (...args: any[]) {
        oldOnPageFinished(...args)
        run()
      }
    }
  }
})()
