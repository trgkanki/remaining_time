import { RemainingCardCounts } from '../utils'
import ankiLocalStorage from './ankiLocalStorage'

export const kLastRCC = '__rt__lastrcc__'

export async function getLastRCC (): Promise<RemainingCardCounts | null> {
  const s = await ankiLocalStorage.getItem(kLastRCC)
  if (!s) return null
  return JSON.parse(s) as RemainingCardCounts
}

export function saveLastRCC (rcc: RemainingCardCounts) {
  ankiLocalStorage.setItem(kLastRCC, JSON.stringify(rcc))
}
