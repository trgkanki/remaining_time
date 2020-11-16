/* eslint-disable camelcase */

declare function pycmd (cmd: string, resultCallback?: (arg: any) => void): any
declare const ADDON_UUID: string
declare const AnkiDroidJS: {
  init(): void;
  ankiGetNewCardCount(): string;
  ankiGetLrnCardCount(): string;
  ankiGetRevCardCount(): string;
  ankiGetCardId(): number;
}
