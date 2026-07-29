import { callPyFunc } from './utils/pyfunc'
import { isAnkiDroid, getAnkiDroidApi } from './utils/apiAnkiDroid'

export interface RemainingCardCounts {
  nu: number;
  lrn: number;
  rev: number;
}

export async function getRemainingReviews (): Promise<RemainingCardCounts> {
  if (isAnkiDroid()) {
    const api = getAnkiDroidApi()
    const [nu, lrn, rev] = await Promise.all([
      api.ankiGetNewCardCount(),
      api.ankiGetLrnCardCount(),
      api.ankiGetRevCardCount()
    ])
    return { nu: nu.value, lrn: lrn.value, rev: rev.value }
  } else {
    const [nu, lrn, rev] = await callPyFunc('getCurrentRemainingCardCount')
    return { nu, lrn, rev }
  }
}

export async function getCurrentCardId (): Promise<number> {
  if (isAnkiDroid()) {
    return (await getAnkiDroidApi().ankiGetCardId()).value
  } else {
    return callPyFunc('getCurrentCardId')
  }
}

/**
 * Convert time duration to string
 *
 * @param time Time in seconds
 */
export function t2s (time: number) {
  if (time < 60) {
    return `${time | 0}s`
  } else if (time < 86400) {
    return `${Math.floor(time / 60) | 0}m`
  } else {
    return ' > day '
  }
}

/**
 * Current time in seconds
 */
export function now () {
  return new Date().getTime() / 1000
}
