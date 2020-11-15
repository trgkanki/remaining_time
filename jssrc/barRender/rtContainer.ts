import pako from 'pako'
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

  let payload = JSON.stringify({
    innerHTML, shadowHtml
  })
  // payload takes about 6kb, passing cookie limit which is used for AnkiDroid.
  // Hence we need to compress this.
  payload = pako.deflate(payload, { to: 'string' })
  payload = btoa(payload)

  ankiLocalStorage.setItem(kRtDomSerializeB64, payload)
}

/**
 * Restore saved DOM from localStorage.
 */
export async function reinstateRtContainer (): Promise<boolean> {
  const rtContainerEl = getRtContainer()
  let payload = await ankiLocalStorage.getItem(kRtDomSerializeB64)
  if (payload) {
    payload = atob(payload)
    payload = pako.inflate(payload, { to: 'string' })
    const { innerHTML, shadowHtml } = JSON.parse(payload)
    rtContainerEl.innerHTML = innerHTML
    const shadowRoot = rtContainerEl.shadowRoot || rtContainerEl.attachShadow({ mode: 'open' })
    shadowRoot.innerHTML = shadowHtml
    return true
  } else return false
}
