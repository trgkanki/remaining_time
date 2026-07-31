import { pakob64Deflate, pakob64Inflate } from '../utils/pakob64'

// Plain window.localStorage, not ankiPersistentStorage: this cache only needs
// to survive until the next card in the same session (see reinstateRtContainer
// below), not an Anki restart, and its payload size scales with note content
// instead of being small and fixed-format like everything ankiPersistentStorage
// manages. On AnkiDroid that combination used to make it the prime suspect for
// a JS-API bridge bug (as of 2026-07-31, AnkiServer.getSessionBytes can read a
// POST body short and corrupt it - more bytes riding along in the Cookie
// header on every request seemed to make this more likely), so this key was
// moved off the cookie-chunking backend entirely.
export const kRtDomSerializeB64 = '_rt_dom_serialize_b64'

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
  localStorage.setItem(kRtDomSerializeB64, pakob64Deflate(payload))
}

/**
 * Restore saved DOM from localStorage.
 */
export async function reinstateRtContainer (): Promise<boolean> {
  const rtContainerEl = getRtContainer()
  const payload = localStorage.getItem(kRtDomSerializeB64)
  if (payload) {
    const { innerHTML, shadowHtml } = JSON.parse(pakob64Inflate(payload))
    rtContainerEl.innerHTML = innerHTML
    const shadowRoot = rtContainerEl.shadowRoot || rtContainerEl.attachShadow({ mode: 'open' })
    shadowRoot.innerHTML = shadowHtml
    return true
  } else return false
}
