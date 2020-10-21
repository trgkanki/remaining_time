import { callPyFunc } from './pyfunc'
import { getAddonConfig } from './addonConfig'
import isMobile from 'is-mobile'

export async function debugLog (format: string, ...args: any[]): Promise<void> {
  if (!isMobile() && await getAddonConfig('debug')) {
    return callPyFunc('log', format, ...args)
  }
}
