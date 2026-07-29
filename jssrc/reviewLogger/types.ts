/* eslint-disable no-unused-vars -- enum members are consumed from other modules */
export enum RCCTConst {
  RESET,
  UPDATE,
  IGNORE,
  UNDO
}

export interface InstReset {
  instType: RCCTConst.RESET;
}

export interface InstUndo {
  instType: RCCTConst.UNDO;
}

export interface InstIgnore {
  instType: RCCTConst.IGNORE;
}

export type InstLogType = 'new' | 'good' | 'again' | 'rev-good' | 'rev-again' | 'unknown'

export interface InstUpdate {
  instType: RCCTConst.UPDATE;
  reviewHash: number;
  dy: number;
  logType: InstLogType;
}

export type EstimatorInst = InstReset | InstIgnore | InstUpdate | InstUndo

/**
 * Figures out what happened to the review queue since the last poll, and
 * translates it into a list of instructions to apply to the Estimator.
 *
 * Mobile lacks any true per-card event source, so its implementation has to
 * guess from remaining-card-count diffs. Desktop can mirror true events from
 * python instead.
 */
export interface ReviewLogger {
  poll (): Promise<EstimatorInst[]>;
}
