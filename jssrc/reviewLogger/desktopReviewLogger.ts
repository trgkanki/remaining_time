import { getRemainingCardLoad, getRemainingReviews } from '../utils'
import ankiLocalStorage from '../utils/ankiLocalStorage'
import { callPyFunc } from '../utils/pyfunc'
import { getLastRCC, saveLastRCC } from '../utils/lastRCC'
import { EstimatorInst, InstLogType, ReviewLogger, RCCTConst } from './types'

interface AnswerEvent {
  seq: number;
  kind: 'answer';
  ease: 1 | 2 | 3 | 4;
  wasNew: boolean;
  wasLearning: boolean;
  wasReview: boolean;
}

interface UndoEvent {
  seq: number;
  kind: 'undo';
}

type ReviewEvent = AnswerEvent | UndoEvent

const kLastSeq = '__rt__lastseq__'

async function getLastSeq (): Promise<number> {
  const s = await ankiLocalStorage.getItem(kLastSeq)
  return s ? Number(s) : 0
}

function saveLastSeq (seq: number) {
  ankiLocalStorage.setItem(kLastSeq, seq.toString())
}

function classify (event: AnswerEvent): InstLogType {
  if (event.wasNew) return 'new'
  if (event.wasLearning) return event.ease === 1 ? 'again' : 'good'
  if (event.wasReview) return event.ease === 1 ? 'rev-again' : 'rev-good'
  return 'unknown'
}

export class DesktopReviewLogger implements ReviewLogger {
  async poll (): Promise<EstimatorInst[]> {
    const sinceSeq = await getLastSeq()
    const events = await callPyFunc('getNewAnswerEvents', sinceSeq) as ReviewEvent[]
    if (events.length === 0) return []

    // dy still comes from the RCC-load diff (not guesswork - already correctly
    // reflects real load removed, incl. edge cases like bury-related new-card
    // decrements). Normally exactly one 'answer' event is drained per poll; on
    // the rare occasion multiple land in one batch, split the observed dy
    // across them rather than double-counting it on each.
    const currentRemainingCards = await getRemainingReviews()
    const prevRemainingCards = await getLastRCC()
    saveLastRCC(currentRemainingCards)

    const totalDy = prevRemainingCards
      ? getRemainingCardLoad(prevRemainingCards) - getRemainingCardLoad(currentRemainingCards)
      : 0
    const answerEventCount = events.filter(e => e.kind === 'answer').length
    const dyPerAnswer = answerEventCount > 0 ? totalDy / answerEventCount : 0

    let maxSeq = sinceSeq
    const instructions: EstimatorInst[] = []
    for (const event of events) {
      maxSeq = Math.max(maxSeq, event.seq)
      if (event.kind === 'undo') {
        instructions.push({ instType: RCCTConst.UNDO })
      } else {
        instructions.push({
          instType: RCCTConst.UPDATE,
          reviewHash: event.seq,
          dy: dyPerAnswer,
          logType: classify(event)
        })
      }
    }

    saveLastSeq(maxSeq)
    return instructions
  }
}
