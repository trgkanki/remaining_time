/* eslint-disable import/no-webpack-loader-syntax */
/* eslint-disable @typescript-eslint/no-var-requires */

import { updateEstimator } from './updater'
import { renderProgressBar } from './barRender'
import { callPyFunc } from './utils/pyfunc'
import { reinstateRtContainer, kRtDomSerializeB64 } from './barRender/rtContainer'
import { isAnkiDroid } from './utils/apiAnkiDroid'
import { Estimator, kRtEstimatorSchema } from './estimator'
import { getAddonConfig } from './utils/addonConfig'
import { now } from './utils'
import ankiLocalStorage from './utils/ankiLocalStorage'
import { kRtLastTime } from './isDoingReview'
import { kLastSeq } from './reviewLogger/desktopReviewLogger'
import { kAnkiDroidDeckRates } from './utils/deckRate'
import { kLastRCC } from './utils/lastRCC'

// All LocalStorage keys ever used by this addon. Kept here so gcStaleKeys can
// clean up chunk cookies left behind by any of them, including keys not used
// on this particular card/page.
const allLocalStorageKeys = [
  kRtDomSerializeB64,
  kRtEstimatorSchema,
  kRtLastTime,
  kLastSeq,
  kAnkiDroidDeckRates,
  kLastRCC
]

async function isQuestionSide (): Promise<boolean> {
  if (isAnkiDroid()) {
    const qaEl = document.getElementById('qa')
    return !!(qaEl && !qaEl.classList.contains('answer'))
  } else {
    return callPyFunc('isQuestionSide')
  }
}

async function isOverview (): Promise<boolean> {
  if (isAnkiDroid()) return false
  else return callPyFunc('isOverview')
}

// If the user has been away for a while (e.g. resuming reviews the next
// day), the persisted estimator's logs are stale and would otherwise report
// a huge/misleading elapsed time. Reset it before it's used for anything.
async function resetEstimatorIfIdle () {
  const idleThreshold = (await getAddonConfig('autoResetIdleSeconds')) as number
  if (idleThreshold <= 0) return

  const estimator = await Estimator.instance()
  if (now() - estimator.lastActivityEpoch > idleThreshold) {
    estimator.reset()
    estimator.save()
  }
}

// eslint-disable-next-line no-inner-declarations
async function main () {
  ankiLocalStorage.gcStaleKeys(allLocalStorageKeys)
  if (await isQuestionSide() || await isOverview()) {
    await resetEstimatorIfIdle()
    await updateEstimator()
  }
  await renderProgressBar()
}

// Since rendering DOM from fresh state needs some time (0.05s or so), the bar
// may not be ready on initial DOM rendering, which results flickering. To prevent
// that, upon rendering we have the rendered result to some fast storage and
// use that as a placeholder on the next rendering.
reinstateRtContainer()
  .finally(() => {
  // after that we start a real rendering. Rendering doesn't take too long (less
  // than 0.1s) so the placeholder won't interfere the user too much.
    main()
  })
