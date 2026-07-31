export function cookieSet (key: string, value: string) {
  // Assigning to document.cookie only sets/updates this one cookie; it does not
  // clear or overwrite other existing cookies, despite looking like a full overwrite.
  document.cookie = `${encodeURIComponent(key)}=${encodeURIComponent(value)}; path=/`
}

export function cookieGet (key: string): string | undefined {
  const prefix = `${encodeURIComponent(key)}=`
  const match = document.cookie.split('; ').find(row => row.startsWith(prefix))
  return match ? decodeURIComponent(match.slice(prefix.length)) : undefined
}

export function cookieDelete (key: string) {
  document.cookie = `${encodeURIComponent(key)}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC`
}

export function cookieKeys (): string[] {
  return document.cookie
    .split('; ')
    .filter(row => row.length > 0)
    .map(row => decodeURIComponent(row.slice(0, row.indexOf('='))))
}
