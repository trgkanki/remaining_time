import { RemainingCardCounts } from '../utils'
import ankiPersistentStorage from './ankiPersistentStorage'

export const kLastRCC = '__rt__lastrcc__'

export async function getLastRCC (): Promise<RemainingCardCounts | null> {
  const s = await ankiPersistentStorage.getItem(kLastRCC)
  if (!s) return null
  return JSON.parse(s) as RemainingCardCounts
}

export function saveLastRCC (rcc: RemainingCardCounts) {
  ankiPersistentStorage.setItem(kLastRCC, JSON.stringify(rcc))
}
