import { callPyFunc } from './pyfunc'
import { getAddonConfig } from './addonConfig'
import { isAnkiDroid } from './apiAnkiDroid'

export async function debugLog (s: string): Promise<void> {
  if (await getAddonConfig('debug')) {
    console.log(s)
    if (!isAnkiDroid()) {
      return callPyFunc('log', s)
    }
  }
}
