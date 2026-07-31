import { callPyFunc } from './pyfunc'
import ankiPersistentStorage from './ankiPersistentStorage'
import { isAnkiDroid, getAnkiDroidApi } from './apiAnkiDroid'

// EMA blend weight for folding this sitting's observed pace into the
// persisted per-deck rate - a slow blend, since this is meant to represent
// the deck's long-run pace across sittings, not just the current one.
const emaDecay = 0.9

export interface DeckRates {
  new?: number;
  rev?: number;
}

export async function getCurrentDeckName (): Promise<string | null> {
  if (isAnkiDroid()) {
    return (await getAnkiDroidApi().ankiGetDeckName()).value
  } else {
    return callPyFunc('getCurrentDeckName')
  }
}

export async function getDeckRates (deckName: string): Promise<DeckRates | null> {
  const store = await getDeckRateStore()
  return store[deckName] ?? null
}

export async function saveDeckRates (deckName: string, rates: DeckRates): Promise<void> {
  const store = await getDeckRateStore()
  store[deckName] = { ...store[deckName], ...rates }
  await setDeckRateStore(store)
}

export function blendDeckRate (oldRate: number | undefined, currentRate: number): number {
  if (oldRate === undefined) return currentRate
  return emaDecay * oldRate + (1 - emaDecay) * currentRate
}

export const kDeckRates = '__rt__deckrates__'

async function getDeckRateStore (): Promise<Record<string, DeckRates>> {
  const s = await ankiPersistentStorage.getItem(kDeckRates)
  return s ? JSON.parse(s) : {}
}

async function setDeckRateStore (rates: Record<string, DeckRates>): Promise<void> {
  await ankiPersistentStorage.setItem(kDeckRates, JSON.stringify(rates))
}
