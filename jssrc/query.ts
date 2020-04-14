import { getCaretParentElement, getCaretCharacterOffsetWithin, setCursorAt } from './caret'
import $ from 'jquery'

function getWordStart (text: string, from: number, allowTrailingSpaces = false): number[] | null {
  var endedWithAlphabet = false
  var j = from - 1
  var spaces = 0
  if (allowTrailingSpaces) {
    for (; j >= 0; j--) {
      if (text.charAt(j) !== ' ') break
    }
    spaces = (from - 1) - j
  }
  for (; j >= 0; j--) {
    var ch = text.charAt(j)
    if (
      (ch >= 'a' && ch <= 'z') ||
      (ch >= 'A' && ch <= 'Z')
    ) {
      endedWithAlphabet = true
      continue
    } else if (ch >= '0' && ch <= '9') {
      endedWithAlphabet = false
      continue
    } else break
  }
  if (!endedWithAlphabet) return null
  else if (allowTrailingSpaces) return [j + 1, spaces]
  else return [j + 1, -1]
}

// https://github.com/gr2m/contenteditable-autocomplete
export function getCurrentQuery (): string | null {
  var container = getCaretParentElement()
  if (!container) return null
  var $container = $(container)
  var cursorAt = getCaretCharacterOffsetWithin(container)
  var text = $container.text()
  var wordStart = getWordStart(text, cursorAt)
  if (wordStart == null) return null
  return text.substring(wordStart[0], cursorAt)
}

// https://github.com/gr2m/contenteditable-autocomplete
export function replaceCurrentQuery (newText: string): void {
  var container = getCaretParentElement()
  if (!container) return

  var cursorAt = getCaretCharacterOffsetWithin(container)
  var text = container.textContent || ''
  var ws = getWordStart(text, cursorAt, true)
  if (ws == null) return
  const [wordStart, spaces] = ws
  for (var i = 0; i < spaces; i++) newText += ' '

  // First of oldText is capital → Capitalize
  var oldText = text.substring(wordStart, cursorAt)
  if (oldText.charAt(0) === oldText.charAt(0).toUpperCase()) { // A-Z
    newText = newText.substring(0, 1).toUpperCase() + newText.substring(1)
  }
  var repText =
              text.substring(0, wordStart) +
              newText +
              text.substring(cursorAt)
  container.textContent = repText
  setCursorAt(container, wordStart + newText.length)
}
