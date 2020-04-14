import { ranker } from './ranker'
import $ from 'jquery'
import { replaceCurrentQuery } from './query'

declare let currentField: Node | null
declare let wordSet: string[]

export function getAutocompleteList (needle: string, wordList: string[], callback: (candidates: string[]) => void): void {
  const N = wordList.length
  const acceptanceTable = new Array(N)
  const indirectSorter = new Array(N)

  const checkPerLoop = 1000
  let i = 0

  function checker (): void {
    for (let j = 0; j < checkPerLoop; j++) {
      if (i === wordList.length) {
        indirectSorter.sort(function (a, b) {
          return acceptanceTable[b] - acceptanceTable[a]
        })

        const ret = []
        for (i = 0; i < Math.min(N, 5); i++) {
          const idx = indirectSorter[i]
          if (acceptanceTable[idx] < 0) break
          ret.push(wordList[idx])
        }
        return callback(ret)
      }
      indirectSorter[i] = i
      acceptanceTable[i] = ranker(needle, wordList[i])
      i++
    }
    setTimeout(checker, 1)
  }
  setTimeout(checker, 1)
}

export function getAutoCompleterSpan (): JQuery<HTMLElement> {
  var $el = $('.wautocompleter')
  if ($el.length === 0) {
    $el = $('<span></span>')
      .css({
        margin: '.3em',
        padding: '.3em',
        'background-color': '#ddd',
        border: '1px solid black'
      })
      .addClass('wautocompleter')
      .appendTo('body')
  }
  return $el
}

export function clearAutocompleteSpan (): void {
  var $el = getAutoCompleterSpan()
  $el.data('autocomplete', null)
  $el.html('-------')
}

var isFindingAutocomplete = false
var anotherAutocompleteQueued: string | null = null
var issueAutocompleteQueued: number | null = null

export function queueAutocompleteIssue (index: number): void {
  if (!isFindingAutocomplete) issueAutocomplete(index)
  else issueAutocompleteQueued = index
}

export function issueAutocomplete (index: number): void {
  var $el = getAutoCompleterSpan()
  var candidates = $el.data('autocomplete')
  if (candidates == null) return // No autocomplete available.
  var candidateIndex = index
  if (candidates.length > candidateIndex) {
    replaceCurrentQuery($el.data('autocomplete')[candidateIndex])
    clearAutocompleteSpan()
  }
}

export function queueAutocomplete (query: string | null): void {
  if (isFindingAutocomplete) {
    anotherAutocompleteQueued = query
    return
  }

  function popTaskQueue (): void {
    if (issueAutocompleteQueued !== null) {
      // Wait for next autocomplete issue.
      if (issueAutocompleteQueued < 0) { // Already waited once.
        anotherAutocompleteQueued = null
        issueAutocompleteQueued += 1000 // Reset to positive
      }
      if (anotherAutocompleteQueued) {
        // Make negative → Wait for one more autocomplete query.
        issueAutocompleteQueued -= 1000
      } else {
        issueAutocomplete(issueAutocompleteQueued)
        issueAutocompleteQueued = null
      }
    }
    if (anotherAutocompleteQueued) {
      anotherAutocompleteQueued = null
      queueAutocomplete(anotherAutocompleteQueued)
    }
  }

  if (!(query && query.length >= 2)) {
    clearAutocompleteSpan()
    popTaskQueue()
    return
  }

  var $el = getAutoCompleterSpan()
  isFindingAutocomplete = true
  getAutocompleteList(query, wordSet, function (autocomplete) {
    if (autocomplete.length === 0 || !currentField) {
      clearAutocompleteSpan()
    } else {
      $el.css('display', 'inline-block')
      var html = "<b title='Press Tab'>" + autocomplete[0] + '</b>'
      for (var i = 1; i < autocomplete.length; i++) {
        html += " / <span title='Press Ctrl+" + i + "'>" + autocomplete[i] + '</span>'
      }
      $el.html(html)
      $el.data('autocomplete', autocomplete)
      $el.insertAfter(currentField)
    }
    isFindingAutocomplete = false
    popTaskQueue()
  })
}
