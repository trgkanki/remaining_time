import { callPyFunc } from './pyfunc'
import ankiLocalStorage from './ankiLocalStorage'

// EMA blend weight for folding this sitting's observed pace into the
// persisted per-deck rate - a slow blend, since this is meant to represent
// the deck's long-run pace across sittings, not just the current one.
const emaDecay = 0.9

export interface DeckRates {
  new?: number;
  rev?: number;
}

export async function getCurrentDeckName (): Promise<string | null> {
  if ((window as any).AnkiDroidJS) {
    return AnkiDroidJS.ankiGetDeckName()
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

export function blendDeckRate (oldRate: number | undefined, currentSlope: number): number {
  if (oldRate === undefined) return currentSlope
  return emaDecay * oldRate + (1 - emaDecay) * currentSlope
}

// TODO: verify if ankidroid persists local storage
// Desktop's ankiLocalStorage implementation is not persistent across
// Anki restarts: use separate backend for storage.
const kAnkiDroidDeckRates = '__rt__deckrates__'

async function getDeckRateStore (): Promise<Record<string, DeckRates>> {
  if ((window as any).AnkiDroidJS) {
    const s = await ankiLocalStorage.getItem(kAnkiDroidDeckRates)
    return s ? JSON.parse(s) : {}
  }
  return (await callPyFunc('getDeckRateConfig')) || {}
}

async function setDeckRateStore (rates: Record<string, DeckRates>): Promise<void> {
  if ((window as any).AnkiDroidJS) {
    await ankiLocalStorage.setItem(kAnkiDroidDeckRates, JSON.stringify(rates))
    return
  }
  await callPyFunc('setDeckRateConfig', rates)
}
