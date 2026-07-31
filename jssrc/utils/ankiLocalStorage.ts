/**
 * ankiLocalStorage: cross-platform localStorage implementation.
 *
 * Local storage is not supported on dataURIs, which is used on desktop Anki. Hence
 * we need an alternative backend for desktop Anki. `ankiLocalStorage.py`
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

/**
 * Garbage-collect stale chunk cookies for the given LocalStorage keys.
 * Useful for a one-off sweep to clean up chunks left behind by versions of
 * this module that predate splitCookieSave's own gc-on-save behavior.
 *
 * @param keys LocalStorage keys to sweep
 */
function gcStaleKeys (keys: string[]) {
  if (!isAnkiDroid()) return
  for (const key of keys) {
    gcChunksAbove(key, chunkTerminatorIndex(key))
  }
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
  gcStaleKeys
}
