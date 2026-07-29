/* eslint-disable camelcase */

declare function pycmd (cmd: string, resultCallback?: (arg: any) => void): any
declare const ADDON_UUID: string

interface AnkiDroidApiResult<T> {
  success: boolean;
  value: T;
}

declare class AnkiDroidJS {
  constructor (contract: { version: string; developer: string });
  ankiGetNewCardCount(): Promise<AnkiDroidApiResult<number>>;
  ankiGetLrnCardCount(): Promise<AnkiDroidApiResult<number>>;
  ankiGetRevCardCount(): Promise<AnkiDroidApiResult<number>>;
  ankiGetCardId(): Promise<AnkiDroidApiResult<number>>;
  ankiGetDeckName(): Promise<AnkiDroidApiResult<string>>;
}
