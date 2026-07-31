import ankiPersistentStorage from '../utils/ankiPersistentStorage'
import { callPyFunc } from '../utils/pyfunc'
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

export const kLastSeq = '__rt__lastseq__'

async function getLastSeq (): Promise<number> {
  const s = await ankiPersistentStorage.getItem(kLastSeq)
  return s ? Number(s) : 0
}

function saveLastSeq (seq: number) {
  ankiPersistentStorage.setItem(kLastSeq, seq.toString())
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
          logType: classify(event)
        })
      }
    }

    saveLastSeq(maxSeq)
    return instructions
  }
}
