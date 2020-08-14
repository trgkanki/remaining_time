/**
 * ankiLocalStorage: cross-platform localStorage implementation.
 *
 * Local storage is not supported on dataURIs, which is used on desktop Anki. Hence
 * we need an alternative backend for desktop Anki. `ankiLocalStorage.py`
 */

import isMobile from 'is-mobile'
import Cookies from 'js-cookie'
import { callPyFunc } from './pyfunc'

export default {
  async setItem (key: string, data: string) {
    if (isMobile()) {
      Cookies.set(key, data)
    } else {
      await callPyFunc('localStorageSetItem', key, data)
    }
  },
  async getItem (key: string): Promise<string | null> {
    if (isMobile()) {
      return Cookies.get(key) || null
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
