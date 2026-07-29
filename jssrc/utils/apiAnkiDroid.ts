const jsApiContract = { version: '0.0.3', developer: 'phu54321@naver.com' }

export function isAnkiDroid (): boolean {
  return typeof AnkiDroidJS !== 'undefined'
}

let cachedApi: AnkiDroidJS | null = null

export function getAnkiDroidApi (): AnkiDroidJS {
  if (!cachedApi) cachedApi = new AnkiDroidJS(jsApiContract)
  return cachedApi
}
