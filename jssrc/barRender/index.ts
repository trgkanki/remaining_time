import { Estimator } from '../estimator'
import { getRemainingReviews, getRemainingCardLoad as reviewLoad } from '../utils'
import { getAddonConfig } from '../utils/addonConfig'
import { getMessage } from './message'
import { getSVG } from './svg'
import { injectCSS } from './injectCSS'

// eslint-disable-next-line import/no-webpack-loader-syntax
const baseStyleCSS = require('!!raw-loader!sass-loader!../basestyle.scss').default as string

export function getRtContainer (): HTMLDivElement {
  let rtContainerEl = document.getElementById('rtContainer') as HTMLDivElement | null
  if (!rtContainerEl) {
    rtContainerEl = document.createElement('div')
    rtContainerEl.id = 'rtContainer'
    rtContainerEl.classList.add('rt-container')
    document.body.append(rtContainerEl)
  }
  return rtContainerEl
}

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
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    rtContainerEl.classList.add('nightMode')
  }

  // reset button
  const resetButton = shadowRoot.querySelector('.rt-reset')
  if (!resetButton) return
  resetButton.addEventListener('click', async () => {
    if (confirm('[Remaining time] Press OK to reset the progress bar.')) {
      const estimator = await Estimator.instance()
      estimator.reset()
      estimator.save()
      renderProgressBar()
    }
  })
}

export async function renderProgressBar () {
  const currentRemainingReviews = await getRemainingReviews()
  const remainingLoad = reviewLoad(currentRemainingReviews)
  if (remainingLoad === 0) return

  const estimator = await Estimator.instance()

  const message = await getMessage(estimator, remainingLoad)
  const svgHtml = getSVG(estimator, remainingLoad)
  await updateDOM(svgHtml, message)
}
