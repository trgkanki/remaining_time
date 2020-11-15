/* eslint-disable import/no-webpack-loader-syntax */
/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable @typescript-eslint/camelcase */

import { updateEstimator } from './updater'
import { renderProgressBar } from './barRender'
import isMobile from 'is-mobile'
import { callPyFunc } from './utils/pyfunc'

async function isQuestionSide (): Promise<boolean> {
  // AnkiDroid
  if (isMobile()) {
    const qaEl = document.getElementById('qa')
    return !!(qaEl && !qaEl.classList.contains('answer'))
  } else {
    return callPyFunc('isQuestionSide')
  }
}

// eslint-disable-next-line no-inner-declarations
async function main () {
  if (await isQuestionSide()) {
    await updateEstimator()
  }
  await renderProgressBar()
}

main()
