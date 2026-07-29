import { callPyFunc } from './pyfunc'
import { getAddonConfig } from './addonConfig'
import { isAnkiDroid } from './apiAnkiDroid'

export async function debugLog (format: string, ...args: any[]): Promise<void> {
  if (!isAnkiDroid() && await getAddonConfig('debug')) {
    return callPyFunc('log', format, ...args)
  }
}
