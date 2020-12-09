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
 * Split payload to smaller chunks for compatibility w/ ankiDroid, which has
 * 6kb cookie limit per cookie value.
 *
 * @param key LocalStorage key to save
 * @param payload Payload to save
 */
async function splitSave (key: string, payload: string) {
  const packetSize = 4096
  let packetIndex = 0
  for (let i = 0; i < payload.length; i += packetSize) {
    const packet = payload.slice(i, i + packetSize)
    ankiLocalStorage.setItem(`${key}_${packetIndex}`, packet)
    packetIndex++
  }
  ankiLocalStorage.setItem(`${key}_${packetIndex}`, '')
}

/**
 * Load things saved with splitSave.
 *
 * @param key LocalStorage key to save
 * @returns Concatenated payload. If payload hasn't been saved, return empty string.
 */
async function splitLoad (key: string): Promise<string> {
  const chunks: string[] = []
  for (let packetIndex = 0; ; packetIndex++) {
    const chunk = await ankiLocalStorage.getItem(`${key}_${packetIndex}`)
    if (!chunk) break
    chunks.push(chunk)
  }
  return chunks.join('')
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
  splitSave(kRtDomSerializeB64, pakob64Deflate(payload))
}

/**
 * Restore saved DOM from localStorage.
 */
export async function reinstateRtContainer (): Promise<boolean> {
  const rtContainerEl = getRtContainer()
  const payload = await splitLoad(kRtDomSerializeB64)
  if (payload) {
    const { innerHTML, shadowHtml } = JSON.parse(pakob64Inflate(payload))
    rtContainerEl.innerHTML = innerHTML
    const shadowRoot = rtContainerEl.shadowRoot || rtContainerEl.attachShadow({ mode: 'open' })
    shadowRoot.innerHTML = shadowHtml
    return true
  } else return false
}
