import { Estimator } from '../estimator'
import { getRemainingReviews, getRemainingCardLoad as reviewLoad } from '../utils'
import { getAddonConfig } from '../utils/addonConfig'
import { getMessage } from './message'
import { getSVG } from './svg'
import { injectCSS } from './injectCSS'
import { getRtContainer, saveRtContainer } from './rtContainer'

// eslint-disable-next-line import/no-webpack-loader-syntax
const baseStyleCSS = require('!!raw-loader!sass-loader!../basestyle.scss').default as string

async function updateDOM (svgHtml: string, progressBarMessage: string) {
  const rtContainerEl = getRtContainer()
  await injectCSS(rtContainerEl)

  // Shadow DOM to isolate styling from external CSS
  const shadowRoot = rtContainerEl.shadowRoot || rtContainerEl.attachShadow({ mode: 'open' })
  const innerCSSText = baseStyleCSS + (await getAddonConfig('barCSS') || '')
  shadowRoot.innerHTML = `
  <div class='rt-container' id='rtContainer'>
    <style>${innerCSSText}</style>
    ${svgHtml}
    <div class='rt-message'>
      ${progressBarMessage}
      <a class='rt-reset' href=#resetRT title='Reset progress bar for this deck'>[⥻]</a>
    </div>
  </div>
  `

  // since shadow DOM isolates CSS hierarchy, we should manually add night mode classes
  // back to shadow dom root
  if (document.body.classList.contains('nightMode')) {
    rtContainerEl.classList.add('nightMode')
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    shadowRoot.getElementById('rtContainer')!.classList.add('nightMode')
  }

  // reset button
  const resetButton = shadowRoot.querySelector('.rt-reset')
  if (!resetButton) return
  const handler = async () => {
    if (confirm('[Remaining time] Press OK to reset the progress bar.')) {
      const estimator = await Estimator.instance()
      estimator.reset()
      estimator.save()
      renderProgressBar()
    }
  }
  // eslint-disable-next-line @typescript-eslint/camelcase
  (window as any)._3cc745f46701204a_click_reset_progress_bar = handler
  resetButton.addEventListener('click', handler)

  saveRtContainer(rtContainerEl)
}

export async function renderProgressBar () {
  const currentRemainingReviews = await getRemainingReviews()
  const remainingLoad = reviewLoad(currentRemainingReviews)
  const estimator = await Estimator.instance()
  const renderOptions = {
    fixedWidth: !!(await getAddonConfig('fixedSegmentWidth'))
  }

  const message = await getMessage(estimator, remainingLoad)
  const svgHtml = getSVG(estimator, remainingLoad, renderOptions)
  await updateDOM(svgHtml, message)
}
