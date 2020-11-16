import { callPyFunc } from './utils/pyfunc'

export interface RemainingCardCounts {
  nu: number;
  lrn: number;
  rev: number;
}

export async function getRemainingReviews (): Promise<RemainingCardCounts> {
  if ((window as any).AnkiDroidJS) {
    const nu = Number(AnkiDroidJS.ankiGetNewCardCount())
    const lrn = Number(AnkiDroidJS.ankiGetLrnCardCount())
    const rev = Number(AnkiDroidJS.ankiGetRevCardCount())
    return { nu, lrn, rev }
  } else {
    const [nu, lrn, rev] = await callPyFunc('getCurrentRemainingCardCount')
    return { nu, lrn, rev }
  }
}

export async function getCurrentCardId (): Promise<number> {
  if ((window as any).AnkiDroidJS) {
    return AnkiDroidJS.ankiGetCardId()
  } else {
    return callPyFunc('getCurrentCardId')
  }
}

export function getRemainingCardLoad ({ nu, lrn, rev }: RemainingCardCounts) {
  return nu * 2 + lrn + rev
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
