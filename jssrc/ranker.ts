const gapScoreHighCut = 3
const wordStartDistHighCut = 4

/**
 * Compute score of how probable `needle` would be candidate for fuzzy
 * matching of `haystack`
 */
export function ranker (needle: string, haystack: string): number {
  const haystackLength = haystack.length
  let inIndex = 0
  let score = 0

  needle = needle.toLowerCase()
  haystack = haystack.toLowerCase()

  for (let i = 0; i < needle.length; i++) {
    const ch = needle[i]
    const prevInIndex = inIndex

    // Find matching inIndex
    while (haystack[inIndex] !== ch) {
      inIndex++
      if (inIndex >= haystackLength) return -1 // Match failed
    }

    // Value smaller distance between match characters
    const gap = inIndex - prevInIndex
    const gapMul = Math.max(1, gapScoreHighCut - gap)
    const wsdMul = Math.max(1, wordStartDistHighCut - inIndex)
    score += 100 * gapMul * wsdMul
    inIndex++
  }

  if (haystackLength < 100) score += 100 - haystackLength

  return score
}
