export function getRemainingReviews () {
  const nu = Number(AnkiDroidJS.ankiGetNewCardCount())
  const lrn = Number(AnkiDroidJS.ankiGetLrnCardCount())
  const rev = Number(AnkiDroidJS.ankiGetRevCardCount())
  return nu * 2 + rev + lrn
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
