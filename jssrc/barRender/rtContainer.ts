import { pakob64Deflate, pakob64Inflate } from '../utils/pakob64'
import ankiLocalStorage from '../utils/ankiLocalStorage'

const kRtDomSerializeB64 = '_rt_dom_serialize_b64'

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

/**
 * Save current DOM hierarchy
 * @param rtContainerEl rtContainer element to save
 */
export function saveRtContainer (rtContainerEl: HTMLDivElement) {
  const innerHTML = rtContainerEl.innerHTML
  const shadowHtml = rtContainerEl.shadowRoot?.innerHTML

  const payload = JSON.stringify({
    innerHTML, shadowHtml
  })
  ankiLocalStorage.setItem(kRtDomSerializeB64, pakob64Deflate(payload))
}

/**
 * Restore saved DOM from localStorage.
 */
export async function reinstateRtContainer (): Promise<boolean> {
  const rtContainerEl = getRtContainer()
  const payload = await ankiLocalStorage.getItem(kRtDomSerializeB64)
  if (payload) {
    const { innerHTML, shadowHtml } = JSON.parse(pakob64Inflate(payload))
    rtContainerEl.innerHTML = innerHTML
    const shadowRoot = rtContainerEl.shadowRoot || rtContainerEl.attachShadow({ mode: 'open' })
    shadowRoot.innerHTML = shadowHtml
    return true
  } else return false
}
