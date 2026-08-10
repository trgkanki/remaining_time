import { callPyFunc } from './pyfunc'
import ankiPersistentStorage from './ankiPersistentStorage'
import { isAnkiDroid, getAnkiDroidApi } from './apiAnkiDroid'

// A category's running pace as a pure exponential smoother's raw
// accumulator (decayed weighted seconds / decayed weighted count), rather
// than a plain rate number - keeping both halves lets a fresh sitting keep
// decaying this exact state instead of re-blending a derived rate through a
// second, separately-tuned smoother.
export interface RateState {
  weightedTime: number;
  weightedCount: number;
}

export interface DeckRates {
  new?: RateState;
  rev?: RateState;
}

export async function getCurrentDeckName (): Promise<string | null> {
  if (isAnkiDroid()) {
    return (await getAnkiDroidApi().ankiGetDeckName()).value
  } else {
    return callPyFunc('getCurrentDeckName')
  }
}

function isRateState (value: unknown): value is RateState {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as RateState).weightedTime === 'number' &&
    typeof (value as RateState).weightedCount === 'number'
  )
}

function sanitizeDeckRates (raw: unknown): DeckRates {
  // old schema (storing raw number instead of object) -> ignore
  if (typeof raw !== 'object' || raw === null) return {}

  const { new: newRate, rev: revRate } = raw as DeckRates
  return {
    new: isRateState(newRate) ? newRate : undefined,
    rev: isRateState(revRate) ? revRate : undefined
  }
}

export async function getDeckRates (deckName: string): Promise<DeckRates | null> {
  const store = await getDeckRateStore()
  return store[deckName] ? sanitizeDeckRates(store[deckName]) : null
}

export async function saveDeckRates (deckName: string, rates: DeckRates): Promise<void> {
  const store = await getDeckRateStore()
  store[deckName] = { ...sanitizeDeckRates(store[deckName]), ...rates }
  await setDeckRateStore(store)
}

export const kDeckRates = '__rt__deckrates__'

async function getDeckRateStore (): Promise<Record<string, DeckRates>> {
  const s = await ankiPersistentStorage.getItem(kDeckRates)
  return s ? JSON.parse(s) : {}
}

async function setDeckRateStore (rates: Record<string, DeckRates>): Promise<void> {
  await ankiPersistentStorage.setItem(kDeckRates, JSON.stringify(rates))
}
