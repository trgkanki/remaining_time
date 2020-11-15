/* eslint-disable import/no-webpack-loader-syntax */
/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable @typescript-eslint/camelcase */

import { updateEstimator } from './updater'
import { renderProgressBar } from './barRender'
import isMobile from 'is-mobile'
import { callPyFunc } from './utils/pyfunc'
import { reinstateRtContainer } from './barRender/rtContainer'

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

// Since rendering DOM from fresh state needs some time (0.05s or so), the bar
// may not be ready on initial DOM rendering, which results flickering. To prevent
// that, upon rendering we ave the rendered result to some fast storage and
// use that as a placeholder on the next rendering.
reinstateRtContainer()
  .finally(() => {
  // after that we start a real rendering. Rendering doesn't take too long (less
  // than 0.1s) so the placeholder won't interfere the user too much.
    main()
  })
