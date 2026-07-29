import { callPyFunc } from './pyfunc'
import ankiLocalStorage from './ankiLocalStorage'

// EMA blend weight for folding this sitting's observed pace into the
// persisted per-deck rate - a slow blend, since this is meant to represent
// the deck's long-run pace across sittings, not just the current one.
const emaDecay = 0.9

export async function getCurrentDeckName (): Promise<string | null> {
  if ((window as any).AnkiDroidJS) {
    return AnkiDroidJS.ankiGetDeckName()
  } else {
    return callPyFunc('getCurrentDeckName')
  }
}

export async function getDeckRate (deckName: string): Promise<number | null> {
  const rates = await getDeckRateStore()
  return rates[deckName] ?? null
}

export async function saveDeckRate (deckName: string, rate: number): Promise<void> {
  const rates = await getDeckRateStore()
  rates[deckName] = rate
  await setDeckRateStore(rates)
}

export function blendDeckRate (oldRate: number | null, currentSlope: number): number {
  if (oldRate === null) return currentSlope
  return emaDecay * oldRate + (1 - emaDecay) * currentSlope
}

// TODO: verify if ankidroid persists local storage
// Desktop's ankiLocalStorage implementation is not persistent across
// Anki restarts: use separate backend for storage.
const kAnkiDroidDeckRates = '__rt__deckrates__'

async function getDeckRateStore (): Promise<Record<string, number>> {
  if ((window as any).AnkiDroidJS) {
    const s = await ankiLocalStorage.getItem(kAnkiDroidDeckRates)
    return s ? JSON.parse(s) : {}
  }
  return (await callPyFunc('getDeckRateConfig')) || {}
}

async function setDeckRateStore (rates: Record<string, number>): Promise<void> {
  if ((window as any).AnkiDroidJS) {
    await ankiLocalStorage.setItem(kAnkiDroidDeckRates, JSON.stringify(rates))
    return
  }
  await callPyFunc('setDeckRateConfig', rates)
}
