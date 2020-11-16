import pako from 'pako'

export function pakob64Deflate (payload: string) {
  return btoa(pako.deflate(payload, { to: 'string' }))
}

export function pakob64Inflate (payload: string) {
  return pako.inflate(atob(payload), { to: 'string' })
}
