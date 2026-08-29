import { callPyFunc } from './pyfunc'
import ankiPersistentStorage from './ankiPersistentStorage'
import { isAnkiDroid } from './apiAnkiDroid'

// The deck's running pace as a pure exponential smoother's raw accumulator
// (decayed weighted seconds / decayed weighted work). Keeping both halves
// lets a fresh sitting continue the same state instead of re-blending a
// derived rate through a second, separately-tuned smoother.
export interface RateState {
  weightedTime: number;
  weightedWork: number;
}

interface DeckRateStore {
  schema: number;
  rates: Record<string, RateState>;
}

const DECK_RATE_SCHEMA_VERSION = 3

export async function getCurrentDeckName (): Promise<string | null> {
  if (isAnkiDroid()) {
    // Ankidroid don't expose a proper way to get currently reviewed deck.
    // ankiGetDeckName() returns individual reviewed card's deck, not the deck currently
    // being reviewed (ex: on studying deck w/ multiple subdecks, or custom study sessions)
    // Just consolidate everything to 'deck' here.
    return 'deck'
  } else {
    return callPyFunc('getCurrentDeckName')
  }
}

function isRateState (value: unknown): value is RateState {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as RateState).weightedTime === 'number' &&
    typeof (value as RateState).weightedWork === 'number'
  )
}

export async function getDeckRate (deckName: string): Promise<RateState | null> {
  const store = await getDeckRateStore()
  return store[deckName] ?? null
}

export async function saveDeckRate (deckName: string, rate: RateState): Promise<void> {
  const store = await getDeckRateStore()
  store[deckName] = rate
  await setDeckRateStore(store)
}

export const kDeckRates = '__rt__deckrates__'

async function getDeckRateStore (): Promise<Record<string, RateState>> {
  const s = await ankiPersistentStorage.getItem(kDeckRates)
  if (!s) return {}

  const value = JSON.parse(s) as Partial<DeckRateStore>
  if (value.schema !== DECK_RATE_SCHEMA_VERSION || typeof value.rates !== 'object' || value.rates === null) return {}

  return Object.fromEntries(
    Object.entries(value.rates).filter((entry): entry is [string, RateState] => isRateState(entry[1]))
  )
}

async function setDeckRateStore (rates: Record<string, RateState>): Promise<void> {
  await ankiPersistentStorage.setItem(kDeckRates, JSON.stringify({
    schema: DECK_RATE_SCHEMA_VERSION,
    rates
  }))
}
