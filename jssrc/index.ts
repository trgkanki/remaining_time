import $ from 'jquery'
import { getAutoCompleterSpan, clearAutocompleteSpan, queueAutocompleteIssue, queueAutocomplete } from './autocomplete'
import { getCurrentQuery } from './query'
import * as KeyCode from './keyCode'

if (!window._wcInitialized) {
  let ctrlPressed = false

  window._wcInitialized = true
  $('body').on('keydown', '[contenteditable]', function (event) {
    const $el = getAutoCompleterSpan()

    if (event.keyCode === KeyCode.CTRL) ctrlPressed = true

    // Ctrl 1-9
    if (
      ctrlPressed &&
          (KeyCode.DIGIT_0 <= event.keyCode && event.keyCode <= KeyCode.DIGIT_9) &&
          $el.data('autocomplete')
    ) {
      queueAutocompleteIssue(event.keyCode - KeyCode.DIGIT_0)
      event.preventDefault()
      return
    }

    // ESC -> clear autocomplete
    if (event.keyCode === KeyCode.ESC && $el.data('autocomplete')) {
      clearAutocompleteSpan()
      event.preventDefault()
      return
    }

    // Tab
    if (event.keyCode === KeyCode.TAB && $el.data('autocomplete')) {
      queueAutocompleteIssue(0)
      event.preventDefault()
    }
  })

  $('body').on('input', '[contenteditable]', function (_event) {
    const query = getCurrentQuery()
    queueAutocomplete(query)
  })

  $('body').on('blur', '[contenteditable]', function (_event) {
    clearAutocompleteSpan()
  })

  $('body').on('keyup', '[contenteditable]', function (event) {
    if (event.keyCode === 17) {
      ctrlPressed = false
    }
  })
}
