export function getRemainingReviews () {
  const nu = Number(AnkiDroidJS.ankiGetNewCardCount())
  const lrn = Number(AnkiDroidJS.ankiGetLrnCardCount())
  const rev = Number(AnkiDroidJS.ankiGetRevCardCount())
  return nu * 2 + rev + lrn
}
