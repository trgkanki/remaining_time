/**
 * ankiPersistentStorage: cross-platform persistent storage, surviving Anki restarts.
 *
 * Desktop Anki's WebEngine no longer serves cards via data: URIs (see
 * `_setHtml` in aqt/webview.py upstream), so window.localStorage is
 * technically available there now - but its origin is a random port chosen
 * fresh on every Anki launch (see aqt/mediasrv.py's MediaServer), so anything
 * written to it is unreachable again after a restart. Hence desktop routes
 * through `ankiPersistentStorage.py`, backed by collection config, instead of
 * that per-launch origin.
 *
 * AnkiDroid has the same random-port problem for its reviewer's local server,
 * but real cookies are scoped by host only (not port), so they survive a
 * restart there - hence the split-into-chunks cookie backend below.
 *
 * NOT everything should go through this module, though: AnkiDroid's WebView
 * JS-API bridge has a bug (as of 2026-07-31) in AnkiServer.getSessionBytes
 * where a POST body can be read short, corrupting the request; the more
 * total bytes ride along in the Cookie header on every request to the
 * reviewer's origin, the likelier this seems to trigger. `kRtDomSerializeB64`
 * (rtContainer.ts's DOM snapshot cache) is the prime suspect - it's the one
 * key here whose payload size scales with note content instead of being a
 * small fixed-format value, so it was moved to plain window.localStorage
 * instead of this module. That's a safe move for that key specifically
 * because it's only ever used to avoid a same-session render flicker; losing
 * it on restart (or on any origin change) is harmless, unlike the other keys
 * this module manages.
 */

import { callPyFunc } from './pyfunc'
import { isAnkiDroid } from './apiAnkiDroid'
import { cookieSet, cookieGet, cookieDelete, cookieKeys } from './cookie'

// Deletes chunk cookies `${key}_N` for N past lastIndex. Not assumed to be
// contiguous with lastIndex - older, already-deployed versions of
// splitCookieSave didn't clean up after themselves, so gaps left over from
// past bugs/versions are possible. Left alone, stale chunks would keep
// riding along on every request's Cookie header forever.
function gcChunksAbove (key: string, lastIndex: number) {
  const chunkPrefix = `${key}_`
  for (const k of cookieKeys()) {
    if (!k.startsWith(chunkPrefix)) continue
    const idx = Number(k.slice(chunkPrefix.length))
    if (Number.isInteger(idx) && idx > lastIndex) {
      cookieDelete(k)
    }
  }
}

/**
 * Split payload to smaller chunks for compatibility w/ ankiDroid, which has
 * 6kb cookie limit per cookie value (after URI-encoding).
 *
 * @param key LocalStorage key to save
 * @param payload Payload to save
 */
function splitCookieSave (key: string, payload: string) {
  const packetSize = 1024
  let packetIndex = 0
  for (let i = 0; i < payload.length; i += packetSize) {
    const packet = payload.slice(i, i + packetSize)
    cookieSet(`${key}_${packetIndex}`, packet)
    packetIndex++
  }
  cookieSet(`${key}_${packetIndex}`, '')
  gcChunksAbove(key, packetIndex)
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
    const chunk = cookieGet(`${key}_${packetIndex}`)
    if (!chunk) break
    chunks.push(chunk)
  }
  return chunks.join('')
}

// Terminator index of a key's chunk sequence, i.e. the first missing/empty
// `${key}_N` chunk - same walk as splitCookieLoad, but only to find the index.
function chunkTerminatorIndex (key: string): number {
  let packetIndex = 0
  for (; cookieGet(`${key}_${packetIndex}`); packetIndex++);
  return packetIndex
}

export default {
  async setItem (key: string, data: string) {
    if (isAnkiDroid()) {
      splitCookieSave(key, data)
    } else {
      await callPyFunc('localStorageSetItem', key, data)
    }
  },
  async getItem (key: string): Promise<string | null> {
    if (isAnkiDroid()) {
      return splitCookieLoad(key) || null
    } else {
      return callPyFunc('localStorageGetItem', key)
    }
  },
  hasItem (key: string) {
    if (isAnkiDroid()) {
      return cookieGet(key) !== undefined
    } else {
      return callPyFunc('localStorageHasItem', key)
    }
  },
  /**
   * Garbage-collect stale chunk cookies for the given LocalStorage keys.
   * Useful for a one-off sweep to clean up chunks left behind by versions of
   * this module that predate splitCookieSave's own gc-on-save behavior.
   */
  gcStaleKeys (keys: string[]) {
    if (!isAnkiDroid()) return
    for (const key of keys) {
      gcChunksAbove(key, chunkTerminatorIndex(key))
    }
  },
  purgeKey (key: string) {
    if (isAnkiDroid()) {
      gcChunksAbove(key, -1)
    } else {
      return callPyFunc('localStoragePurgeItem', key)
    }
  }
}
