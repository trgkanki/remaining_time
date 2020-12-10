/**
 * ankiLocalStorage: cross-platform localStorage implementation.
 *
 * Local storage is not supported on dataURIs, which is used on desktop Anki. Hence
 * we need an alternative backend for desktop Anki. `ankiLocalStorage.py`
 */

import isMobile from 'is-mobile'
import Cookies from 'js-cookie'
import { callPyFunc } from './pyfunc'

/**
 * Split payload to smaller chunks for compatibility w/ ankiDroid, which has
 * 6kb cookie limit per cookie value.
 *
 * @param key LocalStorage key to save
 * @param payload Payload to save
 */
function splitCookieSave (key: string, payload: string) {
  const packetSize = 4096
  let packetIndex = 0
  for (let i = 0; i < payload.length; i += packetSize) {
    const packet = payload.slice(i, i + packetSize)
    Cookies.set(`${key}_${packetIndex}`, packet)
    packetIndex++
  }
  Cookies.set(`${key}_${packetIndex}`, '')
}

/**
 * Load things saved with splitSave.
 *
 * @param key LocalStorage key to save
 * @returns Concatenated payload. If payload hasn't been saved, return empty string.
 */
function splitCookieLoad (key: string): string {
  const chunks: string[] = []
  for (let packetIndex = 0; ; packetIndex++) {
    const chunk = Cookies.get(`${key}_${packetIndex}`)
    if (!chunk) break
    chunks.push(chunk)
  }
  return chunks.join('')
}

export default {
  async setItem (key: string, data: string) {
    if (isMobile()) {
      splitCookieSave(key, data)
    } else {
      await callPyFunc('localStorageSetItem', key, data)
    }
  },
  async getItem (key: string): Promise<string | null> {
    if (isMobile()) {
      return splitCookieLoad(key) || null
    } else {
      return callPyFunc('localStorageGetItem', key)
    }
  },
  hasItem (key: string) {
    if (isMobile()) {
      return Cookies.get(key) !== undefined
    } else {
      return callPyFunc('localStorageHasItem', key)
    }
  }
}
